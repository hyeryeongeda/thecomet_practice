from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.pagination import PageNumberPagination

from django.db.models import Q

from .models import Movie, Genre, Person, HomeSectionEntry
from .serializers import MovieListSerializer, MovieDetailSerializer, GenreSerializer, PersonSerializer
from .services.tmdb import fetch_movie_detail_and_update


class MoviePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 50


@api_view(["GET"])
@permission_classes([AllowAny])
def home(request):
    popular = (
        Movie.objects.filter(home_entries__section="POPULAR")
        .order_by("home_entries__rank")
        .prefetch_related("genres")
        [:20]
    )
    now_playing = (
        Movie.objects.filter(home_entries__section="NOW_PLAYING")
        .order_by("home_entries__rank")
        .prefetch_related("genres")
        [:20]
    )
    top_rated = (
        Movie.objects.filter(home_entries__section="TOP_RATED")
        .order_by("home_entries__rank")
        .prefetch_related("genres")
        [:20]
    )

    return Response({
        "popular": MovieListSerializer(popular, many=True).data,
        "now_playing": MovieListSerializer(now_playing, many=True).data,
        "top_rated": MovieListSerializer(top_rated, many=True).data,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def movie_list(request):
    """
    /api/movies/list/?sort=popular|latest|rating&genre=28&page=1
    - genre: Genre.tmdb_id
    """
    qs = Movie.objects.all().prefetch_related("genres")

    genre_tmdb_id = request.query_params.get("genre")
    if genre_tmdb_id:
        qs = qs.filter(genres__tmdb_id=int(genre_tmdb_id))

    sort = request.query_params.get("sort", "popular")
    if sort == "latest":
        qs = qs.order_by("-release_date", "-popularity")
    elif sort == "rating":
        qs = qs.order_by("-vote_average", "-vote_count")
    else:
        qs = qs.order_by("-popularity", "-vote_count")

    paginator = MoviePagination()
    page = paginator.paginate_queryset(qs, request)
    data = MovieListSerializer(page, many=True).data
    return paginator.get_paginated_response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def movie_detail(request, tmdb_id: int):
    movie = Movie.objects.filter(tmdb_id=tmdb_id).prefetch_related("genres").first()
    if not movie:
        return Response({"detail": "영화를 찾을 수 없습니다. TMDB 동기화를 먼저 실행하세요."}, status=status.HTTP_404_NOT_FOUND)

    # runtime/genres 등 상세가 비어있을 수 있으니, 요청 시 한 번 보정
    try:
        fetch_movie_detail_and_update(movie)
    except Exception:
        pass

    return Response(MovieDetailSerializer(movie).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def genre_list(request):
    qs = Genre.objects.all().order_by("name")
    return Response(GenreSerializer(qs, many=True).data)


@api_view(["GET"])
@permission_classes([AllowAny])
def search(request):
    """
    /api/movies/search/?q=...&type=movie|person
    """
    q = (request.query_params.get("q") or "").strip()
    search_type = request.query_params.get("type", "movie")

    if not q:
        return Response({"detail": "q가 비었습니다."}, status=status.HTTP_400_BAD_REQUEST)

    if search_type == "person":
        people = Person.objects.filter(name__icontains=q).order_by("name")[:30]
        return Response({"type": "person", "results": PersonSerializer(people, many=True).data})

    # default: movie
    movies = Movie.objects.filter(
        Q(title__icontains=q) | Q(original_title__icontains=q)
    ).prefetch_related("genres").order_by("-popularity")[:30]

    return Response({"type": "movie", "results": MovieListSerializer(movies, many=True).data})

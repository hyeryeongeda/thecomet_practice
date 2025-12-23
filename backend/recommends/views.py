from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q, Count, Avg, Prefetch
from movies.models import Movie, Genre, Person
from movies.serializers import MovieListSerializer, PersonSerializer

from reviews.models import Review
try:
    from reviews.models import ReviewLike
except Exception:
    ReviewLike = None

try:
    from accounts.models import Follow
except Exception:
    Follow = None

from .services.ai import run_taste_ai
from .models import TastePromptLog

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_taste(request):
    """
    POST /api/recommends/ai/
    body: { "message": "...", "history": [...] }
    """
    message = (request.data.get("message") or "").strip()
    history = request.data.get("history") or []

    if not message:
        return Response({"detail": "message가 비었습니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 1. AI 분석 수행
    data, raw = run_taste_ai(message, history=history)

    # 로그 저장
    try:
        TastePromptLog.objects.create(
            user=request.user,
            prompt=message,
            response_raw=raw,
            response_json=data if isinstance(data, dict) else None,
        )
    except Exception:
        pass

    # 2. 필터 추출
    filters = data.get("filters") or {}
    genre_names = filters.get("genre_names") or []
    keywords = filters.get("keywords") or []
    titles = filters.get("titles") or [] # AI가 찾은 영화 제목들
    min_vote = float(filters.get("min_vote") or 0)

    # 3. DB 쿼리 구성
    qs = Movie.objects.all().prefetch_related("genres")
    
    # [핵심] 검색 로직 강화: AI가 언급한 제목이 있거나, 장르/키워드 조건에 맞는 영화 찾기
    main_q = Q()

    # (A) 제목 매칭 (AI가 특정 영화를 추천했을 경우)
    if titles:
        for t in titles:
            main_q |= Q(title__icontains=t)

    # (B) 장르 및 키워드 매칭
    sub_q = Q()
    if genre_names:
        g_ids = list(Genre.objects.filter(name__in=genre_names).values_list("tmdb_id", flat=True))
        if g_ids:
            sub_q &= Q(genres__tmdb_id__in=g_ids)

    if keywords:
        k_q = Q()
        for k in keywords:
            k_q |= Q(title__icontains=k) | Q(overview__icontains=k)
        sub_q &= k_q

    # 최종 필터링: (제목 매칭) 또는 (장르&키워드 매칭)
    combined_q = main_q | sub_q
    if combined_q:
        qs = qs.filter(combined_q)

    if min_vote > 0:
        qs = qs.filter(vote_average__gte=min_vote)

    # 중복 제거 및 정렬 (인기순/평점순)
    qs = qs.distinct().order_by("-popularity", "-vote_average")[:12]

    return Response({
        "answer": data.get("answer", "조건에 맞는 영화를 찾아보았습니다."),
        "filters": filters,
        "movies": MovieListSerializer(qs, many=True).data,
    })

# --- 이하 기존 함수들 (변경 없음) ---

@api_view(["GET"])
@permission_classes([AllowAny])
def genre_recommend(request):
    genre_tmdb_id = request.query_params.get("genre")
    if not genre_tmdb_id:
        genres = Genre.objects.all().order_by("name")
        return Response({"genres": [{"tmdb_id": g.tmdb_id, "name": g.name} for g in genres]})
    qs = Movie.objects.filter(genres__tmdb_id=int(genre_tmdb_id)).prefetch_related("genres").order_by("-popularity")[:24]
    return Response({"results": MovieListSerializer(qs, many=True).data})

@api_view(["GET"])
@permission_classes([AllowAny])
def people_recommend(request):
    q = (request.query_params.get("q") or "").strip()
    if q:
        people = Person.objects.annotate(credits_count=Count("movies")).filter(name__icontains=q, credits_count__gt=0).order_by("-credits_count")[:30]
        return Response({"results": PersonSerializer(people, many=True).data})
    try:
        people = Person.objects.annotate(credits_count=Count("movies")).filter(credits_count__gt=0).order_by("-credits_count", "name")[:40]
    except Exception:
        people = Person.objects.filter(movies__isnull=False).distinct()[:20]
    return Response({"results": PersonSerializer(people, many=True).data})

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_recommend(request):
    User = get_user_model()
    me = request.user
    top_reviewers_raw = Review.objects.values("user_id").annotate(cnt=Count("id")).order_by("-cnt")[:10]
    reviewer_ids = [r["user_id"] for r in top_reviewers_raw]
    reviewer_cnt_map = {r["user_id"]: r["cnt"] for r in top_reviewers_raw}
    reviewers = list(User.objects.filter(id__in=reviewer_ids))
    top_liked_users = []
    if ReviewLike is not None:
        top_liked_raw = ReviewLike.objects.values("review__user_id").annotate(cnt=Count("id")).order_by("-cnt")[:10]
        liked_ids = [r["review__user_id"] for r in top_liked_raw]
        liked_cnt_map = {r["review__user_id"]: r["cnt"] for r in top_liked_raw}
        liked_users = list(User.objects.filter(id__in=liked_ids))
        top_liked_users = [{"id": u.id, "username": getattr(u, "username", ""), "received_likes": liked_cnt_map.get(u.id, 0)} for u in liked_users]
    suggested = []
    if Follow is not None:
        try:
            following_ids = set(Follow.objects.filter(follower=me).values_list("following_id", flat=True))
            base = User.objects.exclude(id=me.id).exclude(id__in=following_ids).annotate(reviews_count=Count("reviews")).order_by("-reviews_count")[:10]
            suggested = [{"id": u.id, "username": getattr(u, "username", ""), "reviews_count": getattr(u, "reviews_count", 0)} for u in base]
        except Exception: pass
    return Response({"top_reviewers": [{"id": u.id, "username": getattr(u, "username", ""), "reviews_count": reviewer_cnt_map.get(u.id, 0)} for u in reviewers], "top_liked": top_liked_users, "suggested": suggested})

GENRE_LABELS = ["드라마","SF","판타지","로맨스","뮤지컬","애니메이션","전쟁","가족","다큐멘터리","스릴러","공포","액션"]

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def taste_summary(request):
    me = request.user
    my_reviews_qs = Review.objects.filter(user=me).select_related("movie").order_by("-created_at")
    tmdb_ids = list(my_reviews_qs.values_list("movie__tmdb_id", flat=True).distinct())
    watched_count = len(tmdb_ids)
    if watched_count == 0:
        return Response({"watched_count": 0, "top_genre": "-", "avg_rating": 0, "recent_movie_title": "", "genre_scores": {}, "recommended_movies": [], "detail": "작성된 리뷰가 없습니다."})
    avg_rating = round(float(my_reviews_qs.aggregate(avg=Avg("rating"))["avg"] or 0), 1)
    latest_review = my_reviews_qs.first()
    recent_movie_title = latest_review.movie.title if latest_review else ""
    genre_rows = Movie.objects.filter(tmdb_id__in=tmdb_ids).values("genres__name").annotate(cnt=Count("genres__name")).order_by("-cnt")
    genre_count_map = {row["genres__name"]: row["cnt"] for row in genre_rows if row["genres__name"]}
    top_genres_sorted = sorted(genre_count_map.items(), key=lambda x: x[1], reverse=True)
    top_genre = "/".join([g for g, _ in top_genres_sorted[:2]]) if top_genres_sorted else "-"
    max_cnt = max(genre_count_map.values(), default=0)
    genre_scores = {label: int((genre_count_map.get(label, 0) / max_cnt) * 100) if max_cnt else 0 for label in GENRE_LABELS}
    top_genre_names = [g for g, _ in top_genres_sorted[:2]]
    rec_qs = Movie.objects.all().prefetch_related("genres")
    if top_genre_names: rec_qs = rec_qs.filter(genres__name__in=top_genre_names).distinct()
    if tmdb_ids: rec_qs = rec_qs.exclude(tmdb_id__in=tmdb_ids)
    rec_qs = rec_qs.order_by("-popularity")[:12]
    return Response({"watched_count": watched_count, "top_genre": top_genre, "avg_rating": avg_rating, "recent_movie_title": recent_movie_title, "genre_scores": genre_scores, "recommended_movies": MovieListSerializer(rec_qs, many=True).data})
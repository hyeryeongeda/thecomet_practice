from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

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
    return: { "answer": "...", "movies": [...], "filters": {...} }
    """
    message = (request.data.get("message") or "").strip()
    history = request.data.get("history") or []

    if not message:
        return Response({"detail": "message가 비었습니다."}, status=status.HTTP_400_BAD_REQUEST)

    data, raw = run_taste_ai(message, history=history)

    # 로그 저장(원치 않으면 이 블록 통째로 지워도 됨)
    try:
        TastePromptLog.objects.create(
            user=request.user,
            prompt=message,
            response_raw=raw,
            response_json=data if isinstance(data, dict) else None,
        )
    except Exception:
        pass

    filters = (data.get("filters") or {}) if isinstance(data, dict) else {}
    genre_names = filters.get("genre_names") or []
    keywords = filters.get("keywords") or []
    min_vote = float(filters.get("min_vote") or 0)

    qs = Movie.objects.all().prefetch_related("genres")

    # 장르 이름 -> Genre 매칭 -> movie filter
    if genre_names:
        gq = Q()
        for name in genre_names:
            gq |= Q(name__icontains=name)
        genre_tmdb_ids = list(Genre.objects.filter(gq).values_list("tmdb_id", flat=True))
        if genre_tmdb_ids:
            qs = qs.filter(genres__tmdb_id__in=genre_tmdb_ids).distinct()

    # 키워드 -> title/overview 검색
    if keywords:
        kq = Q()
        for k in keywords:
            kq |= Q(title__icontains=k) | Q(overview__icontains=k)
        qs = qs.filter(kq)

    if min_vote > 0:
        qs = qs.filter(vote_average__gte=min_vote)

    qs = qs.order_by("-vote_average", "-popularity")[:12]

    return Response({
        "answer": data.get("answer") if isinstance(data, dict) else "추천해볼게요.",
        "filters": filters,
        "movies": MovieListSerializer(qs, many=True).data,
    })


@api_view(["GET"])
@permission_classes([AllowAny])
def genre_recommend(request):
    """
    GET /api/recommends/genres/          -> 장르 목록
    GET /api/recommends/genres/?genre=28 -> 해당 장르 영화
    """
    genre_tmdb_id = request.query_params.get("genre")

    if not genre_tmdb_id:
        genres = Genre.objects.all().order_by("name")
        return Response({
            "genres": [{"tmdb_id": g.tmdb_id, "name": g.name} for g in genres]
        })

    qs = (
        Movie.objects
        .filter(genres__tmdb_id=int(genre_tmdb_id))
        .prefetch_related("genres")
        .order_by("-popularity")[:24]
    )
    return Response({"results": MovieListSerializer(qs, many=True).data})



from django.db.models import Count # Count가 임포트되어 있는지 확인하세요.

@api_view(["GET"])
@permission_classes([AllowAny])
def people_recommend(request):
    """
    작품이 1건이라도 있는 인물만 필터링하여 반환
    """
    q = (request.query_params.get("q") or "").strip()
    
    # 1. 검색 시: movies 필드를 사용하여 작품이 있는 사람만 필터링
    if q:
        people = (
            Person.objects
            .annotate(credits_count=Count("movies")) # movieperson_set 대신 movies 사용
            .filter(name__icontains=q, credits_count__gt=0)
            .order_by("-credits_count")[:30]
        )
        return Response({"results": PersonSerializer(people, many=True).data})

    # 2. 기본 추천: movies 필드를 사용하여 작품이 있는 인물 추출
    try:
        people = (
            Person.objects
            .annotate(credits_count=Count("movies")) # movieperson_set 대신 movies 사용
            .filter(credits_count__gt=0)
            .order_by("-credits_count", "name")[:40]
        )
    except Exception as e:
        # 에러 발생 시 Choices에 있던 movies 필드를 사용하여 필터링
        people = Person.objects.filter(movies__isnull=False).distinct()[:20]

    return Response({"results": PersonSerializer(people, many=True).data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def user_recommend(request):
    """
    GET /api/recommends/users/
    return:
      - top_reviewers: 리뷰 많이 쓴 유저
      - top_liked: 좋아요 많이 받은 유저(리뷰가 받은 like)
      - suggested: (가능하면) 내가 아직 팔로우 안 한 유저 추천
    """
    User = get_user_model()
    me = request.user

    # 리뷰 많이 쓴 유저
    top_reviewers_raw = (
        Review.objects.values("user_id")
        .annotate(cnt=Count("id"))
        .order_by("-cnt")[:10]
    )
    reviewer_ids = [r["user_id"] for r in top_reviewers_raw]
    reviewer_cnt_map = {r["user_id"]: r["cnt"] for r in top_reviewers_raw}
    reviewers = list(User.objects.filter(id__in=reviewer_ids))

    # 좋아요 많이 받은 유저(ReviewLike 있으면)
    top_liked_users = []
    if ReviewLike is not None:
        top_liked_raw = (
            ReviewLike.objects.values("review__user_id")
            .annotate(cnt=Count("id"))
            .order_by("-cnt")[:10]
        )
        liked_ids = [r["review__user_id"] for r in top_liked_raw]
        liked_cnt_map = {r["review__user_id"]: r["cnt"] for r in top_liked_raw}
        liked_users = list(User.objects.filter(id__in=liked_ids))
        top_liked_users = [
            {"id": u.id, "username": getattr(u, "username", ""), "received_likes": liked_cnt_map.get(u.id, 0)}
            for u in liked_users
        ]

    # suggested: 팔로우 모델이 있으면 "내가 아직 팔로우 안 한 활동 유저" 추천
    suggested = []
    if Follow is not None:
        try:
            following_ids = set(
                Follow.objects.filter(follower=me).values_list("following_id", flat=True)
            )
            base = (
                User.objects.exclude(id=me.id)
                .exclude(id__in=following_ids)
                .annotate(reviews_count=Count("reviews"))
                .order_by("-reviews_count")[:10]
            )
            suggested = [
                {"id": u.id, "username": getattr(u, "username", ""), "reviews_count": getattr(u, "reviews_count", 0)}
                for u in base
            ]
        except Exception:
            suggested = []

    return Response({
        "top_reviewers": [
            {"id": u.id, "username": getattr(u, "username", ""), "reviews_count": reviewer_cnt_map.get(u.id, 0)}
            for u in reviewers
        ],
        "top_liked": top_liked_users,
        "suggested": suggested,
    })

from django.db.models import Count
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from movies.models import Movie
from movies.serializers import MovieListSerializer
from reviews.models import Review


GENRE_LABELS = [
    "드라마","SF","판타지","로맨스","뮤지컬","애니메이션","전쟁","가족","다큐멘터리","스릴러","공포","액션"
]


def _detect_review_tmdb_field():
    """
    Review 모델에서 '영화 tmdb id'가 들어있는 필드명을 자동 탐지.
    프로젝트마다 tmdb_id, movie_tmdb_id 등 이름이 달라서 안전하게 처리.
    """
    candidates = ["tmdb_id", "movie_tmdb_id", "movie_id", "movie_tmdb"]
    review_field_names = {f.name for f in Review._meta.fields}
    for c in candidates:
        if c in review_field_names:
            return c
    return None


def _detect_review_rating_field():
    """
    Review 모델에서 별점 필드명 탐지(rating/score/stars 등).
    """
    candidates = ["rating", "score", "stars", "star"]
    review_field_names = {f.name for f in Review._meta.fields}
    for c in candidates:
        if c in review_field_names:
            return c
    return None


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def taste_summary(request):
    """
    GET /api/recommends/taste/
    리뷰(=봤다)를 기준으로 취향 통계를 만든다.
    """
    me = request.user
    tmdb_field = _detect_review_tmdb_field()
    rating_field = _detect_review_rating_field()

    if not tmdb_field:
        return Response({
            "watched_count": 0,
            "top_genre": "-",
            "avg_rating": 0,
            "recent_movie_title": "",
            "genre_scores": {},
            "recommended_movies": [],
            "detail": "Review 모델에 tmdb_id 계열 필드가 없어 집계를 할 수 없습니다."
        })

    my_reviews_qs = Review.objects.filter(user=me).order_by("-id")

    # ✅ 본 영화 수 = 내가 리뷰 쓴 영화의 distinct 개수
    tmdb_ids = list(
        my_reviews_qs.values_list(tmdb_field, flat=True).distinct()
    )
    watched_count = len(tmdb_ids)

    # ✅ 영화 정보(Movie 테이블)에 해당 tmdb_id가 있어야 장르/제목을 뽑을 수 있음
    movie_qs = Movie.objects.filter(tmdb_id__in=tmdb_ids).prefetch_related("genres")

    # ✅ 최근 본 영화(=최근 리뷰 영화)
    recent_movie_title = ""
    latest = my_reviews_qs.first()
    if latest:
        latest_tmdb = getattr(latest, tmdb_field, None)
        if latest_tmdb:
            m = movie_qs.filter(tmdb_id=latest_tmdb).first()
            if m:
                recent_movie_title = m.title or ""

    # ✅ 평균 별점 (별점 필드가 없으면 0)
    avg_rating = 0
    if rating_field:
        ratings = list(my_reviews_qs.values_list(rating_field, flat=True))
        ratings = [float(r) for r in ratings if r is not None]
        if ratings:
            avg_rating = round(sum(ratings) / len(ratings), 1)

    # ✅ 장르 선호도(리뷰한 영화들의 장르 빈도)
    # Movie.genres M2M 기준으로 집계
    genre_rows = (
        Movie.objects
        .filter(tmdb_id__in=tmdb_ids)
        .values("genres__name")
        .annotate(cnt=Count("genres__name"))
        .order_by("-cnt")
    )

    genre_count_map = {}
    for row in genre_rows:
        name = row["genres__name"]
        if not name:
            continue
        genre_count_map[name] = row["cnt"]

    # top genre 문자열(가장 많이 등장한 장르 1~2개 합치기)
    top_genres_sorted = sorted(genre_count_map.items(), key=lambda x: x[1], reverse=True)
    if top_genres_sorted:
        top_genre = "/".join([g for g, _ in top_genres_sorted[:2]])
    else:
        top_genre = "-"

    # radar 점수: 라벨 리스트에 맞춰 0~100 스케일
    max_cnt = max(genre_count_map.values(), default=0)
    genre_scores = {}
    for label in GENRE_LABELS:
        c = genre_count_map.get(label, 0)
        genre_scores[label] = int((c / max_cnt) * 100) if max_cnt else 0

    # ✅ 추천 영화: 내가 많이 본 장르(top 1~2개) 기반으로, 아직 리뷰 안 쓴 영화 추천
    top_genre_names = [g for g, _ in top_genres_sorted[:2]]
    rec_qs = Movie.objects.all().prefetch_related("genres")

    if top_genre_names:
        rec_qs = rec_qs.filter(genres__name__in=top_genre_names).distinct()

    if tmdb_ids:
        rec_qs = rec_qs.exclude(tmdb_id__in=tmdb_ids)

    rec_qs = rec_qs.order_by("-popularity")[:12]

    return Response({
        "watched_count": watched_count,
        "top_genre": top_genre,
        "avg_rating": avg_rating,
        "recent_movie_title": recent_movie_title,
        "genre_scores": genre_scores,
        "recommended_movies": MovieListSerializer(rec_qs, many=True).data,
    })

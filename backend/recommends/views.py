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

# 👇 [수정 1] run_taste_ai_reasons, RECOMMEND_LIMIT 추가
from .services.ai import GENRE_LIST, run_taste_ai, run_taste_ai_reasons, RECOMMEND_LIMIT
from .models import TastePromptLog

import re

EXCLUDE_PATTERN = r"([가-힣A-Za-z0-9\s·:_\-]+?)\s*(?:은|는|을|를)?\s*(?:빼고|제외|말고|빼줘|제외해|제외해줘)"

def parse_excludes_from_message(message: str):
    if not message:
        return [], []
    hits = re.findall(EXCLUDE_PATTERN, message)
    exclude_genres, exclude_titles = [], []
    for h in hits:
        term = (h or "").strip().replace("영화", "").strip()
        if not term: continue
        parts = re.split(r"[,\n]|그리고|랑|하고|&|/", term)
        parts = [p.strip() for p in parts if p.strip()]
        for p in parts:
            if p in GENRE_LIST: exclude_genres.append(p)
            else: exclude_titles.append(p)
    return list(dict.fromkeys(exclude_genres)), list(dict.fromkeys(exclude_titles))

def build_title_q(field: str, terms: list[str]) -> Q:
    q = Q()
    for t in terms:
        q |= Q(**{f"{field}__icontains": t})
    return q

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def ai_taste(request):
    message = (request.data.get("message") or "").strip()
    history = request.data.get("history") or []

    if not message:
        return Response({"detail": "message가 비었습니다."}, status=status.HTTP_400_BAD_REQUEST)

    # 1) AI 분석
    data, raw = run_taste_ai(message, history=history)

    try:
        TastePromptLog.objects.create(
            user=request.user, prompt=message, response_raw=raw,
            response_json=data if isinstance(data, dict) else None,
        )
    except Exception: pass

    # 2) 필터 추출
    filters = data.get("filters") or {}
    primary = filters.get("primary_genre_name")
    genre_names = filters.get("genre_names") or []
    keywords = filters.get("keywords") or []
    titles = filters.get("titles") or []
    min_vote = float(filters.get("min_vote") or 0)
    strict = bool(filters.get("strict")) if isinstance(filters.get("strict"), (bool, int)) else False

    exclude_genres_ai = filters.get("exclude_genre_names") or []
    exclude_titles_ai = filters.get("exclude_titles") or []
    exclude_genres_msg, exclude_titles_msg = parse_excludes_from_message(message)

    exclude_genre_names = list(dict.fromkeys([*exclude_genres_ai, *exclude_genres_msg]))
    exclude_titles = list(dict.fromkeys([*exclude_titles_ai, *exclude_titles_msg]))
    titles = [t for t in titles if t not in exclude_titles]

    include_genres = []
    if isinstance(primary, str) and primary.strip(): include_genres.append(primary.strip())
    include_genres += [g for g in genre_names if isinstance(g, str) and g.strip()]
    include_genres = list(dict.fromkeys([g for g in include_genres if g not in exclude_genre_names]))

    # 3) DB 쿼리
    base_qs = Movie.objects.all().prefetch_related("genres")
    if exclude_genre_names: base_qs = base_qs.exclude(genres__name__in=exclude_genre_names)
    if exclude_titles: base_qs = base_qs.exclude(build_title_q("title", exclude_titles))
    if min_vote > 0: base_qs = base_qs.filter(vote_average__gte=min_vote)

    k_q = Q()
    if keywords:
        for k in keywords:
            k = (k or "").strip()
            if not k: continue
            k_q |= Q(title__icontains=k) | Q(overview__icontains=k)

    qs = base_qs
    if include_genres:
        if strict:
            for g in include_genres: qs = qs.filter(genres__name=g)
            qs = qs.distinct()
        else:
            qs = qs.annotate(match_genres=Count("genres", filter=Q(genres__name__in=include_genres), distinct=True)).distinct()

    qs_with_kw = qs
    if k_q: qs_with_kw = qs.filter(k_q).distinct()

    if k_q and not qs_with_kw.exists(): qs_final = qs
    else: qs_final = qs_with_kw

    if include_genres and not qs_final.exists() and k_q: qs_final = base_qs.filter(k_q).distinct()
    if not qs_final.exists() and titles:
        t_q = Q()
        for t in titles: t_q |= Q(title__icontains=t)
        qs_final = base_qs.filter(t_q).distinct()

    if not strict and include_genres:
        qs_final = qs_final.order_by("-match_genres", "-popularity", "-vote_average")
    else:
        qs_final = qs_final.order_by("-popularity", "-vote_average")

    # 👇 [수정 2] 개수 제한 (12개 -> 3개)
    qs_final = qs_final[:RECOMMEND_LIMIT]

    serialized = MovieListSerializer(qs_final, many=True).data

    # 👇 [수정 3] 추천 이유 생성 로직 추가
    reasons_by_tmdb = {}
    if serialized:
        reasons_data, _ = run_taste_ai_reasons(message, serialized)
        reasons_by_tmdb = reasons_data

    # (선택) AI가 준 recommended_reasons가 있다면 병합
    reasons_by_title = data.get("recommended_reasons") or {}
    if isinstance(reasons_by_title, dict):
        for m in serialized:
            tmdb_id = str(m.get("tmdb_id"))
            title = m.get("title")
            if tmdb_id not in reasons_by_tmdb and title in reasons_by_title:
                reasons_by_tmdb[tmdb_id] = reasons_by_title[title]

    return Response({
        "answer": data.get("answer", "조건에 맞는 영화를 찾아보았습니다."),
        "filters": {
            **filters, "exclude_genre_names": exclude_genre_names, "exclude_titles": exclude_titles,
        },
        "movies": serialized,
        "recommended_reasons": reasons_by_tmdb, 
    })

# --- 아래 함수들은 기존과 동일합니다 ---
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
    watched_movies_qs = Movie.objects.filter(tmdb_id__in=tmdb_ids)
    watched_data = []
    for review in my_reviews_qs:
        watched_data.append({
            "tmdb_id": review.movie.tmdb_id,
            "title": review.movie.title,
            "poster_path": review.movie.poster_path,
            "genres": [g.name for g in review.movie.genres.all()],
            "my_rating": review.rating
        })
    watched_count = len(watched_data)
    if watched_count == 0:
        return Response({"watched_count": 0, "top_genre": "-", "avg_rating": 0, "recent_movie_title": "", "genre_scores": {}, "watched_movies": [],"recommended_movies": [], "detail": "작성된 리뷰가 없습니다."})
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
    return Response({"watched_count": watched_count, "top_genre": top_genre, "avg_rating": avg_rating, "recent_movie_title": recent_movie_title, "genre_scores": genre_scores, "watched_movies": watched_data, "recommended_movies": MovieListSerializer(rec_qs, many=True).data})
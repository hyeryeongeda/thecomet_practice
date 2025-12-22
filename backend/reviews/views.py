# backend/reviews/views.py
from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from movies.models import Movie
from .models import Review
from .serializers import ReviewSerializer, RecentReviewSerializer, ReviewCreateSerializer

@api_view(["GET"])
@permission_classes([AllowAny])
def list_movie_reviews(request, tmdb_id: int):
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
    qs = (
        Review.objects.filter(movie=movie)
        .select_related("user", "movie")
        .annotate(likes_count=Count("likes"))
        .order_by("-likes_count", "-created_at")
    )
    return Response(ReviewSerializer(qs, many=True, context={"request": request}).data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_movie_review(request, tmdb_id: int):
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)

    if Review.objects.filter(movie=movie, user=request.user).exists():
        return Response(
            {"detail": "이미 이 영화에 리뷰를 작성했습니다. 수정 기능을 사용하세요."},
            status=status.HTTP_409_CONFLICT,
        )

    serializer = ReviewCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    review = Review.objects.create(
        movie=movie,
        user=request.user,
        content=serializer.validated_data["content"],
        watched=serializer.validated_data["watched"],
        rating=serializer.validated_data["rating"],
    )

    out = (
        Review.objects.filter(id=review.id)
        .select_related("user", "movie")
        .annotate(likes_count=Count("likes"))
        .first()
    )
    return Response(ReviewSerializer(out, context={"request": request}).data, status=status.HTTP_201_CREATED)

@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def update_delete_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)

    if review.user_id != request.user.id:
        return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "DELETE":
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = ReviewCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    review.content = serializer.validated_data["content"]
    review.watched = serializer.validated_data["watched"]
    review.rating = serializer.validated_data["rating"]
    review.save()

    out = (
        Review.objects.filter(id=review.id)
        .select_related("user", "movie")
        .annotate(likes_count=Count("likes"))
        .first()
    )
    return Response(ReviewSerializer(out, context={"request": request}).data)

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_like(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)
    if review.user_id == request.user.id:
        return Response({"detail": "내 리뷰에는 좋아요를 누를 수 없습니다."}, status=400)

    if review.likes.filter(id=request.user.id).exists():
        review.likes.remove(request.user)
        liked = False
    else:
        review.likes.add(request.user)
        liked = True
    return Response({"liked": liked, "like_count": review.likes.count()})

@api_view(["GET"])
@permission_classes([AllowAny])
def recent_reviews(request):
    limit = int(request.query_params.get("limit", 12))
    qs = (
        Review.objects.select_related("user", "movie")
        .annotate(likes_count=Count("likes"))
        .order_by("-created_at")[:limit]
    )
    return Response(RecentReviewSerializer(qs, many=True, context={"request": request}).data)

# ✅ 마이페이지 통합 뷰 (모든 status 대응)
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_reviews(request):
    status_param = request.query_params.get("status", "commented")
    sort_param = request.query_params.get("sort", "latest")
    user = request.user

    # 1. 데이터 소스 결정
    if status_param == "liked":
        # 내가 좋아요 누른 다른 사람들의 리뷰
        qs = Review.objects.filter(likes=user).select_related("movie", "user")
    else:
        # 내가 작성한 활동들
        qs = Review.objects.filter(user=user).select_related("movie", "user")
        if status_param == "watched":
            qs = qs.filter(watched=True)
        elif status_param == "wish":
            # 리뷰를 썼는데 watched=False인 경우를 wish로 가정 (또는 별도 모델 필요)
            qs = qs.filter(watched=False)

    # 2. 공통 가공 및 정렬
    qs = qs.annotate(likes_count=Count("likes"))
    
    if sort_param == "latest": qs = qs.order_by("-created_at")
    elif sort_param == "oldest": qs = qs.order_by("created_at")
    elif sort_param == "rating_high": qs = qs.order_by("-rating", "-created_at")
    elif sort_param == "rating_low": qs = qs.order_by("rating", "-created_at")

    return Response(ReviewSerializer(qs, many=True, context={"request": request}).data)
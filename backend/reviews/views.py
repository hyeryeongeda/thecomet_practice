from django.db.models import Count
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

# 영화 모델 경로가 movies.models인지 확인하세요 (보통 맞습니다)
from movies.models import Movie 
from .models import Review, ReviewComment 
from .serializers import ReviewSerializer, ReviewCreateSerializer, RecentReviewSerializer

# 1. [상세페이지] 리뷰 목록 조회 (이름 유지: list_movie_reviews)
@api_view(["GET"])
@permission_classes([AllowAny])
def list_movie_reviews(request, tmdb_id: int):
    # tmdb_id로 영화를 찾거나 없으면 404
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
    
    qs = (
        Review.objects.filter(movie=movie)
        .select_related("user", "movie")
        .annotate(likes_count=Count("likes"))
        .order_by("-likes_count", "-created_at")
    )
    # context={"request": request}를 넘겨야 시리얼라이저에서 이미지 URL 생성이 잘 됨
    return Response(ReviewSerializer(qs, many=True, context={"request": request}).data)

# 2. [상세페이지] 리뷰 작성 (이름 유지: create_movie_review)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_movie_review(request, tmdb_id: int):
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)

    # 이미 작성했는지 체크
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
        watched=serializer.validated_data.get("watched", False), # get으로 안전하게
        rating=serializer.validated_data["rating"],
    )

    # 작성 후 바로 전체 정보를 리턴 (작성자 프로필 등 포함 위해)
    out = (
        Review.objects.filter(id=review.id)
        .select_related("user", "movie")
        .annotate(likes_count=Count("likes"))
        .first()
    )
    return Response(ReviewSerializer(out, context={"request": request}).data, status=status.HTTP_201_CREATED)

# 3. [상세페이지] 리뷰 수정/삭제 (이름 유지: update_delete_review)
@api_view(["PUT", "DELETE"])
@permission_classes([IsAuthenticated])
def update_delete_review(request, review_id: int):
    review = get_object_or_404(Review, id=review_id)

    if review.user_id != request.user.id:
        return Response({"detail": "권한이 없습니다."}, status=status.HTTP_403_FORBIDDEN)

    if request.method == "DELETE":
        review.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # PUT (수정)
    serializer = ReviewCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    review.content = serializer.validated_data["content"]
    review.watched = serializer.validated_data.get("watched", review.watched)
    review.rating = serializer.validated_data["rating"]
    review.save()

    out = (
        Review.objects.filter(id=review.id)
        .select_related("user", "movie")
        .annotate(likes_count=Count("likes"))
        .first()
    )
    return Response(ReviewSerializer(out, context={"request": request}).data)

# 4. [공통] 리뷰 좋아요 토글 (이름 유지: toggle_like)
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

# 5. [홈] 최근 리뷰 (이름 유지: recent_reviews)
@api_view(["GET"])
@permission_classes([AllowAny])
def recent_reviews(request):
    limit = int(request.query_params.get("limit", 12))
    qs = (
        Review.objects.select_related("user", "movie")
        .annotate(likes_count=Count("likes"))
        .order_by("-created_at")[:limit]
    )
    # RecentReviewSerializer가 있다면 사용, 없으면 ReviewSerializer 사용
    return Response(ReviewSerializer(qs, many=True, context={"request": request}).data)

# 6. [마이페이지] 통합 뷰 (이름 유지: my_reviews) -> 프론트엔드 연결 핵심!
@api_view(["GET"])
@permission_classes([IsAuthenticated])
def my_reviews(request):
    """
    GET /api/reviews/my/?status=commented -> 내가 쓴 코멘트
    GET /api/reviews/my/?status=liked     -> 내가 좋아요 누른 남의 코멘트
    """
    
    status_param = request.query_params.get("status", "commented")
    sort_param = request.query_params.get("sort", "latest")
    user = request.user

    # (1) 데이터 필터링
    if status_param == "liked":
        # 내가 좋아요 누른 리뷰들 (Review 모델의 likes 필드 역참조)
        qs = user.liked_reviews.select_related("movie", "user")
    else:
        # 내가 작성한 리뷰들
        qs = Review.objects.filter(user=user).select_related("movie", "user")
        
        if status_param == "watched":
            qs = qs.filter(watched=True)
        elif status_param == "wish":
            qs = qs.filter(watched=False)
        # commented는 필터 없이 전체(내가 쓴 거)

    # (2) 정렬 및 가공
    qs = qs.annotate(likes_count=Count("likes"))
    
    if sort_param == "latest": qs = qs.order_by("-created_at")
    elif sort_param == "oldest": qs = qs.order_by("created_at")
    elif sort_param == "rating_high": qs = qs.order_by("-rating", "-created_at")
    elif sort_param == "rating_low": qs = qs.order_by("rating", "-created_at")

    return Response(ReviewSerializer(qs, many=True, context={"request": request}).data)


# [추가 1] 대댓글 작성 API
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_review_comment(request, review_id):
    # 1. 부모 리뷰 찾기
    review = get_object_or_404(Review, id=review_id)
    
    # 2. 내용 확인
    content = request.data.get("content")
    if not content:
        return Response({"detail": "내용이 없습니다."}, status=400)
    
    # 3. 대댓글 생성
    comment = ReviewComment.objects.create(
        review=review,
        user=request.user,
        content=content
    )
    
    # 4. 결과 반환 (작성자 프로필 포함)
    return Response({
        "id": comment.id,
        "content": comment.content,
        "user": {
            "username": comment.user.username,
            "profile_image": comment.user.profile_image.url if comment.user.profile_image else None
        },
        "created_at": comment.created_at
    })

# [추가 2] 대댓글 목록 조회 API
@api_view(["GET"])
@permission_classes([AllowAny])
def list_review_comments(request, review_id):
    # 해당 리뷰에 달린 모든 댓글 가져오기
    comments = ReviewComment.objects.filter(review_id=review_id).select_related('user').order_by('created_at')
    
    data = []
    for c in comments:
        data.append({
            "id": c.id,
            "content": c.content,
            "user": {
                "username": c.user.username,
                "profile_image": c.user.profile_image.url if c.user.profile_image else None
            },
            "created_at": c.created_at
        })
    return Response(data)



# [추가] 영화 보고싶어요 토글 (찜하기)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def toggle_movie_wish(request, tmdb_id: int):
    movie = get_object_or_404(Movie, tmdb_id=tmdb_id)
    
    # 1. 해당 영화에 대한 내 기록(Review)이 있는지 확인
    review = Review.objects.filter(movie=movie, user=request.user).first()

    if review:
        # 1-1. 이미 기록이 있는데, '봤어요(watched=True)' 상태라면?
        if review.watched:
            return Response(
                {"detail": "이미 감상한 작품입니다. (코멘트 수정에서 변경 가능)"}, 
                status=400
            )
        
        # 1-2. '보고싶어요(watched=False)' 상태라면? -> 취소(삭제)
        review.delete()
        return Response({"wished": False, "message": "보고싶어요 취소"})
    
    else:
        # 2. 기록이 없다면? -> '보고싶어요' 생성
        Review.objects.create(
            movie=movie,
            user=request.user,
            watched=False,  # 아직 안 봄
            rating=0,       # 별점 0
            content=""      # 내용 없음
        )
        return Response({"wished": True, "message": "보고싶어요 등록"})
    
    
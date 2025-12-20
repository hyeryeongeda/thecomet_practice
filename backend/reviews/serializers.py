# backend/reviews/serializers.py
from rest_framework import serializers
from .models import Review


class ReviewUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()


class ReviewCreateSerializer(serializers.Serializer):
    watched = serializers.BooleanField()
    rating = serializers.IntegerField()
    content = serializers.CharField(max_length=200)

    def validate(self, attrs):
        if attrs.get("watched") is not True:
            raise serializers.ValidationError("리뷰 작성은 '봤어요' 체크가 필요합니다.")

        rating = attrs.get("rating")
        if rating is None:
            raise serializers.ValidationError("별점은 필수입니다.")
        if not (1 <= rating <= 5):
            raise serializers.ValidationError("별점은 1~5 사이여야 합니다.")

        content = (attrs.get("content") or "").strip()
        if not content:
            raise serializers.ValidationError("한줄평을 입력해 주세요.")

        attrs["content"] = content
        return attrs


class ReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)

    # ✅ annotate에서 likes_count로 뽑고, 응답은 like_count로 내려줌
    like_count = serializers.IntegerField(source="likes_count", read_only=True, default=0)

    class Meta:
        model = Review
        fields = [
            "id",
            "movie",
            "user",
            "content",
            "watched",
            "rating",
            "like_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "movie", "user", "like_count", "created_at", "updated_at"]


class RecentReviewSerializer(serializers.ModelSerializer):
    user = ReviewUserSerializer(read_only=True)
    like_count = serializers.IntegerField(source="likes_count", read_only=True, default=0)

    # ✅ 홈에서 리뷰 카드 클릭 → 영화 디테일 이동에 필요
    movie_tmdb_id = serializers.IntegerField(source="movie.tmdb_id", read_only=True)

    class Meta:
        model = Review
        fields = ["id", "user", "content", "rating", "like_count", "movie_tmdb_id", "created_at"]

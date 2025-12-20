from rest_framework import serializers
from .models import Movie, Genre, Person, MovieCredit


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["tmdb_id", "name"]


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ["tmdb_id", "name", "profile_path", "known_for_department"]


class CreditSerializer(serializers.Serializer):
    role_type = serializers.CharField()
    person = PersonSerializer()
    character_name = serializers.CharField(allow_blank=True)
    job = serializers.CharField(allow_blank=True)
    order = serializers.IntegerField()


class MovieListSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True)

    # ✅ 리뷰/좋아요는 reviews 앱 붙일 때 채울 자리(지금은 null)
    top_review = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "id",
            "tmdb_id",
            "title",
            "poster_path",
            "release_date",
            "vote_average",
            "genres",
            "top_review",
        ]

    def get_top_review(self, obj):
        return None


class MovieDetailSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True)
    directors = serializers.SerializerMethodField()
    cast = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "id",
            "tmdb_id",
            "title",
            "original_title",
            "overview",
            "release_date",
            "poster_path",
            "backdrop_path",
            "popularity",
            "vote_average",
            "vote_count",
            "runtime",
            "genres",
            "directors",
            "cast",
        ]

    def _credit_to_dict(self, c: MovieCredit):
        return {
            "role_type": c.role_type,
            "person": {
                "tmdb_id": c.person.tmdb_id,
                "name": c.person.name,
                "profile_path": c.person.profile_path,
                "known_for_department": c.person.known_for_department,
            },
            "character_name": c.character_name,
            "job": c.job,
            "order": c.order,
        }

    def get_directors(self, obj):
        qs = MovieCredit.objects.select_related("person").filter(movie=obj, role_type="DIRECTOR")
        return [self._credit_to_dict(c) for c in qs]

    def get_cast(self, obj):
        qs = MovieCredit.objects.select_related("person").filter(movie=obj, role_type="CAST").order_by("order")[:10]
        return [self._credit_to_dict(c) for c in qs]
from rest_framework import serializers
from django.db.models import Count
from .models import Movie
from reviews.models import Review

class MovieListSerializer(serializers.ModelSerializer):
    top_review = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = [
            "tmdb_id",
            "title",
            "poster_path",
            "vote_average",
            "top_review",
        ]

    def get_top_review(self, obj):
        r = (
            Review.objects.filter(movie=obj)
            .select_related("user")
            .annotate(likes_count=Count("likes"))
            .order_by("-likes_count", "-created_at")
            .first()
        )
        if not r:
            return None
        return {
            "id": r.id,
            "content": r.content,
            "likes_count": r.likes_count,
            "user": {"username": r.user.username},
        }

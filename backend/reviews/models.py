from django.conf import settings
from django.db import models


class Review(models.Model):
    """
    '한줄평' = 핵심 활동 데이터
    - watched=True 체크 + rating 필수
    - 한 유저는 한 영화에 1개의 리뷰만(수정 가능)
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews"
    )
    movie = models.ForeignKey(
        "movies.Movie", on_delete=models.CASCADE, related_name="reviews"
    )

    content = models.CharField(max_length=200)
    watched = models.BooleanField(default=False)
    rating = models.PositiveSmallIntegerField()  # 1~5

    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="liked_reviews", blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "movie"], name="uniq_user_movie_review")
        ]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.movie.tmdb_id} / {self.user} ({self.rating})"

    @property
    def like_count(self):
        return self.likes.count()

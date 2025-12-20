# backend/universe/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("api/auth/", include("accounts.urls")),
    path("api/movies/", include("movies.urls")),
    path("api/reviews/", include("reviews.urls")),
]

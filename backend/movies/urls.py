from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home),
    path("list/", views.movie_list),
    path("genres/", views.genre_list),
    path("search/", views.search),

    # ✅ movie
    path("<int:tmdb_id>/", views.movie_detail),
    path("<int:tmdb_id>/credits/", views.movie_credits),

    # ✅ people
    path("people/<int:tmdb_id>/", views.person_detail),
    path("likes/", views.my_movie_likes, name="my_movie_likes"),
]

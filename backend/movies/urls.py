# backend/movies/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("home/", views.home),
    path("list/", views.movie_list),
    path("genres/", views.genre_list),
    path("search/", views.search),
    path("<int:tmdb_id>/", views.movie_detail),
]


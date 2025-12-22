# backend/reviews/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("recent/", views.recent_reviews),
    path("movie/<int:tmdb_id>/", views.list_movie_reviews),
    path("movie/<int:tmdb_id>/create/", views.create_movie_review),
    path("<int:review_id>/", views.update_delete_review),
    path("<int:review_id>/like/", views.toggle_like),
    path("my/", views.my_reviews, name="my_reviews"),
    
]

from django.urls import path, include
from rest_framework import routers

from books.views import GenreViewSet, AuthorViewSet, BookViewSet

router = routers.DefaultRouter()
router.register("books", BookViewSet, basename="books"),
router.register("genres", GenreViewSet, basename="genres"),
router.register("authors", AuthorViewSet, basename="authors"),


app_name = "catalog"

urlpatterns = [
    path("", include(router.urls)),
]

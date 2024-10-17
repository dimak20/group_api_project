from django.urls import path, include
from rest_framework import routers

from books.views import GenreViewSet, AuthorViewSet, BookViewSet

router = routers.DefaultRouter()
router.register("books", BookViewSet),
router.register("genres", GenreViewSet),
router.register("authors", AuthorViewSet),


app_name = "catalog"

urlpatterns = [
    path("", include(router.urls)),
]

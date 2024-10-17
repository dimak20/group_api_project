from django.urls import path, include
from rest_framework import routers

from books.views import GenreViewSet, AuthorViewSet, BookViewSet

router = routers.DefaultRouter()
router.register("", BookViewSet),
router.register("genres", GenreViewSet),
router.register("authors", AuthorViewSet),


app_name = "books-service"

urlpatterns = [
    path("", include(router.urls)),
]

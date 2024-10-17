from django.urls import path, include
from rest_framework import routers

from books.views import GenreViewSet, AuthorViewSet, BookViewSet

router = routers.DefaultRouter()
router.register("astronomy-shows", GenreViewSet),
router.register("show-themes", AuthorViewSet),
router.register("planetarium-domes", BookViewSet),


app_name = "books-service"

urlpatterns = [
    path("", include(router.urls)),
]

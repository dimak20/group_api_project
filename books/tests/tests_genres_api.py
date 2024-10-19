from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import Genre
from books.serializers import GenreSerializer


GENRES_URL = reverse("catalog:genres-list")


def detail_genre_url(id_):
    return reverse("catalog:genres-detail", args=[id_])


def sample_genre(**params) -> Genre:
    defaults = {"name": "Test Genre"}
    defaults.update(params)
    return Genre.objects.create(**defaults)


class UnauthenticatedGenresApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_books_list_auth_required(self):
        response = self.client.get(GENRES_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedGenresApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_genres_list(self):
        sample_genre()

        response = self.client.get(GENRES_URL)
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_genre_detail(self):
        genre = sample_genre()
        serializer = GenreSerializer(genre)
        url = detail_genre_url(genre.id)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_genre_forbidden(self):
        payload = {"name": "test_genre"}
        response = self.client.post(GENRES_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminGenresApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.admin", password="admin_password"
        )
        self.client.force_authenticate(self.user)

    def test_admin_create_by_admin(self):
        payload = {"name": "Test Genre"}
        response = self.client.post(GENRES_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        book = Genre.objects.get(id=response.data["id"])
        for key in payload:
            self.assertEqual(payload[key], getattr(book, key))

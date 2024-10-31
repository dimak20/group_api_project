from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import Author
from books.serializers import AuthorListSerializer, AuthorRetrieveSerializer


AUTHORS_URL = reverse("catalog:authors-list")


def detail_author_url(id_):
    return reverse("catalog:authors-detail", args=[id_])


def sample_author(**params) -> Author:
    defaults = {"first_name": "Test_name", "last_name": "Test_surname"}
    defaults.update(params)
    return Author.objects.create(**defaults)


class UnauthenticatedAuthorsApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_books_list_auth_required(self):
        response = self.client.get(AUTHORS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedAuthorsApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_authors_list(self):
        sample_author()

        response = self.client.get(AUTHORS_URL)
        authors = Author.objects.all()
        serializer = AuthorListSerializer(authors, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_retrieve_author_detail(self):
        from books.tests.tests_books_api import sample_book

        book = sample_book()
        author = sample_author()
        book.authors.add(author)
        serializer = AuthorRetrieveSerializer(author)

        url = detail_author_url(author.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_author_forbidden(self):
        payload = {"first_name": "Test_name", "last_name": "Test_surname"}
        response = self.client.post(AUTHORS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminAuthorsApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.admin", password="admin_password"
        )
        self.client.force_authenticate(self.user)

    def test_admin_create_by_admin(self):
        payload = {"first_name": "Test_name", "last_name": "Test_surname"}
        response = self.client.post(AUTHORS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        book = Author.objects.get(id=response.data["id"])
        for key in payload:
            self.assertEqual(payload[key], getattr(book, key))

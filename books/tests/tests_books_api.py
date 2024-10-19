from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from books.models import Book
from books.serializers import BookListSerializer, BookRetrieveSerializer
from books.tests.tests_authors_api import sample_author
from books.tests.tests_genres_api import sample_genre


BOOKS_URL = reverse("catalog:books-list")


def detail_book_url(book_id):
    return reverse("catalog:books-detail", args=[book_id])


def sample_book(**params) -> Book:
    defaults = {"title": "test_title"}
    defaults.update(params)
    return Book.objects.create(**defaults)


class UnauthenticatedBooksApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_books_list_auth_required(self):
        response = self.client.get(BOOKS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBooksApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(self.user)

    def test_books_list(self):
        sample_book()
        response = self.client.get(BOOKS_URL)
        books = Book.objects.all()
        serializer = BookListSerializer(books, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["results"], serializer.data)

    def test_books_filtration_and_ordering(self):
        empty_book = sample_book(title="empty_book", year=2000)
        serializer_empty = BookListSerializer(empty_book)

        book_with_author = sample_book(title="book_with_author", year=1000)
        first_author = sample_author(first_name="First", last_name="A")
        book_with_author.authors.add(first_author)
        serializer_with_author = BookListSerializer(book_with_author)

        book_with_genre = sample_book(title="book_with_genre", year=1500)
        second_author = sample_author(first_name="Second", last_name="B")
        genre = sample_genre(name="test")
        book_with_genre.authors.add(second_author)
        book_with_genre.genres.add(genre)
        serializer_with_author_and_genre = BookListSerializer(book_with_genre)

        response = self.client.get(BOOKS_URL, {"title": "author"})
        self.assertEqual(len(response.data["results"]), 1)
        self.assertNotEqual(response.data["results"][0], serializer_empty.data)
        self.assertEqual(response.data["results"][0], serializer_with_author.data)

        response = self.client.get(BOOKS_URL, {"genres": "tes"})
        self.assertEqual(len(response.data["results"]), 1)
        self.assertNotEqual(response.data["results"][0], serializer_empty.data)
        self.assertEqual(
            response.data["results"][0], serializer_with_author_and_genre.data
        )

        response = self.client.get(BOOKS_URL, {"authors__first_name": "firs"})
        self.assertEqual(len(response.data["results"]), 1)
        self.assertNotEqual(response.data["results"][0], serializer_empty.data)
        self.assertEqual(response.data["results"][0], serializer_with_author.data)

        response = self.client.get(BOOKS_URL, {"ordering": "-year"})
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["results"][0], serializer_empty.data)
        self.assertEqual(
            response.data["results"][1], serializer_with_author_and_genre.data
        )
        self.assertEqual(response.data["results"][2], serializer_with_author.data)

        response = self.client.get(BOOKS_URL, {"ordering": "title"})
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["results"][2], serializer_empty.data)
        self.assertEqual(
            response.data["results"][1], serializer_with_author_and_genre.data
        )
        self.assertEqual(response.data["results"][0], serializer_with_author.data)

        response = self.client.get(BOOKS_URL, {"ordering": "author"})
        self.assertEqual(len(response.data["results"]), 3)
        self.assertEqual(response.data["results"][2], serializer_empty.data)
        self.assertEqual(
            response.data["results"][1], serializer_with_author_and_genre.data
        )
        self.assertEqual(response.data["results"][0], serializer_with_author.data)

    def test_retrieve_book_detail(self):
        book = sample_book()
        author = sample_author()
        genre = sample_genre()
        book.authors.add(author)
        book.genres.add(genre)
        serializer = BookRetrieveSerializer(book)

        url = detail_book_url(book.id)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_book_forbidden(self):
        payload = {"title": "test_title"}
        response = self.client.post(BOOKS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AdminBooksApiTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_superuser(
            email="admin@admin.admin", password="admin_password"
        )
        self.client.force_authenticate(self.user)

    def test_book_create_by_admin(self):
        author = sample_author()
        genre = sample_genre()
        payload = {
            "title": "test_title_from_admin",
            "year": 2024,
            "authors": [author.id],
            "genres": [genre.id],
            "cover": "Hard",
            "inventory": 10,
            "daily_fee": "1.99",
        }

        response = self.client.post(BOOKS_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=response.data["id"])

        # Check non-relationship fields
        for key in ["title", "year", "cover", "inventory"]:
            self.assertEqual(payload[key], getattr(book, key))

        # Convert daily_fee to Decimal for comparison
        self.assertEqual(Decimal(payload["daily_fee"]), book.daily_fee)

        # Check many-to-many relationships (authors and genres)
        self.assertEqual(
            list(book.authors.values_list("id", flat=True)), payload["authors"]
        )
        self.assertEqual(
            list(book.genres.values_list("id", flat=True)), payload["genres"]
        )

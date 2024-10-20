from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.filters import OrderingFilter

from books.filters import BookFilter
from books.models import Genre, Author, Book
from books.serializers import (
    GenreSerializer,
    GenreRetrieveSerializer,
    AuthorSerializer,
    AuthorListRetrieveSerializer,
    BookSerializer,
    BookListSerializer,
    BookRetrieveSerializer,
)
from books.schemas.books_filtering_ordering import book_list_create_schema


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()

    def get_serializer_class(self):
        if self.action == "retrieve":
            return GenreRetrieveSerializer
        return GenreSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return AuthorListRetrieveSerializer
        return AuthorSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ["list", "retrieve"]:
            queryset = queryset.prefetch_related("books")
        return queryset


@book_list_create_schema
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = BookFilter
    ordering_fields = ["title", "year", "authors__last_name"]
    ordering = ["title"]

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        elif self.action == "retrieve":
            return BookRetrieveSerializer
        return BookSerializer

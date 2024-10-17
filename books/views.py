from rest_framework import viewsets

from books.models import Genre, Author, Book
from books.serializers import (
    GenreSerializer,
    AuthorSerializer,
    AuthorListRetrieveSerializer,
    BookSerializer,
    BookListSerializer,
    BookRetrieveSerializer,
)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


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


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        elif self.action == "retrieve":
            return BookRetrieveSerializer
        return BookSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ["list", "retrieve"]:
            queryset = queryset.prefetch_related("authors", "genres")
        return queryset

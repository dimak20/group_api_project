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

    @staticmethod
    def separate_ids(ids_list: str):
        return [int(id_) for id_ in ids_list.split(",")]

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset = queryset.prefetch_related("authors", "genres")
            authors = self.request.query_params.get("authors")
            genres = self.request.query_params.get("genres")
            title = self.request.query_params.get("title")

            if authors:
                author_ids = self.separate_ids(authors)
                queryset = queryset.filter(authors__id__in=author_ids)
            if genres:
                genre_ids = self.separate_ids(genres)
                queryset = queryset.filter(genres__id__in=genre_ids)
            if title:
                queryset = queryset.filter(title__icontains=title)
            return queryset.distinct()

        if self.action == "retrieve":
            queryset = queryset.prefetch_related("authors", "genres")

        return queryset

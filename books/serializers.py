from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from books.models import Author, Genre, Book


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name", "description"]


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "first_name", "last_name", "biography"]


class AuthorListSerializer(AuthorSerializer):
    books = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="title"
    )

    class Meta(AuthorSerializer.Meta):
        fields = ["id", "first_name", "last_name", "books"]


class AuthorRetrieveSerializer(AuthorListSerializer):
    class Meta(AuthorListSerializer.Meta):
        fields = AuthorListSerializer.Meta.fields + ["biography"]


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "year",
            "authors",
            "genres",
            "cover",
            "inventory",
            "daily_fee",
            "image"
        )

    def validate(self, attrs):
        Book.validate_year(attrs["year"])
        return attrs


class BookListSerializer(BookSerializer):
    authors = serializers.SerializerMethodField()
    genres = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta(BookSerializer.Meta):
        fields = ["id", "title", "year", "authors", "genres", "image"]

    @extend_schema_field(OpenApiTypes.STR)
    def get_authors(self, obj) -> list[str]:
        authors = obj.authors.all()
        return [f"{author}" for author in authors]


class BookRetrieveSerializer(BookSerializer):
    authors = AuthorSerializer(many=True)
    genres = GenreSerializer(many=True)


class GenreRetrieveSerializer(GenreSerializer):
    books = BookListSerializer(many=True, read_only=True)

    class Meta(GenreSerializer.Meta):
        fields = GenreSerializer.Meta.fields + ["books"]

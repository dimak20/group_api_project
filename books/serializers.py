from rest_framework import serializers

from books.models import Author, Genre, Book


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ["id", "name"]


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "first_name", "last_name"]


class AuthorListRetrieveSerializer(AuthorSerializer):
    books = serializers.SlugRelatedField(many=True, read_only=True, slug_field="title")

    class Meta(AuthorSerializer.Meta):
        fields = AuthorSerializer.Meta.fields + ["books"]


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "authors",
            "genres",
            "cover",
            "inventory",
            "daily_fee",
            "image"
        )


class BookListSerializer(BookSerializer):
    authors = serializers.SerializerMethodField()
    genres = serializers.SlugRelatedField(
        many=True, read_only=True, slug_field="name"
    )

    class Meta(BookSerializer.Meta):
        fields = ["id", "title", "authors", "genres", "image"]

    def get_authors(self, obj):
        authors = obj.authors.all()
        return [f"{author}" for author in authors]


class BookRetrieveSerializer(BookSerializer):
    authors = AuthorSerializer(many=True)
    genres = GenreSerializer(many=True)

import django_filters

from books.models import Book


class BookOrderFilter(django_filters.FilterSet):
    """Custom filter for ordering books by various fields."""
    ordering = django_filters.OrderingFilter(
        fields=(
            ("title", "title"),
            ("year", "year"),
            ("authors__last_name", "author"),
        ),
        field_labels={
            "title": "Title",
            "year": "Year",
            "authors__last_name": "Author",
        }
    )

    class Meta:
        model = Book
        fields = []

import django_filters

from books.models import Book


class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr="icontains")
    authors__first_name = django_filters.CharFilter(
        field_name="authors__first_name", lookup_expr="icontains"
    )
    authors__last_name = django_filters.CharFilter(
        field_name="authors__last_name", lookup_expr="icontains"
    )
    genres = django_filters.CharFilter(
        field_name="genres__name", lookup_expr="icontains"
    )

    class Meta:
        model = Book
        fields = [
            "title",
            "authors__first_name",
            "authors__last_name",
            "genres"
        ]

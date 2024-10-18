import django_filters
from checkout.models import Checkout


class CheckoutFilter(django_filters.FilterSet):
    checkout_date_before = django_filters.DateFilter(
        field_name="checkout_date",
        lookup_expr="lte",
        label="Checkout date is less than or equal to:"
    )

    checkout_date_after = django_filters.DateFilter(
        field_name="checkout_date",
        lookup_expr="gte",
        label="Checkout date is greater than or equal to:"
    )

    checkout_date_exact = django_filters.DateFilter(
        field_name="checkout_date",
        lookup_expr="exact",
        label="Checkout date:"
    )

    is_returned = django_filters.BooleanFilter(
        field_name="actual_return_date",
        lookup_expr="isnull",
        exclude=True,
        label="Exclude actual return date is null:"
    )

    book_title = django_filters.CharFilter(
        field_name="book__title",
        lookup_expr="icontains",
        label="Book title contains:"
    )

    class Meta:
        model = Checkout
        fields = ["checkout_date", "user", "is_returned", "book_title"]

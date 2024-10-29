import django_filters
from django.contrib.auth import get_user_model

from checkout.models import Checkout


User = get_user_model()


class CheckoutFilter(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        label="User",
        empty_label="Select a user"
    )

    user_last_name = django_filters.CharFilter(
        field_name="user__last_name",
        lookup_expr="icontains",
        label="User last name contains"
    )

    book_title = django_filters.CharFilter(
        field_name="book__title",
        lookup_expr="icontains",
        label="Book title contains"
    )

    checkout_date_exact = django_filters.DateFilter(
        field_name="checkout_date",
        lookup_expr="exact",
        label="Checkout date"
    )

    checkout_date_before = django_filters.DateFilter(
        field_name="checkout_date",
        lookup_expr="lte",
        label="Checkout date is less than or equal to"
    )

    checkout_date_after = django_filters.DateFilter(
        field_name="checkout_date",
        lookup_expr="gte",
        label="Checkout date is greater than or equal to"
    )

    is_returned = django_filters.BooleanFilter(
        field_name="actual_return_date",
        lookup_expr="isnull",
        exclude=True,
        label="Show only returned books"
    )

    class Meta:
        model = Checkout
        fields = [
            "user",
            "user_last_name",
            "book_title",
            "checkout_date_exact",
            "checkout_date_before",
            "checkout_date_after",
            "is_returned"
        ]

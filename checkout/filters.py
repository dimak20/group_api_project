import django_filters
from checkout.models import Checkout


class CheckoutFilter(django_filters.FilterSet):
    checkout_date_before = django_filters.DateFilter(
        field_name="checkout_date",
        lookup_expr="lte"
    )
    checkout_date_after = django_filters.DateFilter(
        field_name="checkout_date",
        lookup_expr="gte"
    )
    checkout_date_exact = django_filters.DateFilter(
        field_name="checkout_date",
        lookup_expr="exact"
    )

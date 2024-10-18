import django_filters
from checkout.models import Checkout


class CheckoutOrderFilter(django_filters.FilterSet):
    ordering = django_filters.OrderingFilter(
        fields=(
            ("checkout_date", "checkout_date"),
            ("expected_return_date", "expected_return_date"),
            ("user__username", "user"),
        ),
        field_labels={
            "checkout_date": "Checkout Date",
            "expected_return_date": "Expected Return Date",
            "user__username": "User",
        }
    )

    class Meta:
        model = Checkout
        fields = []

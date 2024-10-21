import django_filters
from checkout.models import Checkout


class CheckoutOrderFilter(django_filters.FilterSet):
    ordering = django_filters.OrderingFilter(
        fields=(
            ("checkout_date", "Checkout Date"),
            ("expected_return_date", "Expected Return Date"),
            ("book__title", "book__title"),
            ("user__last_name", "User Last Name"),
        ),
        field_labels={
            "checkout_date": "Checkout Date",
            "expected_return_date": "Expected Return Date",
            "book__title": "book__title",
            "user__last_name": "User Last Name",
        },
        label="Ordering"
    )

    class Meta:
        model = Checkout
        fields = []

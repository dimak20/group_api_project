import django_filters

from payments.models import StatusChoices, TypeChoices, Payment


class PaymentFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=StatusChoices.choices)
    payment_type = django_filters.ChoiceFilter(choices=TypeChoices.choices)

    class Meta:
        model = Payment
        fields = ["status", "payment_type"]

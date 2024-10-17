from rest_framework import serializers

from checkout.serializers import CheckoutListSerializer, CheckoutDetailSerializer
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "payment_type",
            "checkout",
            "session_url",
            "session_id",
            "money_to_pay"
        ]


class PaymentListSerializer(PaymentSerializer):
    checkout = CheckoutListSerializer(many=True, read_only=True)


class PaymentDetailSerializer(PaymentSerializer):
    checkout = CheckoutListSerializer(many=True, read_only=True)

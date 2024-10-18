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
    checkout = CheckoutListSerializer()

class PaymentDetailSerializer(PaymentSerializer):
    checkout = CheckoutDetailSerializer()

class BorrowingIDSerializer(serializers.Serializer):
    checkout_id = serializers.IntegerField()
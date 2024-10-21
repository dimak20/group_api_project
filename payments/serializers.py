from rest_framework import serializers

from checkout.serializers import CheckoutListSerializer, CheckoutDetailSerializer, CheckoutPaymentSerializer
from payments.models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            "id",
            "status",
            "payment_type",
            "checkout",
            "short_url",
            "session_id",
            "total_amount",
        ]


class PaymentListSerializer(PaymentSerializer):
    checkout = CheckoutPaymentSerializer()


class PaymentDetailSerializer(PaymentSerializer):
    checkout = CheckoutListSerializer()
    class Meta(PaymentSerializer.Meta):
        fields = [
            "id",
            "status",
            "payment_type",
            "checkout",
            "session_url",
            "short_url",
            "session_id",
            "total_amount",
        ]


class BorrowingIDSerializer(serializers.Serializer):
    checkout_id = serializers.IntegerField()

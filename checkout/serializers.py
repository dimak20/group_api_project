from django.utils import timezone
from rest_framework import serializers
from urllib3 import request

from books.serializers import BookSerializer
from checkout.models import Checkout
from user.serializers import UserSerializer


class CheckoutSerializer(serializers.ModelSerializer):
    payments = serializers.StringRelatedField(many=True, read_only=True)

    def validate(self, attrs):

        data = super(CheckoutSerializer, self).validate(attrs=attrs)
        Checkout.validate_book(attrs["book"], serializers.ValidationError)
        if not self.instance:
            Checkout.validate_return_date(
                timezone.now().date(),
                attrs["expected_return_date"],
                serializers.ValidationError
            )

        if self.instance is None and "expected_return_date" not in attrs:
            raise serializers.ValidationError(
                {"expected_return_date": "This field is required."}
            )

        return data

    class Meta:
        model = Checkout
        fields = [
            "id",
            "expected_return_date",
            "book",
            "payments"
        ]

    def update(self, instance, validated_data):
        if (
                "expected_return_date" in validated_data
                and validated_data
        ["expected_return_date"] != instance.expected_return_date
        ):
            raise serializers.ValidationError(
                {"expected_return_date":
                     "You cannot change this field after checkout."}
            )
        return super().update(instance, validated_data)


class CheckoutListSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField(many=False)
    user = serializers.StringRelatedField(many=False)
    payments = serializers.StringRelatedField(many=True)

    class Meta:
        model = Checkout
        fields = [
            "id",
            "checkout_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments"
        ]


class CheckoutDetailSerializer(CheckoutListSerializer):
    book = BookSerializer(many=False, read_only=True)
    user = UserSerializer(many=False, read_only=True)
    payments = serializers.SerializerMethodField()

    def get_payments(self, obj):
        from payments.serializers import PaymentSerializer
        return PaymentSerializer(obj.payments.all(), many=True).data


class CheckoutReturnSerializer(serializers.ModelSerializer):
    book = serializers.StringRelatedField(many=False)
    payments = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Checkout
        fields = [
            "id",
            "book",
            "payments"
        ]


class CheckoutPaymentSerializer(CheckoutListSerializer):
    class Meta(CheckoutListSerializer.Meta):
        fields = [
            "id",
            "checkout_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        request = self.context.get("request")
        if not request.user.is_staff:
            representation.pop("user", None)

        return representation

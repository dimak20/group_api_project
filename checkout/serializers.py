from rest_framework import serializers

from books.serializers import BookSerializer
from user.serializers import UserSerializer
from checkout.models import Checkout


class CheckoutSerializer(serializers.ModelSerializer):
    expected_return = serializers.DateField(required=True)

    class Meta:
        model = Checkout
        fields = [
            "id",
            "checkout_date",
            "expected_return",
            "book",
            "user",
        ]


        def validate(self, attrs):
            Checkout.validate(attrs["book"], serializers.ValidationError())

            if self.instance is None and "expected_return_date" not in attrs:
                raise serializers.ValidationError(
                    {"expected_return_date": "This field is required."}
                )

            return attrs

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

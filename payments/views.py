import logging
from datetime import timedelta
from decimal import Decimal

import stripe
from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from checkout.models import Checkout
from payments.models import Payment, StatusChoices
from payments.serializers import (
    PaymentListSerializer,
    PaymentDetailSerializer,
    PaymentSerializer,
    BorrowingIDSerializer,
)

logger = logging.getLogger(__name__)

DOMAIN = settings.HOME_DOMAIN

WEBHOOK_SECRET = settings.WEBHOOK_SECRET

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

FINE_MULTIPLIER = 2


class PaymentViewSet(viewsets.ModelViewSet):
    model = Payment
    queryset = Payment.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer

        if self.action == "retrieve":
            return PaymentDetailSerializer

        return PaymentSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ["list", "retrieve"] and not self.request.user.is_staff:
            return queryset.filter(
                borrowing__user__id=self.request.user
            ).select_related()

        if self.action in ["list", "retrieve"]:
            return self.queryset.select_related()

        return queryset


@extend_schema(
    request=BorrowingIDSerializer,
    responses={
        201: PaymentSerializer,
        404: "Borrowing not found",
        400: "Bad request",
    },
)
class CreateCheckoutSessionView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BorrowingIDSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        borrowing_id = serializer.validated_data["checkout_id"]
        try:
            borrowing = Checkout.objects.get(id=borrowing_id)
            borrow_duration_days = 3
            money_to_pay = int(
                (
                        Decimal(borrow_duration_days)
                        * borrowing.book.daily_fee
                        * Decimal("100")
                ).quantize(Decimal("1"))
            )
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "usd",
                            "product_data": {
                                "name": borrowing.book.title,
                            },
                            "unit_amount": money_to_pay,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url=DOMAIN + "/api/v1/payments/success/?session_id={CHECKOUT_SESSION_ID}",
                cancel_url=DOMAIN + "/apu/v1/payments/cancel/",
            )
            payment = Payment.objects.create(
                status="pending",
                payment_type="payment",
                checkout=borrowing,
                session_url=checkout_session.url,
                session_id=checkout_session.id,
                money_to_pay=money_to_pay,
            )
            serializer = PaymentSerializer(payment)

            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Checkout.DoesNotExist:
            return JsonResponse(
                {"error": "Borrowing not found."}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class CancelPaymentView(APIView):
    def get(self, request, *args, **kwargs):
        available_until = timezone.now() + timedelta(hours=24)

        message = {
            "message": "You can paid for this borrowing in 24 hours",
            "available_until": available_until.isoformat()
        }

        return Response(message, status=status.HTTP_200_OK)


class SuccessPaymentView(APIView):
    def get(self, request, *args, **kwargs):
        session_id = request.query_params.get("session_id")

        if not session_id:
            return Response("Stripe has failed to provide session id.", status=400)

        payment = get_object_or_404(Payment, session_id=session_id)
        payment.status = StatusChoices.PAID
        payment.save()

        return Response("Your payment was successful!", status=status.HTTP_200_OK)

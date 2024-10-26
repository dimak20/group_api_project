from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payments.views import (
    PaymentViewSet,
    CreateCheckoutSessionView,
    CancelPaymentView,
    SuccessPaymentView,
    StripeWebhookView,
)

app_name = "payment"

router = DefaultRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "create-checkout-session/",
        CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("cancel/", CancelPaymentView.as_view(), name="cancel-url"),
    path("success/", SuccessPaymentView.as_view(), name="success-url"),
    path("stripe/webhook/", StripeWebhookView.as_view(), name="stripe-webhook"),
]

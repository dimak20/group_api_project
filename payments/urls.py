from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payments.views import (
    PaymentViewSet,
    CreateCheckoutSessionView,
    CancelPaymentView,
    SuccessPaymentView,
)

app_name = "payments"

router = DefaultRouter()
router.register("payments", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path(
        "create-checkout-session/",
        CreateCheckoutSessionView.as_view(),
        name="create-checkout-session",
    ),
    path("cancel", CancelPaymentView.as_view(), name="cancel-url"),
    path("success/", SuccessPaymentView.as_view(), name="success-url"),
]

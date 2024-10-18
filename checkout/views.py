from django.db import transaction
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response

from checkout.filters import CheckoutFilter
from checkout.models import Checkout
from checkout.serializers import (
    CheckoutListSerializer,
    CheckoutDetailSerializer,
    CheckoutReturnSerializer,
    CheckoutSerializer
)
from notifications.tasks import send_successful_checkout
from payments.services import create_checkout_session


class CheckoutViewSet(viewsets.ModelViewSet):
    model = Checkout
    queryset = Checkout.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter]
    filterset_class = CheckoutFilter
    ordering_fields = [
        "checkout_date",
        "expected_return_date",
        "book__title",
        "user__last_name"
    ]
    ordering = ["checkout_date"]

    def get_serializer_class(self):

        if self.action == "list":
            return CheckoutListSerializer
        if self.action == "retrieve":
            return CheckoutDetailSerializer
        if self.action == "return_book":
            return CheckoutReturnSerializer

        return CheckoutSerializer

    def get_queryset(self):
        queryset = self.queryset

        if (
            self.action in ("list", "retrieve")
            and not self.request.user.is_staff
        ):
            return queryset.filter(
                user=self.request.user,
                actual_return_date=None
            ).select_related()

        if self.action in ("list", "retrieve"):
            return self.queryset.select_related()

        return queryset

    def perform_create(self, serializer):
        instance = serializer.save(
            user=self.request.user,
        )

        create_checkout_session(instance.id, self.request, overdue=False)

        send_successful_checkout(self.request.user.id, instance.id)

    @action(
        methods=("POST",),
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
        url_path="return"
    )
    def return_book(self, request, *args, **kwargs):
        checkout = self.get_object()
        book = checkout.book
        if checkout.actual_return_date:
            return Response(
                {
                    "Return error": "this book is already returned"
                }
            )
        with transaction.atomic():
            book.inventory += 1
            checkout.actual_return_date=timezone.now()
            book.save()
            checkout.save(update_fields=("actual_return_date",))

        if checkout.actual_return_date > checkout.expected_return_date:
            create_checkout_session(checkout.id, self.request, overdue=True)

        serializer = self.get_serializer(checkout, data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
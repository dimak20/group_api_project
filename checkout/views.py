from tkinter.tix import CheckList

from django.shortcuts import render
from rest_framework import viewsets, permissions

from checkout.models import Checkout
from checkout.serializers import (
    CheckoutListSerializer,
    CheckoutDetailSerializer,
    CheckoutReturnSerializer,
    CheckoutSerializer
)


class CheckoutViewSet(viewsets.ModelViewSet):
    model = Checkout
    queryset = Checkout.objects.all()
    permission_classes = [permissions.IsAuthenticated]

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


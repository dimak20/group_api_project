from tkinter.tix import CheckList

from django.shortcuts import render
from rest_framework import viewsets

from checkout.models import Checkout


class CheckoutViewSet(viewsets.ModelViewSet):
    queryset = Checkout.objects.all()

    def get_serializer_class(self):

        if self.action == "list":
            return ChekoutListSerializer
        if self.action == "retrieve":
            return CheckoutDetailSerializer

        return CheckoutSerializer

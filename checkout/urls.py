from django.urls import include, path
from rest_framework import routers

from checkout import views

router = routers.DefaultRouter()
router.register("", views.CheckoutViewSet)

urlpatterns = [
    path("", include(router.urls)),
               ]

app_name = "checkouts"
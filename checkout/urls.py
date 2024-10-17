from django.urls import include
from rest_framework import routers

from checkout import views

router = routers.DefaultRouter()
router.register("checkout", views.CheckoutViewSet)

urlpatterns = ("", include(router.urls))
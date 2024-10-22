"""
URL configuration for group_library_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        "api/v1/catalog/",
        include("books.urls", namespace="catalog")
    ),
    path(
        "api/v1/checkouts/",
        include("checkout.urls", namespace="checkouts")
    ),
    path(
        "api/v1/user/",
        include("user.urls", namespace="users")
    ),
    path(
        "api/v1/payments/",
        include("payments.urls", namespace="payments"),
    ),
    path("api/v1/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/v1/doc/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/v1/doc/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    path("prometheus/", include("django_prometheus.urls")),
    path("api/v1/handlers/", include("manage_handler.urls", namespace="handlers"))

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

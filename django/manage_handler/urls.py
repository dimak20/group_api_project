from django.urls import path

from manage_handler.views import BotHandler, EmailHandler, ProfileHandler, UnregisterProfileHandler

app_name = "handlers"

urlpatterns = [
    path('test/', BotHandler.as_view(), name="bot-handler"),
    path('get-email/', EmailHandler.as_view(), name="email-handler"),
    path('find-create-profile/', ProfileHandler.as_view(), name="profile-handler"),
    path('find-delete-profile/', UnregisterProfileHandler.as_view(), name="profile-delete-handler"),
]

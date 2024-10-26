from django.urls import path

from rabbit_commander.views import send_message

app_name = "rabbits"
urlpatterns = [
    path("test/", send_message.as_view(), name="test123"),
]

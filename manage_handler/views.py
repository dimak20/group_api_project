from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from notifications.models import NotificationProfile


class BotHandler(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        data = request.data.get("aaa")
        return Response(
            {"re": "Потужний!"},
            status=200
        )


class EmailHandler(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        email = request.data.get("email")
        user = get_user_model().objects.filter(email=email).first()
        if user:
            return Response(
                {"user_id": user.id},
                status=200
            )
        return Response(
            {"user_id": False},
            status=404
        )


class ProfileHandler(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        user_id = request.data.get("user_id")
        chat_id = request.data.get("chat_id")
        profile = NotificationProfile.objects.filter(user_id=user_id).first()
        if profile:
            return Response(
                {"created": False},
                status=200
            )
        else:
            NotificationProfile.objects.create(user_id=user_id, chat_id=chat_id)
            return Response(
                {"created": True},
                status=200
            )


class UnregisterProfileHandler(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        user_id = request.data.get("user_id")
        chat_id = request.data.get("chat_id")
        profile = NotificationProfile.objects.filter(user_id=user_id).first()
        if profile:
            if profile.chat_id == chat_id:
                profile.delete()

                return Response(
                    {"profile": True, "access": True},
                    status=200
                )
            else:

                return Response(
                    {"profile": True, "access": False},
                    status=200
                )
        else:
            return Response(
                {"profile": False},
                status=200
            )

from django.http import JsonResponse
from rest_framework.views import APIView

from .pika_setup import send_message_to_queue


class send_message(APIView):
    permission_classes = []
    authentication_classes = []


    def get(self, request):
        message = "Hello, RabbitMQ!"
        send_message_to_queue(queue_name="PAYMENTS", message=message)
        return JsonResponse({"status": "Message sent"})

from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from .kafka_utils import send_message  # Import Kafka producer function

class KafkaMessageView(View):
    def get(self, request):
        send_message('excel_data', 'Message from Django API!')
        return JsonResponse({'message': 'Sent to Kafka'})

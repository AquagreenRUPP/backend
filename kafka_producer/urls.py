from django.urls import path
from .views import KafkaMessageView

urlpatterns = [
    #path('send-kafka-message/', KafkaMessageView.as_view(), name='send_kafka_message'),
]
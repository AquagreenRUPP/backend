import json
import logging
from kafka import KafkaProducer
from django.conf import settings

logger = logging.getLogger(__name__)

class KafkaProducerClient:
    """Utility class for publishing data to Kafka."""
    
    def __init__(self):
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.topic = settings.KAFKA_TOPIC
        self.producer = None
        self.kafka_enabled = settings.KAFKA_ENABLED
    
    def _connect(self):
        """Connect to Kafka broker."""
        if not self.kafka_enabled:
            logger.info("Kafka is disabled. Skipping connection.")
            return False
            
        if self.producer is not None:
            return True
            
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            logger.info(f"Connected to Kafka broker at {self.bootstrap_servers}")
            return True
        except Exception as e:
            logger.warning(f"Failed to connect to Kafka broker: {str(e)}")
            self.producer = None
            return False
    
    def publish_data(self, data, key=None):
        """Publish data to Kafka topic.
        
        Args:
            data (dict): Data to publish
            key (str, optional): Message key
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.kafka_enabled:
            logger.info("Kafka is disabled. Skipping publish.")
            return True
            
        if not self._connect():
            logger.error("Kafka producer not initialized")
            return False
        
        try:
            key_bytes = key.encode('utf-8') if key else None
            future = self.producer.send(self.topic, value=data, key=key_bytes)
            # Block until the message is sent (or timeout)
            future.get(timeout=10)
            logger.info(f"Published data to topic {self.topic}")
            return True
        except Exception as e:
            logger.error(f"Failed to publish data to Kafka: {str(e)}")
            return False
    
    def close(self):
        """Close the Kafka producer."""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")

# Singleton instance
kafka_producer = KafkaProducerClient()

import json
import logging
from kafka import KafkaProducer, KafkaConsumer
from django.conf import settings

logger = logging.getLogger(__name__)

class KafkaClient:
    def __init__(self):
        self.enabled = settings.KAFKA_ENABLED
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.topic = settings.KAFKA_TOPIC
        self.producer = None
        self.consumer = None
        
        if self.enabled:
            try:
                self.init_producer()
                logger.info(f"Kafka producer initialized with servers: {self.bootstrap_servers}")
            except Exception as e:
                logger.error(f"Failed to initialize Kafka producer: {str(e)}")
    
    def init_producer(self):
        """Initialize the Kafka producer"""
        if not self.enabled:
            return
            
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',  # Wait for all replicas to acknowledge
                retries=3,   # Retry up to 3 times
                retry_backoff_ms=100  # 100ms backoff between retries
            )
        except Exception as e:
            logger.error(f"Error initializing Kafka producer: {str(e)}")
            raise
    
    def init_consumer(self, group_id='aquagreen-consumer', auto_offset_reset='earliest'):
        """Initialize the Kafka consumer"""
        if not self.enabled:
            return
            
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=self.bootstrap_servers,
                group_id=group_id,
                auto_offset_reset=auto_offset_reset,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
            return self.consumer
        except Exception as e:
            logger.error(f"Error initializing Kafka consumer: {str(e)}")
            raise
    
    def publish_data(self, data):
        """Publish data to Kafka topic"""
        if not self.enabled:
            logger.warning("Kafka publishing disabled. Message not sent.")
            return False
            
        if not self.producer:
            try:
                self.init_producer()
            except Exception as e:
                logger.error(f"Failed to initialize Kafka producer for message publishing: {str(e)}")
                return False
        
        try:
            future = self.producer.send(self.topic, data)
            # Block until the message is sent (or timeout after 10 seconds)
            record_metadata = future.get(timeout=10)
            logger.info(f"Message published to Kafka topic: {self.topic}, "  
                       f"partition: {record_metadata.partition}, "  
                       f"offset: {record_metadata.offset}")
            return True
        except Exception as e:
            logger.error(f"Error publishing to Kafka: {str(e)}")
            return False
    
    def consume_messages(self, handler_func, timeout_ms=1000):
        """Consume messages from Kafka topic"""
        if not self.enabled:
            logger.warning("Kafka consumption disabled.")
            return
            
        if not self.consumer:
            try:
                self.init_consumer()
            except Exception as e:
                logger.error(f"Failed to initialize Kafka consumer for message consumption: {str(e)}")
                return
        
        try:
            for message in self.consumer:  
                try:
                    handler_func(message.value)
                except Exception as e:
                    logger.error(f"Error processing Kafka message: {str(e)}")
        except Exception as e:
            logger.error(f"Error consuming from Kafka: {str(e)}")
    
    def close(self):
        """Close Kafka connections"""
        if self.producer:
            self.producer.close()
            logger.info("Kafka producer closed")
        
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")

# Create a singleton instance
kafka_client = KafkaClient()

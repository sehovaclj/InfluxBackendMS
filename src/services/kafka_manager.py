"""
Kafka consumer module for processing and handling messages from a Kafka topic.

This module initializes a Kafka consumer, subscribes to a specific topic,
polls for new messages, and processes them. Each message is deserialized,
logged, and stored in InfluxDB using the `store_data_influx` function.
The consumer gracefully handles Kafka errors and ensures cleanup on exit.
"""

import json

from confluent_kafka import Consumer, KafkaError, Message

from src.config.logging import LoggingConfig
from src.config.kafka import KafkaConfig
from src.services.influx_manager import InfluxManager

# Configure the logger
logger = LoggingConfig.get_logger(__name__)

# initialize influx manager
influx_manager = InfluxManager()


def handle_kafka_error(msg: Message) -> None:
    """
    Handle Kafka errors, specifically end-of-partition events and log
    any other Kafka errors.

    Args:
        msg (confluent_kafka.Message): The Kafka message object containing
            the error.
    """
    # pylint: disable=W0212
    if msg.error().code() == KafkaError._PARTITION_EOF:
        # End of partition event, can be ignored
        logger.info(
            "End of partition reached %s [%d] at offset %d",
            msg.topic(), msg.partition(), msg.offset())
    else:
        # Log other errors
        logger.error("Kafka error: %s", msg.error())


def process_message(msg: Message) -> None:
    """
    Process a Kafka message by deserializing and store in InfluxDB.

    Args:
        msg (confluent_kafka.Message): The Kafka message object containing
            the error.
    """
    msg_dict = json.loads(msg.value().decode('utf-8'))
    logger.info(
        "Received message in topic: %s [%d]",
        msg.topic(), msg.partition())
    influx_manager.store_data_influx(msg_dict)


def start_consumer() -> None:
    """
    Initialize and start a Kafka consumer to process messages from a
    Kafka topic.

    The consumer subscribes to the Kafka topic specified in KafkaConfig, polls
    for new messages, and processes each received message by
    deserializing it and storing it in InfluxDB via the
    `store_data_influx` function.

    This function runs continuously until interrupted. It handles
    errors such as end-of-partition events and logs any other Kafka
    errors. When interrupted, it ensures proper resource cleanup by
    closing the consumer.

    Raises:
        KeyboardInterrupt: Allows user interruption to stop the consumer.
    """
    # Initialize the consumer
    consumer = Consumer(KafkaConfig.consumer_config)
    # Subscribe to the Kafka topic
    consumer.subscribe([KafkaConfig.KAFKA_TOPIC])

    try:
        logger.info("Starting Kafka consumer...")
        while True:
            # Poll for new messages, and wait up to 1 second for a message
            msg = consumer.poll(timeout=1.0)
            if msg is None:
                continue  # No message, continue polling
            if msg.error():
                handle_kafka_error(msg)
                continue
            # Process the message
            process_message(msg)

    except KeyboardInterrupt:
        logger.info("Consumer interrupted by user")
    finally:
        # Clean up and close consumer
        consumer.close()
        logger.info("Kafka consumer closed")
        # also close the influx db connection
        influx_manager.close()
        logger.info("InfluxDB client closed")

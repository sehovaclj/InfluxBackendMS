"""
Module for managing data in InfluxDB.

Classes:
    InfluxManager: A class to interact with InfluxDB for storing battery data.
"""

from typing import Dict
from influxdb_client import Point
from src.config.db import DbConfig
from src.config.logging import LoggingConfig
from src.db.connection import connect_to_influxdb
from src.utils.datetime_utils import utc_now_timestamp

# initialize logger
logger = LoggingConfig.get_logger(__name__)


class InfluxManager:
    """
    A class to manage InfluxDB interactions for storing battery data.

    Attributes:
        client (InfluxDBClient): The InfluxDB client connection.
        write_api (WriteApi): The InfluxDB write API.
    """

    def __init__(self):
        """
        Initializes the InfluxManager by connecting to InfluxDB.
        """
        # Connect to InfluxDB and get both the client and write API
        self.client, self.write_api = connect_to_influxdb()

    def close(self) -> None:
        """
        Closes the InfluxDB client connection.
        """
        self.client.close()

    def store_data_influx(self, message: Dict[str, int]) -> None:
        """
        Processes each message by storing it in InfluxDB.

        Args:
            message (dict): The Kafka consumer message to be processed.
        """
        # get the timestamp from the battery, and now time
        battery_timestamp = message.get("timestamp")
        now_time_utc_ms = utc_now_timestamp()
        # compute latency
        latency_ms = now_time_utc_ms - battery_timestamp

        # Create an InfluxDB data point
        point = (
            Point("battery_data")
            .tag("battery_id", str(message.get('battery_id', -1)))
            .field("voltage", message.get("voltage", -1))
            .field("current", message.get("current", -1))
            .field("temperature", message.get("temperature", -1))
            .field("state_of_charge", message.get("state_of_charge", -1))
            .field("state_of_health", message.get("state_of_health", -1))
            .field("influx_timestamp", now_time_utc_ms)
            .field("latency_ms", latency_ms)
            .time(battery_timestamp, write_precision="ms")
        )

        # Write the data point to InfluxDB
        self.write_api.write(bucket=DbConfig.INFLUX_BUCKET,
                             org=DbConfig.INFLUX_ORG,
                             record=point)
        logger.info("Successfully logged a data point in InfluxDB")

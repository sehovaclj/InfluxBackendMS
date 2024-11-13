"""
This module handles connection to an Influx DB with logging.
"""

from typing import Tuple, Union
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import WriteApi, SYNCHRONOUS
from influxdb_client.client.exceptions import InfluxDBError
from src.config.logging import LoggingConfig
from src.config.db import DbConfig

# Configure the logger
logger = LoggingConfig.get_logger(__name__)


def connect_to_influxdb() -> Union[Tuple[InfluxDBClient, WriteApi], None]:
    """
    Connects to an InfluxDB instance and returns the InfluxDB client
        and Write API if the connection is successful.

    Returns:
        Tuple[InfluxDBClient, WriteApi] or None: InfluxDB client and
            Write API if connected, None otherwise.
    """
    try:
        client = InfluxDBClient(
            url=DbConfig.INFLUX_URL,
            token=DbConfig.INFLUX_TOKEN,
            org=DbConfig.INFLUX_ORG
        )

        if client.ping():
            logger.info("Successfully connected to InfluxDB.")
            return client, client.write_api(write_options=SYNCHRONOUS)
        logger.error("Failed to connect to InfluxDB: Ping failed.")
        return None

    except InfluxDBError as err:
        logger.error("Failed to connect to InfluxDB: %s", err)
        return None

"""
Configures the InfluxDB parameters using environment variables.

Reads from a `.env` file to set InfluxDB parameters.
"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class DbConfig:
    """
    Configuration class for InfluxDB settings.

    This class loads the InfluxDB configuration from environment variables.
    """
    # InfluxDB configuration
    INFLUX_URL = os.getenv('INFLUX_URL')
    INFLUX_TOKEN = os.getenv('INFLUX_TOKEN')
    INFLUX_ORG = os.getenv('INFLUX_ORG')
    INFLUX_BUCKET = os.getenv('INFLUX_BUCKET')

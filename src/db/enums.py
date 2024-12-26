from enum import Enum
from sqlalchemy.pool import QueuePool
from config.settings import (
    SERVER,
    INSTANCE,
    DATABASE,
    DRIVER,
    POOL_CLASS,
    POOL_SIZE,
    MAX_OVERFLOW,
    POOL_TIMEOUT,
    POOL_RECYCLE,
    POOL_PRE_PING,
)


class DatabaseSettings(Enum):
    SERVER = SERVER
    INSTANCE = INSTANCE
    DATABASE = DATABASE  # Assuming a single database value
    DRIVER = DRIVER

    get_connection_string = (
        lambda self: f"mssql+pyodbc://@{self.SERVER.value}\\{self.INSTANCE.value}/{self.DATABASE.value}?driver={self.DRIVER.value}&trusted_connection=yes"
    )
    get_master_connection_string = (
        lambda self: f"mssql+pyodbc://@{self.SERVER.value}\\{self.INSTANCE.value}/master?driver={self.DRIVER.value}&trusted_connection=yes"
    )


class EngineSettings(Enum):
    # SQLAlchemy connection pool configuration
    POOL_CLASS = POOL_CLASS
    POOL_SIZE = POOL_SIZE  # Adjust based on expected concurrency
    MAX_OVERFLOW = MAX_OVERFLOW  # Extra connections beyond pool_size
    POOL_TIMEOUT = POOL_TIMEOUT
    POOL_RECYCLE = POOL_RECYCLE
    POOL_PRE_PING = POOL_PRE_PING

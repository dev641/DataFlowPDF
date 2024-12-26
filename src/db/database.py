from sqlalchemy.orm import sessionmaker
from functools import wraps
from src.db.repository.voter_repository import VoterRepository
from src.db.enums import DatabaseSettings, EngineSettings
from src.db.decorators import (
    create_database,
    analyze_data,
    create_table,
)
from config.settings import DATABASE_INSERT_BATCH_SIZE
from src.utils.logger import setup_logger
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    LargeBinary,
    MetaData,
    Table,
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.db.voter_schema import data
import os

Base = declarative_base()
log = setup_logger(__name__)


class Database:
    def __init__(
        self,
        server,
        instance,
        database,
        driver,
        connection_string,
    ):
        self.server = server
        self.instance = instance
        self.database = database
        self.driver = driver
        self.db_url = connection_string
        self.engine = self.get_engine(db_url=self.db_url)
        # Create the MetaData object
        self.metadata = MetaData()

        # Bind the engine to the MetaData object
        self.metadata.bind = self.engine

        # Create the Base class with the metadata
        self.Base = declarative_base(metadata=self.metadata)
        self.Session = sessionmaker(bind=self.engine)

    def get_engine(self, db_url):
        return create_engine(
            url=db_url,
            poolclass=EngineSettings.POOL_CLASS.value,
            pool_size=EngineSettings.POOL_SIZE.value,  # Adjust based on expected concurrency
            max_overflow=EngineSettings.MAX_OVERFLOW.value,  # Extra connections beyond pool_size
            pool_timeout=EngineSettings.POOL_TIMEOUT.value,
            pool_recycle=EngineSettings.POOL_RECYCLE.value,
            pool_pre_ping=EngineSettings.POOL_PRE_PING.value,
        )

    def execute_query(self, query, params=None):
        """Executes a query and returns the result."""
        with self.engine.connect() as connection:
            result = connection.execute(text(query), params)
            return result.fetchall()

    def execute_transaction(self, query, params=None):
        """Executes a query within a transaction."""
        with self.Session() as session:
            result = session.execute(text(query), params)
            session.commit()
            return result.fetchall()

    def normalize_records(self, data, schema_keys):
        """
        Ensure all records have all keys from the schema with None as default for missing keys.
        """
        normalized_data = []
        for record in data:
            normalized_record = {
                key: record.get(key, None)
                for key in schema_keys
                if key != "id"
            }
            normalized_data.append(normalized_record)
        return normalized_data

    def _insert_data_in_batches(self, table, data, batch_size=500):
        """
        Inserts data into the dynamically created table in batches.
        """
        session = self.Session()
        # Get the column names
        column_names = [column.name for column in table.columns]
        print("Column names:", column_names)
        try:
            # Split the data into batches
            for i in range(0, len(data), batch_size):
                batch = data[i : i + batch_size]
                batch = self.normalize_records(batch, column_names)
                session.execute(table.insert(), batch)
                session.commit()
                print(
                    f"Successfully inserted {len(batch)} rows into {table.name}. Batch {i // batch_size + 1}"
                )
        except Exception as e:
            session.rollback()
            print(f"Error inserting data: {e}")
        finally:
            session.close()

    @analyze_data
    @create_table
    def persist_data(
        self, table_name, table, data, batch_size=DATABASE_INSERT_BATCH_SIZE
    ):
        """
        Analyzes data, creates schema, creates database, and inserts data in batches.
        """
        # Step 4: Insert data in batches
        self._insert_data_in_batches(table, data, batch_size)


@create_database(database_name=DatabaseSettings.DATABASE.value)
def persist_data_in_db(table_name, data, batch_size):
    # Instantiate the Database class
    db = Database(
        server=DatabaseSettings.SERVER.value,
        instance=DatabaseSettings.INSTANCE.value,
        database=DatabaseSettings.DATABASE.value,
        driver=DatabaseSettings.DRIVER.value,
        connection_string=DatabaseSettings.get_connection_string(
            DatabaseSettings
        ),
    )

    db.persist_data(table_name=table_name, data=data, batch_size=batch_size)


# persist_data_in_db(table_name="voters", data=data, batch_size=500)

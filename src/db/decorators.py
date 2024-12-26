from functools import wraps
import inspect
import os
from sqlalchemy import (
    Column,
    Integer,
    String,
    Table,
    Unicode,
    create_engine,
    text,
    LargeBinary,
)

from src.db.enums import DatabaseSettings
from src.utils.logger import setup_logger

log = setup_logger(__name__)


def Query(query_template):
    """Decorator that takes a query, executes it using the Database class, and returns the result."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            log.info(
                f"Starting execution of query for function: {func.__name__}"
            )
            self = args[0]
            # Get the method signature and parameter names
            signature = inspect.signature(func)
            bound_arguments = signature.bind(self, *args, **kwargs)
            bound_arguments.apply_defaults()

            # Extract the parameters and map them to the query
            params = bound_arguments.arguments
            query = query_template.format(**params)
            log.debug(f"Generated query: {query}")

            try:
                result = self.db_instance.execute_query(query)
                log.info(f"Query executed successfully for {func.__name__}")
                return func(self, result, *args, **kwargs)
            except Exception as e:
                log.error(
                    f"Error executing query in {func.__name__}: {str(e)}"
                )
                raise

        return wrapper

    return decorator


def Transaction(query_template):
    """Decorator that takes a query, executes it using the Database class, and returns the result."""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            log.info(f"Starting transaction for function: {func.__name__}")
            # Get the method signature and parameter names
            signature = inspect.signature(func)
            bound_arguments = signature.bind(*args, **kwargs)
            bound_arguments.apply_defaults()

            # Extract the parameters and map them to the query
            params = bound_arguments.arguments
            query = query_template.format(**params)
            log.debug(f"Generated transaction query: {query}")

            try:
                result = self.db_instance.execute_transaction(query)
                log.info(
                    f"Transaction completed successfully for {func.__name__}"
                )
                return func(self, result, *args, **kwargs)
            except Exception as e:
                log.error(
                    f"Error executing transaction in {func.__name__}: {str(e)}"
                )
                raise

        return wrapper

    return decorator


def create_database(database_name):
    log.info(f"Starting database creation check for: {database_name}")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Automatically detect the current Windows user
                current_user = os.getlogin()
                domain_user = f"{os.environ['USERDOMAIN']}\\{current_user}"
                log.debug(f"Detected domain user: {domain_user}")

                # Create an engine connected to the master database
                log.info("Creating database engine connection")
                engine = create_engine(
                    DatabaseSettings.get_master_connection_string(
                        DatabaseSettings
                    ),
                    fast_executemany=True,
                    isolation_level="AUTOCOMMIT",
                )

                with engine.connect() as connection:
                    log.debug(
                        f"Executing database creation query for: {database_name}"
                    )
                    connection.execute(
                        text(
                            f"""
                                IF NOT EXISTS (SELECT * FROM sys.databases WHERE name = '{database_name}')
                                BEGIN
                                    CREATE DATABASE {database_name}
                                    COLLATE Latin1_General_100_CI_AS_SC_UTF8;
                                    PRINT 'Database {database_name} created successfully';
                                END
                                ELSE
                                BEGIN
                                    PRINT 'Database {database_name} already exists';
                                END
                            """
                        )
                    )
                    log.info(
                        f"Database {database_name} creation/check completed successfully"
                    )

            except Exception as e:
                log.error(f"Error during database creation: {str(e)}")
                raise

            return func(*args, **kwargs)

        return wrapper

    return decorator


def analyze_data(func):
    def assign_column_type(key, value, schema):
        if isinstance(value, int):
            schema[key] = Integer
            log.debug(f"Column '{key}' detected as Integer type")
        elif isinstance(value, str):
            schema[key] = Unicode(255)
            log.debug(f"Column '{key}' detected as Unicode type")
            # if any(ord(c) > 127 for c in value):
            #     schema[key] = Unicode(255)
            #     log.debug(f"Column '{key}' detected as Unicode type")
            # else:
            #     schema[key] = String(255)
            #     log.debug(f"Column '{key}' detected as String type")
        elif isinstance(value, bytes):
            schema[key] = LargeBinary
            log.debug(f"Column '{key}' detected as LargeBinary type")
        else:
            schema[key] = Unicode(255)
            log.debug(f"Column '{key}' defaulted to String type")

    @wraps(func)
    def wrapper(*args, **kwargs):
        log.info("Starting data analysis...")
        data = kwargs.get("data", None)
        schema = {}

        log.debug(f"Analyzing {len(data)} records for schema detection")
        for record in data:
            for key, value in record.items():
                # Dynamically determine the column type based on the value
                if key is not None:
                    assign_column_type(key, value, schema)
                else:
                    log.warn("Key is None, column is set to unicode")
                    assign_column_type("column", value, schema)

        log.info(f"Schema analysis completed with {len(schema)} columns")
        # Attach the schema to the function
        setattr(func, "schema", schema)
        # Attach the schema to the wrapper function
        wrapper.schema = schema

        return func(*args, **kwargs)

    return wrapper


def create_table(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        log.info("Starting table creation process...")
        self = args[0]
        table_name = kwargs.get("table_name", None)
        schema = getattr(wrapper, "schema", None)

        log.debug(f"Creating table structure for: {table_name}")
        columns = [Column('id', Integer, primary_key=True, autoincrement=True)]
        for column_name, column_type in schema.items():
            columns.append(Column(column_name, column_type, nullable=True))
            log.debug(f"Added column: {column_name} with type: {column_type}")

        table = Table(table_name, self.metadata, *columns)
        log.info(f"Creating table {table_name} in database")
        table.create(self.engine, checkfirst=True)

        log.debug("Attaching table object to function and wrapper")
        setattr(func, "table", table)
        wrapper.table = table
        kwargs["table"] = table

        log.info(f"Table {table_name} created successfully")
        return func(*args, **kwargs)

    return wrapper

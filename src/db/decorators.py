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
        def wrapper(self, *args, **kwargs):
            # Get the method signature and parameter names
            signature = inspect.signature(func)
            bound_arguments = signature.bind(self, *args, **kwargs)
            bound_arguments.apply_defaults()
            # Extract the parameters and map them to the query
            params = bound_arguments.arguments
            query = query_template.format(**params)
            result = self.db_instance.execute_query(query)
            return func(self, result, *args, **kwargs)

        return wrapper

    return decorator


def Transaction(query_template):
    """Decorator that takes a query, executes it using the Database class, and returns the result."""

    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # Get the method signature and parameter names
            signature = inspect.signature(func)
            bound_arguments = signature.bind(*args, **kwargs)
            bound_arguments.apply_defaults()
            # Extract the parameters and map them to the query
            params = bound_arguments.arguments
            query = query_template.format(**params)
            result = self.db_instance.execute_transaction(query)
            return func(self, result, *args, **kwargs)

        return wrapper

    return decorator


def create_database(database_name):
    print(f"Checked or created the database: {database_name}")

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                # Automatically detect the current Windows user
                current_user = os.getlogin()
                domain_user = f"{os.environ['USERDOMAIN']}\\{current_user}"

                # Print to check the domain_user string format
                print(f"Domain and User: {domain_user}")

                # Create an engine connected to the master database
                engine = create_engine(
                    DatabaseSettings.get_master_connection_string(
                        DatabaseSettings
                    ),
                    fast_executemany=True,
                    isolation_level="AUTOCOMMIT",
                )

                with engine.connect() as connection:
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
                    print(f"Database {database_name} created successfully.")

            except Exception as e:
                print(f"Error: {e}")

            return func(*args, **kwargs)

        return wrapper

    return decorator


def analyze_data(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Analyzing data...")
        data = kwargs.get("data", None)
        schema = {}
        for record in data:
            for key, value in record.items():
                # Dynamically determine the column type based on the value
                if isinstance(value, int):
                    schema[key] = Integer
                elif isinstance(value, str):
                    if any(ord(c) > 127 for c in value):
                        # Use Unicode or UnicodeText for multilingual support (including Hindi)
                        schema[key] = Unicode(
                            255
                        )  # Unicode for supporting non-ASCII characters
                    else:
                        schema[key] = String(
                            255
                        )  # Standard string for ASCII characters
                elif isinstance(
                    value, bytes
                ):  # Check for binary data (images)
                    schema[key] = (
                        LargeBinary  # Use LargeBinary for binary data (image)
                    )
                else:
                    schema[key] = String(255)  # Default type for unknown
        # Attach the schema to the function
        setattr(func, "schema", schema)
        # Attach the schema to the wrapper function (not the original function)
        wrapper.schema = schema

        return func(*args, **kwargs)

    return wrapper


def create_table(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print("Creating table...")
        self = args[0]
        table_name = kwargs.get("table_name", None)
        schema = getattr(wrapper, "schema", None)
        columns = [Column('id', Integer, primary_key=True, autoincrement=True)]
        for column_name, column_type in schema.items():
            columns.append(Column(column_name, column_type, nullable=True))

        table = Table(table_name, self.metadata, *columns)
        table.create(
            self.engine, checkfirst=True
        )  # checkfirst ensures it won't create if already exists
        setattr(func, "table", table)
        wrapper.table = table
        kwargs["table"] = table
        return func(*args, **kwargs)

    return wrapper

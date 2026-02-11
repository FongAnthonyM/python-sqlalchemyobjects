#!/usr/bin/env python
"""updatetable_example.py
An example of how to create and use a BaseUpdateTableSchema and UpdateTableManifestation.

This example demonstrates:
1. Defining a table schema using BaseUpdateTableSchema
2. Creating an UpdateTableManifestation interface for the schema
3. Inserting items with update IDs
4. Querying items based on update IDs
5. Using both synchronous and asynchronous operations
"""

# Header #
__package_name__ = "sqlalchemyobjects"

__author__ = "Anthony Fong"
__credits__ = ["Anthony Fong"]
__copyright__ = "Copyright 2026, Anthony Fong"
__license__ = "MIT"

__version__ = "0.1.0"


# Imports #
# Standard Libraries #
import asyncio
from pathlib import Path

# Third-Party Packages #
import anyio
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped

# Source Packages #
from sqlalchemyobjects import Database
from sqlalchemyobjects.tables.base import BaseUpdateTableSchema, UpdateTableManifestation


# Definitions #
# Table #
# To define an update table, inherit from BaseUpdateTableSchema and define the table name and columns
class LogTableSchema(BaseUpdateTableSchema):
    """A log table schema that tracks updates."""

    # Class Attributes #
    __tablename__ = "log"
    message: Mapped[str]


# To define an UpdateTableManifestation interface, inherit from UpdateTableManifestation
class LogTableManifestation(UpdateTableManifestation):
    """A TableManifestation interface for the LogTableSchema."""

    # Attributes #
    table_schema: type[LogTableSchema]


# Database Schema #
# A database is built from a schema, which is defined from inheriting SQLAlchemy's DeclarativeBase.
class DatabaseSchema(AsyncAttrs, DeclarativeBase):
    """The root of the schema for the database."""


class DatabaseLogTableSchema(LogTableSchema, DatabaseSchema):
    """A log table schema which is a table within the database schema."""


# Example Sections #
def basic_usage_example() -> None:
    """Demonstrates basic usage of BaseUpdateTableSchema and UpdateTableManifestation."""
    print(f"\nBasic Usage\n{'-' * 72}")

    # 1. Setup Database
    db_path = Path("updatetable_example.db")
    db_path.unlink(missing_ok=True)

    database = Database(path=db_path, schema=DatabaseSchema)
    database.create_database()

    # 2. Manifest Table
    log_table = LogTableManifestation(table_schema=DatabaseLogTableSchema, database=database)

    # 3. Insert Items with incrementing update IDs
    print("Inserting logs...")
    log_table.insert({"message": "Event 1", "update_id": 1})
    log_table.insert({"message": "Event 2", "update_id": 2})
    log_table.insert({"message": "Event 3", "update_id": 3})

    # 4. Query last update ID
    last_id = log_table.get_last_update_id()
    print(f"Last update ID: {last_id}")

    # 5. Query items from a specific update ID
    print("\nQuerying logs from update ID 2 (inclusive):")
    results = log_table.get_from_update(2, as_python=True)
    assert isinstance(results, list)
    for log in results:
        print(f"Log: {log['message']} (Update ID: {log['update_id']})")

    database.close()
    db_path.unlink(missing_ok=True)


def advanced_usage_example() -> None:
    """Demonstrates more features like exclusive querying."""
    print(f"\nAdvanced Usage\n{'-' * 72}")

    db_path = Path("updatetable_example_advanced.db")
    db_path.unlink(missing_ok=True)

    database = Database(path=db_path, schema=DatabaseSchema)
    database.create_database()

    log_table = LogTableManifestation(table_schema=DatabaseLogTableSchema, database=database)

    print("Inserting logs...")
    log_table.insert({"message": "Event A", "update_id": 10})
    log_table.insert({"message": "Event B", "update_id": 20})

    # Exclusive query (inclusive=False)
    print("\nQuerying logs after update ID 10 (exclusive):")
    results = log_table.get_from_update(10, inclusive=False, as_python=True)
    assert isinstance(results, list)
    for log in results:
        print(f"Log: {log['message']} (Update ID: {log['update_id']})")

    database.close()
    db_path.unlink(missing_ok=True)


async def async_usage_example() -> None:
    """Demonstrates asynchronous usage of BaseUpdateTableSchema and UpdateTableManifestation."""
    print(f"\nAsync Usage\n{'-' * 72}")

    db_path = anyio.Path("updatetable_example_async.db")
    await db_path.unlink(missing_ok=True)

    # Setup database with async engine
    database = Database(path=db_path.as_posix(), schema=DatabaseSchema, async_engine=True)
    await database.create_database_async()

    log_table = LogTableManifestation(table_schema=DatabaseLogTableSchema, database=database)

    print("Inserting logs asynchronously...")
    await log_table.insert_async({"message": "Async Event 1", "update_id": 100})
    await log_table.insert_async({"message": "Async Event 2", "update_id": 101})

    last_id = await log_table.get_last_update_id_async()
    print(f"Last update ID (async): {last_id}")

    print("\nQuerying logs from update ID 100 asynchronously:")
    results = await log_table.get_from_update_async(100, as_python=True)
    assert isinstance(results, list)
    for log in results:
        print(f"Log: {log['message']} (Update ID: {log['update_id']})")

    await database.close_async()
    await db_path.unlink(missing_ok=True)


def edge_cases_example() -> None:
    """Highlights noteworthy edge cases succinctly."""
    print(f"\nEdge Cases\n{'-' * 72}")

    db_path = Path("updatetable_example_edge.db")
    db_path.unlink(missing_ok=True)

    database = Database(path=db_path, schema=DatabaseSchema)
    database.create_database()

    log_table = LogTableManifestation(table_schema=DatabaseLogTableSchema, database=database)

    # Querying from an empty table
    print("Querying last update ID from an empty table...")
    last_id = log_table.get_last_update_id()
    print(f"Last update ID (should be None): {last_id}")

    # Querying update ID higher than any in table
    print("\nQuerying from update ID 1000 in an empty table...")
    results = log_table.get_from_update(1000, as_python=True)
    print(f"Results: {results}")

    database.close()
    db_path.unlink(missing_ok=True)


# Main #
if __name__ == "__main__":  # pragma: no cover - examples are user-run
    basic_usage_example()
    advanced_usage_example()
    asyncio.run(async_usage_example())
    edge_cases_example()

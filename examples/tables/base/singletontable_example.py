#!/usr/bin/env python
"""singletontable_example.py
An example of how to create and use a BaseSingletonTableSchema and SingletonTableManifestation.

This example demonstrates:
1. Defining a table schema using BaseSingletonTableSchema
2. Creating a SingletonTableManifestation interface for the schema
3. Creating, getting, and setting the single item in the table
4. Using both synchronous and asynchronous operations
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
from sqlalchemyobjects.tables.base import BaseSingletonTableSchema, SingletonTableManifestation


# Definitions #
# Table #
# To define a singleton table, inherit from BaseSingletonTableSchema and define the table name and columns
class ConfigurationTableSchema(BaseSingletonTableSchema):
    """A configuration table schema that only has one row."""

    # Class Attributes #
    __tablename__ = "configuration"
    app_name: Mapped[str]
    debug_mode: Mapped[bool]


# To define a SingletonTableManifestation interface, inherit from SingletonTableManifestation
class ConfigurationTableManifestation(SingletonTableManifestation):
    """A TableManifestation interface for the ConfigurationTableSchema."""

    # Attributes #
    table_schema: type[ConfigurationTableSchema]


# Database Schema #
# A database is built from a schema, which is defined from inheriting SQLAlchemy's DeclarativeBase.
class DatabaseSchema(AsyncAttrs, DeclarativeBase):
    """The root of the schema for the database."""


class DatabaseConfigurationTableSchema(ConfigurationTableSchema, DatabaseSchema):
    """A configuration table schema which is a table within the database schema."""


# Example Sections #
def basic_usage_example() -> None:
    """Demonstrates basic usage of BaseSingletonTableSchema and SingletonTableManifestation."""
    print(f"\nBasic Usage\n{'-' * 72}")

    # 1. Setup Database
    db_path = Path("singletontable_example.db")
    db_path.unlink(missing_ok=True)

    database = Database(path=db_path, schema=DatabaseSchema)
    database.create_database()

    # 2. Manifest Table
    config_table = ConfigurationTableManifestation(table_schema=DatabaseConfigurationTableSchema, database=database)

    # 3. Create the single item
    print("Creating configuration...")
    config_table.create_item({"app_name": "MyApp", "debug_mode": True})

    # 4. Get the item
    print("Getting configuration...")
    config = config_table.get_item()
    print(f"Config: {config}")

    # 5. Set/Update the item
    print("\nUpdating configuration...")
    config_table.set_item({"debug_mode": False})

    updated_config = config_table.get_item()
    print(f"Updated Config: {updated_config}")

    database.close()
    db_path.unlink(missing_ok=True)


async def async_usage_example() -> None:
    """Demonstrates asynchronous usage of BaseSingletonTableSchema and SingletonTableManifestation."""
    print(f"\nAsync Usage\n{'-' * 72}")

    db_path = anyio.Path("singletontable_example_async.db")
    await db_path.unlink(missing_ok=True)

    # Setup database with async engine
    database = Database(path=db_path.as_posix(), schema=DatabaseSchema, async_engine=True)
    await database.create_database_async()

    config_table = ConfigurationTableManifestation(table_schema=DatabaseConfigurationTableSchema, database=database)

    print("Creating configuration asynchronously...")
    await config_table.create_item_async({"app_name": "AsyncApp", "debug_mode": False})

    print("Getting configuration asynchronously...")
    config = await config_table.get_item_async()
    print(f"Config: {config}")

    print("\nUpdating configuration asynchronously...")
    await config_table.set_item_async({"debug_mode": True})

    updated_config = await config_table.get_item_async()
    print(f"Updated Config: {updated_config}")

    await database.close_async()
    await db_path.unlink(missing_ok=True)


def edge_cases_example() -> None:
    """Highlights noteworthy edge cases succinctly."""
    print(f"\nEdge Cases\n{'-' * 72}")

    db_path = Path("singletontable_example_edge.db")
    db_path.unlink(missing_ok=True)

    database = Database(path=db_path, schema=DatabaseSchema)
    database.create_database()

    config_table = ConfigurationTableManifestation(table_schema=DatabaseConfigurationTableSchema, database=database)

    # Getting item before it's created
    print("Getting item from an empty singleton table...")
    config = config_table.get_item()
    print(f"Result (should be None): {config}")

    # Setting item before it's created (should create it if it doesn't exist)
    print("\nSetting item in an empty singleton table...")
    config_table.set_item({"app_name": "NewApp", "debug_mode": True})
    config = config_table.get_item()
    print(f"Result: {config}")

    database.close()
    db_path.unlink(missing_ok=True)


# Main #
if __name__ == "__main__":  # pragma: no cover - examples are user-run
    basic_usage_example()
    asyncio.run(async_usage_example())
    edge_cases_example()

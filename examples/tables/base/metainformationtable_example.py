#!/usr/bin/env python
"""metainformationtable_example.py
An example of how to create and use a BaseMetaInformationTableSchema and MetaInformationTableManifestation.

This example demonstrates:
1. Defining a table schema using BaseMetaInformationTableSchema
2. Creating a MetaInformationTableManifestation interface for the schema
3. Handling meta-information with caching
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
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Source Packages #
from sqlalchemyobjects import Database
from sqlalchemyobjects.tables.base import BaseMetaInformationTableSchema, MetaInformationTableManifestation


# Definitions #
# Table #
# To define a meta-information table, inherit from BaseMetaInformationTableSchema
class MetaInfoTableSchema(BaseMetaInformationTableSchema):
    """A meta-information table schema."""

    # Class Attributes #
    __tablename__ = "meta"
    version: Mapped[str] = mapped_column(default="0.0.0")
    description: Mapped[str] = mapped_column(default="")


# To define a MetaInformationTableManifestation interface, inherit from MetaInformationTableManifestation
class MetaInfoTableManifestation(MetaInformationTableManifestation):
    """A TableManifestation interface for the MetaInfoTableSchema."""

    # Attributes #
    table_schema: type[MetaInfoTableSchema]


# Database Schema #
# A database is built from a schema, which is defined from inheriting SQLAlchemy's DeclarativeBase.
class DatabaseSchema(AsyncAttrs, DeclarativeBase):
    """The root of the schema for the database."""


class DatabaseMetaInfoTableSchema(MetaInfoTableSchema, DatabaseSchema):
    """A meta-information table schema which is a table within the database schema."""


# Example Sections #
def basic_usage_example() -> None:
    """Demonstrates basic usage of BaseMetaInformationTableSchema and MetaInformationTableManifestation."""
    print(f"\nBasic Usage\n{'-' * 72}")

    # 1. Setup Database
    db_path = Path("metainformationtable_example.db")
    db_path.unlink(missing_ok=True)

    database = Database(path=db_path, schema=DatabaseSchema)
    database.create_database()

    # 2. Manifest Table
    # We can provide initial info during construction
    meta_table = MetaInfoTableManifestation(
        table_schema=DatabaseMetaInfoTableSchema,
        database=database,
        init_info={"version": "1.0.0", "description": "Initial Version"},
    )
    # The build method can be used to insert the initial meta-information into the database
    meta_table.build()

    # 3. Get meta-information
    # This retrieves it from the database and caches it
    print("Getting meta-information...")
    info = meta_table.get_meta_information()
    print(f"Meta Info: {info}")

    # 4. Access via property (uses cache)
    print(f"Version from property: {meta_table.meta_information['version']}")

    # 5. Set meta-information (clears cache)
    print("\nUpdating meta-information...")
    meta_table.set_meta_information(item={"version": "1.1.0"})

    # Cache is empty now, so accessing property will fetch from DB again
    print(f"Updated Version: {meta_table.meta_information['version']}")

    database.close()
    db_path.unlink(missing_ok=True)


def advanced_usage_example() -> None:
    """Demonstrates caching features of MetaInformationTableManifestation."""
    print(f"\nAdvanced Usage\n{'-' * 72}")

    db_path = Path("metainformationtable_example_advanced.db")
    db_path.unlink(missing_ok=True)

    database = Database(path=db_path, schema=DatabaseSchema)
    database.create_database()

    meta_table = MetaInfoTableManifestation(table_schema=DatabaseMetaInfoTableSchema, database=database)
    meta_table.create_meta_information(item={"version": "2.0.0", "description": "Advanced Example"})

    # 1. Manually update cache
    print("Updating local cache...")
    meta_table.meta_information["description"] = "Description updated in cache"
    print(f"Cached Info: {meta_table.meta_information}")

    # 2. Save cached info to database
    print("Saving cached info to database...")
    meta_table.save_cached_meta_information()

    # 3. Verify by reloading from database
    # Clear cache by setting _meta_information to empty dict
    meta_table._meta_information = {}
    new_info = meta_table.get_meta_information()
    print(f"Reloaded Info: {new_info}")

    database.close()
    db_path.unlink(missing_ok=True)


async def async_usage_example() -> None:
    """Demonstrates asynchronous usage of BaseMetaInformationTableSchema and MetaInformationTableManifestation."""
    print(f"\nAsync Usage\n{'-' * 72}")

    db_path = anyio.Path("metainformationtable_example_async.db")
    await db_path.unlink(missing_ok=True)

    # Setup database with async engine
    database = Database(path=db_path.as_posix(), schema=DatabaseSchema, async_engine=True)
    await database.create_database_async()

    meta_table = MetaInfoTableManifestation(table_schema=DatabaseMetaInfoTableSchema, database=database)

    print("Creating meta-information asynchronously...")
    await meta_table.create_meta_information_async(item={"version": "3.0.0-async", "description": "Async Demo"})

    print("Getting meta-information asynchronously...")
    info = await meta_table.get_meta_information_async()
    print(f"Meta Info: {info}")

    print("\nUpdating and saving asynchronously...")
    meta_table.meta_information["version"] = "3.1.0-async"
    await meta_table.save_cached_meta_information_async()

    updated_info = await meta_table.get_meta_information_async()
    print(f"Updated Meta Info: {updated_info}")

    await database.close_async()
    await db_path.unlink(missing_ok=True)


def edge_cases_example() -> None:
    """Highlights noteworthy edge cases succinctly."""
    print(f"\nEdge Cases\n{'-' * 72}")

    db_path = Path("metainformationtable_example_edge.db")
    db_path.unlink(missing_ok=True)

    database = Database(path=db_path, schema=DatabaseSchema)
    database.create_database()

    meta_table = MetaInfoTableManifestation(table_schema=DatabaseMetaInfoTableSchema, database=database)

    # Getting from empty table
    print("Getting meta-information from an empty table...")
    info = meta_table.get_meta_information()
    print(f"Result (should be empty dict): {info}")

    database.close()
    db_path.unlink(missing_ok=True)


# Main #
if __name__ == "__main__":  # pragma: no cover - examples are user-run
    basic_usage_example()
    advanced_usage_example()
    asyncio.run(async_usage_example())
    edge_cases_example()

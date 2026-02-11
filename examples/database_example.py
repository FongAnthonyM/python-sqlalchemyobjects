#!/usr/bin/env python
"""database_example.py
An example of how to use the Database class to manage SQLAlchemy connections and sessions. While this example explores
using the Database class directly, it is recommended to create a custom database class that inherits from the
Database class. The inheritance approach is reviewed in the comprehensive example.

This example demonstrates:
1. Initializing a Database object with a SQLite path
2. Opening and closing the database connection
3. Using the database as a context manager
4. Creating synchronous and asynchronous sessions
5. Handling database creation
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
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Source Packages #
from sqlalchemyobjects import Database


# Definitions #
# Schema Definition #
class ExampleDatabaseSchema(DeclarativeBase):
    """The schema class for the example database."""


class UserTableSchema(ExampleDatabaseSchema):
    """A simple user table."""
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column()


# Example Sections #
def basic_usage_example(db_path: Path) -> None:
    """Demonstrates basic initialization and session creation."""
    print(f"\nBasic Usage\n{'-' * 72}")

    # 1. Initialize Database
    # schema can be assigned in the class definition or passed in as an argument
    # Database by default does not have a schema, so we must pass a schema argument otherwise the database will be empty
    # We set create=True to ensure the database file and tables are created.
    print(f"Initializing database at: {db_path}")
    db = Database(path=db_path, schema=ExampleDatabaseSchema, create=True)

    # 2. Open the database
    print("Opening database...")
    db.open()
    print(f"Is database open? {db.is_open}")

    # 3. Create an SQLAlchemy session and use it
    print("Creating a synchronous session...")
    with db.create_session() as session:
        # Add a user using the default SQLAlchemy methodology
        new_user = UserTableSchema(name="Alice")
        session.add(new_user)
        session.commit()
        print("Added user 'Alice' to the database.")

        # Query the user
        user = session.query(UserTableSchema).filter_by(name="Alice").first()
        if user:
            print(f"Queried user: {user.name} (ID: {user.id})")
            assert user.name == "Alice"

    # 4. Close the database
    print("Closing database...")
    db.close()
    print(f"Is database open? {db.is_open}")


def context_manager_example(db_path: Path) -> None:
    """Demonstrates using the Database object as a context manager."""
    print(f"\nContext Manager Usage\n{'-' * 72}")

    print("Using Database as a context manager...")
    with Database(path=db_path, schema=ExampleDatabaseSchema) as db:
        print(f"Is database open? {db.is_open}")

        with db.create_session() as session:
            new_user = UserTableSchema(name="Bob")
            session.add(new_user)
            session.commit()
            print("Added user 'Bob' to the database.")

    print(f"Is database open after context? {db.is_open}")


async def async_usage_example(db_path: anyio.Path) -> None:
    """Demonstrates asynchronous database operations."""
    print(f"\nAsynchronous Usage\n{'-' * 72}")

    # Note: Database class handles path conversion and aiosqlite if async_engine is True for sqlite.
    # We can use anyio.Path to handle paths asynchronously.
    await db_path.unlink(missing_ok=True)
    db = Database(path=db_path.as_posix(), schema=ExampleDatabaseSchema, async_engine=True)

    print("Using Database as an async context manager...")
    async with db as adb:
        print(f"Is database open? {adb.is_open}")
        print(f"Is database async? {adb.is_async}")

        print("Creating an asynchronous session...")
        async with adb.create_async_session() as _:
            # Note: Async operations require await
            print("Async session created successfully.")

    print(f"Is database open after async context? {db.is_open}")


# Main #
if __name__ == "__main__":  # pragma: no cover - examples are user-run
    # Setup temporary database path
    temp_db = Path("example_database.db")

    try:
        basic_usage_example(temp_db)
        context_manager_example(temp_db)
        asyncio.run(async_usage_example(anyio.Path(temp_db)))
    finally:
        # Cleanup
        if temp_db.exists():
            try:
                temp_db.unlink()
                print(f"\nCleaned up {temp_db}")
            except OSError as e:
                print(f"\nCould not clean up {temp_db}: {e}")

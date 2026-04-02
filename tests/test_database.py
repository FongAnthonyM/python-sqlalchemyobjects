"""test_database.py
Tests for the database module.
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
from unittest.mock import patch

# Third-Party Packages #
import pytest
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Source Packages #
from sqlalchemyobjects import BaseTableSchema, Database, TableManifestation
from sqlalchemyobjects.testsuite import DatabaseTestSuite


# Definitions #
# Classes #
class ConcreteDatabaseSchema(DeclarativeBase):
    """A concrete database schema."""


class ConcreteTableSchema(BaseTableSchema, ConcreteDatabaseSchema):
    """A concrete Table Schema for testing."""
    __tablename__ = "concrete_table"
    name: Mapped[str | None] = mapped_column(String, nullable=True)


class ConcreteTableManifestation(TableManifestation):
    """A concrete Table Manifestation for testing."""
    table_schema: type[ConcreteTableSchema] = ConcreteTableSchema


class DatabaseSubclass(Database):
    """A subclass of Database for testing."""

    # Attributes #
    schema: type[ConcreteDatabaseSchema] | None = ConcreteDatabaseSchema
    table_map = Database.table_map | {"testing_table": (ConcreteTableManifestation, ConcreteTableSchema, {})}


class TestDatabase(DatabaseTestSuite):
    """Tests the Database class."""

    # Attributes #
    UnitTestClass: type[DatabaseSubclass] = DatabaseSubclass
    table_schema: type[ConcreteTableSchema] = ConcreteTableSchema  # type: ignore[assignment]

    # Instance Methods #

    # Tests #
    def test_construct_with_schema(self) -> None:
        """Tests constructing with schema."""
        db = self.UnitTestClass(schema=self.UnitTestClass.schema)
        assert db.schema == self.UnitTestClass.schema

    def test_construct_default_path(self) -> None:
        """Tests constructing with default path (None)."""
        db = self.UnitTestClass(init=True)
        assert db.path is None

    def test_create_engine_no_path(self) -> None:
        """Tests create_engine raises ValueError when path is not set."""
        db = self.UnitTestClass(path=None)
        with pytest.raises(ValueError, match="Path is not set"):
            db.create_engine()

    def test_create_database_no_schema(self) -> None:
        """Tests create_database with no schema."""
        db = self.UnitTestClass(schema=None)
        # Ensure schema is None (override class attribute if necessary)
        db.schema = None
        db.create_database(path="test_no_schema.db")
        db.close()

    @pytest.mark.asyncio
    async def test_create_database_async_no_schema(self) -> None:
        """Tests create_database_async with no schema."""
        db = self.UnitTestClass(schema=None)
        # Ensure schema is None
        db.schema = None
        await db.create_database_async(path="test_no_schema_async.db")
        await db.close_async()

    @pytest.mark.asyncio
    async def test_close_async_no_engines(self) -> None:
        """Tests close_async when engines are None."""
        db = self.UnitTestClass()
        # Ensure engines are None
        db._engine = None
        db._async_engine = None
        await db.close_async()
        assert db._engine is None
        assert db._async_engine is None


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])

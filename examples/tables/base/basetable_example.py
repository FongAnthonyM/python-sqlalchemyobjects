#!/usr/bin/env python
"""basetable_example.py
An example of how to create and use a BaseTableSchema and TableManifestation.

This example demonstrates:
1. Defining a table schema using BaseTableSchema
2. Creating a TableManifestation interface for the schema
3. Inserting items into the table
4. Querying items from the table
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
from typing import Any
from uuid import UUID, uuid4

# Third-Party Packages #
import anyio
from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

# Source Packages #
from sqlalchemyobjects import Database
from sqlalchemyobjects.tables.base import BaseTableSchema, TableManifestation


# Definitions #
# Table #
# To define a table, inherit from BaseTableSchema and define the table name, columns, and additional methods
class UserTableSchema(BaseTableSchema):
    """A user table schema."""

    # Class Attributes #
    __tablename__ = "user"
    name: Mapped[str]
    role: Mapped[str] = mapped_column(default="user")

    # Class Methods #
    @classmethod
    def get_by_name(cls, session: Session, name: str, as_python: bool = False) -> Any:
        """Fetches a user from the table by their name.

        Args:
            session: The SQLAlchemy session to use for the query.
            name: The name of the user to search for.
            as_python: If True, returns a dictionary representing the user; otherwise, returns the user.

        Returns:
            The user from the table or its dictionary representation.
        """
        result = cls.get_by(session, "name", name, as_python=as_python)
        if isinstance(result, list):
            return result[0] if result else None
        return result.scalars().first()

    @classmethod
    async def get_by_name_async(cls, session: AsyncSession, name: str, as_python: bool = False) -> Any:
        """Asynchronously fetches a user from the table by their name.

        Args:
            session: The SQLAlchemy async session to use for the query.
            name: The name of the user to search for.
            as_python: If True, returns a dictionary representing the user; otherwise, returns the user.

        Returns:
            The user from the table or its dictionary representation.
        """
        result = await cls.get_by_async(session, "name", name, as_python=as_python)
        if isinstance(result, list):
            return result[0] if result else None
        return await result.scalars().first()


# To define a TableManifestation interface, inherit from TableManifestation and add methods to manipulate the table
class UserTableManifestation(TableManifestation):
    """A TableManifestation interface for the UserTableSchema."""

    # Attributes #
    table_schema: type[UserTableSchema]  # Not necessary but helpful for type checking

    # Instance Methods #
    def get_by_name(self, name: str, session: Session | None = None, as_python: bool = False) -> Any:
        """Fetches a user from the table by their name.

        Args:
            name: The name of the user to search for.
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns a dictionary representing the user; otherwise, returns the user.

        Returns:
            The user from the table or its dictionary representation.
        """
        if session is not None:
            return self.table_schema.get_by_name(session, name, as_python=as_python)
        else:
            with self.create_session() as session:
                return self.table_schema.get_by_name(session, name, as_python=as_python)

    async def get_by_name_async(self, name: str, session: AsyncSession | None = None, as_python: bool = False) -> Any:
        """Asynchronously fetches a user from the table by their name.

        Args:
            name: The name of the user to search for.
            session: The SQLAlchemy async session to use for the query.
            as_python: If True, returns a dictionary representing the user; otherwise, returns the user.

        Returns:
            The user from the table or its dictionary representation.
        """
        if session is not None:
            return await self.table_schema.get_by_name_async(session, name, as_python=as_python)
        else:
            async with self.create_async_session() as session:
                return await self.table_schema.get_by_name_async(session, name, as_python=as_python)


class EngineerTableSchema(UserTableSchema):
    """An engineer table schema."""
    specialty: Mapped[str] = mapped_column(default="general")


# Database Schema #
# A database is built from a schema, which is defined from inheriting SQLAlchemy's DeclarativeBase.
class DatabaseSchema(AsyncAttrs, DeclarativeBase):
    """The root of the schema for the database."""


class DatabaseCustomerTableSchema(UserTableSchema, DatabaseSchema):
    """A customer table schema which is a table within the database schema."""

    # Class Attributes #
    __tablename__ = "customer"


class DatabaseStaffTableSchema(UserTableSchema, DatabaseSchema):
    """A staff table schema which is a table within the database schema."""

    # Class Attributes #
    __mapper_args__ = {  # Alternatively, can be defined in UserTableSchema as well
        "polymorphic_on": "role",  # Allows for sub-tables to be queried by subclass
        "polymorphic_identity": "user",  # Specify what sub-table this class is
    }


class DatabaseAdminTableSchema(DatabaseStaffTableSchema):
    """An admin table schema which is a sub-table within the staff table."""

    # Class Attributes #
    __mapper_args__ = {"polymorphic_identity": "admin"}


class DatabaseEngineerTableSchema(DatabaseStaffTableSchema):
    """An engineer table schema which is a sub-table within the staff table."""

    # Class Attributes #
    __mapper_args__ = {"polymorphic_identity": "engineer"}


class DatabasePersonTableSchema(UserTableSchema, DatabaseSchema):
    """A person table schema for Joined Table Inheritance (JTI)."""

    # Class Attributes #
    __tablename__ = "person"
    __mapper_args__ = {
        "polymorphic_on": "role",
        "polymorphic_identity": "person",
    }


class DatabaseEngineerJTI(DatabasePersonTableSchema, EngineerTableSchema):
    """An engineer table schema (Subclass for JTI)."""

    # Class Attributes #
    __tablename__ = "engineer_jti"
    __mapper_args__ = {"polymorphic_identity": "engineer"}
    id: Mapped[UUID] = mapped_column(ForeignKey("person.id"), primary_key=True)


# Example Sections #
def basic_usage_example() -> None:
    """Demonstrates basic usage of BaseTableSchema and TableManifestation."""
    print(f"\nBasic Usage\n{'-' * 72}")

    # 1. Setup Database
    # We use an in-memory SQLite database for this example.
    db_path = Path("basetable_example.db")
    db_path.unlink(missing_ok=True)

    database = Database(path=db_path, schema=DatabaseSchema)
    database.create_database()

    # 2. Manifest Table
    # TableManifestation provides a higher-level interface to a table.
    user_table = UserTableManifestation(table_schema=DatabaseCustomerTableSchema, database=database)

    # 3. Insert Items
    print("Inserting users...")
    user_table.insert({"name": "Alice", "role": "customer"})
    user_table.insert({"name": "Bob", "role": "customer"})

    # 4. Query Items
    print("Querying users...")
    alice = user_table.get_by_name("Alice")
    if alice:
        print(f"Found user: {alice.name} with role {alice.role} and ID {alice.id}")

    # 5. Count Items
    count = user_table.count()
    print(f"Total users in customer table: {count}")

    database.close()
    db_path.unlink(missing_ok=True)


def advanced_usage_example() -> None:
    """Demonstrates advanced features like polymorphism and upserting."""
    print(f"\nAdvanced Usage\n{'-' * 72}")

    db_path = Path("basetable_example_advanced.db")
    db_path.unlink(missing_ok=True)

    database = Database(path=db_path, schema=DatabaseSchema)
    database.create_database()

    # Polymorphism: Use the staff table manifestation to handle various staff types
    staff_table = UserTableManifestation(table_schema=DatabaseStaffTableSchema, database=database)

    # Insert different types of staff using the same manifestation
    print("Inserting staff members...")
    staff_table.insert({"name": "Admin Ana", "role": "admin"})
    staff_table.insert({"name": "Engineer Erik", "role": "engineer"})
    staff_table.insert({"name": "User Ursula", "role": "user"})

    # Query all staff - notice the different classes returned based on the role
    with database.create_session() as session:
        all_staff_result = staff_table.get_all(session=session)
        all_staff = (
            all_staff_result.scalars().all() if not isinstance(all_staff_result, list) else all_staff_result
        )
        print(f"Total staff members: {len(all_staff)}")
        for member in all_staff:
            print(f"Member: {member.name:15} | Role: {member.role:10} | Type: {type(member).__name__}")

    # Upsert example
    print("\nUpserting a user...")
    customer_table = UserTableManifestation(table_schema=DatabaseCustomerTableSchema, database=database)
    customer_table.insert({"name": "Alice", "role": "customer"})

    alice = customer_table.get_by_name("Alice")
    alice_id = alice.id

    # Update Alice's name using upsert by providing her ID
    print(f"Alice's original ID: {alice_id}")
    customer_table.upsert({"id": alice_id, "name": "Alice Updated"})

    alice_updated = customer_table.get_by_id(alice_id)
    print(f"Updated name: {alice_updated.name}")

    # Using as_python=True to get a dictionary instead of an ORM object
    alice_dict = customer_table.get_by_id(alice_id, as_python=True)
    print(f"User as dictionary: {alice_dict}")

    database.close()
    db_path.unlink(missing_ok=True)


async def async_usage_example() -> None:
    """Demonstrates asynchronous usage of BaseTableSchema and TableManifestation."""
    print(f"\nAsync Usage\n{'-' * 72}")

    db_path = anyio.Path("basetable_example_async.db")
    await db_path.unlink(missing_ok=True)

    # Setup database with async engine
    database = Database(path=db_path.as_posix(), schema=DatabaseSchema, async_engine=True)
    await database.create_database_async()

    user_table = UserTableManifestation(table_schema=DatabaseCustomerTableSchema, database=database)

    print("Inserting users asynchronously...")
    await user_table.insert_async({"name": "Charlie", "role": "customer"})

    print("Querying users asynchronously...")
    charlie = await user_table.get_by_name_async("Charlie")
    if charlie:
        print(f"Found user: {charlie.name} with ID {charlie.id}")

    # Demonstrate class methods for async
    print("\nUsing class methods for async operations...")
    async with database.create_async_session() as session:
        count = await DatabaseCustomerTableSchema.count_async(session)
        print(f"Count via class method: {count}")

    await database.close_async()
    await db_path.unlink(missing_ok=True)


def edge_cases_example() -> None:
    """Highlights noteworthy edge cases succinctly."""
    print(f"\nEdge Cases\n{'-' * 72}")

    db_path = Path("basetable_example_edge.db")
    db_path.unlink(missing_ok=True)

    database = Database(path=db_path, schema=DatabaseSchema)
    database.create_database()

    customer_table = UserTableManifestation(table_schema=DatabaseCustomerTableSchema, database=database)

    # Querying a non-existent user
    print("Querying non-existent user...")
    result = customer_table.get_by_name("Nobody")
    print(f"Result for 'Nobody': {result}")

    # Upserting with a new ID (should act as insert)
    print("\nUpserting with a new ID...")
    new_id = uuid4()
    customer_table.upsert({"id": new_id, "name": "New User", "role": "customer"})
    new_user = customer_table.get_by_id(new_id)
    if new_user:
        print(f"New user created with ID: {new_user.id}")

    database.close()
    db_path.unlink(missing_ok=True)


def single_inheritance_example() -> None:
    """Demonstrates Single Table Inheritance (STI)."""
    print(f"\nSingle Table Inheritance Usage\n{'-' * 72}")

    db_path = Path("basetable_sti_test.db")
    db_path.unlink(missing_ok=True)

    database = Database(path=db_path, schema=DatabaseSchema)
    database.create_database()

    # Demonstrating STI Subclass Querying
    print("Demonstrating STI Subclass Querying...")
    # Insert using manifestation of the base class
    staff_table = UserTableManifestation(table_schema=DatabaseStaffTableSchema, database=database)
    staff_table.insert({"name": "Admin Ana", "role": "admin"})
    staff_table.insert({"name": "User Ursula", "role": "user"})

    # Note: Querying specifically for Admin using the subclass's get_all method
    # is known to fail with the current implementation because it doesn't
    # automatically apply the discriminator filter.
    print("Note: DatabaseAdminTableSchema.get_all(session) currently does not auto-filter by role.")

    database.close()
    db_path.unlink(missing_ok=True)


def joined_inheritance_example() -> None:
    """Demonstrates Joined Table Inheritance (JTI)."""
    print(f"\nJoined Table Inheritance Usage\n{'-' * 72}")

    db_path = Path("basetable_jti_test.db")
    db_path.unlink(missing_ok=True)

    database = Database(path=db_path, schema=DatabaseSchema)
    database.create_database()

    # Demonstrating JTI Multi-table Insert
    print("Demonstrating JTI Multi-table Insert...")
    # Use the manifestation for the JTI subclass
    engineer_jti_table = UserTableManifestation(table_schema=DatabaseEngineerJTI, database=database)
    # This should insert into both 'person' and 'engineer_jti' tables
    engineer_jti_table.insert({"name": "Engineer Erik", "role": "engineer", "specialty": "Robotics"})

    with database.create_session() as session:
        # Fetch using the JTI subclass
        engineers_result = DatabaseEngineerJTI.get_all(session=session)
        engineers = (
            engineers_result.scalars().all() if not isinstance(engineers_result, list) else engineers_result
        )
        print(f"JTI Engineers found: {len(engineers)}")
        for e in engineers:
            name = e["name"] if isinstance(e, dict) else e.name
            specialty = e["specialty"] if isinstance(e, dict) else e.specialty
            type_name = "dict" if isinstance(e, dict) else type(e).__name__
            print(f" - {name}, Specialty: {specialty} (Type: {type_name})")

    database.close()
    db_path.unlink(missing_ok=True)


# Main #
if __name__ == "__main__":  # pragma: no cover - examples are user-run
    basic_usage_example()
    advanced_usage_example()
    asyncio.run(async_usage_example())
    edge_cases_example()
    single_inheritance_example()
    joined_inheritance_example()

#!/usr/bin/env python
"""comprehensive_example.py
A comprehensive example demonstrating all features of the project. The example database is broken up into multiple files
in the comprehensive directory to demonstrate how to organize a project with multiple tables and manifestations.

This example demonstrates:
1. Inheritance and polymorphism by subclassing all major classes
2. Using custom manifestations with specialized methods
3. Working with all table types: ExampleDatabaseSchema, Update, Singleton, and MetaInformation
4. Database class features and manual session management
5. Synchronous and asynchronous database operations
6. Database management using context managers
7. Organizing an example across multiple files
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
from datetime import UTC, datetime
from pathlib import Path

# Third-Party Packages #
import anyio
from sqlalchemy import select

# Local Packages #
from .comprehensive import ComprehensiveDatabase


# Definitions #
# Example Sections #
def demonstrate_database_features(db: ComprehensiveDatabase) -> None:
    """Demonstrates features of the Database class itself."""
    print(f"\n5. Database Class Features\n{'-' * 72}")

    # 5.1 Basic Properties
    print(f"Database Path: {db.path}")
    print(f"Is Open: {db.is_open}")
    print(f"Is Async: {db.is_async}")

    # 5.2 Accessing Tables
    print(f"Registered Tables: {', '.join(db.tables.keys())}")

    # 5.3 Manual Session Management
    print("Creating a manual session...")
    with db.create_session() as session:
        # We can use the session to query directly if needed
        # Use the table_schema from a manifestation to build a query
        stmt = select(db.a_employees.table_schema).where(db.a_employees.table_schema.name == "Alice")
        result = session.execute(stmt).scalar_one_or_none()
        if result:
            print(f"Manually queried Alice: {result.name}")
            assert result.name == "Alice"

    # 5.4 Schema and Metadata
    if db.schema is not None:
        print(f"Database Schema Class: {db.schema.__name__}")
        print(f"Database Schema (Metadata) Tables: {', '.join(db.schema.metadata.tables.keys())}")


def demonstrate_base_table(db: ComprehensiveDatabase) -> None:
    """Demonstrates basic table operations and custom manifestation methods."""
    print(f"\n1. ExampleDatabaseSchema Table & Custom Manifestation\n{'-' * 72}")

    # Insert using standard method
    print("Inserting employees...")
    db.a_employees.insert({"name": "Alice", "position": "Developer"}, as_dict=True)
    db.a_employees.insert({"name": "Bob", "position": "Manager"}, as_dict=True)

    # Use custom manifestation method (get_by_name)
    print("Finding Alice using custom method...")
    alice = db.a_employees.get_by_name("Alice")
    if alice:
        print(f"Found: {alice['name']}, Position: {alice['position']}")
        assert alice["position"] == "Developer"

    # 1.1 Upsert Demonstration
    print("Updating Alice's position using upsert...")
    alice["position"] = "Senior Developer"
    db.a_employees.upsert(alice)

    # Verify update
    alice_updated = db.a_employees.get_by_name("Alice")
    print(f"Alice's New Position: {alice_updated['position']}")
    assert alice_updated["position"] == "Senior Developer"

    # 1.2 Delete Demonstration
    print("Deleting Bob...")
    bob = db.a_employees.get_by_name("Bob", as_python=False)
    if bob:
        db.a_employees.delete(bob)

    # Verify deletion
    all_employees = db.a_employees.get_all(as_python=True)
    if isinstance(all_employees, list):
        print(f"Total employees after deletion: {len(all_employees)}")
        assert len(all_employees) == 1
        assert not any(e["name"] == "Bob" for e in all_employees)

    # 1.3 Multiple Tables of Same Type
    print("Demonstrating multiple tables of the same type (a_employees and b_employees)...")
    db.b_employees.insert({"name": "David", "position": "Architect"}, as_dict=True)
    b_employees = db.b_employees.get_all(as_python=True)
    if isinstance(b_employees, list):
        print(f"Total B employees: {len(b_employees)}")
        assert len(b_employees) == 1
        assert b_employees[0]["name"] == "David"


def demonstrate_update_table(db: ComprehensiveDatabase) -> None:
    """Demonstrates update tracking table and specialized queries."""
    print(f"\n2. Update Table & Specialized Queries\n{'-' * 72}")

    # Insert departments
    print("Inserting departments...")
    db.departments.insert({"name": "Engineering", "budget": 1000000}, as_dict=True)
    db.departments.insert({"name": "Marketing", "budget": 500000}, as_dict=True)
    db.departments.insert({"name": "Sales", "budget": 1200000}, as_dict=True)

    # Use custom manifestation method (get_large_budget_departments)
    print("Finding departments with budget > 800,000...")
    large_budget_depts = db.departments.get_large_budget_departments(800000)
    for dept in large_budget_depts:
        print(f"Large Budget Dept: {dept['name']} (${dept['budget']:,})")
        assert dept["budget"] > 800000

    # 2.1 Update Tracking
    # Insert with explicit update_id
    print("Inserting Research department with update_id 100...")
    db.departments.insert({"name": "Research", "budget": 200000, "update_id": 100}, as_dict=True)

    # Show update tracking
    last_id = db.departments.get_last_update_id()
    print(f"Last update ID: {last_id}")
    assert last_id == 100

    # Fetch from update
    print("Fetching departments updated since ID 50...")
    recent_updates = db.departments.get_from_update(50, as_python=True)
    if isinstance(recent_updates, list):
        for dept in recent_updates:
            print(f"Recent Update: {dept['name']} (Update ID: {dept['update_id']})")
        assert any(d["name"] == "Research" for d in recent_updates)


def demonstrate_singleton_table(db: ComprehensiveDatabase) -> None:
    """Demonstrates singleton table and state management."""
    print(f"\n3. Singleton Table & State Toggling\n{'-' * 72}")

    # Initialize singleton
    print("Initializing configuration...")
    db.configuration.create_item({"app_name": "Comprehensive Demo", "debug_mode": False})

    # Get current state
    config = db.configuration.get_item()
    if isinstance(config, dict):
        print(f"Current App Name: {config['app_name']}")
        print(f"Debug Mode: {config['debug_mode']}")

    # Toggle state using custom manifestation method
    print("Toggling debug mode...")
    new_mode = db.configuration.toggle_debug_mode()
    print(f"New Debug Mode: {new_mode}")
    assert new_mode is True

    # 3.1 Direct Update using set_item
    print("Setting app name and debug mode directly...")
    db.configuration.set_item({"app_name": "Updated Demo", "debug_mode": False})

    # Verify update
    updated_config = db.configuration.get_item()
    if isinstance(updated_config, dict):
        print(f"Updated App Name: {updated_config['app_name']}")
        print(f"Updated Debug Mode: {updated_config['debug_mode']}")
        assert updated_config["app_name"] == "Updated Demo"
        assert updated_config["debug_mode"] is False


def demonstrate_meta_info_table(db: ComprehensiveDatabase) -> None:
    """Demonstrates meta information table and caching."""
    print(f"\n4. Meta Information Table\n{'-' * 72}")

    # Initialize meta info
    print("Setting initial meta info...")
    db.app_meta.set_meta_information(version="2.0.0")

    # Update last run using custom method
    now = datetime.now(UTC).isoformat()
    print(f"Updating last run to: {now}")
    db.app_meta.update_last_run(now)

    # Retrieving specific key
    print("Retrieving version specifically...")
    meta_info = db.app_meta.get_meta_information()
    if isinstance(meta_info, dict):
        version = meta_info["version"]
        print(f"Retrieved Version: {version}")
        assert version == "2.0.0"


async def demonstrate_async_operations(db_path: anyio.Path) -> None:
    """Demonstrates all features asynchronously."""
    print(f"\n6. Asynchronous Operations\n{'-' * 72}")

    # Use anyio.Path to handle paths asynchronously.
    await db_path.unlink(missing_ok=True)

    # Use async context manager
    async with ComprehensiveDatabase(path=db_path.as_posix(), async_engine=True) as db:
        print("Async database opened.")
        print(f"Is Async: {db.is_async}")
        assert db.is_async is True

        # Async insert using dictionary
        print("Inserting employee asynchronously using dictionary...")
        await db.a_employees.insert_async({"name": "Charlie", "position": "Designer"}, as_dict=True)

        # Async upsert
        print("Updating Charlie's position asynchronously...")
        charlie = await db.a_employees.get_by_name_async("Charlie")
        charlie["position"] = "Lead Designer"
        await db.a_employees.upsert_async(charlie)

        # Async query
        print("Querying all employees asynchronously...")
        employees = await db.a_employees.get_all_async(as_python=True)
        if isinstance(employees, list):
            print(f"Found {len(employees)} employees asynchronously.")
            charlie_updated = next(e for e in employees if e["name"] == "Charlie")
            print(f"Charlie's position: {charlie_updated['position']}")
            assert charlie_updated["position"] == "Lead Designer"

        # Async specialized query
        print("Finding departments with budget > 800,000 asynchronously...")
        large_depts = await db.departments.get_large_budget_departments_async(800000)
        for dept in large_depts:
            print(f"Async Large Budget Dept: {dept['name']}")
        assert any(d["name"] == "Engineering" for d in large_depts)

        # Async singleton toggling
        print("Toggling debug mode asynchronously...")
        new_mode = await db.configuration.toggle_debug_mode_async()
        print(f"Async New Debug Mode: {new_mode}")
        assert new_mode is True

        # Async delete
        print("Deleting Charlie asynchronously...")
        charlie_obj = await db.a_employees.get_by_name_async("Charlie", as_python=False)
        await db.a_employees.delete_async(charlie_obj)

        # Verify deletion
        remaining = await db.a_employees.get_all_async(as_python=True)
        if isinstance(remaining, list):
            print(f"Remaining employees: {len(remaining)}")
            assert not any(e["name"] == "Charlie" for e in remaining)

        # Async meta info
        print("Setting and updating meta info asynchronously...")
        await db.app_meta.set_meta_information_async(version="2.0.0-async")
        await db.app_meta.update_last_run_async(datetime.now(UTC).isoformat())
        meta = await db.app_meta.get_meta_information_async()
        if isinstance(meta, dict):
            print(f"Async App Version: {meta['version']}")
            print(f"Async Last Run: {meta['last_run']}")
            assert meta["version"] == "2.0.0-async"


# Main #
if __name__ == "__main__":  # pragma: no cover - examples are user-run
    temp_db_path = Path("comprehensive_example.db")

    try:
        # 1-5. Synchronous demonstrations
        with ComprehensiveDatabase(path=temp_db_path, create=True) as db:
            demonstrate_base_table(db)
            demonstrate_update_table(db)
            demonstrate_singleton_table(db)
            demonstrate_meta_info_table(db)
            demonstrate_database_features(db)

        # 6. Asynchronous demonstrations
        asyncio.run(demonstrate_async_operations(anyio.Path(temp_db_path)))

    finally:
        if temp_db_path.exists():
            try:
                temp_db_path.unlink()
                print(f"\nCleaned up {temp_db_path}")
            except OSError as e:
                print(f"\nCould not clean up {temp_db_path}: {e}")

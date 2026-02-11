"""basetabletestsuite.py
Test suites for the base table manifestations and schemas.
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
import copy
import pickle
from collections.abc import Generator
from typing import Any
from uuid import UUID

# Third-Party Packages #
import pytest
from baseobjects.testsuite import BaseClassTestSuite, BaseReducibleTestSuite
from sqlalchemy import Engine, create_engine, func, select
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session

# Local Packages #
from ..database import Database
from ..tables.base.basetable import BaseTableSchema, TableManifestation


# Definitions #
# Classes #
class TableSchemaMixin(BaseTableSchema, DeclarativeBase):
    """A Mixin class for testing BaseTableSchema functionality."""


class BaseTableSchemaTestSuite(BaseClassTestSuite):
    """A Testsuite for the BaseTableSchema class.

    This class tests the functionality of the BaseTableSchema class.
    """

    # Class Attributes #
    UnitTestClass: type[TableSchemaMixin]

    # Instance Methods #
    # Helper Methods #
    def create_engine(self) -> Engine:
        """Creates the database engine.

        Returns:
            The database engine.
        """
        db_engine = create_engine("sqlite:///:memory:")
        self.UnitTestClass.metadata.create_all(db_engine)
        return db_engine

    async def create_async_engine(self) -> AsyncEngine:
        """Creates the asynchronous database engine.

        Returns:
            The asynchronous database engine.
        """
        db_async_engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with db_async_engine.begin() as conn:
            await conn.run_sync(self.UnitTestClass.metadata.create_all)
        return db_async_engine

    def get_table_length(self, session: Session) -> int:
        """Gets the number of rows in the table.

        Args:
            session: The database session.

        Returns:
            The number of rows.
        """
        result = session.scalar(select(func.count()).select_from(self.UnitTestClass))
        return result if result is not None else 0

    async def get_async_table_length(self, session: AsyncSession) -> int:
        """Gets the number of rows in the table asynchronously.

        Args:
            session: The database session.

        Returns:
            The number of rows.
        """
        result = await session.scalar(select(func.count()).select_from(self.UnitTestClass))
        return result if result is not None else 0

    # Tests #
    # Instantiation #
    def test_instance_creation(self, *args: Any, **kwargs: Any) -> None:
        """Tests that instances of the class can be created.

        Args:
            *args: Positional arguments list to pass to the class constructor.
            **kwargs: Keyword arguments to pass to the class constructor.
        """
        instance = self.UnitTestClass()
        assert isinstance(instance, self.UnitTestClass)

    # ConcreteDatabaseSchema
    def test_get_column_names(self) -> None:
        """Tests the get_column_names method."""
        columns = self.UnitTestClass.get_column_names()
        assert "id" in columns

    @pytest.mark.parametrize(
        ("id_value", "expected"),
        [
            ("00000000-0000-0000-0000-000000000001", UUID(int=1)),
            (1, UUID(int=1)),
            (UUID(int=1), UUID(int=1)),
            (1.5, 1.5),
        ],
    )
    def test_to_sql_types(self, id_value: Any, expected: Any) -> None:
        """Tests the to_sql_types method."""
        data = {"id": id_value}
        sql_data = self.UnitTestClass.to_sql_types(data)
        assert sql_data["id"] == expected

    def test_from_sql_types(self) -> None:
        """Tests the from_sql_types method."""
        # By default from_sql_types doesn't do much in BaseTableSchema unless overridden
        data = {"id": UUID(int=1)}
        python_data = self.UnitTestClass.from_sql_types(data)
        assert python_data["id"] == UUID(int=1)

    @pytest.mark.parametrize("format_dict", [True, False])
    def test_item_from_dict(self, format_dict: bool) -> None:
        """Tests the item_from_dict method."""
        data = {"id": UUID(int=1)}
        item = self.UnitTestClass.item_from_dict(data, _format_dict=format_dict)
        assert isinstance(item, self.UnitTestClass)
        assert item.id == UUID(int=1)

    def test_to_sql_types_no_id(self) -> None:
        """Tests the to_sql_types method with no ID."""
        data = {"name": "test"}
        sql_data = self.UnitTestClass.to_sql_types(data)
        assert "id" not in sql_data
        assert sql_data["name"] == "test"

    # Modification
    @pytest.mark.parametrize(("item", "expected"), [({"id": UUID(int=1)}, 1)])
    @pytest.mark.parametrize("as_dict", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_insert(self, item: dict[str, Any], as_dict: bool, begin: bool, expected: int) -> None:
        """Tests the insert method.

        Args:
            item: The item to insert.
            as_dict: Whether to insert as a dictionary.
            begin: Whether to begin a transaction.
            expected: The expected number of entries.
        """
        item_obj: Any
        if not as_dict:
            item_obj = self.UnitTestClass.item_from_dict(item)
        else:
            item_obj = item

        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                self.UnitTestClass.insert(session=session, item=item_obj, as_dict=as_dict, begin=begin)
                if not begin:
                    session.commit()
                n_entries = self.get_table_length(session=session)
        finally:
            db_engine.dispose()
        assert n_entries == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("item", "expected"), [({"id": UUID(int=1)}, 1)])
    @pytest.mark.parametrize("as_dict", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_insert_async(self, item: dict[str, Any], as_dict: bool, begin: bool, expected: int) -> None:
        """Tests the insert_async method.

        Args:
            item: The item to insert.
            as_dict: Whether to insert as a dictionary.
            begin: Whether to begin a transaction.
            expected: The expected number of entries.
        """
        item_obj: Any
        if not as_dict:
            item_obj = self.UnitTestClass.item_from_dict(item)
        else:
            item_obj = item

        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                await self.UnitTestClass.insert_async(session=session, item=item_obj, as_dict=as_dict, begin=begin)
                if not begin:
                    await session.commit()
                n_entries = await self.get_async_table_length(session=session)
        finally:
            await db_engine.dispose()
        assert n_entries == expected

    @pytest.mark.parametrize(("items", "expected"), [([{"id": UUID(int=1)}, {"id": UUID(int=2)}], 2)])
    @pytest.mark.parametrize("begin", [True, False])
    @pytest.mark.parametrize("as_dict", [True, False])
    def test_insert_all(self, items: list[dict[str, Any]], as_dict: bool, begin: bool, expected: int) -> None:
        """Tests the insert_all method.

        Args:
            items: The items to insert.
            as_dict: Whether to insert as a dictionary.
            begin: Whether to begin a transaction.
            expected: The expected number of entries.
        """
        items_to_insert: list[Any] = items
        if not as_dict:
            items_to_insert = [self.UnitTestClass.item_from_dict(i) for i in items]

        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                self.UnitTestClass.insert_all(session=session, items=items_to_insert, as_dict=as_dict, begin=begin)
                if not begin:
                    session.commit()
                n_entries = self.get_table_length(session=session)
        finally:
            db_engine.dispose()
        assert n_entries == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("items", "expected"), [([{"id": UUID(int=1)}, {"id": UUID(int=2)}], 2)])
    @pytest.mark.parametrize("begin", [True, False])
    @pytest.mark.parametrize("as_dict", [True, False])
    async def test_insert_all_async(
        self,
        items: list[dict[str, Any]],
        as_dict: bool,
        begin: bool,
        expected: int,
    ) -> None:
        """Tests the insert_all_async method.

        Args:
            items: The items to insert.
            as_dict: Whether to insert as a dictionary.
            begin: Whether to begin a transaction.
            expected: The expected number of entries.
        """
        items_to_insert: list[Any] = items
        if not as_dict:
            items_to_insert = [self.UnitTestClass.item_from_dict(i) for i in items]

        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                await self.UnitTestClass.insert_all_async(
                    session=session,
                    items=items_to_insert,
                    as_dict=as_dict,
                    begin=begin,
                )
                if not begin:
                    await session.commit()
                n_entries = await self.get_async_table_length(session=session)
        finally:
            await db_engine.dispose()
        assert n_entries == expected

    @pytest.mark.parametrize(("entry", "expected"), [({"id": UUID(int=1), "name": "new"}, "new")])
    @pytest.mark.parametrize("begin", [True, False])
    @pytest.mark.parametrize("update", [True, False])
    def test_upsert(self, entry: dict[str, Any], begin: bool, update: bool, expected: Any) -> None:
        """Tests the upsert method.

        Args:
            entry: The entry to upsert.
            begin: Whether to begin a transaction.
            update: Whether to update.
            expected: The expected result.
        """
        column = "name" if "name" in self.UnitTestClass.get_column_names() else "id"
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                if update:
                    initial_entry: dict[str, Any] = {"id": UUID(int=1)}
                    if column != "id":
                        initial_entry[column] = "old"
                    self.UnitTestClass.insert(
                        session=session,
                        item=initial_entry,
                        as_dict=True,
                        begin=True,
                    )

                self.UnitTestClass.upsert(session=session, entry=entry, begin=begin)
                if not begin:
                    session.commit()

                item_obj = session.get(self.UnitTestClass, entry["id"])
                assert item_obj is not None
                res_val = getattr(item_obj, column)
        finally:
            db_engine.dispose()
        assert res_val == (expected if column != "id" else entry["id"])

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("entry", "expected"), [({"id": UUID(int=1), "name": "new"}, "new")])
    @pytest.mark.parametrize("begin", [True, False])
    @pytest.mark.parametrize("update", [True, False])
    async def test_upsert_async(
        self,
        entry: dict[str, Any],
        begin: bool,
        update: bool,
        expected: str,
    ) -> None:
        """Tests the upsert_async method.

        Args:
            entry: The entry to upsert.
            begin: Whether to begin a transaction.
            update: Whether to update.
            expected: The expected result.
        """
        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                if update:
                    await self.UnitTestClass.insert_async(
                        session=session,
                        item={"id": UUID(int=1), "name": "old"},
                        as_dict=True,
                        begin=True,
                    )

                await self.UnitTestClass.upsert_async(session=session, entry=entry, begin=begin)
                if not begin:
                    await session.commit()

                item_obj = await session.get(self.UnitTestClass, entry["id"])
                assert item_obj is not None
                item_name = getattr(item_obj, "name", None)
        finally:
            await db_engine.dispose()
        assert item_name == expected

    @pytest.mark.parametrize(
        ("entries", "expected"),
        [
            ([{"id": UUID(int=1), "name": "1"}, {"id": UUID(int=2), "name": "2"}], ("1", "2")),
        ],
    )
    @pytest.mark.parametrize("begin", [True, False])
    @pytest.mark.parametrize("update", [True, False])
    def test_upsert_all(
        self,
        entries: list[dict[str, Any]],
        begin: bool,
        update: bool,
        expected: tuple[str, ...],
    ) -> None:
        """Tests the upsert_all method.

        Args:
            entries: The entries to upsert.
            begin: Whether to begin a transaction.
            update: Whether to update.
            expected: The expected results.
        """
        column = "name" if "name" in self.UnitTestClass.get_column_names() else "id"
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                if update:
                    self.UnitTestClass.insert_all(
                        session=session,
                        items=[{"id": UUID(int=1), "name": "old1"}, {"id": UUID(int=2), "name": "old2"}],
                        as_dict=True,
                        begin=True,
                    )

                self.UnitTestClass.upsert_all(session=session, entries=entries, begin=begin)
                if not begin:
                    session.commit()

                item_objs = [session.get(self.UnitTestClass, e["id"]) for e in entries]
                assert all(item_obj is not None for item_obj in item_objs)
                item_names = tuple(getattr(item_obj, column) for item_obj in item_objs)
        finally:
            db_engine.dispose()
        assert item_names == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("entries", "expected"),
        [
            ([{"id": UUID(int=1), "name": "1"}, {"id": UUID(int=2), "name": "2"}], ("1", "2")),
        ],
    )
    @pytest.mark.parametrize("begin", [True, False])
    @pytest.mark.parametrize("update", [True, False])
    async def test_upsert_all_async(
        self,
        entries: list[dict[str, Any]],
        begin: bool,
        update: bool,
        expected: tuple[str, ...],
    ) -> None:
        """Tests the upsert_all_async method.

        Args:
            entries: The entries to upsert.
            begin: Whether to begin a transaction.
            update: Whether to update.
            expected: The expected results.
        """
        column = "name" if "name" in self.UnitTestClass.get_column_names() else "id"
        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                if update:
                    await self.UnitTestClass.insert_all_async(
                        session=session,
                        items=[{"id": UUID(int=1), "name": "old1"}, {"id": UUID(int=2), "name": "old2"}],
                        as_dict=True,
                        begin=True,
                    )

                await self.UnitTestClass.upsert_all_async(session=session, entries=entries, begin=begin)
                if not begin:
                    await session.commit()

                item_objs = [await session.get(self.UnitTestClass, e["id"]) for e in entries]
                assert all(item_obj is not None for item_obj in item_objs)
                item_names = tuple(getattr(item_obj, column) for item_obj in item_objs)
        finally:
            await db_engine.dispose()
        assert item_names == expected

    def test_upsert_all_missing_key(self) -> None:
        """Tests the upsert_all method with missing key."""
        columns = self.UnitTestClass.get_column_names()
        column = "name" if "name" in columns else ("update_id" if "update_id" in columns else None)
        if column is None:
            pytest.skip("No suitable column for missing key test")
        val = "no_id" if column == "name" else 1

        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                entries = [{column: val}]
                self.UnitTestClass.upsert_all(session=session, entries=entries, begin=True)
                session.commit()

                items = session.execute(select(self.UnitTestClass)).scalars().all()
                assert len(items) == 1
                assert getattr(items[0], column) == val
        finally:
            db_engine.dispose()

    @pytest.mark.asyncio
    async def test_upsert_all_async_missing_key(self) -> None:
        """Tests the upsert_all_async method with missing key."""
        columns = self.UnitTestClass.get_column_names()
        column = "name" if "name" in columns else ("update_id" if "update_id" in columns else None)
        if column is None:
            pytest.skip("No suitable column for missing key test")
        val = "no_id" if column == "name" else 1

        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                entries = [{column: val}]
                await self.UnitTestClass.upsert_all_async(session=session, entries=entries, begin=True)
                await session.commit()

                items = [i async for i in (await session.stream(select(self.UnitTestClass))).scalars()]
                assert len(items) == 1
                assert getattr(items[0], column) == val
        finally:
            await db_engine.dispose()

    @pytest.mark.parametrize("begin", [True, False])
    def test_delete_item(self, begin: bool) -> None:
        """Tests the delete_item method."""
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                item = {"id": UUID(int=1)}
                self.UnitTestClass.insert(session=session, item=item, as_dict=True, begin=True)

                # Fetch item to delete
                item_obj = session.get(self.UnitTestClass, item["id"])
                assert item_obj is not None
                session.commit()

                self.UnitTestClass.delete(session=session, item=item_obj, begin=begin)
                if not begin:
                    session.commit()

                n_entries = self.get_table_length(session=session)
        finally:
            db_engine.dispose()
        assert n_entries == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("begin", [True, False])
    async def test_delete_item_async(self, begin: bool) -> None:
        """Tests the delete_item_async method."""
        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                item = {"id": UUID(int=1)}
                await self.UnitTestClass.insert_async(session=session, item=item, as_dict=True, begin=True)

                # Fetch item to delete
                item_obj = await session.get(self.UnitTestClass, item["id"])
                assert item_obj is not None
                await session.commit()

                await self.UnitTestClass.delete_async(session=session, item=item_obj, begin=begin)
                if not begin:
                    await session.commit()

                n_entries = await self.get_async_table_length(session=session)
        finally:
            await db_engine.dispose()
        assert n_entries == 0

    # Queries
    def test_count(self) -> None:
        """Tests the count method."""
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                items = [
                    {"id": UUID(int=1)},
                    {"id": UUID(int=2)},
                ]
                self.UnitTestClass.insert_all(session=session, items=items, as_dict=True, begin=True)

                count = self.UnitTestClass.count(session=session)
        finally:
            db_engine.dispose()
        assert count == 2

    @pytest.mark.asyncio
    async def test_count_async(self) -> None:
        """Tests the count_async method."""
        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                items = [
                    {"id": UUID(int=1)},
                    {"id": UUID(int=2)},
                ]
                await self.UnitTestClass.insert_all_async(session=session, items=items, as_dict=True, begin=True)

                count = await self.UnitTestClass.count_async(session=session)
        finally:
            await db_engine.dispose()
        assert count == 2

    @pytest.mark.parametrize("as_python", [True, False])
    def test_get_by_id(self, as_python: bool) -> None:
        """Tests the get_by_id method."""
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                item = {"id": UUID(int=1)}
                self.UnitTestClass.insert(session=session, item=item, as_dict=True, begin=True)

                result = self.UnitTestClass.get_by_id(session=session, id_=item["id"], as_python=as_python)
        finally:
            db_engine.dispose()

        if as_python:
            assert isinstance(result, dict)
            assert result["id"] == item["id"]
        else:
            assert isinstance(result, self.UnitTestClass)
            assert result.id == item["id"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("as_python", [True, False])
    async def test_get_by_id_async(self, as_python: bool) -> None:
        """Tests the get_by_id_async method."""
        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                item = {"id": UUID(int=1)}
                await self.UnitTestClass.insert_async(session=session, item=item, as_dict=True, begin=True)

                result = await self.UnitTestClass.get_by_id_async(session=session, id_=item["id"], as_python=as_python)
        finally:
            await db_engine.dispose()

        if as_python:
            assert isinstance(result, dict)
            assert result["id"] == item["id"]
        else:
            assert isinstance(result, self.UnitTestClass)
            assert result.id == item["id"]

    @pytest.mark.parametrize("as_python", [True, False])
    def test_get_by(self, as_python: bool) -> None:
        """Tests the get_by method."""
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                item = {"id": UUID(int=1)}
                self.UnitTestClass.insert(session=session, item=item, as_dict=True, begin=True)

                results = self.UnitTestClass.get_by(
                    session=session, column_name="id", value=item["id"], as_python=as_python
                )

                if not as_python:
                    final_results: Any = results.scalars().all()  # type: ignore
                else:
                    final_results = results
        finally:
            db_engine.dispose()

        assert len(final_results) == 1
        if as_python:
            assert isinstance(final_results[0], dict)
            assert final_results[0]["id"] == item["id"]
        else:
            assert isinstance(final_results[0], self.UnitTestClass)
            assert final_results[0].id == item["id"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("as_python", [True, False])
    async def test_get_by_async(self, as_python: bool) -> None:
        """Tests the get_by_async method."""
        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                item = {"id": UUID(int=1)}
                await self.UnitTestClass.insert_async(session=session, item=item, as_dict=True, begin=True)

                results = await self.UnitTestClass.get_by_async(
                    session=session,
                    column_name="id",
                    value=item["id"],
                    as_python=as_python,
                )

                if not as_python:
                    final_results: Any = [r async for r in results.scalars()]  # type: ignore
                else:
                    final_results = results
        finally:
            await db_engine.dispose()

        assert len(final_results) == 1
        if as_python:
            assert isinstance(final_results[0], dict)
            assert final_results[0]["id"] == item["id"]
        else:
            assert isinstance(final_results[0], self.UnitTestClass)
            assert final_results[0].id == item["id"]

    @pytest.mark.parametrize("as_python", [True, False])
    def test_get_all(self, as_python: bool) -> None:
        """Tests the get_all method."""
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                items = [
                    {"id": UUID(int=1)},
                    {"id": UUID(int=2)},
                ]
                self.UnitTestClass.insert_all(session=session, items=items, as_dict=True, begin=True)

                results = self.UnitTestClass.get_all(session=session, as_python=as_python)

                if not as_python:
                    final_results: Any = results.scalars().all()  # type: ignore
                else:
                    final_results = results
        finally:
            db_engine.dispose()

        if as_python:
            assert isinstance(final_results, list)
            assert len(final_results) == 2
            assert isinstance(final_results[0], dict)
        else:
            assert len(final_results) == 2
            assert isinstance(final_results[0], self.UnitTestClass)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("as_python", [True, False])
    async def test_get_all_async(self, as_python: bool) -> None:
        """Tests the get_all_async method."""
        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                items = [
                    {"id": UUID(int=1)},
                    {"id": UUID(int=2)},
                ]
                await self.UnitTestClass.insert_all_async(session=session, items=items, as_dict=True, begin=True)

                results = await self.UnitTestClass.get_all_async(session=session, as_python=as_python)

                if not as_python:
                    final_results: Any = [r async for r in results.scalars()]  # type: ignore
                else:
                    final_results = results
        finally:
            await db_engine.dispose()

        if as_python:
            assert isinstance(final_results, list)
            assert len(final_results) == 2
            assert isinstance(final_results[0], dict)
        else:
            assert len(final_results) == 2
            assert isinstance(final_results[0], self.UnitTestClass)

    def test_create_find_column_value_statement(self) -> None:
        """Tests the create_find_column_value_statement method."""
        stmt = self.UnitTestClass.create_find_column_value_statement("id", UUID(int=1))
        assert stmt is not None

    def test_create_find_column_values_statement(self) -> None:
        """Tests the create_find_column_values_statement method."""
        stmt = self.UnitTestClass.create_find_column_values_statement("id", [UUID(int=1), UUID(int=2)])
        assert stmt is not None

    # Row Instance Methods
    @pytest.mark.skip(reason="update test not implemented")
    def test_update_instance(self, update_kwargs: dict[str, Any], expected: str) -> None:
        """Tests the update method."""

    @pytest.mark.skip(reason="as_sql_dict test not implemented")
    def test_as_sql_dict(self, item: dict[str, Any]) -> None:
        """Tests the as_sql_dict method."""

    @pytest.mark.skip(reason="as_sql_dict_async test not implemented")
    async def test_as_sql_dict_async(self, item: dict[str, Any]) -> None:
        """Tests the as_sql_dict_async method."""

    @pytest.mark.skip(reason="as_python_dict test not implemented")
    def test_as_python_dict(self, item: dict[str, Any]) -> None:
        """Tests the as_python_dict method."""

    @pytest.mark.skip(reason="as_python_dict_async test not implemented")
    async def test_as_python_dict_async(self, item: dict[str, Any]) -> None:
        """Tests the as_python_dict_async method."""


class BaseTableManifestationTestSuite(BaseReducibleTestSuite):
    """A Testsuite for the TableManifestation class.

    This class tests the functionality of the TableManifestation class. It inherits from BaseClassTestSuite to leverage
    common testing functionality.
    """

    # Class Attributes #
    UnitTestClass: type[TableManifestation]
    db_schema: type[DeclarativeBase]
    table_schema: type[TableSchemaMixin]

    # Instance Methods #
    # Helper Methods #
    def create_new_table_manifestation(self, **kwargs: Any) -> TableManifestation:
        """Creates a new table manifestation.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            The new table manifestation.
        """
        database = None
        if "database" not in kwargs:
            database = Database(path=":memory:", schema=self.db_schema, open_=False, create_tables=True)
            kwargs["database"] = database

        obj = self.UnitTestClass(table_schema=self.table_schema, **kwargs)
        if database is not None:
            obj._test_db_ref = database  # type: ignore[attr-defined]
        return obj

    def get_table_length(self, session: Session) -> int:
        """Gets the number of rows in the table.

        Args:
            session: The database session.

        Returns:
            The number of rows.
        """
        result = session.scalar(select(func.count()).select_from(self.table_schema))
        return result if result is not None else 0

    async def get_async_table_length(self, session: AsyncSession) -> int:
        """Gets the number of rows in the table asynchronously.

        Args:
            session: The database session.

        Returns:
            The number of rows.
        """
        result = await session.scalar(select(func.count()).select_from(self.table_schema))
        return result if result is not None else 0

    # Fixtures #
    @pytest.fixture
    def database(self) -> Generator[Database]:
        """Creates a database fixture.

        Yields:
            Database: A Database instance for testing.
        """
        db = Database(path=":memory:", schema=self.db_schema, open_=False, create_tables=False)
        yield db
        db.close()

    @pytest.fixture
    def test_object(self, database: Database) -> TableManifestation:
        """Creates a test object.

        Args:
            database: The database fixture.

        Returns:
            TableManifestation: A TableManifestation instance for testing.
        """
        return self.UnitTestClass(table_schema=self.table_schema, database=database)

    # Tests #
    # Instantiation #
    def test_instance_creation(self, *args: Any, **kwargs: Any) -> None:
        """Tests that instances of the class can be created.

        Args:
            *args: Positional arguments list to pass to the class constructor.
            **kwargs: Keyword arguments to pass to the class constructor.
        """
        instance = self.UnitTestClass()
        assert isinstance(instance, self.UnitTestClass)

    def test_database_property(self, test_object: TableManifestation) -> None:
        """Tests the database property.

        Args:
            test_object: The test object.
        """
        assert isinstance(test_object.database, Database)

    def test_construct(self, database: Database) -> None:
        """Tests the construct method."""
        # Test with no arguments
        obj = TableManifestation(init=False)
        obj.construct()
        assert obj._database is None

        # Test with arguments
        obj = TableManifestation(init=False)
        obj.construct(table_schema=self.table_schema, database=database)
        assert obj.database is database
        assert obj.table_schema is self.table_schema

    # Pickling
    def test_pickling(self, test_object: Any) -> None:
        """Tests pickling the object."""
        # Keep database alive by pickling it together
        dumped = pickle.dumps((test_object, test_object.database))
        loaded_obj, loaded_db = pickle.loads(dumped)
        try:
            assert loaded_obj.database is loaded_db
            assert loaded_obj.table_schema is not None
        finally:
            loaded_db.close()

    def test_getstate_not_dict(self, test_object: TableManifestation) -> None:
        """Tests __getstate__ when super returns a non-dict."""
        # Standard Libraries #
        import unittest.mock

        with unittest.mock.patch(
            "sqlalchemyobjects.tables.base.basetable.BaseReducible.__getstate__", return_value=None
        ):
            state = test_object.__getstate__()
        assert state is None

    @pytest.mark.parametrize("method", ["copy", "method"])
    def test_deepcopy_operations(
        self,
        test_object: TableManifestation,
        method: str,
        memo: dict[Any, Any] | None = None,
    ) -> None:
        """Tests deepcopy operations."""
        if memo is None:
            memo = {}

        if method == "copy":
            deepcopied_obj, deepcopied_db = copy.deepcopy((test_object, test_object.database))

            try:
                assert deepcopied_obj is not test_object
                assert isinstance(deepcopied_obj, self.UnitTestClass)

                assert deepcopied_db is not test_object.database
                assert isinstance(deepcopied_db, Database)

                # The deepcopied object should reference the deepcopied database
                assert deepcopied_obj.database is deepcopied_db
                assert deepcopied_db.path == test_object.database.path
            finally:
                deepcopied_db.close()
        else:
            obj_deepcopy = test_object.deepcopy(memo=memo)

            assert obj_deepcopy is not test_object
            assert isinstance(obj_deepcopy, self.UnitTestClass)

    @pytest.mark.skip(reason="build test not implemented")
    def test_build(self) -> None:
        """Tests the build method."""

    @pytest.mark.skip(reason="load test not implemented")
    def test_load(self) -> None:
        """Tests the load method."""

    def test_create_session(self, test_object: TableManifestation) -> None:
        """Tests the create_session method."""
        test_object.database.create_database()
        session = test_object.create_session()
        assert isinstance(session, Session)
        session.close()

    @pytest.mark.asyncio
    async def test_create_async_session(self, test_object: TableManifestation) -> None:
        """Tests the create_async_session method."""
        await test_object.database.create_database_async()
        try:
            session = test_object.create_async_session()
            assert isinstance(session, AsyncSession)
            await session.close()
        finally:
            await test_object.database.close_async()

    # ExampleDatabaseSchema
    def test_to_sql_types(self, test_object: TableManifestation) -> None:
        """Tests the to_sql_types method delegation."""
        data = {"id": "00000000-0000-0000-0000-000000000001"}
        sql_data = test_object.to_sql_types(data)
        assert sql_data["id"] == UUID(int=1)

    def test_from_sql_types(self, test_object: TableManifestation) -> None:
        """Tests the from_sql_types method delegation."""
        data = {"id": UUID(int=1)}
        python_data = test_object.from_sql_types(data)
        assert python_data["id"] == UUID(int=1)

    def test_item_from_dict(self, test_object: TableManifestation) -> None:
        """Tests the item_from_dict method delegation."""
        data = {"id": UUID(int=1)}
        item = test_object.item_from_dict(data)
        assert isinstance(item, self.table_schema)
        assert item.id == UUID(int=1)

    # Modification
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(("item", "expected"), [({"id": UUID(int=1)}, 1)])
    @pytest.mark.parametrize("as_dict", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_insert(
        self,
        test_object: TableManifestation,
        use_session: bool,
        item: dict[str, Any],
        as_dict: bool,
        begin: bool,
        expected: int,
    ) -> None:
        """Tests the insert method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            item: The item to insert.
            as_dict: Whether to insert as a dictionary.
            begin: Whether to begin a transaction.
            expected: The expected number of entries.
        """
        item_obj: Any
        if not as_dict:
            item_obj = test_object.item_from_dict(item)
        else:
            item_obj = item

        test_object.database.create_database()
        try:
            if use_session:
                with test_object.create_session() as session:
                    test_object.insert(item_obj, session=session, as_dict=as_dict, begin=begin)
                    if not begin:
                        session.commit()
            else:
                test_object.insert(item_obj, as_dict=as_dict, begin=begin)

            with test_object.create_session() as session:
                n_entries = self.get_table_length(session=session)
        finally:
            test_object.database.close()
        assert n_entries == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(("item", "expected"), [({"id": UUID(int=1)}, 1)])
    @pytest.mark.parametrize("as_dict", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_insert_async(
        self,
        test_object: TableManifestation,
        use_session: bool,
        item: dict[str, Any],
        as_dict: bool,
        begin: bool,
        expected: int,
    ) -> None:
        """Tests the insert_async method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            item: The item to insert.
            as_dict: Whether to insert as a dictionary.
            begin: Whether to begin a transaction.
            expected: The expected number of entries.
        """
        item_obj: Any
        if not as_dict:
            item_obj = test_object.item_from_dict(item)
        else:
            item_obj = item

        await test_object.database.create_database_async()
        try:
            if use_session:
                async with test_object.create_async_session() as session:
                    await test_object.insert_async(item_obj, session=session, as_dict=as_dict, begin=begin)
                    if not begin:
                        await session.commit()
            else:
                await test_object.insert_async(item_obj, as_dict=as_dict, begin=begin)

            async with test_object.create_async_session() as session:
                n_entries = await self.get_async_table_length(session=session)
        finally:
            await test_object.database.close_async()
        assert n_entries == expected

    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(
        ("items", "expected"),
        [
            ([{"id": UUID(int=1), "name": "1"}, {"id": UUID(int=2), "name": "2"}], 2),
        ],
    )
    @pytest.mark.parametrize("as_dict", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_insert_all(
        self,
        test_object: TableManifestation,
        use_session: bool,
        items: list[dict[str, Any]],
        as_dict: bool,
        begin: bool,
        expected: int,
    ) -> None:
        """Tests the insert_all method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            items: The items to insert.
            as_dict: Whether to insert as a dictionary.
            begin: Whether to begin a transaction.
            expected: The expected number of entries.
        """
        items_to_insert: list[Any] = items
        if not as_dict:
            items_to_insert = [self.table_schema.item_from_dict(i) for i in items]

        test_object.database.create_database()
        try:
            if use_session:
                with test_object.create_session() as session:
                    test_object.insert_all(items_to_insert, session=session, begin=begin, as_dict=as_dict)
                    if not begin:
                        session.commit()
            else:
                test_object.insert_all(items_to_insert, begin=begin, as_dict=as_dict)

            with test_object.create_session() as session:
                n_entries = self.get_table_length(session=session)
        finally:
            test_object.database.close()
        assert n_entries == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(
        ("items", "expected"),
        [
            ([{"id": UUID(int=1), "name": "1"}, {"id": UUID(int=2), "name": "2"}], 2),
        ],
    )
    @pytest.mark.parametrize("as_dict", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_insert_all_async(
        self,
        test_object: TableManifestation,
        use_session: bool,
        items: list[dict[str, Any]],
        as_dict: bool,
        begin: bool,
        expected: int,
    ) -> None:
        """Tests the insert_all_async method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            items: The items to insert.
            as_dict: Whether to insert as a dictionary.
            begin: Whether to begin a transaction.
            expected: The expected number of entries.
        """
        items_to_insert: list[Any] = items
        if not as_dict:
            items_to_insert = [self.table_schema.item_from_dict(i) for i in items]

        await test_object.database.create_database_async()
        try:
            if use_session:
                async with test_object.create_async_session() as session:
                    await test_object.insert_all_async(items_to_insert, session=session, begin=begin, as_dict=as_dict)
                    if not begin:
                        await session.commit()
            else:
                await test_object.insert_all_async(items_to_insert, begin=begin, as_dict=as_dict)

            async with test_object.create_async_session() as session:
                n_entries = await self.get_async_table_length(session=session)
        finally:
            await test_object.database.close_async()
        assert n_entries == expected

    @pytest.mark.skip(reason="upsert test not implemented")
    def test_upsert(
        self,
        test_object: TableManifestation,
        use_session: bool,
        entry: dict[str, Any],
        begin: bool,
        update: bool,
        expected: Any,
    ) -> None:
        """Tests the upsert_entry method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            entry: The entry to upsert.
            begin: Whether to use a transaction.
            update: Whether to update.
            expected: The expected result.
        """

    @pytest.mark.skip(reason="upsert_async test not implemented")
    async def test_upsert_async(
        self,
        test_object: TableManifestation,
        use_session: bool,
        entry: dict[str, Any],
        begin: bool,
        update: bool,
        expected: Any,
    ) -> None:
        """Tests the upsert_async method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            entry: The entry to upsert.
            begin: Whether to use a transaction.
            update: Whether to update.
            expected: The expected result.
        """

    @pytest.mark.skip(reason="upsert_all test not implemented")
    def test_upsert_all(
        self,
        test_object: TableManifestation,
        use_session: bool,
        entries: list[dict[str, Any]],
        begin: bool,
        update: bool,
        expected: tuple[Any, ...],
    ) -> None:
        """Tests the upsert_entries method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            entries: The entries to upsert.
            begin: Whether to use a transaction.
            update: Whether to update.
            expected: The expected results.
        """

    @pytest.mark.skip(reason="upsert_all_async test not implemented")
    async def test_upsert_all_async(
        self,
        test_object: TableManifestation,
        use_session: bool,
        entries: list[dict[str, Any]],
        begin: bool,
        update: bool,
        expected: tuple[Any, ...],
    ) -> None:
        """Tests the upsert_all_async method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            entries: The entries to upsert.
            begin: Whether to use a transaction.
            update: Whether to update.
            expected: The expected results.
        """

    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_delete_item(self, test_object: TableManifestation, use_session: bool, begin: bool) -> None:
        """Tests the delete_item method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            begin: Whether to use a transaction.
        """
        test_object.database.create_database()
        test_object.insert(item={"id": UUID(int=1)}, as_dict=True, begin=True)

        if use_session:
            with test_object.create_session() as session:
                item = session.get(self.table_schema, UUID(int=1))
                assert item is not None
                if begin:
                    session.commit()
                test_object.delete(item, session=session, begin=begin)
                if not begin:
                    session.commit()
        else:
            with test_object.create_session() as session:
                item = session.get(self.table_schema, UUID(int=1))
            assert item is not None
            test_object.delete(item, begin=begin)

        with test_object.create_session() as session:
            assert session.get(self.table_schema, UUID(int=1)) is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_delete_item_async(self, test_object: TableManifestation, use_session: bool, begin: bool) -> None:
        """Tests the delete_item_async method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            begin: Whether to use a transaction.
        """
        await test_object.database.create_database_async()
        await test_object.insert_async(item={"id": UUID(int=1)}, as_dict=True, begin=True)

        if use_session:
            async with test_object.create_async_session() as session:
                item = await session.get(self.table_schema, UUID(int=1))
                assert item is not None
                if begin:
                    await session.commit()
                await test_object.delete_async(item, session=session, begin=begin)
                if not begin:
                    await session.commit()
        else:
            async with test_object.create_async_session() as session:
                item = await session.get(self.table_schema, UUID(int=1))
            assert item is not None
            await test_object.delete_async(item, begin=begin)

        async with test_object.create_async_session() as session:
            assert await session.get(self.table_schema, UUID(int=1)) is None

    # Queries
    @pytest.mark.parametrize("use_session", [True, False])
    def test_count(self, test_object: TableManifestation, use_session: bool) -> None:
        """Tests the count method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
        """
        test_object.database.create_database()
        try:
            items = [{"id": UUID(int=1)}, {"id": UUID(int=2)}]
            test_object.insert_all(items=items, as_dict=True, begin=True)

            if use_session:
                with test_object.create_session() as session:
                    count = test_object.count(session=session)
            else:
                count = test_object.count()
        finally:
            test_object.database.close()

        assert count == 2

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    async def test_count_async(self, test_object: TableManifestation, use_session: bool) -> None:
        """Tests the count_async method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
        """
        await test_object.database.create_database_async()
        try:
            items = [{"id": UUID(int=1)}, {"id": UUID(int=2)}]
            await test_object.insert_all_async(items=items, as_dict=True, begin=True)

            if use_session:
                async with test_object.create_async_session() as session:
                    count = await test_object.count_async(session=session)
            else:
                count = await test_object.count_async()
        finally:
            await test_object.database.close_async()

        assert count == 2

    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("as_python", [True, False])
    def test_get_by_id(self, test_object: TableManifestation, use_session: bool, as_python: bool) -> None:
        """Tests the get_by_id method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            as_python: Whether to return as python objects.
        """
        test_object.database.create_database()
        try:
            item = {"id": UUID(int=1)}
            test_object.insert(item=item, as_dict=True, begin=True)

            if use_session:
                with test_object.create_session() as session:
                    result = test_object.get_by_id(id_=item["id"], session=session, as_python=as_python)
            else:
                result = test_object.get_by_id(id_=item["id"], as_python=as_python)
        finally:
            test_object.database.close()

        if as_python or isinstance(result, dict):
            assert isinstance(result, dict)
            assert result["id"] == item["id"]
        else:
            assert isinstance(result, self.table_schema)
            assert result.id == item["id"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("as_python", [True, False])
    async def test_get_by_id_async(self, test_object: TableManifestation, use_session: bool, as_python: bool) -> None:
        """Tests the get_by_id_async method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            as_python: Whether to return as python objects.
        """
        await test_object.database.create_database_async()
        try:
            item = {"id": UUID(int=1)}
            await test_object.insert_async(item=item, as_dict=True, begin=True)

            if use_session:
                async with test_object.create_async_session() as session:
                    result = await test_object.get_by_id_async(id_=item["id"], session=session, as_python=as_python)
            else:
                result = await test_object.get_by_id_async(id_=item["id"], as_python=as_python)
        finally:
            await test_object.database.close_async()

        if as_python or isinstance(result, dict):
            assert isinstance(result, dict)
            assert result["id"] == item["id"]
        else:
            assert isinstance(result, self.table_schema)
            assert result.id == item["id"]

    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("as_python", [True, False])
    def test_get_by(self, test_object: TableManifestation, use_session: bool, as_python: bool) -> None:
        """Tests the get_by method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            as_python: Whether to return as python objects.
        """
        test_object.database.create_database()
        try:
            item = {"id": UUID(int=1)}
            test_object.insert(item=item, as_dict=True, begin=True)

            if use_session:
                with test_object.create_session() as session:
                    final_results = test_object.get_by(
                        column_name="id", value=item["id"], session=session, as_python=as_python
                    )
                    if not isinstance(final_results, list):
                        final_results = list(final_results.scalars().all())
            else:
                final_results = test_object.get_by(column_name="id", value=item["id"], as_python=as_python)
                if not isinstance(final_results, list):
                    final_results = list(final_results.scalars().all())
        finally:
            test_object.database.close()

        assert isinstance(final_results, list)
        assert len(final_results) == 1
        if as_python or isinstance(final_results[0], dict):
            assert isinstance(final_results[0], dict)
            assert final_results[0]["id"] == item["id"]
        else:
            assert isinstance(final_results[0], self.table_schema)
            assert final_results[0].id == item["id"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("as_python", [True, False])
    async def test_get_by_async(self, test_object: TableManifestation, use_session: bool, as_python: bool) -> None:
        """Tests the get_by_async method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            as_python: Whether to return as python objects.
        """
        await test_object.database.create_database_async()
        try:
            item = {"id": UUID(int=1)}
            await test_object.insert_async(item=item, as_dict=True, begin=True)

            if use_session:
                async with test_object.create_async_session() as session:
                    final_results = await test_object.get_by_async(
                        column_name="id",
                        value=item["id"],
                        session=session,
                        as_python=as_python,
                    )
                    if not isinstance(final_results, list):
                        final_results = list(await final_results.scalars().all())
            else:
                final_results = await test_object.get_by_async(column_name="id", value=item["id"], as_python=as_python)
                if not isinstance(final_results, list):
                    final_results = list(await final_results.scalars().all())
        finally:
            await test_object.database.close_async()

        assert isinstance(final_results, list)
        assert len(final_results) == 1
        if as_python or isinstance(final_results[0], dict):
            assert isinstance(final_results[0], dict)
            assert final_results[0]["id"] == item["id"]
        else:
            assert isinstance(final_results[0], self.table_schema)
            assert final_results[0].id == item["id"]

    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("as_python", [True, False])
    def test_get_all(self, test_object: TableManifestation, use_session: bool, as_python: bool) -> None:
        """Tests the get_all method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            as_python: Whether to return as python objects.
        """
        test_object.database.create_database()
        try:
            item = self.table_schema(id=UUID(int=1))
            test_object.insert(item, begin=True)

            if use_session:
                with test_object.create_session() as session:
                    final_items = test_object.get_all(session=session, as_python=as_python)
                    if not isinstance(final_items, list):
                        final_items = list(final_items.scalars().all())
            else:
                final_items = test_object.get_all(as_python=as_python)
                if not isinstance(final_items, list):
                    final_items = list(final_items.scalars().all())
        finally:
            test_object.database.close()

        assert isinstance(final_items, list)
        if as_python or (final_items and isinstance(final_items[0], dict)):
            assert len(final_items) == 1
            assert final_items[0]["id"] == UUID(int=1)
        else:
            assert len(final_items) == 1
            assert final_items[0].id == UUID(int=1)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("as_python", [True, False])
    async def test_get_all_async(self, test_object: TableManifestation, use_session: bool, as_python: bool) -> None:
        """Tests the get_all_async method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            as_python: Whether to return as python objects.
        """
        await test_object.database.create_database_async()
        try:
            item = self.table_schema(id=UUID(int=1))
            await test_object.insert_async(item, begin=True)

            if use_session:
                async with test_object.create_async_session() as session:
                    final_items = await test_object.get_all_async(session=session, as_python=as_python)
                    if not isinstance(final_items, list):
                        final_items = list(await final_items.scalars().all())
            else:
                final_items = await test_object.get_all_async(as_python=as_python)
                if not isinstance(final_items, list):
                    final_items = list(await final_items.scalars().all())
        finally:
            await test_object.database.close_async()

        assert isinstance(final_items, list)
        if as_python or (final_items and isinstance(final_items[0], dict)):
            assert len(final_items) == 1
            assert final_items[0]["id"] == UUID(int=1)
        else:
            assert len(final_items) == 1
            assert final_items[0].id == UUID(int=1)


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])

"""updatetabletestsuite.py
Test suites for the update table manifestations and schemas.
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
from typing import Any
from uuid import UUID

# Third-Party Packages #
import pytest
from sqlalchemy import Result
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Session

# Local Packages #
from ..tables.base import BaseUpdateTableSchema, UpdateTableManifestation
from .basetabletestsuite import BaseTableManifestationTestSuite, BaseTableSchemaTestSuite


# Definitions #
# Classes #
class ConcreteDatabaseSchema(AsyncAttrs, DeclarativeBase):
    """A concrete Database Schema for testing."""


class ConcreteUpdateTableSchema(BaseUpdateTableSchema, ConcreteDatabaseSchema):
    """A concrete Update Table Schema for testing."""

    __tablename__ = "update_table_test"


class ConcreteUpdateTableManifestation(UpdateTableManifestation):
    """A concrete Table Manifestation for testing."""

    table_schema: type[ConcreteUpdateTableSchema] = ConcreteUpdateTableSchema


class UpdateTableSchemaTestSuite(BaseTableSchemaTestSuite):
    """A Testsuite for the BaseUpdateTableSchema class.

    This class tests the functionality of the BaseUpdateTableSchema class. It inherits from BaseTableSchemaTestSuite to
    leverage common testing functionality.
    """

    # Attributes #
    UnitTestClass: type[BaseUpdateTableSchema] = ConcreteUpdateTableSchema  # type: ignore[assignment]

    # Tests #
    @pytest.mark.parametrize(("entry", "expected"), [({"id": UUID(int=1), "update_id": 10}, 10)])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_upsert(self, entry: dict[str, Any], begin: bool, update: bool, expected: int) -> None:
        """Tests the upsert method.

        Args:
            entry: The entry to upsert.
            begin: Whether to begin a transaction.
            update: Whether to update.
            expected: The expected result.
        """
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                if update:
                    self.UnitTestClass.insert(
                        session=session,
                        item={"id": UUID(int=1), "update_id": 1},
                        as_dict=True,
                        begin=True,
                    )

                self.UnitTestClass.upsert(session=session, entry=entry, begin=begin)
                if not begin:
                    session.commit()

                item_obj = session.get(self.UnitTestClass, entry["id"])
                assert item_obj is not None
                item_name = item_obj.update_id
        finally:
            db_engine.dispose()
        assert item_name == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("entry", "expected"), [({"id": UUID(int=1), "update_id": 10}, 10)])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_upsert_async(self, entry: dict[str, Any], begin: bool, update: bool, expected: int) -> None:
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
                        item={"id": UUID(int=1), "update_id": 1},
                        as_dict=True,
                        begin=True,
                    )

                await self.UnitTestClass.upsert_async(session=session, entry=entry, begin=begin)
                if not begin:
                    await session.commit()

                item_obj = await session.get(self.UnitTestClass, entry["id"])
                assert item_obj is not None
                item_name = item_obj.update_id
        finally:
            await db_engine.dispose()
        assert item_name == expected

    @pytest.mark.parametrize(
        ("entries", "expected"),
        [
            ([{"id": UUID(int=1), "update_id": 10}, {"id": UUID(int=2), "update_id": 20}], (10, 20)),
        ],
    )
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_upsert_all(
        self,
        entries: list[dict[str, Any]],
        begin: bool,
        update: bool,
        expected: tuple[int, ...],
    ) -> None:
        """Tests the upsert_all method.

        Args:
            entries: The entries to upsert.
            begin: Whether to begin a transaction.
            update: Whether to update.
            expected: The expected results.
        """
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                if update:
                    initial_items = [
                        {"id": UUID(int=1), "update_id": 1},
                        {"id": UUID(int=2), "update_id": 2},
                    ]
                    self.UnitTestClass.insert_all(session=session, items=initial_items, as_dict=True, begin=True)

                self.UnitTestClass.upsert_all(session=session, entries=entries, begin=begin)
                if not begin:
                    session.commit()

                check_data = []
                for i, item in enumerate(entries):
                    item_obj = session.get(self.UnitTestClass, item["id"])
                    assert item_obj is not None
                    check_data.append((item_obj.update_id, expected[i]))
        finally:
            db_engine.dispose()
        for actual, expected_val in check_data:
            assert actual == expected_val

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("entries", "expected"),
        [
            ([{"id": UUID(int=1), "update_id": 10}, {"id": UUID(int=2), "update_id": 20}], (10, 20)),
        ],
    )
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_upsert_all_async(
        self,
        entries: list[dict[str, Any]],
        begin: bool,
        update: bool,
        expected: tuple[int, ...],
    ) -> None:
        """Tests the upsert_all_async method.

        Args:
            entries: The entries to upsert.
            begin: Whether to begin a transaction.
            update: Whether to update.
            expected: The expected results.
        """
        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                if update:
                    initial_items = [
                        {"id": UUID(int=1), "update_id": 1},
                        {"id": UUID(int=2), "update_id": 2},
                    ]
                    await self.UnitTestClass.insert_all_async(
                        session=session, items=initial_items, as_dict=True, begin=True
                    )

                await self.UnitTestClass.upsert_all_async(session=session, entries=entries, begin=begin)
                if not begin:
                    await session.commit()

                check_data = []
                for i, item in enumerate(entries):
                    item_obj = await session.get(self.UnitTestClass, item["id"])
                    assert item_obj is not None
                    check_data.append((item_obj.update_id, expected[i]))
        finally:
            await db_engine.dispose()
        for actual, expected_val in check_data:
            assert actual == expected_val

    @pytest.mark.parametrize(
        ("entries", "expected"),
        [
            ([], None),
            ([{"id": UUID(int=1), "update_id": 10}], 10),
            ([{"id": UUID(int=1), "update_id": 10}, {"id": UUID(int=2), "update_id": 20}], 20),
            ([{"id": UUID(int=1), "update_id": 20}, {"id": UUID(int=2), "update_id": 10}], 20),
        ],
    )
    def test_get_last_update_id(self, entries: list[dict[str, Any]], expected: int | None) -> None:
        """Tests the get_last_update_id method."""
        db_engine = self.create_engine()
        try:
            cls = self.UnitTestClass
            with Session(db_engine) as session:
                for entry in entries:
                    session.add(cls(**entry))
                session.commit()

                last_id = cls.get_last_update_id(session)
                assert last_id == expected
        finally:
            db_engine.dispose()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("entries", "expected"),
        [
            ([], None),
            ([{"id": UUID(int=1), "update_id": 10}], 10),
            ([{"id": UUID(int=1), "update_id": 10}, {"id": UUID(int=2), "update_id": 20}], 20),
            ([{"id": UUID(int=1), "update_id": 20}, {"id": UUID(int=2), "update_id": 10}], 20),
        ],
    )
    async def test_get_last_update_id_async(self, entries: list[dict[str, Any]], expected: int | None) -> None:
        """Tests the get_last_update_id_async method."""
        db_engine = await self.create_async_engine()
        try:
            cls = self.UnitTestClass
            async with AsyncSession(db_engine) as session:
                for entry in entries:
                    session.add(cls(**entry))
                await session.commit()

                last_id = await cls.get_last_update_id_async(session)
                assert last_id == expected
        finally:
            await db_engine.dispose()

    @pytest.mark.parametrize(
        "entries",
        [
            [
                {"id": UUID(int=1), "update_id": 5},
                {"id": UUID(int=2), "update_id": 10},
                {"id": UUID(int=3), "update_id": 15},
            ]
        ],
    )
    @pytest.mark.parametrize(
        ("update_id", "inclusive", "expected_count", "expected_ids"),
        [
            (10, True, 2, {10, 15}),
            (10, False, 1, {15}),
            (5, True, 3, {5, 10, 15}),
            (15, True, 1, {15}),
            (15, False, 0, set()),
            (20, True, 0, set()),
        ],
    )
    @pytest.mark.parametrize("as_python", [True, False])
    def test_get_from_update(
        self,
        entries: list[dict[str, Any]],
        update_id: int,
        inclusive: bool,
        expected_count: int,
        expected_ids: set[int],
        as_python: bool,
    ) -> None:
        """Tests the get_from_update method."""
        db_engine = self.create_engine()
        try:
            cls = self.UnitTestClass
            with Session(db_engine) as session:
                for entry in entries:
                    session.add(cls(**entry))
                session.commit()

                results = cls.get_from_update(session, update_id, inclusive=inclusive, as_python=as_python)
                if as_python:
                    assert isinstance(results, list)
                    final_results = results
                else:
                    final_results = results.scalars().all()  # type: ignore[union-attr, assignment]

                if as_python:
                    assert len(final_results) == expected_count
                    assert {r["update_id"] for r in final_results} == expected_ids
                else:
                    assert len(final_results) == expected_count
                    assert {r.update_id for r in final_results} == expected_ids  # type: ignore[attr-defined]
        finally:
            db_engine.dispose()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "entries",
        [
            [
                {"id": UUID(int=1), "update_id": 5},
                {"id": UUID(int=2), "update_id": 10},
                {"id": UUID(int=3), "update_id": 15},
            ]
        ],
    )
    @pytest.mark.parametrize(
        ("update_id", "inclusive", "expected_count", "expected_ids"),
        [
            (10, True, 2, {10, 15}),
            (10, False, 1, {15}),
            (5, True, 3, {5, 10, 15}),
            (15, True, 1, {15}),
            (15, False, 0, set()),
            (20, True, 0, set()),
        ],
    )
    @pytest.mark.parametrize("as_python", [True, False])
    async def test_get_from_update_async(
        self,
        entries: list[dict[str, Any]],
        update_id: int,
        inclusive: bool,
        expected_count: int,
        expected_ids: set[int],
        as_python: bool,
    ) -> None:
        """Tests the get_from_update_async method."""
        db_engine = await self.create_async_engine()
        try:
            cls = self.UnitTestClass
            async with AsyncSession(db_engine) as session:
                for entry in entries:
                    session.add(cls(**entry))
                await session.commit()

                results = await cls.get_from_update_async(session, update_id, inclusive=inclusive, as_python=as_python)
                if as_python:
                    assert isinstance(results, list)
                    final_results = results
                else:
                    results_obj = results
                    final_results = results_obj.scalars().all()  # type: ignore[union-attr, assignment]

                assert len(final_results) == expected_count
                if as_python:
                    assert {r["update_id"] for r in final_results} == expected_ids
                else:
                    assert {r.update_id for r in final_results} == expected_ids  # type: ignore[attr-defined]
        finally:
            await db_engine.dispose()

    # Row Instance Methods
    @pytest.mark.parametrize(
        ("update_kwargs", "expected"),
        [
            ({"update_id": 10}, 10),
            ({"update_id": 10, "_format_entry": False}, 10),
        ],
    )
    def test_update_instance(self, update_kwargs: dict[str, Any], expected: int) -> None:
        """Tests the update_instance method."""
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                item = {"id": UUID(int=1), "update_id": 1}
                self.UnitTestClass.insert(session=session, item=item, as_dict=True, begin=True)

                # Fetch item to delete
                item_obj = session.get(self.UnitTestClass, item["id"])
                assert item_obj is not None
                session.commit()

                item_obj.update_instance(**update_kwargs)
        finally:
            db_engine.dispose()

        assert item_obj.update_id == expected

    @pytest.mark.parametrize(
        "item",
        [
            {"id": UUID(int=1), "update_id": 10},
            {"id": UUID(int=2), "update_id": None},
        ],
    )
    def test_as_sql_dict(self, item: dict[str, Any]) -> None:
        """Tests the as_sql_dict method."""
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                self.UnitTestClass.insert(session=session, item=item, as_dict=True, begin=True)
                item_obj = session.get(self.UnitTestClass, item["id"])
                assert item_obj is not None
                result = item_obj.as_sql_dict()
        finally:
            db_engine.dispose()
        if item.get("update_id") is None and result.get("update_id") == 0:
            result = result.copy()
            result["update_id"] = None
        assert result == item

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "item",
        [
            {"id": UUID(int=1), "update_id": 10},
            {"id": UUID(int=2), "update_id": None},
        ],
    )
    async def test_as_sql_dict_async(self, item: dict[str, Any]) -> None:
        """Tests the as_sql_dict_async method."""
        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                await self.UnitTestClass.insert_async(session=session, item=item, as_dict=True, begin=True)
                item_obj = await session.get(self.UnitTestClass, item["id"])
                assert item_obj is not None
                result = await item_obj.as_sql_dict_async()
        finally:
            await db_engine.dispose()
        if item.get("update_id") is None and result.get("update_id") == 0:
            result = result.copy()
            result["update_id"] = None
        assert result == item

    @pytest.mark.parametrize(
        "item",
        [
            {"id": UUID(int=1), "update_id": 10},
            {"id": UUID(int=2), "update_id": None},
        ],
    )
    def test_as_python_dict(self, item: dict[str, Any]) -> None:
        """Tests the as_python_dict method."""
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                self.UnitTestClass.insert(session=session, item=item, as_dict=True, begin=True)
                item_obj = session.get(self.UnitTestClass, item["id"])
                assert item_obj is not None
                result = item_obj.as_python_dict()
        finally:
            db_engine.dispose()
        if item.get("update_id") is None and result.get("update_id") == 0:
            result = result.copy()
            result["update_id"] = None
        assert result == item

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "item",
        [
            {"id": UUID(int=1), "update_id": 10},
            {"id": UUID(int=2), "update_id": None},
        ],
    )
    async def test_as_python_dict_async(self, item: dict[str, Any]) -> None:
        """Tests the as_python_dict_async method."""
        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                await self.UnitTestClass.insert_async(session=session, item=item, as_dict=True, begin=True)
                item_obj = await session.get(self.UnitTestClass, item["id"])
                assert item_obj is not None
                result = await item_obj.as_python_dict_async()
        finally:
            await db_engine.dispose()
        if item.get("update_id") is None and result.get("update_id") == 0:
            result = result.copy()
            result["update_id"] = None
        assert result == item


class UpdateTableManifestationTestSuite(BaseTableManifestationTestSuite):
    """A Testsuite for the UpdateTableManifestation class.

    This class tests the functionality of the UpdateTableManifestation class. It inherits from
    BaseTableManifestationTestSuite to leverage common testing functionality.
    """

    # Attributes #
    UnitTestClass: type[UpdateTableManifestation] = UpdateTableManifestation
    db_schema: type[ConcreteDatabaseSchema] = ConcreteDatabaseSchema
    table_schema: type[ConcreteUpdateTableSchema] = ConcreteUpdateTableSchema  # type: ignore[assignment]

    # Instance Methods #
    # Tests #
    # Modification
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(("entry", "expected"), [({"id": UUID(int=1), "update_id": 10}, 10)])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_upsert(
        self,
        test_object: UpdateTableManifestation,
        use_session: bool,
        entry: dict[str, Any],
        begin: bool,
        update: bool,
        expected: int,
    ) -> None:
        """Tests the upsert_entry method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            entry: The entry to upsert.
            begin: Whether to begin a transaction.
            update: Whether to update.
            expected: The expected result.
        """
        test_object.database.create_database()
        if update:
            test_object.insert(item={"id": UUID(int=1), "update_id": 1}, as_dict=True, begin=True)

        if use_session:
            with test_object.create_session() as session:
                test_object.upsert(entry, session=session, begin=begin)
                if not begin:
                    session.commit()
        else:
            test_object.upsert(entry, begin=begin)

        with test_object.create_session() as session:
            item_obj = session.get(self.table_schema, entry["id"])
            assert item_obj is not None
            item_name = item_obj.update_id
        test_object.database.close()
        assert item_name == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(("entry", "expected"), [({"id": UUID(int=1), "update_id": 10}, 10)])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_upsert_async(
        self,
        test_object: UpdateTableManifestation,
        use_session: bool,
        entry: dict[str, Any],
        begin: bool,
        update: bool,
        expected: int,
    ) -> None:
        """Tests the upsert_entry_async method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            entry: The entry to upsert.
            begin: Whether to begin a transaction.
            update: Whether to update.
            expected: The expected result.
        """
        await test_object.database.create_database_async()
        if update:
            await test_object.insert_async(item={"id": UUID(int=1), "update_id": 11}, as_dict=True, begin=True)

        if use_session:
            async with test_object.create_async_session() as session:
                await test_object.upsert_async(entry, session=session, begin=begin)
                if not begin:
                    await session.commit()
        else:
            await test_object.upsert_async(entry, begin=begin)

        async with test_object.create_async_session() as session:
            item_obj = await session.get(self.table_schema, entry["id"])
            assert item_obj is not None
            item_name = item_obj.update_id
        await test_object.database.close_async()
        assert item_name == expected

    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(
        ("entries", "expected"),
        [
            ([{"id": UUID(int=1), "update_id": 10}, {"id": UUID(int=2), "update_id": 20}], (10, 20)),
        ],
    )
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_upsert_all(
        self,
        test_object: UpdateTableManifestation,
        use_session: bool,
        entries: list[dict[str, Any]],
        begin: bool,
        update: bool,
        expected: tuple[int, ...],
    ) -> None:
        """Tests the upsert_entries method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            entries: The entries to upsert.
            begin: Whether to begin a transaction.
            update: Whether to update.
            expected: The expected results.
        """
        test_object.database.create_database()
        if update:
            initial_items = [
                {"id": UUID(int=1), "update_id": 1},
                {"id": UUID(int=2), "update_id": 2},
            ]
            test_object.insert_all(items=initial_items, as_dict=True, begin=True)

        if use_session:
            with test_object.create_session() as session:
                test_object.upsert_all(entries, session=session, begin=begin)
                if not begin:
                    session.commit()
        else:
            test_object.upsert_all(entries, begin=begin)

        with test_object.create_session() as session:
            check_data = []
            for i, item in enumerate(entries):
                item_obj = session.get(self.table_schema, item["id"])
                assert item_obj is not None
                check_data.append((item_obj.update_id, expected[i]))
        test_object.database.close()
        for actual, expected_val in check_data:
            assert actual == expected_val

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(
        ("entries", "expected"),
        [
            ([{"id": UUID(int=1), "update_id": 10}, {"id": UUID(int=2), "update_id": 20}], (10, 20)),
        ],
    )
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_upsert_all_async(
        self,
        test_object: UpdateTableManifestation,
        use_session: bool,
        entries: list[dict[str, Any]],
        begin: bool,
        update: bool,
        expected: tuple[int, ...],
    ) -> None:
        """Tests the upsert_all_async method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            entries: The entries to upsert.
            begin: Whether to begin a transaction.
            update: Whether to update.
            expected: The expected results.
        """
        await test_object.database.create_database_async()
        if update:
            initial_items = [
                {"id": UUID(int=1), "update_id": 1},
                {"id": UUID(int=2), "update_id": 2},
            ]
            await test_object.insert_all_async(items=initial_items, as_dict=True, begin=True)

        if use_session:
            async with test_object.create_async_session() as session:
                await test_object.upsert_all_async(entries, session=session, begin=begin)
                if not begin:
                    await session.commit()
        else:
            await test_object.upsert_all_async(entries, begin=begin)

        async with test_object.create_async_session() as session:
            check_data = []
            for i, item in enumerate(entries):
                item_obj = await session.get(self.table_schema, item["id"])
                assert item_obj is not None
                check_data.append((item_obj.update_id, expected[i]))
        await test_object.database.close_async()
        for actual, expected_val in check_data:
            assert actual == expected_val

    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(
        ("items", "expected"),
        [
            ([{"id": UUID(int=1), "update_id": 10}, {"id": UUID(int=2), "update_id": 20}], 2),
        ],
    )
    @pytest.mark.parametrize("as_dict", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_insert_all(
        self,
        test_object: UpdateTableManifestation,
        use_session: bool,
        items: list[dict[str, Any]],
        as_dict: bool,
        begin: bool,
        expected: int,
    ) -> None:
        """Tests the insert_all method."""
        items_to_insert: list[Any] = items
        if not as_dict:
            items_to_insert = [self.table_schema.item_from_dict(i) for i in items]

        test_object.database.create_database()
        if use_session:
            with test_object.create_session() as session:
                test_object.insert_all(items_to_insert, session=session, begin=begin, as_dict=as_dict)
                if not begin:
                    session.commit()
        else:
            test_object.insert_all(items_to_insert, begin=begin, as_dict=as_dict)

        with test_object.create_session() as session:
            count = self.get_table_length(session)
        test_object.database.close()
        assert count == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(
        ("items", "expected"),
        [
            ([{"id": UUID(int=1), "update_id": 10}, {"id": UUID(int=2), "update_id": 20}], 2),
        ],
    )
    @pytest.mark.parametrize("as_dict", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_insert_all_async(
        self,
        test_object: UpdateTableManifestation,
        use_session: bool,
        items: list[dict[str, Any]],
        as_dict: bool,
        begin: bool,
        expected: int,
    ) -> None:
        """Tests the insert_all_async method."""
        items_to_insert: list[Any] = items
        if not as_dict:
            items_to_insert = [self.table_schema.item_from_dict(i) for i in items]

        await test_object.database.create_database_async()
        if use_session:
            async with test_object.create_async_session() as session:
                await test_object.insert_all_async(items_to_insert, session=session, begin=begin, as_dict=as_dict)
                if not begin:
                    await session.commit()
        else:
            await test_object.insert_all_async(items_to_insert, begin=begin, as_dict=as_dict)

        async with test_object.create_async_session() as session:
            count = await self.get_async_table_length(session)
        await test_object.database.close_async()
        assert count == expected

    @pytest.mark.parametrize(
        ("entries", "expected"),
        [
            ([], None),
            ([{"id": UUID(int=1), "update_id": 10}], 10),
            ([{"id": UUID(int=1), "update_id": 10}, {"id": UUID(int=2), "update_id": 20}], 20),
            ([{"id": UUID(int=1), "update_id": 20}, {"id": UUID(int=2), "update_id": 10}], 20),
        ],
    )
    @pytest.mark.parametrize("use_session", [True, False])
    def test_get_last_update_id(
        self,
        test_object: UpdateTableManifestation,
        entries: list[dict[str, Any]],
        expected: int | None,
        use_session: bool,
    ) -> None:
        """Tests the get_last_update_id method."""
        test_object.database.create_database()
        for entry in entries:
            test_object.insert(entry)

        session = None
        if use_session:
            session = test_object.create_session()
        try:
            assert test_object.get_last_update_id(session=session) == expected
        finally:
            if session:
                session.close()
            test_object.database.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("entries", "expected"),
        [
            ([], None),
            ([{"id": UUID(int=1), "update_id": 10}], 10),
            ([{"id": UUID(int=1), "update_id": 10}, {"id": UUID(int=2), "update_id": 20}], 20),
            ([{"id": UUID(int=1), "update_id": 20}, {"id": UUID(int=2), "update_id": 10}], 20),
        ],
    )
    @pytest.mark.parametrize("use_session", [True, False])
    async def test_get_last_update_id_async(
        self,
        test_object: UpdateTableManifestation,
        entries: list[dict[str, Any]],
        expected: int | None,
        use_session: bool,
    ) -> None:
        """Tests the get_last_update_id_async method."""
        await test_object.database.create_database_async()
        for entry in entries:
            await test_object.insert_async(entry)

        session = None
        if use_session:
            session = test_object.create_async_session()
        try:
            assert await test_object.get_last_update_id_async(session=session) == expected
        finally:
            if session:
                await session.close()
            await test_object.database.close_async()

    @pytest.mark.parametrize(
        "entries",
        [
            [
                {"id": UUID(int=1), "update_id": 5},
                {"id": UUID(int=2), "update_id": 10},
                {"id": UUID(int=3), "update_id": 15},
            ]
        ],
    )
    @pytest.mark.parametrize(
        ("update_id", "inclusive", "expected_count", "expected_ids"),
        [
            (10, True, 2, {10, 15}),
            (10, False, 1, {15}),
            (5, True, 3, {5, 10, 15}),
            (15, True, 1, {15}),
            (15, False, 0, set()),
            (20, True, 0, set()),
        ],
    )
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("as_python", [True, False])
    def test_get_from_update(
        self,
        test_object: UpdateTableManifestation,
        entries: list[dict[str, Any]],
        update_id: int,
        inclusive: bool,
        expected_count: int,
        expected_ids: set[int],
        use_session: bool,
        as_python: bool,
    ) -> None:
        """Tests the get_from_update method."""
        # if not use_session and not as_python:
        #     pytest.skip("Cannot return Result object from closed session")
        test_object.database.create_database()
        for entry in entries:
            test_object.insert(entry)

        session = None
        if use_session:
            session = test_object.create_session()
        try:
            results = test_object.get_from_update(update_id, session=session, inclusive=inclusive, as_python=as_python)
            if as_python or not use_session:
                assert isinstance(results, list)
                assert len(results) == expected_count
                assert {r["update_id"] for r in results} == expected_ids
            else:
                assert isinstance(results, Result)
                final_results = results.scalars().all()
                assert len(final_results) == expected_count
                assert {r.update_id for r in final_results} == expected_ids
        finally:
            if session:
                session.close()
            test_object.database.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "entries",
        [
            [
                {"id": UUID(int=1), "update_id": 5},
                {"id": UUID(int=2), "update_id": 10},
                {"id": UUID(int=3), "update_id": 15},
            ]
        ],
    )
    @pytest.mark.parametrize(
        ("update_id", "inclusive", "expected_count", "expected_ids"),
        [
            (10, True, 2, {10, 15}),
            (10, False, 1, {15}),
            (5, True, 3, {5, 10, 15}),
            (15, True, 1, {15}),
            (15, False, 0, set()),
            (20, True, 0, set()),
        ],
    )
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("as_python", [True, False])
    async def test_get_from_update_async(
        self,
        test_object: UpdateTableManifestation,
        entries: list[dict[str, Any]],
        update_id: int,
        inclusive: bool,
        expected_count: int,
        expected_ids: set[int],
        use_session: bool,
        as_python: bool,
    ) -> None:
        """Tests the get_from_update_async method."""
        await test_object.database.create_database_async()
        for entry in entries:
            await test_object.insert_async(entry)

        session = None
        if use_session:
            session = test_object.create_async_session()
        try:
            results = await test_object.get_from_update_async(
                update_id, session=session, inclusive=inclusive, as_python=as_python
            )
            if as_python or not use_session:
                assert isinstance(results, list)
                assert len(results) == expected_count
                assert {r["update_id"] for r in results} == expected_ids
            else:
                assert isinstance(results, Result)
                final_results = results.scalars().all()
                assert len(final_results) == expected_count
                assert {r.update_id for r in final_results} == expected_ids

        finally:
            if session:
                await session.close()
            await test_object.database.close_async()


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])

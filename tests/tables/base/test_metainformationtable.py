"""test_metainformationtable.py
Tests for the metainformationtable module.
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
from sqlalchemy import String
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

# Source Packages #
from sqlalchemyobjects import BaseMetaInformationTableSchema, Database, MetaInformationTableManifestation
from sqlalchemyobjects.testsuite import (
    MetaInformationTableManifestationTestSuite,
    MetaInformationTableSchemaTestSuite,
)


# Definitions #
# Classes #
class ConcreteDatabaseSchema(AsyncAttrs, DeclarativeBase):
    """A concrete database schema."""


class ConcreteTableSchema(BaseMetaInformationTableSchema, ConcreteDatabaseSchema):
    """A concrete Table Schema for testing."""
    __tablename__ = "concrete_table"
    name: Mapped[str | None] = mapped_column(String, nullable=True)


class ConcreteTableManifestation(MetaInformationTableManifestation):
    """A concrete Table Manifestation for testing."""
    table_schema: type[ConcreteTableSchema] = ConcreteTableSchema


class TestMetaInformationTableSchema(MetaInformationTableSchemaTestSuite):
    """Tests the BaseMetaInformationTableSchema class."""

    # Attributes #
    UnitTestClass: type[ConcreteTableSchema] = ConcreteTableSchema

    # Instance Methods #
    def generate_item(self) -> dict[str, Any]:
        """Generates a test item.

        Returns:
            The test item.
        """
        return {"id": UUID(int=1), "name": "first"}

    def generate_update_item(self) -> dict[str, Any]:
        """Generates an update item.

        Returns:
            The update item.
        """
        return {"id": UUID(int=1), "name": "second"}

    # Tests #
    # Modification
    @pytest.mark.parametrize(("entry", "expected"), [({"id": UUID(int=1), "name": "new"}, "new")])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_upsert(self, entry: dict[str, Any], begin: bool, update: bool, expected: str) -> None:
        """Tests the upsert method."""
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                if update:
                    self.UnitTestClass.insert(
                        session=session,
                        item={"id": UUID(int=1), "name": "old"},
                        as_dict=True,
                        begin=True,
                    )

                self.UnitTestClass.upsert(session=session, entry=entry, begin=begin)
                if not begin:
                    session.commit()

                item_obj = session.get(self.UnitTestClass, entry["id"])
                assert item_obj is not None
                item_name = item_obj.name
        finally:
            db_engine.dispose()
        assert item_name == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("entry", "expected"), [({"id": UUID(int=1), "name": "new"}, "new")])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_upsert_async(self, entry: dict[str, Any], begin: bool, update: bool, expected: str) -> None:
        """Tests the upsert_async method."""
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
                item_name = item_obj.name
        finally:
            await db_engine.dispose()
        assert item_name == expected

    @pytest.mark.parametrize(("entries", "expected"), [
        ([{"id": UUID(int=1), "name": "new1"}, {"id": UUID(int=2), "name": "new2"}], ("new1", "new2")),
    ])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_upsert_all(
        self,
        entries: list[dict[str, Any]],
        begin: bool,
        update: bool,
        expected: tuple[str, ...],
    ) -> None:
        """Tests the upsert_all method."""
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                if update:
                    initial_items = [
                        {"id": UUID(int=1), "name": "old1"},
                        {"id": UUID(int=2), "name": "old2"},
                    ]
                    self.UnitTestClass.insert_all(session=session, items=initial_items, as_dict=True, begin=True)

                self.UnitTestClass.upsert_all(session=session, entries=entries, begin=begin)
                if not begin:
                    session.commit()

                check_data = []
                for i, item in enumerate(entries):
                    item_obj = session.get(self.UnitTestClass, item["id"])
                    assert item_obj is not None
                    check_data.append((item_obj.name, expected[i]))
        finally:
            db_engine.dispose()
        for actual, expected_val in check_data:
            assert actual == expected_val

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("entries", "expected"), [
        ([{"id": UUID(int=1), "name": "new1"}, {"id": UUID(int=2), "name": "new2"}], ("new1", "new2")),
    ])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_upsert_all_async(
        self,
        entries: list[dict[str, Any]],
        begin: bool,
        update: bool,
        expected: tuple[str, ...],
    ) -> None:
        """Tests the upsert_all_async method."""
        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                if update:
                    initial_items = [
                        {"id": UUID(int=1), "name": "old1"},
                        {"id": UUID(int=2), "name": "old2"},
                    ]
                    await self.UnitTestClass.insert_all_async(session=session, items=initial_items, as_dict=True,
                                                              begin=True)

                await self.UnitTestClass.upsert_all_async(session=session, entries=entries, begin=begin)
                if not begin:
                    await session.commit()

                check_data = []
                for i, item in enumerate(entries):
                    item_obj = await session.get(self.UnitTestClass, item["id"])
                    assert item_obj is not None
                    check_data.append((item_obj.name, expected[i]))
        finally:
            await db_engine.dispose()
        for actual, expected_val in check_data:
            assert actual == expected_val

    def test_set_item(self) -> None:
        """Tests the set_item method."""
        db_engine = self.create_engine()
        try:
            cls = self.UnitTestClass
            with Session(db_engine) as session:
                cls.create_item(session, id=UUID(int=1), name="old")
                session.commit()

                cls.set_item(session, item={"name": "new"}, begin=True)

                # Verify
                fetched = session.get(cls, UUID(int=1))
                assert fetched is not None
                assert fetched.name == "new"
        finally:
            db_engine.dispose()

    @pytest.mark.asyncio
    async def test_set_item_async(self) -> None:
        """Tests the set_item_async method."""
        db_engine = await self.create_async_engine()
        try:
            cls = self.UnitTestClass
            async with AsyncSession(db_engine) as session:
                await cls.create_item_async(session, id=UUID(int=1), name="old")
                await session.commit()

                await cls.set_item_async(session, item={"name": "new"}, begin=True)

                # Verify
                fetched = await session.get(cls, UUID(int=1))
                assert fetched is not None
                assert fetched.name == "new"
        finally:
            await db_engine.dispose()

    def test_set_meta_information(self) -> None:
        """Tests the set_meta_information method."""
        self.generate_item()
        self.generate_update_item()

        db_engine = self.create_engine()
        try:
            cls = self.UnitTestClass
            with Session(db_engine) as session:
                cls.create_meta_information(session, id=UUID(int=1), name="old")
                session.commit()

                cls.set_meta_information(session, name="new")
                session.commit()

                info = cls.get_meta_information(session)
                assert isinstance(info, dict)
                assert info["name"] == "new"
        finally:
            db_engine.dispose()

    @pytest.mark.asyncio
    async def test_set_meta_information_async(self) -> None:
        """Tests the set_meta_information_async method."""
        db_engine = await self.create_async_engine()
        try:
            cls = self.UnitTestClass
            async with AsyncSession(db_engine) as session:
                await cls.create_meta_information_async(session, id=UUID(int=1), name="old")
                await session.commit()

                await cls.set_meta_information_async(session, name="new")
                await session.commit()

                info = await cls.get_meta_information_async(session)
                assert isinstance(info, dict)
                assert info["name"] == "new"
        finally:
            await db_engine.dispose()

    # Row Instance Methods
    @pytest.mark.parametrize(("update_kwargs", "expected"), [
        ({"name": "new_name"}, "new_name"),
        ({"name": "new_name", "_format_entry": False}, "new_name"),
    ])
    def test_update_instance(self, update_kwargs: dict[str, Any], expected: str) -> None:
        """Tests the update_instance method."""
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                item = {"id": UUID(int=1), "name": "old"}
                self.UnitTestClass.insert(session=session, item=item, as_dict=True, begin=True)

                # Fetch item to delete
                item_obj = session.get(self.UnitTestClass, item["id"])
                assert item_obj is not None
                session.commit()

                item_obj.update_instance(**update_kwargs)
        finally:
            db_engine.dispose()

        assert item_obj.name == expected

    @pytest.mark.parametrize("item", [
        {"id": UUID(int=1), "name": "test"},
        {"id": UUID(int=2), "name": None},
    ])
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
        assert result == item

    @pytest.mark.asyncio
    @pytest.mark.parametrize("item", [
        {"id": UUID(int=1), "name": "test"},
        {"id": UUID(int=2), "name": None},
    ])
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
        assert result == item

    @pytest.mark.parametrize("item", [
        {"id": UUID(int=1), "name": "test"},
        {"id": UUID(int=2), "name": None},
    ])
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
        assert result == item

    @pytest.mark.asyncio
    @pytest.mark.parametrize("item", [
        {"id": UUID(int=1), "name": "test"},
        {"id": UUID(int=2), "name": None},
    ])
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
        assert result == item


class TestMetaInformationTableManifestation(MetaInformationTableManifestationTestSuite):
    """Tests the MetaInformationTableManifestation class."""

    # Class Attributes #
    UnitTestClass: type[ConcreteTableManifestation] = ConcreteTableManifestation
    db_schema: type[ConcreteDatabaseSchema] = ConcreteDatabaseSchema
    table_schema: type[ConcreteTableSchema] = ConcreteTableSchema

    # Instance Methods #
    def generate_item(self) -> dict[str, Any]:
        """Generates a test item.

        Returns:
            The test item.
        """
        return {"id": UUID(int=1), "name": "first"}

    def generate_update_item(self) -> dict[str, Any]:
        """Generates an update item.

        Returns:
            The update item.
        """
        return {"id": UUID(int=1), "name": "second"}

    # Tests #
    def test_build(self) -> None:
        """Tests the build method."""
        table_manifestation = self.create_new_table_manifestation()
        try:
            table_manifestation.database.create_database()
            table_manifestation.build()
            # build is a placeholder in base, just ensure it runs
            assert True
        finally:
            table_manifestation.database.close()

    def test_load(self) -> None:
        """Tests the load method."""
        table_manifestation = self.create_new_table_manifestation()
        try:
            table_manifestation.database.create_database()
            table_manifestation.load()
            # load is a placeholder in base, just ensure it runs
            assert True
        finally:
            table_manifestation.database.close()

    # Modification
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(("entry", "expected"), [({"id": UUID(int=1), "name": "new"}, "new")])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_upsert(
        self,
        test_object: MetaInformationTableManifestation,
        use_session: bool,
        entry: dict[str, Any],
        begin: bool,
        update: bool,
        expected: str,
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
        test_object.database.create_database()
        try:
            if update:
                test_object.insert(item={"id": UUID(int=1), "name": "old"}, as_dict=True, begin=True)

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
                item_name = item_obj.name
        finally:
            test_object.database.close()
        assert item_name == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(("entry", "expected"), [({"id": UUID(int=1), "name": "new"}, "new")])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_upsert_async(
        self,
        test_object: MetaInformationTableManifestation,
        use_session: bool,
        entry: dict[str, Any],
        begin: bool,
        update: bool,
        expected: str,
    ) -> None:
        """Tests the upsert_entry_async method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            entry: The entry to upsert.
            begin: Whether to use a transaction.
            update: Whether to update.
            expected: The expected result.
        """
        await test_object.database.create_database_async()
        try:
            if update:
                await test_object.insert_async(item={"id": UUID(int=1), "name": "old"}, as_dict=True, begin=True)

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
                item_name = item_obj.name
        finally:
            await test_object.database.close_async()
        assert item_name == expected

    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(("entries", "expected"), [
        ([{"id": UUID(int=1), "name": "new1"}, {"id": UUID(int=2), "name": "new2"}], ("new1", "new2")),
    ])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_upsert_all(
        self,
        test_object: MetaInformationTableManifestation,
        use_session: bool,
        entries: list[dict[str, Any]],
        begin: bool,
        update: bool,
        expected: tuple[str, ...],
    ) -> None:
        """Tests the upsert_entries method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            entries: The entries to upsert.
            begin: Whether to use a transaction.
            update: Whether to update.
            expected: The expected result.
        """
        test_object.database.create_database()
        try:
            if update:
                initial_items = [
                    {"id": UUID(int=1), "name": "old1"},
                    {"id": UUID(int=2), "name": "old2"},
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
                    check_data.append((item_obj.name, expected[i]))
        finally:
            test_object.database.close()
        for actual, expected_val in check_data:
            assert actual == expected_val

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize(("entries", "expected"), [
        ([{"id": UUID(int=1), "name": "new1"}, {"id": UUID(int=2), "name": "new2"}], ("new1", "new2")),
    ])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_upsert_all_async(
        self,
        test_object: MetaInformationTableManifestation,
        use_session: bool,
        entries: list[dict[str, Any]],
        begin: bool,
        update: bool,
        expected: tuple[str, ...],
    ) -> None:
        """Tests the upsert_all_async method.

        Args:
            test_object: The test object.
            use_session: Whether to use a session.
            entries: The entries to upsert.
            begin: Whether to use a transaction.
            update: Whether to update.
            expected: The expected result.
        """
        await test_object.database.create_database_async()
        try:
            if update:
                initial_items = [
                    {"id": UUID(int=1), "name": "old1"},
                    {"id": UUID(int=2), "name": "old2"},
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
                    check_data.append((item_obj.name, expected[i]))
        finally:
            await test_object.database.close_async()

        for actual, expected_val in check_data:
            assert actual == expected_val

    @pytest.mark.parametrize("use_session", [True, False])
    def test_set_item(self, database: Database, use_session: bool) -> None:
        """Tests the set_item method."""
        item = self.generate_item()
        update_item = self.generate_update_item()

        table = self.create_new_table_manifestation(database=database)
        table.database.create_database()

        # Setup data
        with table.create_session() as s:
            s.add(self.table_schema(**item))
            s.commit()

        session = None
        if use_session:
            session = table.create_session()

        try:
            update_data = update_item.copy()
            if "id" in update_data:
                del update_data["id"]

            table.set_item(item=update_data, session=session)
            if session is not None:
                session.commit()

            fetched_dict = table.get_item(session=session)
            assert isinstance(fetched_dict, dict)
            for k, v in update_data.items():
                assert fetched_dict[k] == v
        finally:
            if session:
                session.close()
            table.database.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    async def test_set_item_async(self, database: Database, use_session: bool) -> None:
        """Tests the set_item_async method."""
        item = self.generate_item()
        update_item = self.generate_update_item()

        table = self.create_new_table_manifestation(database=database)
        await table.database.create_database_async()

        # Setup data
        async with table.create_async_session() as s:
            s.add(self.table_schema(**item))
            await s.commit()

        session = None
        if use_session:
            session = table.create_async_session()

        try:
            update_data = update_item.copy()
            if "id" in update_data:
                del update_data["id"]

            await table.set_item_async(item=update_data, session=session)
            if session is not None:
                await session.commit()

            fetched_dict = await table.get_item_async(session=session)
            assert isinstance(fetched_dict, dict)
            for k, v in update_data.items():
                assert fetched_dict[k] == v
        finally:
            if session:
                await session.close()
            await table.database.close_async()


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])

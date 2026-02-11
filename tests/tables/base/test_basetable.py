"""test_basetable.py
Tests for the basetable module.
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
from sqlalchemy import ForeignKey, String, select
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

# Source Packages #
from sqlalchemyobjects import BaseTableSchema, TableManifestation
from sqlalchemyobjects.testsuite import BaseTableManifestationTestSuite, BaseTableSchemaTestSuite


# Definitions #
# Classes #
# Tables
class UserTableSchema(BaseTableSchema):
    """A user table schema."""
    __tablename__ = "users"
    name: Mapped[str] = mapped_column(String)
    type: Mapped[str] = mapped_column(String)


class EmployeeTableSchema(UserTableSchema):
    """An employee table schema."""
    __tablename__ = "employees"
    specialty: Mapped[str] = mapped_column(String)


# Database Schema
class ConcreteDatabaseSchema(AsyncAttrs, DeclarativeBase):
    """A concrete database schema."""


class ConcreteTableSchema(BaseTableSchema, ConcreteDatabaseSchema):
    """A concrete Table Schema for testing."""
    __tablename__ = "concrete_table"
    name: Mapped[str | None] = mapped_column(String, nullable=True)


class ConcreteTableManifestation(TableManifestation):
    """A concrete Table Manifestation for testing."""
    table_schema: type[ConcreteTableSchema] = ConcreteTableSchema


class STIBase(UserTableSchema, ConcreteDatabaseSchema):
    """Base class for STI testing."""
    __tablename__ = "sti_base"
    # Use the actual column attribute for polymorphic_on to ensure correct discriminator handling
    __mapper_args__ = {"polymorphic_on": UserTableSchema.type, "polymorphic_identity": "base"}


class STISub(STIBase):
    """Subclass for STI testing."""
    __mapper_args__ = {"polymorphic_identity": "sub"}


class JTIBase(UserTableSchema, ConcreteDatabaseSchema):
    """Base class for JTI testing."""
    __tablename__ = "jti_base"
    # Use the actual column attribute for polymorphic_on to ensure correct discriminator handling
    __mapper_args__ = {"polymorphic_on": UserTableSchema.type, "polymorphic_identity": "base"}


class JTISub(JTIBase, EmployeeTableSchema):
    """Subclass for JTI testing."""
    __tablename__ = "jti_sub"
    __mapper_args__ = {"polymorphic_identity": "sub"}
    id: Mapped[UUID] = mapped_column(ForeignKey("jti_base.id"), primary_key=True)


# Tests #
class TestBaseTableSchema(BaseTableSchemaTestSuite):
    """Tests the BaseTableSchema class."""

    # Attributes #
    UnitTestClass: type[ConcreteTableSchema] = ConcreteTableSchema  # type: ignore[assignment]

    # Instance Methods #
    # Tests #
    # Modification
    @pytest.mark.parametrize(("entry", "expected"), [({"id": UUID(int=1), "name": "new"}, "new")])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_upsert(self, entry: dict[str, Any], begin: bool, update: bool, expected: str) -> None:
        """Tests the upsert method."""
        db_engine = self.create_engine()
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
        db_engine.dispose()
        assert item_name == expected

    @pytest.mark.asyncio
    @pytest.mark.parametrize(("entry", "expected"), [({"id": UUID(int=1), "name": "new"}, "new")])
    @pytest.mark.parametrize("update", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_upsert_async(self, entry: dict[str, Any], begin: bool, update: bool, expected: str) -> None:
        """Tests the upsert_async method."""
        db_engine = await self.create_async_engine()
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
        await db_engine.dispose()
        for actual, expected_val in check_data:
            assert actual == expected_val

    def test_upsert_all_missing_key(self) -> None:
        """Tests the upsert_all method with missing key."""
        db_engine = self.create_engine()
        try:
            with Session(db_engine) as session:
                entries = [{"name": "no_id"}]
                self.UnitTestClass.upsert_all(session=session, entries=entries, begin=True)
                session.commit()

                items = session.execute(select(self.UnitTestClass)).scalars().all()
                assert len(items) == 1
                assert items[0].name == "no_id"
        finally:
            db_engine.dispose()

    @pytest.mark.asyncio
    async def test_upsert_all_async_missing_key(self) -> None:
        """Tests the upsert_all_async method with missing key."""
        db_engine = await self.create_async_engine()
        try:
            async with AsyncSession(db_engine) as session:
                entries = [{"name": "no_id"}]
                await self.UnitTestClass.upsert_all_async(session=session, entries=entries, begin=True)
                await session.commit()

                items = [i async for i in (await session.stream(select(self.UnitTestClass))).scalars()]
                assert len(items) == 1
                assert items[0].name == "no_id"
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

    def test_sti_polymorphic_loading(self) -> None:
        """Tests Single Table Inheritance polymorphic loading."""
        db_engine = self.create_engine()
        ConcreteDatabaseSchema.metadata.create_all(db_engine)
        with Session(db_engine) as session:
            # Insert via base class with sub identity
            STIBase.insert(session, {"name": "Sub1", "type": "sub"}, as_dict=True)
            session.commit()

            # Query via base class
            results = STIBase.get_all(session)
            assert not isinstance(results, list)
            items = results.scalars().all()
            assert len(items) == 1
            assert isinstance(items[0], STISub)
            assert items[0].name == "Sub1"
        db_engine.dispose()

    def test_sti_subclass_get_all_filters(self) -> None:
        """Tests that STI subclass get_all auto-filters by discriminator."""
        db_engine = self.create_engine()
        ConcreteDatabaseSchema.metadata.create_all(db_engine)
        with Session(db_engine) as session:
            STIBase.insert(session, {"name": "Base1", "type": "base"}, as_dict=True)
            STIBase.insert(session, {"name": "Sub1", "type": "sub"}, as_dict=True)
            session.commit()

            results = STISub.get_all(session)
            assert not isinstance(results, list)
            items = results.scalars().all()
            assert len(items) == 1
            assert isinstance(items[0], STISub)
            assert items[0].name == "Sub1"
        db_engine.dispose()

    def test_jti_multi_table_insert(self) -> None:
        """Tests Joined Table Inheritance multi-table insertion."""
        db_engine = self.create_engine()
        ConcreteDatabaseSchema.metadata.create_all(db_engine)
        with Session(db_engine) as session:
            # Insert via subclass
            JTISub.insert(session, {"name": "Eng1", "type": "sub", "specialty": "Robotics"}, as_dict=True)
            session.commit()

            # Verify in both tables
            base_items = session.execute(select(JTIBase)).scalars().all()
            sub_items = session.execute(select(JTISub)).scalars().all()
            assert len(base_items) == 1
            assert len(sub_items) == 1
            assert isinstance(sub_items[0], JTISub)
            assert sub_items[0].name == "Eng1"
            assert sub_items[0].specialty == "Robotics"
        db_engine.dispose()

    def test_sti_subclass_get_by_id(self) -> None:
        """Tests that STI subclass get_by_id executes the discriminator-filtered path.

        Ensures the STI-specific branch in BaseTableSchema.get_by_id is covered.
        """
        db_engine = self.create_engine()
        ConcreteDatabaseSchema.metadata.create_all(db_engine)
        try:
            with Session(db_engine) as session:
                # Insert a subclass row explicitly with a fixed ID via the base class to set discriminator
                STIBase.insert(session, {"id": UUID(int=123), "name": "X", "type": "sub"}, as_dict=True)
                session.commit()

                # Fetch via subclass API which should use the discriminator-aware query path
                item = STISub.get_by_id(session, UUID(int=123))
                assert isinstance(item, STISub)
                assert item is not None
                assert item.name == "X"
        finally:
            db_engine.dispose()

    @pytest.mark.asyncio
    async def test_sti_subclass_get_by_id_async(self) -> None:
        """Tests that STI subclass get_by_id_async executes the discriminator-filtered path."""
        db_engine = await self.create_async_engine()
        # Create tables for the ConcreteDatabaseSchema (STI base/sub share this metadata)
        async with db_engine.begin() as conn:
            await conn.run_sync(ConcreteDatabaseSchema.metadata.create_all)
        try:
            async with AsyncSession(db_engine) as session:
                # Insert a subclass row explicitly with a fixed ID via the base class to set discriminator
                await STIBase.insert_async(
                    session,
                    {"id": UUID(int=456), "name": "Y", "type": "sub"},
                    as_dict=True,
                    begin=True,
                )
                await session.commit()

                # Fetch via subclass API which should use the discriminator-aware query path
                item = await STISub.get_by_id_async(session, UUID(int=456))
                assert isinstance(item, STISub)
                assert item is not None
                assert item.name == "Y"
        finally:
            await db_engine.dispose()


class TestBaseTableManifestation(BaseTableManifestationTestSuite):
    """Tests the TableManifestation class."""

    # Class Attributes #
    UnitTestClass: type[ConcreteTableManifestation] = ConcreteTableManifestation
    db_schema: type[ConcreteDatabaseSchema] = ConcreteDatabaseSchema
    table_schema: type[ConcreteTableSchema] = ConcreteTableSchema  # type: ignore[assignment]

    # Instance Methods #
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
        test_object: TableManifestation,
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
        test_object: TableManifestation,
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
        test_object: TableManifestation,
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
        test_object: TableManifestation,
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


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])

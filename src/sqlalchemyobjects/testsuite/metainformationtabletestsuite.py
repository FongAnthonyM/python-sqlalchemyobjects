"""metainformationtabletestsuite.py
Test suites for the meta information table manifestations and schemas.
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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Session

# Local Packages #
from ..database import Database
from ..tables.base.metainformationtable import BaseMetaInformationTableSchema, MetaInformationTableManifestation
from .singletontabletestsuite import SingletonTableManifestationTestSuite, SingletonTableSchemaTestSuite


# Definitions #
# Classes #
class MetaInformationTableSchemaTestSuite(SingletonTableSchemaTestSuite):
    """A Testsuite for the BaseMetaInformationTableSchema class.

    This class tests the functionality of the BaseMetaInformationTableSchema class. It inherits from
    SingletonTableSchemaTestSuite to leverage common testing functionality.
    """

    # Attributes #
    UnitTestClass: type[BaseMetaInformationTableSchema]

    # Instance Methods #
    # Helper Methods
    def generate_item(self) -> dict[str, Any]:
        """Generates a test item.

        Returns:
            A dictionary representing the test item.
        """
        return {"id": UUID(int=1)}

    def generate_update_item(self) -> dict[str, Any]:
        """Generates an update item.

        Returns:
            A dictionary representing the update item.
        """
        return {"id": UUID(int=1)}

    # Tests #
    def test_create_meta_information(self) -> None:
        """Tests the create_meta_information method."""
        item = self.generate_item()
        db_engine = self.create_engine()
        try:
            cls = self.UnitTestClass
            with Session(db_engine) as session:
                cls.create_meta_information(session, **item)
                session.commit()

                # Verify
                fetched = session.get(cls, item["id"])
                for k, v in item.items():
                    assert getattr(fetched, k) == v
        finally:
            db_engine.dispose()

    @pytest.mark.asyncio
    async def test_create_meta_information_async(self) -> None:
        """Tests the create_meta_information_async method."""
        item = self.generate_item()
        db_engine = await self.create_async_engine()
        try:
            cls = self.UnitTestClass
            async with AsyncSession(db_engine) as session:
                await cls.create_meta_information_async(session, **item)
                await session.commit()

                # Verify
                fetched = await session.get(cls, item["id"])
                for k, v in item.items():
                    assert getattr(fetched, k) == v
        finally:
            await db_engine.dispose()

    def test_get_meta_information(self) -> None:
        """Tests the get_meta_information method."""
        item = self.generate_item()
        db_engine = self.create_engine()
        try:
            cls = self.UnitTestClass
            with Session(db_engine) as session:
                session.add(cls(**item))
                session.commit()

                info = cls.get_meta_information(session)
                assert isinstance(info, dict)
                for k, v in item.items():
                    assert info[k] == v
        finally:
            db_engine.dispose()

    @pytest.mark.asyncio
    async def test_get_meta_information_async(self) -> None:
        """Tests the get_meta_information_async method."""
        item = self.generate_item()
        db_engine = await self.create_async_engine()
        try:
            cls = self.UnitTestClass
            async with AsyncSession(db_engine) as session:
                session.add(cls(**item))
                await session.commit()

                info = await cls.get_meta_information_async(session)
                assert isinstance(info, dict)
                for k, v in item.items():
                    assert info[k] == v
        finally:
            await db_engine.dispose()

    @pytest.mark.skip(reason="not implemented")
    def test_set_meta_information(self) -> None:
        """Tests the set_meta_information method."""

    @pytest.mark.skip(reason="not implemented")
    @pytest.mark.asyncio
    async def test_set_meta_information_async(self) -> None:
        """Tests the set_meta_information_async method."""


class MetaInformationTableManifestationTestSuite(SingletonTableManifestationTestSuite):
    """A Testsuite for the MetaInformationTableManifestation class.

    This class tests the functionality of the MetaInformationTableManifestation class. It inherits from
    SingletonTableTestSuite to leverage common testing functionality.
    """

    # Attributes #
    UnitTestClass: type[MetaInformationTableManifestation] = MetaInformationTableManifestation
    db_schema: type[DeclarativeBase]
    table_schema: type[BaseMetaInformationTableSchema]

    # Instance Methods #
    def generate_item(self) -> dict[str, Any]:
        """Generates a test item.

        Returns:
            A dictionary representing the test item.
        """
        return {"id": UUID(int=1)}

    def generate_update_item(self) -> dict[str, Any]:
        """Generates an update item.

        Returns:
            A dictionary representing the update item.
        """
        return {"id": UUID(int=1)}

    # Fixtures #
    @pytest.fixture
    def test_object(self, database: Database) -> MetaInformationTableManifestation:
        """Creates a test object.

        Args:
            database: The database fixture.

        Returns:
            MetaInformationTableManifestation: A MetaInformationTableManifestation instance for testing.
        """
        return self.UnitTestClass(table_schema=self.table_schema, database=database)  # type: ignore

    # Tests #
    def test_init_no_init(self, test_object: MetaInformationTableManifestation) -> None:
        """Tests initialization with init=False."""
        init_info = self.generate_item()
        obj = self.UnitTestClass(
            table_schema=self.table_schema,  # type: ignore
            database=test_object.database,
            init_info=init_info,
            init=False,
        )
        assert obj._meta_information != init_info
        assert obj._meta_information == {}

    def test_construct_with_init_info(self, test_object: MetaInformationTableManifestation) -> None:
        """Tests the construct method with init_info."""
        init_info = self.generate_item()
        test_object.construct(init_info=init_info)
        assert test_object._meta_information == init_info

    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_create_meta_information(
        self, test_object: MetaInformationTableManifestation, use_session: bool, begin: bool
    ) -> None:
        """Tests the create_meta_information method."""
        item = self.generate_item()
        test_object.database.create_database()

        session = None
        if use_session:
            session = test_object.create_session()

        try:
            test_object.create_meta_information(item=item, session=session, begin=begin)
            if session is not None:
                session.commit()

            info = test_object.get_meta_information(session=session)
            assert isinstance(info, dict)
            for k, v in item.items():
                assert info[k] == v
        finally:
            if session:
                session.close()
            test_object.database.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_create_meta_information_async(
        self, test_object: MetaInformationTableManifestation, use_session: bool, begin: bool
    ) -> None:
        """Tests the create_meta_information_async method."""
        item = self.generate_item()
        await test_object.database.create_database_async()

        session = None
        if use_session:
            session = test_object.create_async_session()

        try:
            await test_object.create_meta_information_async(item=item, session=session, begin=begin)
            if session is not None:
                await session.commit()

            info = await test_object.get_meta_information_async(session=session)
            assert isinstance(info, dict)
            for k, v in item.items():
                assert info[k] == v
        finally:
            if session:
                await session.close()
            await test_object.database.close_async()

    def test_get_meta_information_empty(self, test_object: MetaInformationTableManifestation) -> None:
        """Tests getting meta information when table is empty."""
        test_object.database.create_database()

        # Test as_python=False returns None when empty
        info = test_object.get_meta_information(as_python=False)
        assert info is None

        # Test as_python=True returns empty dict
        info_dict = test_object.get_meta_information(as_python=True)
        assert info_dict == {}

        test_object.database.close()

    @pytest.mark.asyncio
    async def test_get_meta_information_async_empty(self, test_object: MetaInformationTableManifestation) -> None:
        """Tests getting meta information asynchronously when table is empty."""
        await test_object.database.create_database_async()

        # Test as_python=False returns None when empty
        info = await test_object.get_meta_information_async(as_python=False)
        assert info is None

        # Test as_python=True returns empty dict
        info_dict = await test_object.get_meta_information_async(as_python=True)
        assert info_dict == {}

        await test_object.database.close_async()

    @pytest.mark.parametrize("use_session", [True, False])
    def test_get_meta_information(self, test_object: MetaInformationTableManifestation, use_session: bool) -> None:
        """Tests the get_meta_information method."""
        item = self.generate_item()
        test_object.database.create_database()
        test_object.create_meta_information(item=item)

        session = None
        if use_session:
            session = test_object.create_session()

        try:
            info = test_object.get_meta_information(session=session)
            assert isinstance(info, dict)
            for k, v in item.items():
                assert info[k] == v
        finally:
            if session:
                session.close()
            test_object.database.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    async def test_get_meta_information_async(
        self, test_object: MetaInformationTableManifestation, use_session: bool
    ) -> None:
        """Tests the get_meta_information_async method."""
        item = self.generate_item()
        await test_object.database.create_database_async()
        await test_object.create_meta_information_async(item=item)

        session = None
        if use_session:
            session = test_object.create_async_session()

        try:
            info = await test_object.get_meta_information_async(session=session)
            assert isinstance(info, dict)
            for k, v in item.items():
                assert info[k] == v
        finally:
            if session:
                await session.close()
            await test_object.database.close_async()

    def test_get_meta_information_as_schema(self, test_object: MetaInformationTableManifestation) -> None:
        """Tests the get_meta_information method returning schema."""
        item = self.generate_item()
        test_object.database.create_database()
        test_object.create_meta_information(item=item)

        info = test_object.get_meta_information(as_python=False)
        assert isinstance(info, BaseMetaInformationTableSchema)
        for k, v in item.items():
            assert getattr(info, k) == v

        test_object.database.close()

    @pytest.mark.asyncio
    async def test_get_meta_information_async_as_schema(self, test_object: MetaInformationTableManifestation) -> None:
        """Tests the get_meta_information_async method returning schema."""
        item = self.generate_item()
        await test_object.database.create_database_async()
        await test_object.create_meta_information_async(item=item)

        info = await test_object.get_meta_information_async(as_python=False)
        assert isinstance(info, BaseMetaInformationTableSchema)
        for k, v in item.items():
            assert getattr(info, k) == v

        await test_object.database.close_async()

    def test_meta_information_property(self, test_object: MetaInformationTableManifestation) -> None:
        """Tests the meta_information property."""
        item = self.generate_item()
        test_object.database.create_database()
        test_object.create_meta_information(item=item)

        # Test property access (should trigger load)
        for k, v in item.items():
            assert test_object.meta_information[k] == v
        test_object.database.close()

    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_set_meta_information(
        self, test_object: MetaInformationTableManifestation, use_session: bool, begin: bool
    ) -> None:
        """Tests the set_meta_information method."""
        item = self.generate_item()
        update_item = self.generate_update_item()
        test_object.database.create_database()
        test_object.create_meta_information(item=item)

        session = None
        if use_session:
            session = test_object.create_session()

        try:
            update_data = update_item.copy()
            if "id" in update_data:
                del update_data["id"]

            test_object.set_meta_information(item=update_data, session=session, begin=begin)
            if session is not None:
                session.commit()

            info = test_object.get_meta_information(session=session)
            assert isinstance(info, dict)
            for k, v in update_data.items():
                assert info[k] == v
        finally:
            if session:
                session.close()
            test_object.database.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_set_meta_information_async(
        self, test_object: MetaInformationTableManifestation, use_session: bool, begin: bool
    ) -> None:
        """Tests the set_meta_information_async method."""
        item = self.generate_item()
        update_item = self.generate_update_item()
        await test_object.database.create_database_async()
        await test_object.create_meta_information_async(item=item)

        session = None
        if use_session:
            session = test_object.create_async_session()

        try:
            update_data = update_item.copy()
            if "id" in update_data:
                del update_data["id"]

            await test_object.set_meta_information_async(item=update_data, session=session, begin=begin)
            if session is not None:
                await session.commit()

            info = await test_object.get_meta_information_async(session=session)
            assert isinstance(info, dict)
            for k, v in update_data.items():
                assert info[k] == v
        finally:
            if session:
                await session.close()
            await test_object.database.close_async()

    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    def test_save_cached_meta_information(
        self, test_object: MetaInformationTableManifestation, use_session: bool, begin: bool
    ) -> None:
        """Tests the save_cached_meta_information method."""
        item = self.generate_item()
        update_item = self.generate_update_item()
        test_object.database.create_database()
        test_object.create_meta_information(item=item)

        # Ensure loaded
        _ = test_object.meta_information

        # Modify cache
        update_data = update_item.copy()
        if "id" in update_data:
            del update_data["id"]
        test_object.meta_information.update(update_data)

        session = None
        if use_session:
            session = test_object.create_session()

        try:
            test_object.save_cached_meta_information(session=session, begin=begin)
            if session is not None:
                session.commit()

            # Reload from DB to verify persistence
            with test_object.create_session() as s:
                info = test_object.get_meta_information(session=s)
                assert isinstance(info, dict)
                for k, v in update_data.items():
                    assert info[k] == v
        finally:
            if session:
                session.close()
            test_object.database.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    @pytest.mark.parametrize("begin", [True, False])
    async def test_save_cached_meta_information_async(
        self, test_object: MetaInformationTableManifestation, use_session: bool, begin: bool
    ) -> None:
        """Tests the save_cached_meta_information_async method."""
        item = self.generate_item()
        update_item = self.generate_update_item()
        await test_object.database.create_database_async()
        await test_object.create_meta_information_async(item=item)

        # Ensure loaded
        _ = await test_object.get_meta_information_async()

        # Modify cache
        update_data = update_item.copy()
        if "id" in update_data:
            del update_data["id"]
        test_object.meta_information.update(update_data)

        session = None
        if use_session:
            session = test_object.create_async_session()

        try:
            await test_object.save_cached_meta_information_async(session=session, begin=begin)
            if session is not None:
                await session.commit()

            # Reload from DB to verify persistence
            async with test_object.create_async_session() as s:
                info = await test_object.get_meta_information_async(session=s)
                assert isinstance(info, dict)
                for k, v in update_data.items():
                    assert info[k] == v
        finally:
            if session:
                await session.close()
            await test_object.database.close_async()


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])

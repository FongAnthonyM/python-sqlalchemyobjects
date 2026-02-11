"""singletontabletestsuite.py
Test suites for the singleton table manifestations and schemas.
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
from ..tables.base.singletontable import BaseSingletonTableSchema, SingletonTableManifestation
from .basetabletestsuite import BaseTableManifestationTestSuite, BaseTableSchemaTestSuite


# Definitions #
# Classes #
class SingletonTableSchemaTestSuite(BaseTableSchemaTestSuite):
    """A Testsuite for the BaseSingletonTableSchema class.

    This class tests the functionality of the BaseSingletonTableSchema class. It inherits from
    BaseTableSchemaTestSuite to leverage common testing functionality.
    """

    # Attributes #
    UnitTestClass: type[BaseSingletonTableSchema]  # type: ignore[assignment]

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
    def test_create_item(self) -> None:
        """Tests the create_item method."""
        item = self.generate_item()
        update_item = self.generate_update_item()

        db_engine = self.create_engine()
        try:
            cls = self.UnitTestClass
            with Session(db_engine) as session:
                # Create
                cls.create_item(session, **item)
                session.commit()

                # Verify Create
                fetched = session.get(cls, item["id"])
                for k, v in item.items():
                    assert getattr(fetched, k) == v

                # Update
                cls.create_item(session, **update_item)
                session.commit()

                # Verify Update
                session.expire(fetched)
                fetched = session.get(cls, update_item["id"])
                for k, v in update_item.items():
                    assert getattr(fetched, k) == v
        finally:
            db_engine.dispose()

    @pytest.mark.asyncio
    async def test_create_item_async(self) -> None:
        """Tests the create_item_async method."""
        item = self.generate_item()
        update_item = self.generate_update_item()

        db_engine = await self.create_async_engine()
        try:
            cls = self.UnitTestClass
            async with AsyncSession(db_engine) as session:
                # Create
                await cls.create_item_async(session, **item)
                await session.commit()

                # Verify Create
                fetched = await session.get(cls, item["id"])
                for k, v in item.items():
                    assert getattr(fetched, k) == v

                # Update
                await cls.create_item_async(session, **update_item)
                await session.commit()

                # Verify Update
                session.expire(fetched)
                fetched = await session.get(cls, update_item["id"])
                for k, v in update_item.items():
                    assert getattr(fetched, k) == v
        finally:
            await db_engine.dispose()

    def test_get_item(self) -> None:
        """Tests the get_item method."""
        item = self.generate_item()

        db_engine = self.create_engine()
        try:
            cls = self.UnitTestClass
            with Session(db_engine) as session:
                session.add(cls(**item))
                session.commit()

                fetched_dict = cls.get_item(session)
                assert isinstance(fetched_dict, dict)
                for k, v in item.items():
                    assert fetched_dict[k] == v
        finally:
            db_engine.dispose()

    @pytest.mark.asyncio
    async def test_get_item_async(self) -> None:
        """Tests the get_item_async method."""
        item = self.generate_item()

        db_engine = await self.create_async_engine()
        try:
            cls = self.UnitTestClass
            async with AsyncSession(db_engine) as session:
                session.add(cls(**item))
                await session.commit()

                fetched_dict = await cls.get_item_async(session)
                assert isinstance(fetched_dict, dict)
                for k, v in item.items():
                    assert fetched_dict[k] == v
        finally:
            await db_engine.dispose()

    @pytest.mark.skip(reason="not implemented")
    def test_set_item(self) -> None:
        """Tests the set_item method."""

    @pytest.mark.skip(reason="not implemented")
    @pytest.mark.asyncio
    async def test_set_item_async(self) -> None:
        """Tests the set_item_async method."""


class SingletonTableManifestationTestSuite(BaseTableManifestationTestSuite):
    """A Testsuite for the SingletonTableManifestation class.

    This class tests the functionality of the SingletonTableManifestation class. It inherits from
    BaseTableManifestationTestSuite to leverage common testing functionality.
    """

    # Attributes #
    UnitTestClass: type[SingletonTableManifestation] = SingletonTableManifestation
    db_schema: type[DeclarativeBase]
    table_schema: type[BaseSingletonTableSchema]  # type: ignore[assignment]

    # Helper Methods #
    def create_new_table_manifestation(self, **kwargs: Any) -> SingletonTableManifestation:
        """Creates a new table manifestation.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            The new table manifestation.
        """
        return super().create_new_table_manifestation(**kwargs)  # type: ignore

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
    @pytest.mark.parametrize("use_session", [True, False])
    def test_create_item(self, database: Database, use_session: bool) -> None:
        """Tests the create_item method."""
        item = self.generate_item()
        update_item = self.generate_update_item()

        table = self.create_new_table_manifestation(database=database)
        table.database.create_database()

        session = None
        if use_session:
            session = table.create_session()

        try:
            # Create
            table.create_item(item=item, session=session)
            if session is not None:
                session.commit()

            # Verify
            fetched_dict = table.get_item(session=session)
            assert isinstance(fetched_dict, dict)
            for k, v in item.items():
                assert fetched_dict[k] == v

            # Update
            table.create_item(item=update_item, session=session)
            if session is not None:
                session.commit()

            fetched_dict = table.get_item(session=session)
            assert isinstance(fetched_dict, dict)
            for k, v in update_item.items():
                assert fetched_dict[k] == v

        finally:
            if session:
                session.close()
            table.database.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    async def test_create_item_async(self, database: Database, use_session: bool) -> None:
        """Tests the create_item_async method."""
        item = self.generate_item()
        update_item = self.generate_update_item()

        table = self.create_new_table_manifestation(database=database)
        await table.database.create_database_async()

        session = None
        if use_session:
            session = table.create_async_session()

        try:
            # Create
            await table.create_item_async(item=item, session=session)
            if session is not None:
                await session.commit()

            # Verify
            fetched_dict = await table.get_item_async(session=session)
            assert isinstance(fetched_dict, dict)
            for k, v in item.items():
                assert fetched_dict[k] == v

            # Update
            await table.create_item_async(item=update_item, session=session)
            if session is not None:
                await session.commit()

            fetched_dict = await table.get_item_async(session=session)
            assert isinstance(fetched_dict, dict)
            for k, v in update_item.items():
                assert fetched_dict[k] == v

        finally:
            if session:
                await session.close()
            await table.database.close_async()

    @pytest.mark.parametrize("use_session", [True, False])
    def test_get_item(self, database: Database, use_session: bool) -> None:
        """Tests the get_item method."""
        item = self.generate_item()

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
            fetched_dict = table.get_item(session=session)
            assert isinstance(fetched_dict, dict)
            for k, v in item.items():
                assert fetched_dict[k] == v
        finally:
            if session:
                session.close()
            table.database.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    async def test_get_item_async(self, database: Database, use_session: bool) -> None:
        """Tests the get_item_async method."""
        item = self.generate_item()

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
            fetched_dict = await table.get_item_async(session=session)
            assert isinstance(fetched_dict, dict)
            for k, v in item.items():
                assert fetched_dict[k] == v
        finally:
            if session:
                await session.close()
            await table.database.close_async()

    @pytest.mark.skip(reason="not implemented")
    @pytest.mark.parametrize("use_session", [True, False])
    def test_set_item(self, database: Database, use_session: bool) -> None:
        """Tests the set_item method.

        Args:
            database: The database fixture.
            use_session: Whether to use a session.
        """

    @pytest.mark.skip(reason="not implemented")
    @pytest.mark.asyncio
    @pytest.mark.parametrize("use_session", [True, False])
    async def test_set_item_async(self, database: Database, use_session: bool) -> None:
        """Tests the set_item_async method.

        Args:
            database: The database fixture.
            use_session: Whether to use a session.
        """


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])

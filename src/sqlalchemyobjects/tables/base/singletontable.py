"""singletontable.py
Classes for a table with stores a single item in an SQLAlchemy ORM model.

This module contains the classes for outlining singleton class tables to be used in a SQLAlchemy ORM model. A singleton
table is a table that contains only one entry.
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

# Third-Party Packages #
from sqlalchemy import lambda_stmt, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

# Local Packages #
from .basetable import BaseTableSchema, TableManifestation


# Definitions #
# Classes #
class BaseSingletonTableSchema(BaseTableSchema):
    """A table schema for storing a single item (row) in an SQLAlchemy ORM model. An instance is the row in the table.

    Attributes:
        __tablename__: The name of the table.
        id: The primary key column of the table, using UUIDs.
    """

    # Class Attributes #
    __tablename__ = "basesingleton"

    # Class Methods #
    @classmethod
    def create_item(
        cls,
        session: Session,
        item: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Creates or updates the single item in the table.

        If an item already exists, it updates the item; otherwise, it inserts a new item.

        Args:
            session: The SQLAlchemy session to use for the operation.
            item: A dictionary representing the item to create or update. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the item.
        """
        if item is None:
            item = {}
        item.update(kwargs)

        if begin:
            with session.begin():
                result = session.execute(lambda_stmt(lambda: select(cls))).scalar()
                if result is None:
                    cls.insert(session=session, item=item, as_dict=True, begin=False)
                else:
                    result.update_instance(item)
        else:
            result = session.execute(lambda_stmt(lambda: select(cls))).scalar()
            if result is None:
                cls.insert(session=session, item=item, as_dict=True, begin=False)
            else:
                result.update_instance(item)

    @classmethod
    async def create_item_async(
        cls,
        session: AsyncSession,
        item: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously creates or updates the single item in the table.

        If an item already exists, it updates the item; otherwise, it inserts a new item.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            item: A dictionary representing the item to create or update. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the item.
        """
        if item is None:
            item = {}
        item.update(kwargs)

        statement = lambda_stmt(lambda: select(cls))
        if begin:
            async with session.begin():
                result = (await session.execute(statement)).scalar()
                if result is None:
                    await cls.insert_async(session=session, item=item, as_dict=True, begin=False)
                else:
                    result.update_instance(item)
        else:
            result = (await session.execute(statement)).scalar()
            if result is None:
                await cls.insert_async(session=session, item=item, as_dict=True, begin=False)
            else:
                result.update_instance(item)

    @classmethod
    def get_item(
        cls,
        session: Session,
        as_python: bool = True,
    ) -> dict[str, Any] | BaseSingletonTableSchema | None:
        """Retrieves the item from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns the item as a dictionary; otherwise, returns the table object. Defaults to True.

        Returns:
            The item, either as a dictionary or as a table object.
        """
        obj = session.execute(lambda_stmt(lambda: select(cls))).scalar()
        return (obj.as_python_dict() if as_python else obj) if obj is not None else None

    @classmethod
    async def get_item_async(
        cls,
        session: AsyncSession,
        as_python: bool = True,
    ) -> dict[str, Any] | BaseSingletonTableSchema | None:
        """Asynchronously retrieves the single item from the table.

        Args:
            session: The SQLAlchemy async session to use for the query.
            as_python: If True, returns the item as a dictionary; otherwise, returns the table object. Defaults to True.

        Returns:
            The item, either as a dictionary or as a table object.
        """
        obj = (await session.execute(lambda_stmt(lambda: select(cls)))).scalar()
        return (await obj.as_python_dict_async() if as_python else obj) if obj is not None else None

    @classmethod
    def set_item(
        cls,
        session: Session,
        item: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Sets the single item in the table.

        Updates the existing item with the provided information.

        Args:
            session: The SQLAlchemy session to use for the operation.
            item: A dictionary representing the item to update. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the item.
        """
        if item is None:
            item = {}
        item.update(kwargs)

        if begin:
            with session.begin():
                if (item_obj := session.execute(lambda_stmt(lambda: select(cls))).scalar()) is not None:
                    item_obj.update_instance(item)
                else:
                    cls.insert(session=session, item=item, as_dict=True, begin=False)
        else:
            if (item_obj := session.execute(lambda_stmt(lambda: select(cls))).scalar()) is not None:
                item_obj.update_instance(item)
            else:
                cls.insert(session=session, item=item, as_dict=True, begin=False)

    @classmethod
    async def set_item_async(
        cls,
        session: AsyncSession,
        item: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously sets the single item in the table.

        Updates the existing item with the provided information.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            item: A dictionary representing the item to update. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the item.
        """
        if item is None:
            item = {}
        item.update(kwargs)

        statement = lambda_stmt(lambda: select(cls))
        if begin:
            async with session.begin():
                if (item_obj := (await session.execute(statement)).scalar()) is not None:
                    item_obj.update_instance(item)
                else:
                    await cls.insert_async(session=session, item=item, as_dict=True, begin=False)
        else:
            if (item_obj := (await session.execute(statement)).scalar()) is not None:
                item_obj.update_instance(item)
            else:
                await cls.insert_async(session=session, item=item, as_dict=True, begin=False)


class SingletonTableManifestation(TableManifestation):
    """An interface for a singleton table implemented in an SQLAlchemy database.

    Attributes:
        _database: A weak reference to the SQAlchemy database to interface with.
        table_schema: The SQLAlchemy declarative table which this object act as the interface for.
    """

    # Attributes #
    table_schema: type[BaseSingletonTableSchema]

    # Instance Methods #
    # Table
    def create_item(
        self,
        item: dict[str, Any] | None = None,
        session: Session | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Creates or updates the single item in the table.

        If an item already exists, it updates the item; otherwise, it inserts a new item.

        Args:
            item: A dictionary representing the item to create or update. Defaults to None.
            session: The SQLAlchemy session to use for the operation.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the item.
        """
        if session is not None:
            self.table_schema.create_item(session, item, begin=begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table_schema.create_item(session, item, begin=True, **kwargs)

    async def create_item_async(
        self,
        item: dict[str, Any] | None = None,
        session: AsyncSession | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously creates or updates the single item in the table.

        If an item already exists, it updates the item; otherwise, it inserts a new item.

        Args:
            item: A dictionary representing the item to create or update. Defaults to None.
            session: The SQLAlchemy async session to use for the operation.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the item.
        """
        if session is not None:
            await self.table_schema.create_item_async(session, item, begin=begin, **kwargs)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.create_item_async(session, item, begin=True, **kwargs)

    def get_item(
        self,
        session: Session | None = None,
        as_python: bool = True,
    ) -> dict[str, Any] | BaseSingletonTableSchema | None:
        """Retrieves the item from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns the item as a dictionary; otherwise, returns the table object. Defaults to True.

        Returns:
            The item, either as a dictionary or as a table object.
        """
        if session is not None:
            return self.table_schema.get_item(session, as_python=as_python)
        else:
            with self.create_session() as session:
                return self.table_schema.get_item(session, as_python=as_python)

    async def get_item_async(
        self,
        session: AsyncSession | None = None,
        as_python: bool = True,
    ) -> dict[str, Any] | BaseSingletonTableSchema | None:
        """Asynchronously retrieves the single item from the table.

        Args:
            session: The SQLAlchemy async session to use for the query.
            as_python: If True, returns the item as a dictionary; otherwise, returns the table object. Defaults to True.

        Returns:
            The item, either as a dictionary or as a table object.
        """
        if session is not None:
            return await self.table_schema.get_item_async(session, as_python=as_python)
        else:
            async with self.create_async_session() as session:
                return await self.table_schema.get_item_async(session, as_python=as_python)

    def set_item(
        self,
        item: dict[str, Any] | None = None,
        session: Session | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Sets the single item in the table.

        Updates the existing item with the provided information.

        Args:
            item: A dictionary representing the item to update. Defaults to None.
            session: The SQLAlchemy session to use for the operation.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the item.
        """
        if session is not None:
            self.table_schema.set_item(session, item, begin=begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table_schema.set_item(session, item, begin=True, **kwargs)

    async def set_item_async(
        self,
        item: dict[str, Any] | None = None,
        session: AsyncSession | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously sets the single item in the table.

        Updates the existing item with the provided information.

        Args:
            item: A dictionary representing the item to update. Defaults to None.
            session: The SQLAlchemy async session to use for the operation.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the item.
        """
        if session is not None:
            await self.table_schema.set_item_async(session, item, begin=begin, **kwargs)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.set_item_async(session, item, begin=True, **kwargs)

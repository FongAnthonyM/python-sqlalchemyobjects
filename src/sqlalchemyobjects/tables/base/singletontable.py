"""singletontable.py
Classes for a table with stores a single item in an SQLAlchemy ORM model.
"""
# Package Header #
from ...header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
from typing import Any, Union

# Third-Party Packages #
from sqlalchemy import select, lambda_stmt
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

# Local Packages #
from .basetable import BaseTableSchema, TableManifestation


# Definitions #
# Classes #
class BaseSingletonTableSchema(BaseTableSchema):
    """A schema for a table with stores a single item in an SQLAlchemy ORM model.

    Class Attributes:
        __tablename__: The name of the table.
        __mapper_args__: Mapper arguments for SQLAlchemy ORM configurations.

    Columns:
        id: The primary key column of the table, using UUIDid: The primary key column of the table, using UUIDs.
    """

    # Class Attributes #
    __tablename__ = "basesingleton"
    __mapper_args__ = {"polymorphic_identity": "basesingleton"}

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
        if begin:
            with session.begin():
                result = session.execute(lambda_stmt(lambda: select(cls))).scalar()
                if result is None:
                    cls.insert(session=session, item=item, as_dict=True, begin=False, **kwargs)
                else:
                    result.update(item, **kwargs)
        else:
            result = session.execute(lambda_stmt(lambda: select(cls))).scalar()
            if result is None:
                cls.insert(session=session, item=item, as_dict=True, begin=False, **kwargs)
            else:
                result.update(item, **kwargs)

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
        statement = lambda_stmt(lambda: select(cls))
        if begin:
            async with session.begin():
                result = (await session.execute(statement)).scalar()
                if result is None:
                    await cls.insert_async(session=session, item=item, as_dict=True, begin=False, **kwargs)
                else:
                    result.update(item, **kwargs)
        else:
            result = (await session.execute(statement)).scalar()
            if result is None:
                await cls.insert_async(session=session, item=item, as_dict=True, begin=False, **kwargs)
            else:
                result.update(item, **kwargs)

    @classmethod
    def get_item(
        cls,
        session: Session,
        as_python: bool = True,
    ) -> Union[dict[str, Any], "BaseSingletonTableSchema", None]:
        """Retrieves the item from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns the item as a dictionary; otherwise, returns the table object. Defaults to True.

        Returns:
            Union[dict[str, Any], BaseSingletonTableSchema]: The item, either as a dictionary or as a table object.
        """
        obj = session.execute(lambda_stmt(lambda: select(cls))).scalar()
        return (obj.as_python_dict() if as_python else obj) if obj is not None else None

    @classmethod
    async def get_item_async(
        cls,
        session: AsyncSession,
        as_python: bool = True,
    ) -> Union[dict[str, Any], "BaseSingletonTableSchema", None]:
        """Asynchronously retrieves the single item from the table.

        Args:
            session: The SQLAlchemy async session to use for the query.
            as_python: If True, returns the item as a dictionary; otherwise, returns the table object. Defaults to True.

        Returns:
            Union[dict[str, Any], BaseSingletonTableSchema]: The item, either as a dictionary or as a table object.
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
        if begin:
            with session.begin():
                session.execute(lambda_stmt(lambda: select(cls))).scalar().update(item, **kwargs)
        else:
            session.execute(lambda_stmt(lambda: select(cls))).scalar().update(item, **kwargs)

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
        statement = lambda_stmt(lambda: select(cls))
        if begin:
            async with session.begin():
                (await session.execute(statement)).scalar().update(item, **kwargs)
        else:
            (await session.execute(statement)).scalar().update(item, **kwargs)


class SingletonTableManifestation(TableManifestation):
    """The manifestation of a SingletonTable.

    Attributes:
        _database: A weak reference to the SQAlchemy database to interface with.
        table_schema: The SQLAlchemy declarative table which this object act as the interface for.

    Args:
        table_schema: The SQLAlchemy declarative table which this object act as the interface for.
        database: The SQAlchemy database to interface with.
        init: Determines if this object will construct.
        **kwargs: Additional keyword arguments.
    """

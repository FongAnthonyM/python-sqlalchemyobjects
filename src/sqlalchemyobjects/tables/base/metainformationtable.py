"""metainformationtable.py
Classes for storing meta-information in a SQLAlchemy ORM model.
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
from typing import Any, Optional, Union

# Third-Party Packages #
from sqlalchemy.orm import Session, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession

# Local Packages #
from .singletontable import BaseSingletonTableSchema, SingletonTableManifestation


# Definitions #
# Classes #
class BaseMetaInformationTableSchema(BaseSingletonTableSchema):
    """A schema for a table for storing meta-information in a SQLAlchemy ORM model.

    This class extends the BaseTable class and provides additional methods for creating, retrieving, and updating
    meta-information entries in the table.

    Class Attributes:
        __tablename__: The name of the table.
        __mapper_args__: Mapper arguments for SQLAlchemy ORM configurations.
    """

    # Class Attributes #
    __tablename__ = "metainformation"
    __mapper_args__ = {"polymorphic_identity": "metainformation"}

    # Class Methods #
    @classmethod
    def create_information(
        cls,
        session: Session,
        item: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Creates or updates meta-information in the table.

        If an item already exists, it updates the item; otherwise, it inserts a new item.

        Args:
            session: The SQLAlchemy session to use for the operation.
            item: A dictionary representing the item to create or update. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the item.
        """
        cls.create_item(session=session, item=item, begin=begin, **kwargs)

    @classmethod
    async def create_information_async(
        cls,
        session: AsyncSession,
        item: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously creates or updates meta-information in the table.

        If an item already exists, it updates the item; otherwise, it inserts a new item.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            item: A dictionary representing the item to create or update. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the item.
        """
        await cls.create_item_async(session=session, item=item, begin=begin, **kwargs)

    @classmethod
    def get_information(
        cls,
        session: Session,
        as_python: bool = True,
    ) -> Union[dict[str, Any], "BaseSingletonTableSchema"]:
        """Retrieves meta-information from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns the item as a dictionary; otherwise, returns the table object. Defaults to True.

        Returns:
            Union[dict[str, Any], BaseMetaInformationTableSchema]: The meta-information item, either as a dictionary or as a table object.
        """
        return cls.get_item(session=session, as_python=as_python)

    @classmethod
    async def get_information_async(
        cls,
        session: AsyncSession,
        as_python: bool = True,
    ) -> Union[dict[str, Any], "BaseSingletonTableSchema"]:
        """Asynchronously retrieves meta-information from the table.

        Args:
            session: The SQLAlchemy async session to use for the query.
            as_python: If True, returns the item as a dictionary; otherwise, returns the table object. Defaults to True.

        Returns:
            Union[dict[str, Any], BaseMetaInformationTableSchema]: The meta-information item, either as a dictionary or as a table object.
        """
        return await cls.get_item_async(session=session, as_python=as_python)

    @classmethod
    def set_information(
        cls,
        session: Session,
        item: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Sets meta-information in the table.

        Updates the existing item with the provided information.

        Args:
            session: The SQLAlchemy session to use for the operation.
            item: A dictionary representing the item to update. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the item.
        """
        cls.set_item(session=session, item=item, begin=begin, **kwargs)

    @classmethod
    async def set_information_async(
        cls,
        session: AsyncSession,
        item: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously sets meta-information in the table.

        Updates the existing item with the provided information.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            item: A dictionary representing the item to update. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the item.
        """
        await cls.set_item_async(session=session, item=item, begin=begin, **kwargs)


class MetaInformationTableManifestation(SingletonTableManifestation):
    """The manifestation of a MetaInformationTable.

    Attributes:
        _database: A weak reference to the SQAlchemy database to interface with.
        table_schema: The SQLAlchemy declarative table which this object act as the interface for.
        _meta_information: Cached meta-information.

    Args:
        table_schema: The SQLAlchemy declarative table which this object act as the interface for.
        database: The SQAlchemy database to interface with.
        init_info: Initial meta-information.
        init: Determines if this object will construct.
        **kwargs: Additional keyword arguments.
    """

    # Attributes #
    _meta_information: dict[str, Any] = {}

    # Properties #
    @property
    def meta_information(self) -> dict[str, Any]:
        """Gets the meta-information.

        Returns:
            dict[str, Any]: The meta-information.
        """
        if not self._meta_information:
            self.get_meta_information()
        return self._meta_information

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        table_schema: type[DeclarativeBase] | None = None,
        database: Optional["BaseDatabase"] = None,
        init_info: dict[str, Any] | None = None,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # Attributes #
        self._meta_information = self._meta_information.copy()

        # Parent Attributes #
        super().__init__(init=False)

        # Object Construction #
        if init:
            self.construct(table_schema, database, **kwargs)

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        table_schema: Any = None,
        database: str | None = None,
        init_info: dict[str, Any] | None = None,
        **kwargs: dict[str, Any] | None,
    ) -> None:
        """Constructs this object.

        Args:
            table_schema: The object which this object is a component of.
            table_name: The name of the table.
            init_info: Initial meta-information.
            **kwargs: Additional keyword arguments.
        """
        if init_info is not None:
            self._meta_information.update(init_info)

        super().construct(table_schema, database, **kwargs)

    def build(self, *args: Any, **kwargs: Any) -> None:
        """Builds the table."""
        self.create_meta_information(item=self._meta_information, begin=True)

    def load(self, *args: Any, **kwargs: Any) -> None:
        """Loads the component."""
        self.get_meta_information()

    # Meta Information
    def create_meta_information(
        self,
        session: Session | None = None,
        item: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Creates meta-information in the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            item: The meta-information item to create.
            begin: If True, begins a transaction for the operation.
            **kwargs: Additional keyword arguments.
        """
        if session is not None:
            self.table_schema.create_information(session=session, item=item, begin=begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table_schema.create_information(session=session, item=item, begin=True, **kwargs)

    async def create_meta_information_async(
        self,
        session: AsyncSession | None = None,
        item: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously creates meta-information in the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            item: The meta-information item to create.
            begin: If True, begins a transaction for the operation.
            **kwargs: Additional keyword arguments.
        """
        if session is not None:
            await self.table_schema.create_information_async(
                session=session,
                item=item,
                begin=begin,
                **kwargs,
            )
        else:
            async with self.create_async_session() as session:
                await self.table_schema.create_information_async(
                    session=session,
                    item=item,
                    begin=begin,
                    **kwargs,
                )

    def get_meta_information(
        self,
        session: Session | None = None,
        as_python: bool = True,
    ) -> dict[str, Any] | BaseMetaInformationTableSchema:
        """Gets meta-information from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns the meta-information as a dictionary.

        Returns:
            dict[str, Any] | BaseMetaInformationTableSchema: The meta-information.
        """
        if session is not None:
            _meta_information = self.table_schema.get_information(session, as_python=False)
        else:
            with self.create_session() as session:
                _meta_information = self.table_schema.get_information(session, as_python=False)

        self._meta_information.update(_meta_information.as_python_dict())
        return self._meta_information.copy() if as_python else _meta_information

    async def get_meta_information_async(
        self,
        session: AsyncSession | None = None,
        as_python: bool = True,
    ) -> dict[str, Any] | BaseMetaInformationTableSchema:
        """Asynchronously gets meta-information from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns the meta-information as a dictionary.

        Returns:
            dict[str, Any] | BaseMetaInformationTableSchema: The meta-information.
        """
        if session is not None:
            _meta_information = await self.table_schema.get_information_async(session, as_python=False)
        else:
            async with self.create_async_session() as session:
                _meta_information = await self.table_schema.get_information_async(session, as_python=False)

        self._meta_information.update(await _meta_information.as_python_dict_async())
        return self._meta_information.copy() if as_python else _meta_information

    def set_meta_information(
        self,
        session: Session | None = None,
        item: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Sets meta-information in the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            item: The meta-information item to set.
            begin: If True, begins a transaction for the operation.
            **kwargs: Additional keyword arguments.
        """
        if session is not None:
            self.table_schema.set_information(session=session, item=item, begin=begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table_schema.set_information(session=session, item=item, begin=True, **kwargs)
        self._meta_information.clear()

    async def set_meta_information_async(
        self,
        session: AsyncSession | None = None,
        item: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously sets meta-information in the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            item: The meta-information item to set.
            begin: If True, begins a transaction for the operation.
            **kwargs: Additional keyword arguments.
        """
        if session is not None:
            await self.table_schema.set_information_async(session=session, item=item, begin=begin, **kwargs)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.set_information_async(
                    session=session,
                    item=item,
                    begin=True,
                    **kwargs,
                )
        self._meta_information.clear()

    def save_cached_meta_information(
        self,
        session: AsyncSession | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Saves cached meta-information to the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            begin: If True, begins a transaction for the operation.
            **kwargs: Additional keyword arguments.
        """
        if session is not None:
            self.table_schema.set_information(session=session, item=self._meta_information, begin=begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table_schema.set_information(session=session, item=self._meta_information, begin=True, **kwargs)

    async def save_cached_meta_information_async(
        self,
        session: AsyncSession | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously saves cached meta-information to the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            begin: If True, begins a transaction for the operation.
            **kwargs: Additional keyword arguments.
        """
        if session is not None:
            await self.table_schema.set_information_async(session=session, item=self._meta_information, begin=begin, **kwargs)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.set_information_async(
                    session=session,
                    item=self._meta_information,
                    begin=True,
                    **kwargs,
                )

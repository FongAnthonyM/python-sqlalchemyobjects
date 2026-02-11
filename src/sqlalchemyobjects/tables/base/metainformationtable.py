"""metainformationtable.py
Classes for storing meta-information in a SQLAlchemy ORM model.

This module contains the classes for storing meta-information in a SQLAlchemy ORM model. It provides the
BaseMetaInformationTableSchema class, which is a schema for a table for storing meta-information, and the
MetaInformationTableManifestation class, which is a manifestation of a meta-information table.
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
from typing import TYPE_CHECKING, Any

# Third-Party Packages #
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Session

# Local Packages #
from .singletontable import BaseSingletonTableSchema, SingletonTableManifestation

if TYPE_CHECKING:
    # Local Packages #
    from ...database import Database as BaseDatabase


# Definitions #
# Classes #
class BaseMetaInformationTableSchema(BaseSingletonTableSchema):
    """A table schema for storing meta-information in an SQLAlchemy ORM model. An instance is the row in the table.

    This class extends the BaseSingletonTableSchema class and provides additional methods for creating, retrieving, and
    updating meta-information entries in the table.

    Attributes:
        __tablename__: The name of the table.
    """

    # Class Attributes #
    __tablename__ = "metainformation"

    # Class Methods #
    @classmethod
    def create_meta_information(
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
    async def create_meta_information_async(
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
    def get_meta_information(
        cls,
        session: Session,
        as_python: bool = True,
    ) -> dict[str, Any] | BaseSingletonTableSchema | None:
        """Retrieves meta-information from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns the item as a dictionary; otherwise, returns the table object. Defaults to True.

        Returns:
            The meta-information item, either as a dictionary or as a table object.
        """
        return cls.get_item(session=session, as_python=as_python)

    @classmethod
    async def get_meta_information_async(
        cls,
        session: AsyncSession,
        as_python: bool = True,
    ) -> dict[str, Any] | BaseSingletonTableSchema | None:
        """Asynchronously retrieves meta-information from the table.

        Args:
            session: The SQLAlchemy async session to use for the query.
            as_python: If True, returns the item as a dictionary; otherwise, returns the table object. Defaults to True.

        Returns:
            The meta-information item, either as a dictionary or as a table object.
        """
        return await cls.get_item_async(session=session, as_python=as_python)

    @classmethod
    def set_meta_information(
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
    async def set_meta_information_async(
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
    """An interface for a meta-information table implemented in an SQLAlchemy database.

    Attributes:
        _database: A weak reference to the SQAlchemy database to interface with.
        table_schema: The SQLAlchemy declarative table which this object act as the interface for.
        _meta_information: Cached meta-information.
    """

    # Attributes #
    _meta_information: dict[str, Any] = {}
    table_schema: type[BaseMetaInformationTableSchema]

    # Properties #
    @property
    def meta_information(self) -> dict[str, Any]:
        """The meta-information."""
        if not self._meta_information:
            self.get_meta_information()
        return self._meta_information

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        table_schema: type[DeclarativeBase] | None = None,
        database: BaseDatabase | None = None,
        init_info: dict[str, Any] | None = None,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initializes a new MetaInformationTableManifestation instance.

        Args:
            table_schema: The SQLAlchemy declarative table which this object act as the interface for.
            database: The SQAlchemy database to interface with.
            init_info: Initial meta-information.
            init: Determines if this object will construct.
            **kwargs: Additional keyword arguments.
        """
        # Attributes #
        self._meta_information = self._meta_information.copy()

        # Parent Attributes #
        super().__init__(init=False)

        # Object Construction #
        if init:
            self.construct(table_schema, database, init_info, **kwargs)

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        table_schema: Any = None,
        database: BaseDatabase | None = None,
        init_info: dict[str, Any] | None = None,
        **kwargs: dict[str, Any] | None,
    ) -> None:
        """Constructs this object with the given arguments.

        Args:
            table_schema: The SQLAlchemy declarative table which this object act as the interface for.
            database: A reference to a BaseDatabase instance.
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
            self.table_schema.create_meta_information(session=session, item=item, begin=begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table_schema.create_meta_information(session=session, item=item, begin=begin, **kwargs)
                if not begin:
                    session.commit()

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
            await self.table_schema.create_meta_information_async(
                session=session,
                item=item,
                begin=begin,
                **kwargs,
            )
        else:
            async with self.create_async_session() as session:
                await self.table_schema.create_meta_information_async(
                    session=session,
                    item=item,
                    begin=begin,
                    **kwargs,
                )
                if not begin:
                    await session.commit()

    def get_meta_information(
        self,
        session: Session | None = None,
        as_python: bool = True,
    ) -> dict[str, Any] | BaseMetaInformationTableSchema | None:
        """Gets meta-information from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns the meta-information as a dictionary.

        Returns:
            The meta-information.
        """
        if session is not None:
            meta_info_item = self.table_schema.get_meta_information(session, as_python=False)
        else:
            with self.create_session() as session:
                meta_info_item = self.table_schema.get_meta_information(session, as_python=False)

        if meta_info_item is not None and not isinstance(meta_info_item, dict):
            self._meta_information.update(meta_info_item.as_python_dict())
        return self._meta_information.copy() if as_python else meta_info_item  # type: ignore[return-value]

    async def get_meta_information_async(
        self,
        session: AsyncSession | None = None,
        as_python: bool = True,
    ) -> dict[str, Any] | BaseMetaInformationTableSchema | None:
        """Asynchronously gets meta-information from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns the meta-information as a dictionary.

        Returns:
            The meta-information.
        """
        if session is not None:
            meta_info_item = await self.table_schema.get_meta_information_async(session, as_python=False)
        else:
            async with self.create_async_session() as session:
                meta_info_item = await self.table_schema.get_meta_information_async(session, as_python=False)

        if meta_info_item is not None and not isinstance(meta_info_item, dict):
            self._meta_information.update(await meta_info_item.as_python_dict_async())
        return self._meta_information.copy() if as_python else meta_info_item  # type: ignore[return-value]

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
            self.table_schema.set_meta_information(session=session, item=item, begin=begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table_schema.set_meta_information(session=session, item=item, begin=begin, **kwargs)
                if not begin:
                    session.commit()
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
            await self.table_schema.set_meta_information_async(session=session, item=item, begin=begin, **kwargs)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.set_meta_information_async(
                    session=session,
                    item=item,
                    begin=begin,
                    **kwargs,
                )
                if not begin:
                    await session.commit()
        self._meta_information.clear()

    def save_cached_meta_information(
        self,
        session: Session | None = None,
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
            self.table_schema.set_meta_information(session=session, item=self._meta_information, begin=begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table_schema.set_meta_information(
                    session=session,
                    item=self._meta_information,
                    begin=begin,
                    **kwargs,
                )
                if not begin:
                    session.commit()

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
            await self.table_schema.set_meta_information_async(
                session=session,
                item=self._meta_information,
                begin=begin,
                **kwargs,
            )
        else:
            async with self.create_async_session() as session:
                await self.table_schema.set_meta_information_async(
                    session=session,
                    item=self._meta_information,
                    begin=begin,
                    **kwargs,
                )
                if not begin:
                    await session.commit()

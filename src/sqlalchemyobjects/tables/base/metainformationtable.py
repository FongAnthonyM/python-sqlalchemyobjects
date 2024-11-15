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
from .singletontable import BaseSingletonTable, SingletonTableManifestation


# Definitions #
# Classes #
class BaseMetaInformationTable(BaseSingletonTable):
    """A table for storing meta-information in a SQLAlchemy ORM model.

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
        entry: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Creates or updates meta-information in the table.

        If an entry already exists, it updates the entry; otherwise, it inserts a new entry.

        Args:
            session: The SQLAlchemy session to use for the operation.
            entry: A dictionary representing the entry to create or update. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        cls.create_entry(session=session, entry=entry, begin=begin, **kwargs)

    @classmethod
    async def create_information_async(
        cls,
        session: AsyncSession,
        entry: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously creates or updates meta-information in the table.

        If an entry already exists, it updates the entry; otherwise, it inserts a new entry.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            entry: A dictionary representing the entry to create or update. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        await cls.create_entry_async(session=session, entry=entry, begin=begin, **kwargs)

    @classmethod
    def get_information(
        cls,
        session: Session,
        as_entry: bool = True,
    ) -> Union[dict[str, Any], "BaseSingletonTable"]:
        """Retrieves meta-information from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_entry: If True, returns the entry as a dictionary; otherwise, returns the table object. Defaults to True.

        Returns:
            Union[dict[str, Any], BaseMetaInformationTable]: The meta-information entry, either as a dictionary or as a table object.
        """
        return cls.get_entry(session=session, as_entry=as_entry)

    @classmethod
    async def get_information_async(
        cls,
        session: AsyncSession,
        as_entry: bool = True,
    ) -> Union[dict[str, Any], "BaseSingletonTable"]:
        """Asynchronously retrieves meta-information from the table.

        Args:
            session: The SQLAlchemy async session to use for the query.
            as_entry: If True, returns the entry as a dictionary; otherwise, returns the table object. Defaults to True.

        Returns:
            Union[dict[str, Any], BaseMetaInformationTable]: The meta-information entry, either as a dictionary or as a table object.
        """
        return await cls.get_entry_async(session=session, as_entry=as_entry)

    @classmethod
    def set_information(
        cls,
        session: Session,
        entry: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Sets meta-information in the table.

        Updates the existing entry with the provided information.

        Args:
            session: The SQLAlchemy session to use for the operation.
            entry: A dictionary representing the entry to update. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        cls.set_entry(session=session, entry=entry, begin=begin, **kwargs)

    @classmethod
    async def set_information_async(
        cls,
        session: AsyncSession,
        entry: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously sets meta-information in the table.

        Updates the existing entry with the provided information.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            entry: A dictionary representing the entry to update. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        await cls.set_entry_async(session=session, entry=entry, begin=begin, **kwargs)


class MetaInformationTableManifestation(SingletonTableManifestation):
    """The manifestation of a MetaInformationTable.

    Attributes:
        _database: A weak reference to the SQAlchemy database to interface with.
        table: The SQLAlchemy declarative table which this object act as the interface for.
        _meta_information: Cached meta-information.

    Args:
        table: The SQLAlchemy declarative table which this object act as the interface for.
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
        table: type[DeclarativeBase] | None = None,
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
            self.construct(table, database, init_info, **kwargs)

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        composite: Any = None,
        table_name: str | None = None,
        init_info: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            composite: The object which this object is a component of.
            table_name: The name of the table.
            init_info: Initial meta-information.
            **kwargs: Additional keyword arguments.
        """
        self._meta_information.update(init_info)

        super().construct(composite, table_name, **kwargs)

    def build(self, *args: Any, **kwargs: Any) -> None:
        """Builds the table."""
        self.create_meta_information(entry=self._meta_information, begin=True)

    def load(self, *args: Any, **kwargs: Any) -> None:
        """Loads the component."""
        self.get_meta_information()

    # Meta Information
    def create_meta_information(
        self,
        session: Session | None = None,
        entry: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Creates meta-information in the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            entry: The meta-information entry to create.
            begin: If True, begins a transaction for the operation.
            **kwargs: Additional keyword arguments.
        """
        if session is not None:
            self.table.create_information(session=session, entry=entry, begin=begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table.create_information(session=session, entry=entry, begin=True, **kwargs)

    async def create_meta_information_async(
        self,
        session: AsyncSession | None = None,
        entry: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously creates meta-information in the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            entry: The meta-information entry to create.
            begin: If True, begins a transaction for the operation.
            **kwargs: Additional keyword arguments.
        """
        if session is not None:
            await self.table.create_information_async(
                session=session,
                entry=entry,
                begin=begin,
                **kwargs,
            )
        else:
            async with self.create_async_session() as session:
                await self.table.create_information_async(
                    session=session,
                    entry=entry,
                    begin=begin,
                    **kwargs,
                )

    def get_meta_information(
        self,
        session: Session | None = None,
        as_entry: bool = True,
    ) -> dict[str, Any] | BaseMetaInformationTable:
        """Gets meta-information from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_entry: If True, returns the meta-information as a dictionary.

        Returns:
            dict[str, Any] | BaseMetaInformationTable: The meta-information.
        """
        if session is not None:
            _meta_information = self.table.get_information(session, as_entry=False)
        else:
            with self.create_session() as session:
                _meta_information = self.table.get_information(session, as_entry=False)

        self._meta_information.update(_meta_information.as_entry())
        return self._meta_information.copy() if as_entry else _meta_information

    async def get_meta_information_async(
        self,
        session: AsyncSession | None = None,
        as_entry: bool = True,
    ) -> dict[str, Any] | BaseMetaInformationTable:
        """Asynchronously gets meta-information from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_entry: If True, returns the meta-information as a dictionary.

        Returns:
            dict[str, Any] | BaseMetaInformationTable: The meta-information.
        """
        if session is not None:
            _meta_information = await self.table.get_information_async(session, as_entry=False)
        else:
            async with self.create_async_session() as session:
                _meta_information = await self.table.get_information_async(session, as_entry=False)

        self._meta_information.update(_meta_information.as_entry())
        return self._meta_information.copy() if as_entry else _meta_information

    def set_meta_information(
        self,
        session: Session | None = None,
        entry: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Sets meta-information in the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            entry: The meta-information entry to set.
            begin: If True, begins a transaction for the operation.
            **kwargs: Additional keyword arguments.
        """
        if session is not None:
            self.table.set_information(session=session, entry=entry, begin=begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table.set_information(session=session, entry=entry, begin=True, **kwargs)
        self._meta_information.clear()

    async def set_meta_information_async(
        self,
        session: AsyncSession | None = None,
        entry: dict[str, Any] | None = None,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously sets meta-information in the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            entry: The meta-information entry to set.
            begin: If True, begins a transaction for the operation.
            **kwargs: Additional keyword arguments.
        """
        if session is not None:
            await self.table.set_information_async(session=session, entry=entry, begin=begin, **kwargs)
        else:
            async with self.create_async_session() as session:
                await self.table.set_information_async(
                    session=session,
                    entry=entry,
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
            self.table.set_information(session=session, entry=self._meta_information, begin=begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table.set_information(session=session, entry=self._meta_information, begin=True, **kwargs)

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
            await self.table.set_information_async(session=session, entry=self._meta_information, begin=begin, **kwargs)
        else:
            async with self.create_async_session() as session:
                await self.table.set_information_async(
                    session=session,
                    entry=self._meta_information,
                    begin=True,
                    **kwargs,
                )

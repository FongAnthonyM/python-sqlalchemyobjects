"""basedatabasecomponent.py.py

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
from typing import Any, Iterable

# Third-Party Packages #
from sqlalchemy import Result
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

# Local Packages #
from ...tables import BaseTable
from .basedatabasecomponent import BaseDatabaseComponent


# Definitions #
# Classes #
class BaseTableComponent(BaseDatabaseComponent):
    """A basic component for a database which is meant to interact with a table.

    Attributes:
        _composite: A weak reference to the object which this object is a component of.
        table_name: The name of the table.
        _table: The table class.

    Args:
        composite: The object which this object is a component of.
        table_name: The name of the table.
        init: Determines if this object will construct.
        **kwargs: Keyword arguments for inheritance.
    """

    # Attributes #
    table_name: str = ""
    _table: type[BaseTable] | None = None

    # Properties #
    @property
    def table(self) -> type[BaseTable]:
        """Gets the table class.

        Returns:
            type[BaseTable]: The table class.
        """
        if self._table is None:
            self._table = self._composite().tables[self.table_name]
        return self._table

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        composite: Any = None,
        table_name: str | None = None,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # Parent Attributes #
        super().__init__(init=False)

        # Object Construction #
        if init:
            self.construct(composite, table_name, **kwargs)

    # Pickling
    def __getstate__(self) -> dict[str, Any]:
        """Creates a dictionary of attributes which can be used to rebuild this object.

        Returns:
            dict: A dictionary of this object's attributes.
        """
        state = super().__getstate__()
        for name in ("_table",):
            if name in state:
                del state[name]
        return state

    # Instance Methods #
    # Constructors/Destructors
    def construct(self, composite: Any = None, table_name: str | None = None, **kwargs: Any) -> None:
        """Constructs this object.

        Args:
            composite: The object which this object is a component of.
            table_name: The name of the table.
            **kwargs: Additional keyword arguments.
        """
        if table_name is not None:
            self.table_name = table_name

        super().construct(composite=composite, **kwargs)

    # Table
    def get_all(self, session: Session | None = None, as_entries: bool = False) -> Result | list[dict[str, Any]]:
        """Fetches all entries from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_entries: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            Result | list[dict[str, Any]]: The result of the query, either as a Result object or as a list of dictionaries.
        """
        if session is not None:
            return self.table.get_all(session, as_entries=as_entries)
        else:
            with self.create_session() as session:
                return self.table.get_all(session, as_entries=as_entries)

    async def get_all_async(
        self,
        session: AsyncSession | None = None,
        as_entries: bool = False,
    ) -> Result | list[dict[str, Any]]:
        """Asynchronously fetches all entries from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_entries: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            Result | list[dict[str, Any]]: The result of the query, either as a Result object or as a list of dictionaries.
        """
        if session is not None:
            return await self.table.get_all_async(session, as_entries=as_entries)
        else:
            async with self.create_async_session() as session:
                return await self.table.get_all_async(session, as_entries=as_entries)

    def insert(
        self,
        item: Any = None,
        entry: dict[str, Any] | None = None,
        session: Session | None = None,
        as_entry: bool = False,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Inserts an item into the table.

        Args:
            item: The item to insert. Defaults to None.
            entry: A dictionary representing the entry to insert. Defaults to None.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            as_entry: If True, creates the item from the entry dictionary. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        if session is not None:
            self.table.insert(session, item, entry, as_entry, begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table.insert(session, item, entry, as_entry, begin, **kwargs)

    async def insert_async(
        self,
        item: Any = None,
        entry: dict[str, Any] | None = None,
        session: AsyncSession | None = None,
        as_entry: bool = False,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously inserts an item into the table.

        Args:
            item: The item to insert. Defaults to None.
            entry: A dictionary representing the entry to insert. Defaults to None.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            as_entry: If True, creates the item from the entry dictionary. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        if session is not None:
            await self.table.insert_async(session, item, entry, as_entry, begin, **kwargs)
        else:
            async with self.create_async_session() as session:
                await self.table.insert_async(session, item, entry, as_entry, begin, **kwargs)

    def insert_all(
        self,
        items: Iterable[Any] = (),
        session: Session | None = None,
        as_entries: bool = False,
        begin: bool = False,
    ) -> None:
        """Inserts multiple items into the table.

        Args:
            items: The items to insert. Defaults to an empty iterable.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            as_entries: If True, creates the items from the entry dictionaries. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            self.table.insert_all(session, items, as_entries, begin)
        else:
            with self.create_session() as session:
                self.table.insert_all(session, items, as_entries, begin)

    async def insert_all_async(
        self,
        items: Iterable[Any] = (),
        session: AsyncSession | None = None,
        as_entries: bool = False,
        begin: bool = False,
    ) -> None:
        """Asynchronously inserts multiple items into the table.

        Args:
            items: The items to insert. Defaults to an empty iterable.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            as_entries: If True, creates the items from the entry dictionaries. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            await self.table.insert_all_async(session, items, as_entries, begin)
        else:
            async with self.create_async_session() as session:
                await self.table.insert_all_async(session, items, as_entries, begin)

    def update_entry(
        self,
        entry: dict[str, Any] | None = None,
        session: Session | None = None,
        key: str = "id_",
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Updates an entry in the table.

        Args:
            entry: A dictionary representing the entry to update. Defaults to None.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            key: The key to identify the entry. Defaults to "id_".
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        if session is not None:
            self.table.update_entry(session, entry, key, begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table.update_entry(session, entry, key, begin, **kwargs)

    async def update_entry_async(
        self,
        entry: dict[str, Any] | None = None,
        session: AsyncSession | None = None,
        key: str = "id_",
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Asynchronously updates an entry in the table.

        Args:
            entry: A dictionary representing the entry to update. Defaults to None.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            key: The key to identify the entry. Defaults to "id_".
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        if session is not None:
            await self.table.update_entry_async(session, entry, key, begin, **kwargs)
        else:
            async with self.create_async_session() as session:
                await self.table.update_entry_async(session, entry, key, begin, **kwargs)

    def update_entries(
        self,
        entries: Iterable[dict[str, Any]] | None = None,
        session: Session | None = None,
        key: str = "id_",
        begin: bool = False,
    ) -> None:
        """Updates multiple entries in the table.

        Args:
            entries: An iterable of dictionaries representing the entries to update. Defaults to None.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            key: The key to identify the entries. Defaults to "id_".
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            self.table.update_entries(session, entries, key, begin)
        else:
            with self.create_session() as session:
                self.table.update_entries(session, entries, key, begin)

    async def update_entries_async(
        self,
        entries: Iterable[dict[str, Any]] | None = None,
        session: AsyncSession | None = None,
        key: str = "id_",
        begin: bool = False,
    ) -> None:
        """Asynchronously updates multiple entries in the table.

        Args:
            entries: An iterable of dictionaries representing the entries to update. Defaults to None.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            key: The key to identify the entries. Defaults to "id_".
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            await self.table.update_entries_async(session, entries, key, begin)
        else:
            async with self.create_async_session() as session:
                await self.table.update_entries_async(session, entries, key, begin)

    def delete_item(
        self,
        item: BaseTable,
        session: Session | None = None,
        begin: bool = False,
    ) -> None:
        """Deletes an item from the table.

        Args:
            item: The item to delete.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            self.table.delete_item(session, item, begin)
        else:
            with self.create_session() as session:
                self.table.delete_item(session, item, begin)

    async def delete_item_async(
        self,
        item: BaseTable,
        session: AsyncSession | None = None,
        begin: bool = False,
    ) -> None:
        """Asynchronously deletes an item from the table.

        Args:
            item: The item to delete.
            session: The SQLAlchemy session to apply the modification. Defaults to None.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            await self.table.delete_item_async(session, item, begin)
        else:
            async with self.create_async_session() as session:
                await self.table.delete_item_async(session, item, begin)

"""basetable.py
Classes for outlining base class tables to be used in a SQLAlchemy ORM model.
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
from collections.abc import Iterable
from typing import Any, Optional
import uuid
from weakref import ref

# Third-Party Packages #
from baseobjects import BaseObject
from sqlalchemy import Uuid, Result, select, lambda_stmt
from sqlalchemy.orm import mapped_column, Session, DeclarativeBase
from sqlalchemy.ext.asyncio import AsyncSession

# Local Packages #


# Definitions #
# Classes #
class BaseTableSchema:
    """A base class for a table schema to be used in a SQLAlchemy ORM model.

    This class and its subclasses should be multi-inherited along with SQLAlchemy's ContentsFileSchema or
    ContentsFileAsyncSchema to create a mixin class which will properly implement table in SQLite. Mainly, this class
    is for defining a SQLite table through the SQLAlchemy ORM. The class attributes of the class define the properties
    of the table itself. The class methods can be used to interface with the table, as such, there are methods for
    common operations such as insert, update, delete, and fetch operations.

    Class Attributes:
        __tablename__: The name of the table.
        __mapper_args__: Mapper arguments for SQLAlchemy ORM configurations.

    Columns:
        id: The primary key column of the table, using UUIDs.
    """

    # Class Attributes #
    __tablename__: str = "base"
    __mapper_args__: dict[str, str] = {"polymorphic_identity": "base"}

    # Columns #
    id = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)

    # Class Methods #
    @classmethod
    def format_entry_kwargs(cls, id_: str | uuid.UUID | None = None, **kwargs: Any) -> dict[str, Any]:
        """Formats entry keyword arguments for creating or updating table entries.

        Args:
            id_ (str | uuid.UUID | None): The ID of the entry, if specified.
            **kwargs (Any): Additional keyword arguments for the entry.

        Returns:
            dict[str, Any]: A dictionary of keyword arguments for the entry.
        """
        if id_ is not None:
            kwargs["id_"] = uuid.UUID(hex=id_) if isinstance(id_, str) else id_
        return kwargs

    @classmethod
    def item_from_entry(cls, dict_: dict[str, Any] | None = None, /, **kwargs) -> "BaseTable":
        """Creates an item from a dictionary entry or keyword arguments.

        Args:
            dict_: A dictionary representing the entry.
            **kwargs: Additional keyword arguments for the entry.

        Returns:
            BaseTable: The new item from the table.
        """
        return cls(**cls.format_entry_kwargs(**(({} if dict_ is None else dict_) | kwargs)))

    @classmethod
    def get_all(cls, session: Session, as_entries: bool = False) -> Result | list[dict[str, Any]]:
        """Fetches all entries from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_entries: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            Result | list[dict[str, Any]]: The result of the query, either as a Result object or as a list of dictionaries.
        """
        results = session.execute(lambda_stmt(lambda: select(cls)))
        return [r.as_entry() for r in results.scalars()] if as_entries else results

    @classmethod
    async def get_all_async(cls, session: AsyncSession, as_entries: bool = False) -> Result | list[dict[str, Any]]:
        """Fetches all entries from the table asynchronously.

        Args:
            session: The SQLAlchemy async session to use for the query.
            as_entries: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            Result | list[dict[str, Any]]: The result of the query, either as a Result object or as a list of dictionaries.
        """
        results = await session.execute(lambda_stmt(lambda: select(cls)))
        return [r.as_entry() for r in results.scalars()] if as_entries else results

    @classmethod
    def insert(
        cls,
        session: Session,
        item: Any = None,
        entry: dict[str, Any] | None = None,
        as_entry: bool = False,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Inserts an item into the table.

        Args:
            session: The SQLAlchemy session to use for the operation.
            item: The item to insert. Defaults to None.
            entry: A dictionary representing the entry to insert. Defaults to None.
            as_entry: If True, creates the item from the entry dictionary. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        if as_entry:
            item = cls.item_from_entry(**(({} if entry is None else entry) | kwargs))

        if begin:
            with session.begin():
                session.add(item)
        else:
            session.add(item)

    @classmethod
    async def insert_async(
        cls,
        session: AsyncSession,
        item: Any = None,
        entry: dict[str, Any] | None = None,
        as_entry: bool = False,
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Inserts an item into the table asynchronously.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            item: The item to insert. Defaults to None.
            entry: A dictionary representing the entry to insert. Defaults to None.
            as_entry: If True, creates the item from the entry dictionary. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        if as_entry:
            item = cls.item_from_entry(**(({} if entry is None else entry) | kwargs))

        if begin:
            async with session.begin():
                session.add(item)
        else:
            session.add(item)

    @classmethod
    def insert_all(
        cls,
        session: Session,
        items: Iterable[Any],
        as_entries: bool = False,
        begin: bool = False,
    ) -> None:
        """Inserts multiple items into the table.

        Args:
            session: The SQLAlchemy session to use for the operation.
            items: The items to insert.
            as_entries: If True, creates the items from the entry dictionaries. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if as_entries:
            items = [cls.item_from_entry(i) for i in items]

        if begin:
            with session.begin():
                session.add_all(items)
        else:
            session.add_all(items)

    @classmethod
    async def insert_all_async(
        cls,
        session: AsyncSession,
        items: Iterable[Any],
        as_entries: bool = False,
        begin: bool = False,
    ) -> None:
        """Inserts multiple items into the table asynchronously.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            items: The items to insert.
            as_entries: If True, creates the items from the entry dictionaries. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if as_entries:
            items = [cls.item_from_entry(i) for i in items]

        if begin:
            async with session.begin():
                session.add_all(items)
        else:
            session.add_all(items)

    @classmethod
    def _create_find_statement(cls, key: str, value: Any):
        """Creates a SQLAlchemy statement to find an entry by a specific key and value.

        Args:
            key: The key (column name) to search by.
            value: The value to search for.

        Returns:
            lambda_stmt: The SQLAlchemy statement to find the entry.
        """
        column = getattr(cls, key)
        statement = lambda_stmt(lambda: select(cls))
        statement += lambda s: s.where(column == value)
        return statement

    @classmethod
    def update_entry(
        cls,
        session: Session,
        entry: dict[str, Any] | None = None,
        key: str = "id_",
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Updates an entry in the table.

        Args:
            session: The SQLAlchemy session to use for the operation.
            entry: A dictionary representing the entry to update. Defaults to None.
            key: The key (column name) to search by. Defaults to "id_".
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        entry.update(kwargs)
        statement = cls._create_find_statement(key, entry[key])
        if begin:
            with session.begin():
                item = session.execute(statement).scalar()
                if item is None:
                    cls.insert(session=session, entry=entry, as_entry=True)
                else:
                    item.update(entry)
        else:
            item = session.execute(statement).scalar()
            if item is None:
                cls.insert(session=session, entry=entry, as_entry=True)
            else:
                item.update(entry)

    @classmethod
    async def update_entry_async(
        cls,
        session: AsyncSession,
        entry: dict[str, Any] | None = None,
        key: str = "id_",
        begin: bool = False,
        **kwargs: Any,
    ) -> None:
        """Updates an entry in the table asynchronously.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            entry: A dictionary representing the entry to update. Defaults to None.
            key: The key (column name) to search by. Defaults to "id_".
            begin: If True, begins a transaction for the operation. Defaults to False.
            **kwargs: Additional keyword arguments for the entry.
        """
        entry.update(kwargs)
        statement = cls._create_find_statement(key, entry[key])
        if begin:
            async with session.begin():
                item = (await session.execute(statement)).scalar()
                if item is None:
                    await cls.insert_async(session=session, entry=entry, as_entry=True)
                else:
                    item.update(entry)
        else:
            item = (await session.execute(statement)).scalar()
            if item is None:
                await cls.insert_async(session=session, entry=entry, as_entry=True)
            else:
                item.update(entry)

    @classmethod
    def update_entries(
        cls,
        session: Session,
        entries: Iterable[dict[str, Any]] | None = None,
        key: str = "id_",
        begin: bool = False,
    ) -> None:
        """Updates multiple entries in the table.

        Args:
            session: The SQLAlchemy session to use for the operation.
            entries: A list of dictionaries representing the entries to update. Defaults to None.
            key: The key (column name) to search by. Defaults to "id_".
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        items = []
        if begin:
            with session.begin():
                for entry in entries:
                    item = session.execute(cls._create_find_statement(key, entry[key])).scalar()
                    if item is None:
                        items.append(entry)
                    else:
                        item.update(entry)
                if items:
                    cls.insert_all(session=session, items=items, as_entries=True)
        else:
            for entry in entries:
                item = session.execute(cls._create_find_statement(key, entry[key])).scalar()
                if item is None:
                    items.append(entry)
                else:
                    item.update(entry)
            if items:
                cls.insert_all(session=session, items=items, as_entries=True)

    @classmethod
    async def update_entries_async(
        cls,
        session: AsyncSession,
        entries: Iterable[dict[str, Any]] | None = None,
        key: str = "id_",
        begin: bool = False,
    ) -> None:
        """Updates multiple entries in the table asynchronously.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            entries: A list of dictionaries representing the entries to update. Defaults to None.
            key: The key (column name) to search by. Defaults to "id_".
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        items = []
        if begin:
            async with session.begin():
                for entry in entries:
                    item = (await session.execute(cls._create_find_statement(key, entry[key]))).scalar()
                    if item is None:
                        items.append(entry)
                    else:
                        item.update(entry)
                if items:
                    await cls.insert_all_async(session=session, items=items, as_entries=True)
        else:
            for entry in entries:
                item = (await session.execute(cls._create_find_statement(key, entry[key]))).scalar()
                if item is None:
                    items.append(entry)
                else:
                    item.update(entry)
            if items:
                await cls.insert_all_async(session=session, items=items, as_entries=True)

    @classmethod
    def delete_item(
        cls,
        session: Session,
        item: "BaseTable",
        begin: bool = False,
    ) -> None:
        """Deletes an item from the table.

        Args:
            session: The SQLAlchemy session to use for the operation.
            item: The item to delete.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if begin:
            with session.begin():
                session.delete(item)
        else:
            session.delete(item)

    @classmethod
    async def delete_item_async(
        cls,
        session: AsyncSession,
        item: "BaseTable",
        begin: bool = False,
    ) -> None:
        """Deletes an item from the table asynchronously.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            item: The item to delete.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if begin:
            async with session.begin():
                await session.delete(item)
        else:
            await session.delete(item)

    # Instance Methods #
    def update(self, dict_: dict[str, Any] | None = None, /, **kwargs) -> None:
        """Updates the row of the table with the provided dictionary or keyword arguments.

        Args:
            dict_: A dictionary of attributes/columns to update. Defaults to None.
            **kwargs: Additional keyword arguments for the attributes to update.
        """

    def as_dict(self) -> dict[str, Any]:
        """Creates a dictionary with all the contents of the row.

        Returns:
            dict[str, Any]: A dictionary representation of the row.
        """
        return {"id": self.id}

    def as_entry(self) -> dict[str, Any]:
        """Creates a dictionary with the entry contents of the row.

        Returns:
            dict[str, Any]: A dictionary representation of the entry.
        """
        return {"id": self.id}


class TableManifestation(BaseObject):
    """This object acts as the manifestation (an interface) of a table implemented in an SQLAlchemy database.

    Attributes:
        _database: A weak reference to the SQAlchemy database to interface with.
        table: The SQLAlchemy declarative table which this object act as the interface for.

    Args:
        table_schema: The SQLAlchemy declarative table which this object act as the interface for.
        database: The SQAlchemy database to interface with.
        init: Determines if this object will construct.
        **kwargs: Additional keyword arguments.
    """

    # Attributes #
    _database: ref["BaseDatabase"] | None = None
    table_schema: type[DeclarativeBase] | None = None

    # Properties #
    @property
    def database(self) -> Optional["BaseDatabase"]:
        """The database object associated with the table manifestation."""
        return None if self._database is None else self._database()

    @database.setter
    def database(self, value: Any) -> None:
        """Sets the database object associated with the table_schema manifestation."""
        self._database = ref(value)

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        table_schema: type[DeclarativeBase] | None = None,
        database: Optional["BaseDatabase"] = None,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        # Parent Attributes #
        super().__init__(init=False)

        # Object Construction #
        if init:
            self.construct(table_schema, database, **kwargs)

    # Pickling
    def __getstate__(self) -> dict[str, Any]:
        """Creates a dictionary of attributes which can be used to rebuild this object.

        Returns:
            dict: A dictionary of this object's attributes.
        """
        state = super().__getstate__()
        state["_database"] = None
        return state

    # Instance Methods #
    # Construction/Destruction
    def construct(
        self,
        table_schema: type[DeclarativeBase] | None = None,
        database: Optional["BaseDatabase"] = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object.

        Args:
            table_schema: The SQLAlchemy declarative table which this object act as the interface for.
            database: A reference to a BaseDatabase instance.
            **kwargs: Additional keyword arguments to pass to the superclass construct method.
        """
        if database is not None:
            self._database = ref(database)

        if table_schema is not None:
            self.table_schema = table_schema

        super().construct(**kwargs)

    def build(self, *args: Any, **kwargs: Any) -> None:
        """Builds the table."""

    def load(self, *args: Any, **kwargs: Any) -> None:
        """Load the table."""

    # Session
    def create_session(self, *args: Any, **kwargs: Any) -> Session:
        """Creates a new SQLAlchemy session.

        Args:
            *args: Positional arguments for session creation.
            **kwargs: Keyword arguments for session creation.

        Returns:
            Session: A new SQLAlchemy session.
        """
        return self._database().create_session(*args, **kwargs)

    def create_async_session(self, *args: Any, **kwargs: Any) -> AsyncSession:
        """Creates a new asynchronous SQLAlchemy session.

        Args:
            *args : Positional arguments for session creation.
            **kwargs: Keyword arguments for session creation.

        Returns:
            AsyncSession: A new asynchronous SQLAlchemy session.
        """
        return self._database().create_async_session(*args, **kwargs)

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
            return self.table_schema.get_all(session, as_entries=as_entries)
        else:
            with self.create_session() as session:
                return self.table_schema.get_all(session, as_entries=as_entries)

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
            return await self.table_schema.get_all_async(session, as_entries=as_entries)
        else:
            async with self.create_async_session() as session:
                return await self.table_schema.get_all_async(session, as_entries=as_entries)

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
            self.table_schema.insert(session, item, entry, as_entry, begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table_schema.insert(session, item, entry, as_entry, begin, **kwargs)

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
            await self.table_schema.insert_async(session, item, entry, as_entry, begin, **kwargs)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.insert_async(session, item, entry, as_entry, begin, **kwargs)

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
            self.table_schema.insert_all(session, items, as_entries, begin)
        else:
            with self.create_session() as session:
                self.table_schema.insert_all(session, items, as_entries, begin)

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
            await self.table_schema.insert_all_async(session, items, as_entries, begin)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.insert_all_async(session, items, as_entries, begin)

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
            self.table_schema.update_entry(session, entry, key, begin, **kwargs)
        else:
            with self.create_session() as session:
                self.table_schema.update_entry(session, entry, key, begin, **kwargs)

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
            await self.table_schema.update_entry_async(session, entry, key, begin, **kwargs)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.update_entry_async(session, entry, key, begin, **kwargs)

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
            self.table_schema.update_entries(session, entries, key, begin)
        else:
            with self.create_session() as session:
                self.table_schema.update_entries(session, entries, key, begin)

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
            await self.table_schema.update_entries_async(session, entries, key, begin)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.update_entries_async(session, entries, key, begin)

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
            self.table_schema.delete_item(session, item, begin)
        else:
            with self.create_session() as session:
                self.table_schema.delete_item(session, item, begin)

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
            await self.table_schema.delete_item_async(session, item, begin)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.delete_item_async(session, item, begin)

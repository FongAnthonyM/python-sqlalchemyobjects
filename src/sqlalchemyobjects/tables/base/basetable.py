"""basetable.py
Classes for outlining base class tables to be used in a SQLAlchemy ORM model.

This module contains the base classes for tables and table manifestations in the sqlalchemyobjects package. It provides
the BaseTableSchema class, which is a base class for SQLAlchemy ORM models, and the TableManifestation class, which is a
wrapper around a table and a database connection.
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
from asyncio import gather
from collections import deque
from collections.abc import Iterable
from itertools import chain
from typing import TYPE_CHECKING, Any, ClassVar
from uuid import UUID, uuid4
from weakref import ReferenceType

# Third-Party Packages #
from baseobjects import BaseReducible
from sqlalchemy import Result, StatementLambdaElement, Uuid, func, inspect, lambda_stmt, select
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Session, mapped_column

if TYPE_CHECKING:
    # Local Packages #
    from ...database import Database


# Definitions #
# Classes #
class BaseTableSchema:
    """A base class for a table schema in an SQLAlchemy ORM model. Instances are rows in the table.

    This class and its subclasses should be multi-inherited along with SQLAlchemy's ContentsFileSchema or
    ContentsFileAsyncSchema to create a mixin class which will properly implement table in SQLite. Mainly, this class
    is for defining an SQLite table through the SQLAlchemy ORM. The class attributes of the class define the properties
    of the table itself. The class methods can be used to interface with the table, as such, there are methods for
    common operations such as insert, update, delete, and fetch operations.

    Attributes:
        __tablename__: The name of the table.
    """

    # Class Attributes #
    __tablename__: str = "base"
    _is_single_table_inheritance: ClassVar[bool] = False
    _sti_polymorphic_on: ClassVar[Any] = None
    _sti_polymorphic_identity: ClassVar[Any] = None

    # Columns #
    id = mapped_column(Uuid, primary_key=True, default=uuid4)

    # Class Magic Methods #
    def __init_subclass__(cls, **kwargs: Any) -> None:
        """Initializes a new subclass.

        Args:
            **kwargs: Keyword arguments for inheritance.
        """
        super().__init_subclass__(**kwargs)
        cls._determine_single_inheritance()

    # Class Methods #
    @classmethod
    def _determine_single_inheritance(cls) -> None:
        try:  # Best-effort; if not an ORM-mapped class, just return
            mapper = inspect(cls)
        except Exception:
            return
        else:
            inherits = getattr(mapper, "inherits", None)
            local_table = getattr(mapper, "local_table", None)
            base_local_table = getattr(inherits, "local_table", None) if inherits is not None else None

            # Detect STI: subclass (has inherits) and shares the same local table as base
            if (
                inherits is not None
                and local_table is not None
                and local_table is base_local_table
                and (polymorphic_on := getattr(mapper, "polymorphic_on", None)) is not None
                and (polymorphic_identity := getattr(mapper, "polymorphic_identity", None)) is not None
            ):
                cls._is_single_table_inheritance = True
                cls._sti_polymorphic_on = polymorphic_on
                cls._sti_polymorphic_identity = polymorphic_identity

    # Base
    @classmethod
    def get_column_names(cls) -> list[str]:
        """Gets the names of the columns in the table.

        Returns:
            The names of the columns in the table.
        """
        return cls.__table__.columns.keys()  # type: ignore[attr-defined, no-any-return]

    @classmethod
    def to_sql_types(cls, dict_: dict[str, Any] | None = None, /, **kwargs: Any) -> dict[str, Any]:
        """Casts Python types of an entry to SQLAlchemy types.

        Only table item elements (columns) which must be cast to an SQLAlchemy type are cast to SQLAlchemy types.
        Additionally, all elements are optional, such that they do not need to be provided. This way any subset of the
        elements can be cast. For example: when updating a table item, a few elements can be updated without providing
        all elements.

        Args:
            dict_: A dictionary representing the entry with Python types.
            **kwargs: Additional keyword arguments for the entry.

        Returns:
            A dictionary representing the entry with SQLAlchemy types.
        """
        # Create new entry
        sql_entry = kwargs if dict_ is None else dict_ | kwargs

        # Format ID
        if (id_ := sql_entry.get("id", None)) is not None:
            match id_:
                case UUID():
                    pass
                case str():
                    sql_entry["id"] = UUID(hex=id_)
                case int():
                    sql_entry["id"] = UUID(int=id_)

        # Return new entry
        return sql_entry

    @classmethod
    def from_sql_types(cls, dict_: dict[str, Any] | None = None, /, **kwargs: Any) -> dict[str, Any]:
        """Casts SQLAlchemy types of an entry to Python types.

        Only table item elements (columns) which must cast to a Python type are cast to Python types. Additionally, all
        elements are optional, such that they do not need to be provided. This way any subset of the elements can be
        cast. For example: when querying a table item, a few columns can be selected without providing all columns.

        Args:
            dict_: A dictionary representing the entry with SQLAlchemy types.
            **kwargs: Additional keyword arguments for the entry.

        Returns:
            A dictionary representing the entry with Python types.
        """
        return kwargs if dict_ is None else dict_ | kwargs

    @classmethod
    def item_from_dict(
        cls,
        dict_: dict[str, Any] | None = None,
        /,
        *,
        _format_dict: bool = True,
        **kwargs: Any,
    ) -> BaseTableSchema:
        """Creates an item from a dictionary entry or keyword arguments.

        Args:
            dict_: A dictionary representing the entry.
            _format_dict: If True, formats the entry.
            **kwargs: Additional keyword arguments for the entry.

        Returns:
            The new item from the table.
        """
        return cls(**(cls.to_sql_types(dict_, **kwargs) if _format_dict else ((dict_ or {}) | kwargs)))

    # SQLAlchemy Statements
    @classmethod
    def _apply_sti_subclass_filter(cls, statement: StatementLambdaElement) -> StatementLambdaElement:
        """Appends a discriminator filter for STI subclass queries when applicable.

        For Single Table Inheritance, selecting a subclass should implicitly filter by the subclass' polymorphic
        identity. While SQLAlchemy normally handles this when selecting the subclass, in some contexts (e.g., generic
        helpers), adding the filter explicitly ensures consistent behavior.

        Returns:
            The SQLAlchemy statement with the filter applied.
        """
        if cls._is_single_table_inheritance:
            statement += lambda s: s.where(cls._sti_polymorphic_on == cls._sti_polymorphic_identity)
        return statement

    @classmethod
    def create_find_column_value_statement(cls, column_name: str, value: Any) -> StatementLambdaElement:
        """Creates an SQLAlchemy statement to find an item by a specific column's value.

        Args:
            column_name: The key (column name) to search by.
            value: The value to search for.

        Returns:
            lambda_stmt: The SQLAlchemy statement to find the entry.
        """
        column = getattr(cls, column_name)
        statement = lambda_stmt(lambda: select(cls))
        statement += lambda s: s.where(column == value)
        # Apply STI subclass discriminator filter if applicable
        return cls._apply_sti_subclass_filter(statement)

    @classmethod
    def create_find_column_values_statement(cls, column_name: str, values: Iterable[Any]) -> StatementLambdaElement:
        """Creates an SQLAlchemy statement to find items by a specific column's values.

        Args:
            column_name: The key (column name) to search by.
            values: The values to search for.

        Returns:
            lambda_stmt: The SQLAlchemy statement to find the entries.
        """
        column = getattr(cls, column_name)
        statement = lambda_stmt(lambda: select(cls))
        statement += lambda s: s.where(column.in_(values))
        # Apply STI subclass discriminator filter if applicable
        return cls._apply_sti_subclass_filter(statement)

    # Modification
    @classmethod
    def insert(
        cls,
        session: Session,
        item: Any,
        as_dict: bool = False,
        begin: bool = False,
    ) -> None:
        """Inserts an item into the table.

        Args:
            session: The SQLAlchemy session to use for the operation.
            item: The item to insert can be either an instance (row) of the table or a dict.
            as_dict: If True, creates an instance (row) of the table from the dictionary. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if as_dict or isinstance(item, dict):
            item = cls.item_from_dict(**item)

        if begin:
            with session.begin():
                session.add(item)
        else:
            session.add(item)

    @classmethod
    async def insert_async(
        cls,
        session: AsyncSession,
        item: Any,
        as_dict: bool = False,
        begin: bool = False,
    ) -> None:
        """Asynchronously inserts an item into the table.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            item: The item to insert can be either an instance (row) of the table or a dict.
            as_dict: If True, creates an instance (row) of the table from the dictionary. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if as_dict or isinstance(item, dict):
            item = cls.item_from_dict(**item)

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
        as_dict: bool = False,
        begin: bool = False,
    ) -> None:
        """Inserts multiple items into the table.

        Args:
            session: The SQLAlchemy session to use for the operation.
            items: The items to insert.
            as_dict: If True, creates the instances (rows) of the table from the dictionaries. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if as_dict:
            items = [cls.item_from_dict(i) for i in items]

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
        as_dict: bool = False,
        begin: bool = False,
    ) -> None:
        """Asynchronously inserts multiple items into the table.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            items: The items to insert.
            as_dict: If True, creates the instances (rows) of the table from the dictionaries. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if as_dict:
            items = [cls.item_from_dict(i) for i in items]

        if begin:
            async with session.begin():
                session.add_all(items)
        else:
            session.add_all(items)

    @classmethod
    def upsert(
        cls,
        session: Session,
        entry: dict[str, Any],
        key: str = "id",
        begin: bool = False,
    ) -> None:
        """Updates an entry in the table if it exists, otherwise, creates a new entry.

        Args:
            session: The SQLAlchemy session to use for the operation.
            entry: A dictionary representing the entry to update. Defaults to None.
            key: The key (column name) to search by. Defaults to "id".
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        statement = cls.create_find_column_value_statement(key, entry[key])
        if begin:
            with session.begin():
                item = session.execute(statement).scalar()
                if item is None:
                    cls.insert(session=session, item=entry, as_dict=True)
                else:
                    item.update_instance(entry)
        else:
            item = session.execute(statement).scalar()
            if item is None:
                cls.insert(session=session, item=entry, as_dict=True)
            else:
                item.update_instance(entry)

    @classmethod
    async def upsert_async(
        cls,
        session: AsyncSession,
        entry: dict[str, Any],
        key: str = "id",
        begin: bool = False,
    ) -> None:
        """Asynchronously, updates an entry in the table if it exists, otherwise, creates a new entry.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            entry: A dictionary representing the entry to update. Defaults to None.
            key: The key (column name) to search by. Defaults to "id".
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        statement = cls.create_find_column_value_statement(key, entry[key])
        if begin:
            async with session.begin():
                item = (await session.execute(statement)).scalar()
                if item is None:
                    await cls.insert_async(session=session, item=entry, as_dict=True)
                else:
                    item.update_instance(entry)
        else:
            item = (await session.execute(statement)).scalar()
            if item is None:
                await cls.insert_async(session=session, item=entry, as_dict=True)
            else:
                item.update_instance(entry)

    @classmethod
    def upsert_all(
        cls,
        session: Session,
        entries: Iterable[dict[str, Any]],
        key: str = "id",
        begin: bool = False,
    ) -> None:
        """Updates multiple entries in the table if they exist, otherwise, creates new entries.

        Args:
            session: The SQLAlchemy session to use for the operation.
            entries: A list of dictionaries representing the entries to update. Defaults to None.
            key: The key (column name) to search by. Defaults to "id".
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        # Separate entries with and without "key"
        entry_dict = {}
        entry_dequed: deque[dict[str, Any]] = deque()
        for entry in entries:
            if (value := entry.get(key, None)) is not None:
                entry_dict[value] = entry
            else:
                entry_dequed.append(entry)

        # Create find statement to find all items to update
        find_statement = cls.create_find_column_values_statement(key, entry_dict.keys())

        if begin:
            with session.begin():
                # Find all items to update
                items = session.execute(find_statement)

                # Update found items and remove them from dict
                for item in items.scalars():
                    item.update_instance(entry_dict.pop(getattr(item, key)))

                # Insert all other entries in dict and deque
                cls.insert_all(session, chain(entry_dict.values(), entry_dequed), as_dict=True)
        else:
            # Find all items to update
            items = session.execute(find_statement)

            # Update found items and remove them from dict
            for item in items.scalars():
                item.update_instance(entry_dict.pop(getattr(item, key)))

            # Insert all other entries in dict and deque
            cls.insert_all(session, chain(entry_dict.values(), entry_dequed), as_dict=True)

    @classmethod
    async def upsert_all_async(
        cls,
        session: AsyncSession,
        entries: Iterable[dict[str, Any]],
        key: str = "id",
        begin: bool = False,
    ) -> None:
        """Asynchronously, updates multiple entries in the table if they exist, otherwise, creates new entries.

        Args:
            session: The SQLAlchemy async session to use for the operation.
            entries: A list of dictionaries representing the entries to update. Defaults to None.
            key: The key (column name) to search by. Defaults to "id".
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        # Separate entries with and without "key"
        entry_dict = {}
        entry_dequed: deque[dict[str, Any]] = deque()
        for entry in entries:
            if (value := entry.get(key, None)) is not None:
                entry_dict[value] = entry
            else:
                entry_dequed.append(entry)

        # Create find statement to find all items to update
        find_statement = cls.create_find_column_values_statement(key, entry_dict.keys())

        if begin:
            async with session.begin():
                # Find all items to update
                items = [i async for i in (await session.stream(find_statement)).scalars()]

                # Update found items and remove them from dict
                for item, value in zip(
                    items,
                    await gather(*(getattr(i.awaitable_attrs, key) for i in items)),
                    strict=True,
                ):
                    item.update_instance(entry_dict.pop(value))

                # Insert all other entries in dict and deque
                await cls.insert_all_async(session, chain(entry_dict.values(), entry_dequed), as_dict=True)
        else:
            # Find all items to update
            items = [i async for i in (await session.stream(find_statement)).scalars()]

            # Update found items and remove them from dict
            for item, value in zip(
                items,
                await gather(*(getattr(i.awaitable_attrs, key) for i in items)),
                strict=True,
            ):
                item.update_instance(entry_dict.pop(value))

            # Insert all other entries in dict and deque
            await cls.insert_all_async(session, chain(entry_dict.values(), entry_dequed), as_dict=True)

    @classmethod
    def delete(
        cls,
        session: Session,
        item: BaseTableSchema,
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
    async def delete_async(
        cls,
        session: AsyncSession,
        item: BaseTableSchema,
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

    # Queries
    @classmethod
    def count(cls, session: Session) -> int:
        """Counts the number of entries in the table.

        Args:
            session: The SQLAlchemy session to use for the query.

        Returns:
            The number of entries in the table.
        """
        stmt = lambda_stmt(lambda: select(func.count()).select_from(cls))
        stmt = cls._apply_sti_subclass_filter(stmt)
        return session.execute(stmt).scalar_one()  # type: ignore[no-any-return]

    @classmethod
    async def count_async(cls, session: AsyncSession) -> int:
        """Asynchronously counts the number of entries in the table.

        Args:
            session: The SQLAlchemy async session to use for the query.

        Returns:
            The number of entries in the table.
        """
        stmt = lambda_stmt(lambda: select(func.count()).select_from(cls))
        stmt = cls._apply_sti_subclass_filter(stmt)
        return (await session.execute(stmt)).scalar_one()  # type: ignore[no-any-return]

    @classmethod
    def get_by_id(cls, session: Session, id_: Any, as_python: bool = False) -> Any:
        """Fetches an entry from the table by its ID.

        Args:
            session: The SQLAlchemy session to use for the query.
            id_: The ID of the entry to search for.
            as_python: If True, returns a dictionary representing the entry; otherwise, returns the item.

        Returns:
            The item from the table or its dictionary representation.
        """
        if cls._is_single_table_inheritance:
            stmt = cls.create_find_column_value_statement("id", id_)
            result = session.execute(stmt).scalar()
        else:
            result = session.get(cls, id_)
        return result.as_python_dict() if as_python and result is not None else result

    @classmethod
    async def get_by_id_async(cls, session: AsyncSession, id_: Any, as_python: bool = False) -> Any:
        """Asynchronously fetches an entry from the table by its ID.

        Args:
            session: The SQLAlchemy async session to use for the query.
            id_: The ID of the entry to search for.
            as_python: If True, returns a dictionary representing the entry; otherwise, returns the item.

        Returns:
            The item from the table or its dictionary representation.
        """
        if cls._is_single_table_inheritance:
            stmt = cls.create_find_column_value_statement("id", id_)
            result = (await session.execute(stmt)).scalar()
        else:
            result = await session.get(cls, id_)
        return await result.as_python_dict_async() if as_python and result is not None else result

    @classmethod
    def get_by(
        cls,
        session: Session,
        column_name: str,
        value: Any,
        as_python: bool = False,
    ) -> Result[Any] | list[dict[str, Any]]:
        """Fetches all entries from the table by a specific column value.

        Args:
            session: The SQLAlchemy session to use for the query.
            column_name: The name of the column to search by.
            value: The value to search for.
            as_python: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            The result of the query, either as a Result object or as a list of dictionaries.
        """
        stmt = cls.create_find_column_value_statement(column_name, value)
        result = session.execute(stmt)
        return [r.as_python_dict() for r in result.scalars().all()] if as_python else result

    @classmethod
    async def get_by_async(
        cls,
        session: AsyncSession,
        column_name: str,
        value: Any,
        as_python: bool = False,
    ) -> AsyncResult[Any] | list[dict[str, Any]]:
        """Asynchronously fetches all entries from the table by a specific column value.

        Args:
            session: The SQLAlchemy async session to use for the query.
            column_name: The name of the column to search by.
            value: The value to search for.
            as_python: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            The result of the query, either as a Result object or as a list of dictionaries.
        """
        stmt = cls.create_find_column_value_statement(column_name, value)
        result = await session.stream(stmt)
        return await gather(*[r.as_python_dict_async() async for r in result.scalars()]) if as_python else result

    @classmethod
    def get_all(cls, session: Session, as_python: bool = False) -> Result[Any] | list[dict[str, Any]]:
        """Fetches all entries from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            The result of the query, either as a Result object or as a list of dictionaries.
        """
        stmt = lambda_stmt(lambda: select(cls))
        stmt = cls._apply_sti_subclass_filter(stmt)
        result = session.execute(stmt)
        return [r.as_python_dict() for r in result.scalars().all()] if as_python else result

    @classmethod
    async def get_all_async(
        cls,
        session: AsyncSession,
        as_python: bool = False,
    ) -> AsyncResult[Any] | list[dict[str, Any]]:
        """Asynchronously fetches all entries from the table.

        Args:
            session: The SQLAlchemy async session to use for the query.
            as_python: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            The result of the query, either as a Result object or as a list of dictionaries.
        """
        stmt = lambda_stmt(lambda: select(cls))
        stmt = cls._apply_sti_subclass_filter(stmt)
        result = await session.stream(stmt)
        return await gather(*[r.as_python_dict_async() async for r in result.scalars()]) if as_python else result

    # Instance Methods #
    def update_instance(
        self,
        dict_: dict[str, Any] | None = None,
        /,
        *,
        _format_entry: bool = True,
        **kwargs: Any,
    ) -> None:
        """Updates the row of the table with the provided dictionary or keyword arguments.

        Args:
            dict_: A dictionary of attributes/columns to update. Defaults to None.
            _format_entry: If True, formats the entry. Defaults to True.
            **kwargs: Additional keyword arguments for the attributes to update.
        """
        updates = self.to_sql_types(dict_, **kwargs) if _format_entry else ((dict_ or {}) | kwargs)
        if "id" in updates:
            del updates["id"]
        for key, value in updates.items():
            setattr(self, key, value)

    def as_sql_dict(self) -> dict[str, Any]:
        """Creates a dictionary of the table item as SQLAlchemy types.

        Returns:
            A dictionary representation of the table item as SQLAlchemy types.
        """
        return {n: getattr(self, n) for n in self.get_column_names()}

    async def as_sql_dict_async(self) -> dict[str, Any]:
        """Asynchronously creates a dictionary of the table item as SQLAlchemy types.

        Returns:
            A dictionary representation of the table item as SQLAlchemy types.
        """
        names = self.get_column_names()
        return dict(
            zip(
                names,
                await gather(*(getattr(self.awaitable_attrs, n) for n in names)),  # type: ignore[attr-defined]
                strict=True,
            )
        )

    def as_python_dict(self) -> dict[str, Any]:
        """Creates a dictionary of the table item as Python types.

        Returns:
            A dictionary representation of the table item as Python types.
        """
        return self.from_sql_types(self.as_sql_dict())

    async def as_python_dict_async(self) -> dict[str, Any]:
        """Asynchronously creates a dictionary of the table item as Python types.

        Returns:
            A dictionary representation of the table item as Python types.
        """
        return self.from_sql_types(await self.as_sql_dict_async())


class TableManifestation(BaseReducible):
    """An interface for a table implemented in an SQLAlchemy database.

    Attributes:
        _database: A weak reference to the SQAlchemy database to interface with.
    """

    # Attributes #
    _database: ReferenceType[Database] | None = None
    table_schema: type[BaseTableSchema]

    # Properties #
    @property
    def database(self) -> Database:
        """The database object associated with the table manifestation."""
        return self._database()  # type: ignore[return-value, misc]

    @database.setter
    def database(self, value: Any) -> None:
        """Sets the database object associated with the table_schema manifestation."""
        self._database = ReferenceType(value)

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        table_schema: type[DeclarativeBase] | None = None,
        database: Database | None = None,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initializes a new TableManifestation instance.

        Args:
            table_schema: The SQLAlchemy declarative table which this object act as the interface for.
            database: The SQAlchemy database to interface with.
            init: Determines if this object will construct.
            **kwargs: Additional keyword arguments.
        """
        # Parent Attributes #
        super().__init__(init=False)

        # Object Construction #
        if init:
            self.construct(table_schema, database, **kwargs)

    # Pickling
    def __getstate__(self) -> dict[str, Any] | tuple[dict[str, Any] | None, dict[str, Any]] | None:
        """Gets the object's state for pickling.

        Returns:
            The state returned will be either of the following types based on the presence of __dict__ and __slots__:
                None: __dict__ nor __slots__ are present.
                dict: __dict__ is present and __slots__ is not present.
                tuple[None, dict]: __dict__ is not present and __slots__ is present.
                tuple[dict, dict]: __dict__ is present and __slots__ is present.
        """
        state = super().__getstate__()
        if isinstance(state, dict):
            state["_database"] = self._database() if self._database is not None else None
        return state

    def __setstate__(self, state: Any) -> None:
        """Sets the object's state from a pickled state.

        By default, the state can be one of the following types with the corresponding behavior:
            None: Will not set any state.
            dict: Will set the __dict__ attribute to the state.
            tuple[None, dict]: Will set the slot values to the second dict of the tuple.
            tuple[dict, dict]: Will set the __dict__ attribute to the first dict of the tuple and set the slot values
                to the second dict of the tuple.

        Args:
            state: An object which can be used to set the state of this object.
        """
        # Remove strong reference
        db_ref = None
        if isinstance(state, dict):
            db_ref = state.pop("_database", None)

        # Set State
        super().__setstate__(state)

        # Set weak reference
        if db_ref is not None:
            self.database = db_ref

    # Instance Methods #
    # Construction/Destruction
    def construct(
        self,
        table_schema: type[DeclarativeBase] | None = None,
        database: Database | None = None,
        **kwargs: Any,
    ) -> None:
        """Constructs this object with the given arguments.

        Args:
            table_schema: The SQLAlchemy declarative table which this object act as the interface for.
            database: A reference to a BaseDatabase instance.
            **kwargs: Additional keyword arguments to pass to the superclass construct method.
        """
        if database is not None:
            self._database = ReferenceType(database)

        if table_schema is not None:
            self.table_schema = table_schema  # type: ignore[assignment]

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
        return self.database.create_session(*args, **kwargs)

    def create_async_session(self, *args: Any, **kwargs: Any) -> AsyncSession:
        """Creates a new asynchronous SQLAlchemy session.

        Args:
            *args : Positional arguments for session creation.
            **kwargs: Keyword arguments for session creation.

        Returns:
            AsyncSession: A new asynchronous SQLAlchemy session.
        """
        return self.database.create_async_session(*args, **kwargs)

    # Table
    # ExampleDatabaseSchema
    def to_sql_types(self, dict_: dict[str, Any] | None = None, /, **kwargs: Any) -> dict[str, Any]:
        """Casts Python types of an entry to SQLAlchemy types.

        Only table item elements (columns) which must cast to an SQLAlchemy type are cast to SQLAlchemy types.
        Additionally, all elements are optional, such that they do not need to be provided. This way any subset of the
        elements can cast. For example: when updating a table item, a few elements can updated without providing all
        elements.

        Args:
            dict_: A dictionary representing the entry with Python types.
            **kwargs: Additional keyword arguments for the entry.

        Returns:
            dict[str, Any]: A dictionary representing the entry with SQLAlchemy types.
        """
        return self.table_schema.to_sql_types(dict_, **kwargs)

    def from_sql_types(self, dict_: dict[str, Any] | None = None, /, **kwargs: Any) -> dict[str, Any]:
        """Casts SQLAlchemy types of an entry to Python types.

        Only table item elements (columns) which must cast to a Python type are cast to Python types. Additionally, all
        elements are optional, such that they do not need to be provided. This way any subset of the elements can cast.
        For example: when querying a table item, a few columns can be selected without providing all columns.

        Args:
            dict_: A dictionary representing the entry with SQLAlchemy types.
            **kwargs: Additional keyword arguments for the entry.

        Returns:
            dict[str, Any]: A dictionary representing the entry with Python types.
        """
        return self.table_schema.from_sql_types(dict_, **kwargs)

    def item_from_dict(
        self,
        dict_: dict[str, Any] | None = None,
        /,
        *,
        _format_dict: bool = True,
        **kwargs: Any,
    ) -> BaseTableSchema:
        """Creates an item from a dictionary entry or keyword arguments.

        Args:
            dict_: A dictionary representing the entry.
            _format_dict: If True, formats the entry.
            **kwargs: Additional keyword arguments for the entry.

        Returns:
            The new item from the table.
        """
        return self.table_schema.item_from_dict(dict_, _format_dict=_format_dict, **kwargs)

    # Modification
    def insert(
        self,
        item: Any,
        session: Session | None = None,
        as_dict: bool = False,
        begin: bool = False,
    ) -> None:
        """Inserts an item into the table.

        Args:
            item: The item to insert can be either an item or a dict. Defaults to None.
            session: The SQLAlchemy session to use for the operation.
            as_dict: If True, creates the item from the entry dictionary. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            self.table_schema.insert(session, item, as_dict=as_dict, begin=begin)
        else:
            with self.create_session() as session:
                self.table_schema.insert(session, item, as_dict=as_dict, begin=True)

    async def insert_async(
        self,
        item: Any,
        session: AsyncSession | None = None,
        as_dict: bool = False,
        begin: bool = False,
    ) -> None:
        """Asynchronously inserts an item into the table.

        Args:
            item: The item to insert can be either an item or a dict. Defaults to None.
            session: The SQLAlchemy session to use for the operation.
            as_dict: If True, creates the item from the entry dictionary. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            await self.table_schema.insert_async(session, item, as_dict=as_dict, begin=begin)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.insert_async(session, item, as_dict=as_dict, begin=True)

    def insert_all(
        self,
        items: Iterable[Any],
        session: Session | None = None,
        as_dict: bool = False,
        begin: bool = False,
    ) -> None:
        """Inserts multiple items into the table.

        Args:
            items: The items to insert.
            session: The SQLAlchemy session to use for the operation.
            as_dict: If True, creates the items from the entry dictionaries. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            self.table_schema.insert_all(session, items, as_dict=as_dict, begin=begin)
        else:
            with self.create_session() as session:
                self.table_schema.insert_all(session, items, as_dict=as_dict, begin=True)

    async def insert_all_async(
        self,
        items: Iterable[Any],
        session: AsyncSession | None = None,
        as_dict: bool = False,
        begin: bool = False,
    ) -> None:
        """Asynchronously inserts multiple items into the table.

        Args:
            items: The items to insert.
            session: The SQLAlchemy async session to use for the operation.
            as_dict: If True, creates the items from the entry dictionaries. Defaults to False.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            await self.table_schema.insert_all_async(session, items, as_dict=as_dict, begin=begin)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.insert_all_async(session, items, as_dict=as_dict, begin=True)

    def upsert(
        self,
        entry: dict[str, Any],
        session: Session | None = None,
        key: str = "id",
        begin: bool = False,
    ) -> None:
        """Updates an entry in the table if it exists, otherwise, creates a new entry.

        Args:
            entry: A dictionary representing the entry to update. Defaults to None.
            session: The SQLAlchemy session to use for the operation.
            key: The key (column name) to search by. Defaults to "id".
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            self.table_schema.upsert(session, entry, key=key, begin=begin)
        else:
            with self.create_session() as session:
                self.table_schema.upsert(session, entry, key=key, begin=True)

    async def upsert_async(
        self,
        entry: dict[str, Any],
        session: AsyncSession | None = None,
        key: str = "id",
        begin: bool = False,
    ) -> None:
        """Asynchronously, updates an entry in the table if it exists, otherwise, creates a new entry.

        Args:
            entry: A dictionary representing the entry to update. Defaults to None.
            session: The SQLAlchemy async session to use for the operation.
            key: The key (column name) to search by. Defaults to "id".
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            await self.table_schema.upsert_async(session, entry, key, begin)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.upsert_async(session, entry, key, begin=True)

    def upsert_all(
        self,
        entries: Iterable[dict[str, Any]],
        session: Session | None = None,
        key: str = "id",
        begin: bool = False,
    ) -> None:
        """Updates multiple entries in the table if they exist, otherwise, creates new entries.

        Args:
            entries: A list of dictionaries representing the entries to update. Defaults to None.
            session: The SQLAlchemy session to use for the operation.
            key: The key (column name) to search by. Defaults to "id".
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            self.table_schema.upsert_all(session, entries, key, begin=begin)
        else:
            with self.create_session() as session:
                self.table_schema.upsert_all(session, entries, key, begin=True)

    async def upsert_all_async(
        self,
        entries: Iterable[dict[str, Any]],
        session: AsyncSession | None = None,
        key: str = "id",
        begin: bool = False,
    ) -> None:
        """Asynchronously, updates multiple entries in the table if they exist, otherwise, creates new entries.

        Args:
            entries: A list of dictionaries representing the entries to update. Defaults to None.
            session: The SQLAlchemy async session to use for the operation.
            key: The key (column name) to search by. Defaults to ``"id"``.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            await self.table_schema.upsert_all_async(session, entries, key, begin=begin)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.upsert_all_async(session, entries, key, begin=True)

    def delete(
        self,
        item: BaseTableSchema,
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
            self.table_schema.delete(session, item, begin=begin)
        else:
            with self.create_session() as session:
                self.table_schema.delete(session, item, begin=True)

    async def delete_async(
        self,
        item: BaseTableSchema,
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
            await self.table_schema.delete_async(session, item, begin=begin)
        else:
            async with self.create_async_session() as session:
                await self.table_schema.delete_async(session, item, begin=True)

    # Queries
    def count(self, session: Session | None = None) -> int:
        """Counts the number of entries in the table.

        Args:
            session: The SQLAlchemy session to use for the query.

        Returns:
            The number of entries in the table.
        """
        if session is not None:
            return self.table_schema.count(session)
        else:
            with self.create_session() as session:
                return self.table_schema.count(session)

    async def count_async(self, session: AsyncSession | None = None) -> int:
        """Asynchronously counts the number of entries in the table.

        Args:
            session: The SQLAlchemy async session to use for the query.

        Returns:
            The number of entries in the table.
        """
        if session is not None:
            return await self.table_schema.count_async(session)
        else:
            async with self.create_async_session() as session:
                return await self.table_schema.count_async(session)

    def get_by_id(self, id_: Any, session: Session | None = None, as_python: bool = False) -> Any:
        """Fetches an entry from the table by its ID.

        Args:
            id_: The ID of the entry to search for.
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns a dictionary representing the entry; otherwise, returns the item.

        Returns:
            The item from the table or its dictionary representation.
        """
        if session is not None:
            return self.table_schema.get_by_id(session, id_, as_python=as_python)
        else:
            with self.create_session() as session:
                return self.table_schema.get_by_id(session, id_, as_python=as_python)

    async def get_by_id_async(self, id_: Any, session: AsyncSession | None = None, as_python: bool = False) -> Any:
        """Asynchronously fetches an entry from the table by its ID.

        Args:
            id_: The ID of the entry to search for.
            session: The SQLAlchemy async session to use for the query.
            as_python: If True, returns a dictionary representing the entry; otherwise, returns the item.

        Returns:
            The item from the table or its dictionary representation.
        """
        if session is not None:
            return await self.table_schema.get_by_id_async(session, id_, as_python=as_python)
        else:
            async with self.create_async_session() as session:
                return await self.table_schema.get_by_id_async(session, id_, as_python=as_python)

    def get_by(
        self,
        column_name: str,
        value: Any,
        session: Session | None = None,
        as_python: bool = False,
    ) -> Result[Any] | list[Any]:
        """Fetches all entries from the table by a specific column value.

        Args:
            column_name: The name of the column to search by.
            value: The value to search for.
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            The result of the query, either as a Result object or as a list.
        """
        if session is not None:
            return self.table_schema.get_by(session, column_name, value, as_python=as_python)
        else:
            with self.create_session() as session:
                result = self.table_schema.get_by(session, column_name, value, as_python=as_python)
                return list(result.scalars().all()) if not as_python and isinstance(result, Result) else result

    async def get_by_async(
        self,
        column_name: str,
        value: Any,
        session: AsyncSession | None = None,
        as_python: bool = False,
    ) -> AsyncResult[Any] | list[Any]:
        """Asynchronously fetches all entries from the table by a specific column value.

        Args:
            column_name: The name of the column to search by.
            value: The value to search for.
            session: The SQLAlchemy async session to use for the query.
            as_python: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            The result of the query, either as a Result object or as a list.
        """
        if session is not None:
            return await self.table_schema.get_by_async(session, column_name, value, as_python=as_python)
        else:
            async with self.create_async_session() as session:
                result = await self.table_schema.get_by_async(session, column_name, value, as_python=as_python)
                if not as_python and isinstance(result, AsyncResult):
                    return list(await result.scalars().all())
                return result

    def get_all(self, session: Session | None = None, as_python: bool = False) -> Result[Any] | list[Any]:
        """Fetches all entries from the table.

        Args:
            session: The SQLAlchemy session to use for the query.
            as_python: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            The result of the query, either as a Result object or as a list.
        """
        if session is not None:
            return self.table_schema.get_all(session, as_python=as_python)
        else:
            with self.create_session() as session:
                result = self.table_schema.get_all(session, as_python=as_python)
                return list(result.scalars().all()) if not as_python and isinstance(result, Result) else result

    async def get_all_async(
        self,
        session: AsyncSession | None = None,
        as_python: bool = False,
    ) -> AsyncResult[Any] | list[Any]:
        """Asynchronously, fetches all entries from the table.

        Args:
            session: The SQLAlchemy async session to use for the query.
            as_python: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
           The result of the query, either as a Result object or as a list.
        """
        if session is not None:
            return await self.table_schema.get_all_async(session, as_python=as_python)
        else:
            async with self.create_async_session() as session:
                result = await self.table_schema.get_all_async(session, as_python=as_python)
                if not as_python and isinstance(result, AsyncResult):
                    return list(await result.scalars().all())
                return result

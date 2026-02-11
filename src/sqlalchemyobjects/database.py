"""database.py
Manages the database including creating, opening, and modifying the database.

This module contains the Database class, which is a wrapper around SQLAlchemy's Engine and Session objects. It provides
a convenient interface for managing the database, including creating the database, opening connections, and managing
sessions.
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
import asyncio
from asyncio import run
from collections.abc import Iterable
from enum import StrEnum
from pathlib import Path
from typing import Any, Self

# Third-Party Packages #
from baseobjects import BaseReducible
from sqlalchemy import Engine, create_engine
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

# Local Packages #
from .tables import TableManifestation


# Definitions #
# Classes #
class SQLAlchemyBackends(StrEnum):
    """SQLAlchemy Engine Backends."""

    SQLITE = "sqlite://"
    POSTGRESQL = "postgresql://"
    POSTGRESQL_PSYCOPG2 = "postgresql+psycopg2://"
    POSTGRESQL_PG8000 = "postgresql+pg8000://"
    MYSQL = "mysql://"
    MYSQL_MYSQLDB = "mysql+mysqldb://"
    MYSQL_PYMYSQL = "mysql+pymysql://"
    ORACLE = "oracle+oracledb://"
    MSSQL = "mssql+pyodbc://"


class SQLAlchemyAsyncBackends(StrEnum):
    """SQLAlchemy Engine Async Backends."""

    SQLITE = "sqlite+aiosqlite://"
    POSTGRESQL = "postgresql+asyncpg://"
    POSTGRESQL_PSYCOPG2 = "postgresql+asyncpg://"
    MYSQL = "mysql+aiomysql://"
    MYSQL_MYSQLDB = "mysql+aiomysql://"
    ORACLE = "oracle+oracledb://"


class SQLiteModes(StrEnum):
    """SQLite URI Mode Strings."""

    RO = "ro"
    RW = "rw"
    RWC = "rwc"
    MEMORY = "memory"


class Database(BaseReducible):
    """Manages the database including creating, opening, and modifying the database.

    Attributes:
        _backend: The SQLAlchemy engine backend.
        _async_backend: The SQLAlchemy engine async backend.
        _path: The file path to the database.
        _engine: The SQLAlchemy engine for synchronous operations.
        _async_engine: The SQLAlchemy engine for asynchronous operations.
        _session_maker: Factory for creating synchronous sessions.
        _async_session_maker: Factory for creating asynchronous sessions.
    """

    # Attributes #
    _backend: SQLAlchemyBackends = SQLAlchemyBackends.SQLITE
    _async_backend: SQLAlchemyAsyncBackends = SQLAlchemyAsyncBackends.SQLITE
    _path: Path | None = None
    url: str | None = None
    _mode: SQLiteModes = SQLiteModes.RWC

    _engine: Engine | None = None
    _async_engine: AsyncEngine | None = None

    session_maker_kwargs: dict[str, Any] = {}
    _session_maker: sessionmaker[Session] | None = None

    async_session_maker_kwargs: dict[str, Any] = {}
    _async_session_maker: async_sessionmaker[AsyncSession] | None = None

    schema: type[DeclarativeBase] | None = None
    table_map: dict[str, tuple[type[TableManifestation], type[DeclarativeBase], dict[str, Any]]] = {}
    tables: dict[str, TableManifestation]

    # Properties #
    @property
    def backend(self) -> str:
        """The SQLAlchemy engine backend."""
        return self._backend.value

    @backend.setter
    def backend(self, value: SQLAlchemyBackends | str) -> None:
        """Sets the SQLAlchemy engine backend."""
        self._backend = SQLAlchemyBackends(value) if isinstance(value, str) else value

    @property
    def async_backend(self) -> str:
        """The SQLAlchemy engine async backend."""
        return self._async_backend.value

    @async_backend.setter
    def async_backend(self, value: SQLAlchemyAsyncBackends | str) -> None:
        """Sets the SQLAlchemy engine async backend."""
        self._async_backend = SQLAlchemyAsyncBackends(value) if isinstance(value, str) else value

    @property
    def path(self) -> Path | None:
        """The path to the database file."""
        return self._path

    @path.setter
    def path(self, value: str | Path | None) -> None:
        """Sets the path to the database file.

        Args:
            value: The new path to the database file.
        """
        if isinstance(value, Path) or value is None:
            self._path = value
        else:
            self._path = Path(value)

    @property
    def mode(self) -> str:
        """The mode to use for the database."""
        return self._mode.value

    @mode.setter
    def mode(self, value: SQLiteModes | str) -> None:
        """Sets the mode to use for the database.

        Raises:
            ValueError: If the database is open.
        """
        if self.is_open:
            msg = "Cannot change mode while the database is open. Close the database first."
            raise ValueError(msg)
        self._mode = SQLiteModes(value) if isinstance(value, str) else value

    @property
    def full_url(self) -> str:
        """The full URL to the database.

        Raises:
            ValueError: If both path and URL are set, or if the backend is unsupported for path, or if path is not set.
        """
        if self._path is not None and self.url is not None:
            msg = "Cannot have both a path and a URL"
            raise ValueError(msg)
        if self._path is not None:
            if self._backend == SQLAlchemyBackends.SQLITE:
                url = self._path.as_posix()
            else:
                msg = f"Unsupported backend for path: {self._backend}"
                raise ValueError(msg)
        elif self.url is not None:
            url = self.url
        else:
            msg = "Path is not set"
            raise ValueError(msg)

        if self._backend == SQLAlchemyBackends.SQLITE:
            if "mode=" not in url:
                url = f"{url}{'&' if '?' in url else '?'}mode={self._mode.value}"

            if "://" not in url:
                if not url.startswith("/"):
                    url = "/" + url
                return self._backend.value + url

        if "://" in url:
            if url.startswith(self._async_backend.value):
                return url.replace(self._async_backend.value, self._backend.value, 1)
            return url
        else:
            return self._backend.value + url

    @property
    def async_full_url(self) -> str:
        """The full URL to the database for the async engine.

        Raises:
            ValueError: If both path and URL are set, or if the backend is unsupported for path, or if path is not set.
        """
        if self._path is not None and self.url is not None:
            msg = "Cannot have both a path and a URL"
            raise ValueError(msg)
        if self._path is not None:
            if self._async_backend == SQLAlchemyAsyncBackends.SQLITE:
                url = self._path.as_posix()
            else:
                msg = f"Unsupported backend for path: {self._async_backend}"
                raise ValueError(msg)
        elif self.url is not None:
            url = self.url
        else:
            msg = "Path is not set"
            raise ValueError(msg)

        if self._async_backend == SQLAlchemyAsyncBackends.SQLITE:
            if "mode=" not in url:
                url = f"{url}{'&' if '?' in url else '?'}mode={self._mode.value}"

            if "://" not in url:
                if not url.startswith("/"):
                    url = "/" + url
                return self._async_backend.value + url

        if "://" in url:
            if url.startswith(self._backend.value) and not url.startswith(self._async_backend.value):
                return url.replace(self._backend.value, self._async_backend.value, 1)
            return url
        else:
            return self._async_backend.value + url

    @property
    def is_open(self) -> bool:
        """Checks if the database is open."""
        return self._engine is not None or self._async_engine is not None

    @property
    def is_async(self) -> bool:
        """Checks if the asynchronous engine is available."""
        return self._async_engine is not None

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        path: str | Path | None = None,
        schema: type[DeclarativeBase] | None = None,
        table_map: dict[str, tuple[type[TableManifestation], type[DeclarativeBase], dict[str, Any]]] | None = None,
        open_: bool = False,
        mode: SQLiteModes | str | None = None,
        create: bool = False,
        async_engine: bool = False,
        *,
        init: bool = True,
        **kwargs: Any,
    ) -> None:
        """Initializes the Database object.

        Args:
            path: The path to the database file.
            schema: The database schema class.
            table_map: A map which outlines which table are within this database.
            open_: Whether to open the database. Defaults to False.
            create: Whether to create the database. Defaults to False.
            mode: When the database is SQLite, the mode to use. Defaults to None.
            async_engine: Whether to create an asynchronous engine. Defaults to False.
            init: Whether to initialize the object.
            **kwargs: Additional keyword arguments.
        """
        # New Attributes #
        self.tables = {}
        self.session_maker_kwargs = self.session_maker_kwargs.copy()
        self.async_session_maker_kwargs = self.async_session_maker_kwargs.copy()

        # Parent Attributes #
        super().__init__()

        # Object Construction #
        if init:
            self.construct(
                path,
                schema,
                table_map,
                open_,
                mode,
                create,
                async_engine=async_engine,
                **kwargs,
            )

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
            state["is_open"] = self.is_open
            state["is_async"] = self.is_async
            for name in ("_engine", "_async_engine", "_session_maker", "_async_session_maker"):
                if name in state:
                    del state[name]
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
        # Remove "open" attribute
        was_open = False
        was_async = False
        if isinstance(state, dict):
            was_open = state.pop("is_open", False)
            was_async = state.pop("is_async", False)

        # Set State
        super().__setstate__(state)

        # Open the File if it was open
        if was_open:
            self.open(async_engine=was_async)

    # Context Managers
    def __enter__(self) -> Self:
        """Enters the context manager.

        Returns:
            The database object.
        """
        if not self.is_open:
            self.open()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exits the context manager."""
        self.close()

    async def __aenter__(self) -> Self:
        """Enters the asynchronous context manager.

        Returns:
            The database object.
        """
        if not self.is_open or self._async_engine is None:
            self.open(async_engine=True)
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Exits the asynchronous context manager."""
        await self.close_async()

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        path: str | Path | None = None,
        schema: type[DeclarativeBase] | None = None,
        table_map: dict[str, tuple[type[TableManifestation], type[DeclarativeBase], dict[str, Any]]] | None = None,
        open_: bool = False,
        mode: SQLiteModes | str | None = None,
        create: bool = False,
        async_engine: bool = False,
        **kwargs: Any,
    ) -> None:
        """Constructs the Database object.

        Args:
            path: The path to the database file.
            schema: The database schema class.
            table_map: A map which outlines which table are within this database.
            open_: Whether to open the database. Defaults to False.
            mode: When the database is SQLite, the mode to use. Defaults to None.
            create: Whether to create the database. Defaults to False.
            async_engine: Whether to create an asynchronous engine. Defaults to False.
            **kwargs: Additional keyword arguments.
        """
        if path is not None:
            self.path = path

        if mode is not None:
            self.mode = mode

        if schema is not None:
            self.schema = schema

        if table_map is not None:
            self.table_map = table_map

        self.manifest_tables()

        if create:
            self.create_database(async_engine=async_engine, **kwargs)
        elif open_:
            self.open(async_engine=async_engine, **kwargs)

        if create and not open_:
            self.close()

        super().construct()

    # Engine
    def create_engine(
        self,
        path: Path | None = None,
        url: str | None = None,
        mode: SQLiteModes | str | None = None,
        async_engine: bool = False,
        **kwargs: Any,
    ) -> None:
        """Creates the SQLAlchemy engine.

        Args:
            path: The path to the database.
            url: The URL to the database.
            mode: When the database is SQLite, the mode to use. Defaults to None.
            async_engine: Whether to create an asynchronous engine. Defaults to False.
            **kwargs: Additional keyword arguments.
        """
        if mode is not None:
            self.mode = mode

        if url is not None:
            self.url = url
            self.path = None
        elif path is not None:
            self.path = path
            self.url = None

        if self._path is not None and (
            self._backend == SQLAlchemyBackends.SQLITE or self._async_backend == SQLAlchemyAsyncBackends.SQLITE
        ):
            self._path.parent.mkdir(parents=True, exist_ok=True)

        self._engine = create_engine(self.full_url, **kwargs)
        self._async_engine = create_async_engine(self.async_full_url, **kwargs) if async_engine else None

    # Database
    def create_database(
        self,
        path: str | Path | None = None,
        mode: SQLiteModes | str | None = None,
        async_engine: bool = False,
        **kwargs: Any,
    ) -> None:
        """Creates the database.

        Args:
            path: The path to the database.
            mode: When the database is SQLite, the mode to use. Defaults to None.
            async_engine: Whether to create an asynchronous engine. Defaults to False.
            **kwargs: Additional keyword arguments.
        """
        if path is not None and path != self._path:
            self.path = path
            if self._engine is not None:
                self.close()

        if self._engine is None:
            self.create_engine(mode=mode, async_engine=async_engine, **kwargs)
            self.build_session_maker()
            if self._async_engine is not None:
                self.build_async_session_maker()

        if self.schema is not None and self._engine is not None:
            self.schema.metadata.create_all(self._engine)

    async def create_database_async(self, path: str | Path | None = None, **kwargs: Any) -> None:
        """Asynchronously creates the database.

        Args:
            path: The path to the database.
            **kwargs: Additional keyword arguments.
        """
        if path is not None and path != self._path:
            self.path = path
            if self._engine or self._async_engine is not None:
                await self.close_async()

        if self._async_engine is None:
            self.create_engine(async_engine=True, **kwargs)
            self.build_session_maker()
            self.build_async_session_maker()

        if self._async_engine is not None and self.schema is not None:
            async with self._async_engine.begin() as conn:
                await conn.run_sync(self.schema.metadata.create_all)

    def open(self, mode: SQLiteModes | str | None = None, async_engine: bool = False, **kwargs: Any) -> Database:
        """Opens the database.

        Args:
            mode: When the database is SQLite, the mode to use. Defaults to None.
            async_engine: Whether to create an asynchronous engine. Defaults to False.
            **kwargs: Additional keyword arguments.

        Returns:
            The opened database.
        """
        if (not async_engine and self._engine is not None) or (async_engine and self._async_engine is not None):
            return self

        self.create_engine(mode=mode, async_engine=async_engine, **kwargs)
        self.build_session_maker()
        if self._async_engine is not None:
            self.build_async_session_maker()
        return self

    def close(self) -> bool:
        """Closes the database.

        Returns:
            True if the database is closed, False otherwise.
        """
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
        self._session_maker = None
        if self._async_engine is not None:
            coro = self._async_engine.dispose()
            try:
                run(coro)
            except RuntimeError:
                try:
                    loop = asyncio.get_running_loop()
                    if loop.is_running():
                        task = loop.create_task(coro)
                        # We don't want to wait for the task to complete here, as this is the synchronous close method.
                        # However, we should keep a reference to it to avoid it being garbage collected.
                        if not hasattr(self, "_closing_tasks"):
                            self._closing_tasks = set()
                        self._closing_tasks.add(task)
                        task.add_done_callback(self._closing_tasks.discard)
                    else:
                        coro.close()
                except RuntimeError:
                    coro.close()
            except Exception:
                coro.close()
                raise
            self._async_engine = None
        self._async_session_maker = None
        return self._engine is None and self._async_engine is None

    async def close_async(self) -> bool:
        """Asynchronously closes the database.

        Returns:
            True if the database is closed, False otherwise.
        """
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
        if self._async_engine is not None:
            await self._async_engine.dispose()
            self._async_engine = None
        self._async_session_maker = None
        return self._engine is None and self._async_engine is None

    # Session
    def build_session_maker(self, **kwargs: Any) -> sessionmaker[Session]:
        """Builds the synchronous session maker.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            The synchronous session maker.
        """
        self._session_maker = sessionmaker(self._engine, **kwargs)
        return self._session_maker

    def build_async_session_maker(self, **kwargs: Any) -> async_sessionmaker[AsyncSession]:
        """Builds the asynchronous session maker.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            The asynchronous session maker.
        """
        self._async_session_maker = async_sessionmaker(self._async_engine, **kwargs)
        return self._async_session_maker

    def create_session(self, *args: Any, **kwargs: Any) -> Session:
        """Creates a synchronous session.

        Args:
            *args: Positional arguments for session creation.
            **kwargs: Keyword arguments for session creation.

        Returns:
            A new synchronous session.

        Raises:
            OSError: If the database is not open.
        """
        if not self.is_open:
            msg = "Database not open"
            raise OSError(msg)

        if (args or kwargs) or self._session_maker is None:
            return Session(self._engine, *args, **kwargs)
        return self._session_maker()

    def create_async_session(self, *args: Any, **kwargs: Any) -> AsyncSession:
        """Creates an asynchronous session.

        Args:
            *args: Positional arguments for session creation.
            **kwargs: Keyword arguments for session creation.

        Returns:
            A new asynchronous session.

        Raises:
            OSError: If the database is not open.
        """
        if not self.is_open:
            msg = "Database not open"
            raise OSError(msg)

        if self._async_engine is None:
            msg = "Async engine is not available"
            raise OSError(msg)

        if (args or kwargs) or self._async_session_maker is None:
            return AsyncSession(self._async_engine, *args, **kwargs)
        return self._async_session_maker()

    # Tables
    def manifest_tables(
        self,
        table_map: dict[str, tuple[type[TableManifestation], type[DeclarativeBase], dict[str, Any]]] | None = None,
    ) -> None:
        """Manifests the table from the table map.

        Args:
            table_map: The map of tables to manifest the table from. If None, uses the default table map.
        """
        if table_map is None:
            table_map = self.table_map
        for name, (table_type, table_schema, kwargs) in table_map.items():
            self.tables[name] = table_type(table_schema=table_schema, database=self, **kwargs)

    def build_tables(self) -> None:
        """Builds the tables."""
        for table in self.tables.values():
            table.build()

    def load_tables(self) -> None:
        """Loads the tables."""
        for table in self.tables.values():
            table.load()

    # Table Operations
    def insert(self, item: Any, session: Session | None = None, begin: bool = False) -> None:
        """Inserts an item into the database.

        Args:
            item: The item to insert.
            session: The SQLAlchemy session to use for the operation.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            if begin:
                with session.begin():
                    session.add(item)
            else:
                session.add(item)
        else:
            with self.create_session() as session:
                with session.begin():
                    session.add(item)

    async def insert_async(self, item: Any, session: AsyncSession | None = None, begin: bool = False) -> None:
        """Asynchronously inserts an item into the database.

        Args:
            item: The item to insert.
            session: The SQLAlchemy session to use for the operation.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            if begin:
                async with session.begin():
                    session.add(item)
            else:
                session.add(item)
        else:
            async with self.create_async_session() as session:
                async with session.begin():
                    session.add(item)

    def insert_all(self, items: Iterable[Any], session: Session | None = None, begin: bool = False) -> None:
        """Inserts items into the database.

        Args:
            items: The items to insert.
            session: The SQLAlchemy session to use for the operation.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            if begin:
                with session.begin():
                    session.add_all(items)
            else:
                session.add_all(items)
        else:
            with self.create_session() as session:
                with session.begin():
                    session.add_all(items)

    async def insert_all_async(
        self,
        items: Iterable[Any],
        session: AsyncSession | None = None,
        begin: bool = False,
    ) -> None:
        """Asynchronously inserts items into the database.

        Args:
            items: The items to insert.
            session: The SQLAlchemy session to use for the operation.
            begin: If True, begins a transaction for the operation. Defaults to False.
        """
        if session is not None:
            if begin:
                async with session.begin():
                    session.add_all(items)
            else:
                session.add_all(items)
        else:
            async with self.create_async_session() as session:
                async with session.begin():
                    session.add_all(items)

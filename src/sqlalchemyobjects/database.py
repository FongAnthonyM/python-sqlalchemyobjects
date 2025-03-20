"""database.py
Manages the database including creating, opening, and modifying the database.
"""
# Package Header #
from .header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
from asyncio import run
import pathlib
from pathlib import Path
from typing import Any

# Third-Party Packages #
from baseobjects import BaseObject
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker

# Local Packages #
from .tables import TableManifestation


# Definitions #
# Classes #
class Database(BaseObject):
    """Manages the database including creating, opening, and modifying the database.

    Attributes:
        _path: The file path to the database.
        url: The URL to the database.
        _engine: The SQLAlchemy engine for synchronous operations.
        _async_engine: The SQLAlchemy engine for asynchronous operations.
        session_maker_kwargs: Keyword arguments for the synchronous session maker.
        _session_maker: Factory for creating synchronous sessions.
        async_session_maker_kwargs: Keyword arguments for the asynchronous session maker.
        _async_session_maker: Factory for creating asynchronous sessions.
        schema: The database schema class.
        table_map: A map which outlines which table are within this database.
        tables: A dictionary of tables within this database.

    Args:
        path: The path to the database file.
        schema: The database schema class.
        table_map: A map which outlines which table are within this database.
        open_: Whether to open the database. Defaults to False.
        create: Whether to create the database. Defaults to False.
        init: Whether to initialize the object.
        **kwargs: Additional keyword arguments.
    """
    # Attributes #
    _path: Path | None = None
    url: str | None = None

    _engine: Engine | None = None
    _async_engine: AsyncEngine | None = None

    session_maker_kwargs: dict[str, Any] = {}
    _session_maker: sessionmaker | None = None

    async_session_maker_kwargs: dict[str, Any] = {}
    _async_session_maker: async_sessionmaker | None = None

    schema: type[DeclarativeBase] | None = None
    table_map: dict[str, tuple[type[TableManifestation], type[DeclarativeBase], dict[str, Any]]] = {}
    tables: dict[str, TableManifestation]

    # Properties #
    @property
    def path(self) -> Path:
        """The path to the database file.

        Returns:
            pathlib.Path: The path to the database file.
        """
        return self._path

    @path.setter
    def path(self, value: str | Path) -> None:
        """Sets the path to the database file.

        Args:
            value: The new path to the database file.
        """
        if isinstance(value, pathlib.Path) or value is None:
            self._path = value
        else:
            self._path = pathlib.Path(value)

    @property
    def is_open(self) -> bool:
        """Checks if the database is open.

        Returns:
            bool: True if the database is open, False otherwise.
        """
        return self._engine is not None and self._async_engine is not None

    # Magic Methods #
    # Construction/Destruction
    def __init__(
        self,
        path: str | Path | None = None,
        schema: type[DeclarativeBase] | None = None,
        table_map: dict[str, tuple[type[TableManifestation], type[DeclarativeBase], dict[str, Any]]] | None = None,
        open_: bool = False,
        create: bool = False,
        *,
        init: bool = True,
        **kwargs,
    ) -> None:
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
                create,
                **kwargs,
            )

    # Pickling
    def __getstate__(self) -> dict[str, Any]:
        """Creates a dictionary of attributes which can be used to rebuild this object.

        Returns:
            dict: A dictionary of this object's attributes.
        """
        state = super().__getstate__()
        state["is_open"] = self.is_open
        for name in ("_engine", "_async_engine", "_session_maker", "_async_session_maker"):
            if name in state:
                del state[name]
        return state

    def __setstate__(self, state: dict[str, Any]) -> None:
        """Builds this object based on a dictionary of corresponding attributes.

        Args:
            state (dict[str, Any]): The attributes to build this object from.
        """
        was_open = state.pop("is_open")
        super().__setstate__(state=state)
        for table in self.tables.values():
            table.database = self
        if was_open:
            self.open()

    # Instance Methods #
    # Constructors/Destructors
    def construct(
        self,
        path: str | pathlib.Path | None = None,
        schema: type[DeclarativeBase] | None = None,
        table_map: dict[str, tuple[type[TableManifestation], type[DeclarativeBase], dict[str, Any]]] | None = None,
        open_: bool = False,
        create: bool = False,
        **kwargs,
    ) -> None:
        """Constructs the Database object.

        Args:
            path: The path to the database file.
            schema: The database schema class.
            table_map: A map which outlines which table are within this database.
            open_: Whether to open the database. Defaults to False.
            create: Whether to create the database. Defaults to False.
            **kwargs: Additional keyword arguments.
        """
        if path is not None:
            self.path = path

        if schema is not None:
            self.schema = schema

        if table_map is not None:
            self.table_map = table_map

        self.manifest_tables()

        if create:
            self.create_database()
        elif open_:
            self.open(**kwargs)

        if create and not open_:
            self.close()

        super().construct()

    # Engine
    def create_engine(self, path: Path | None = None, url: str | None = None, **kwargs) -> None:
        """Creates the SQLAlchemy engine.

        Args:
            path: The path to the database.
            url: The URL to the database.
            **kwargs: Additional keyword arguments.
        """
        if url is None:
            path_str = path.as_posix() if path else self._path.as_posix()
            location = f"sqlite:///{path_str}"
            location_async = f"sqlite+aiosqlite:///{path_str}"
        else:
            location = url
            location_async = url.replace("sqlite", "sqlite+aiosqlite")

        self._engine = create_engine(location, **kwargs)
        self._async_engine = create_async_engine(location_async, **kwargs)

    # Database
    def create_database(self, path: str | pathlib.Path | None = None, **kwargs) -> None:
        """Creates the database.

        Args:
            path: The path to the database.
            **kwargs: Additional keyword arguments.
        """
        if path is not None:
            self.path = path

        if self._engine is None or path is not None:
            self.create_engine(**kwargs)
            self.build_session_maker()
            self.build_async_session_maker()

        self.schema.metadata.create_all(self._engine)

    async def create_database_async(self, path: str | pathlib.Path | None = None, **kwargs) -> None:
        """Asynchronously creates the database.

        Args:
            path: The path to the database.
            **kwargs: Additional keyword arguments.
        """
        if path is not None:
            self.path = path

        if self._async_engine is None or path is not None:
            self.create_engine(**kwargs)
            self.build_session_maker()
            self.build_async_session_maker()

        async with self._async_engine.begin() as conn:
            await conn.run_sync(self.schema.metadata.create_all)

    def open(self, **kwargs: Any) -> "Database":
        """Opens the database.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            Database: The opened database.
        """
        self.create_engine(**kwargs)
        self.build_session_maker()
        self.build_async_session_maker()
        return self

    def close(self) -> bool:
        """Closes the database.

        Returns:
            bool: True if the database is closed, False otherwise.
        """
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
        self._session_maker = None
        if self._async_engine is not None:
            self._async_engine.dispose()
            self._async_engine = None
        self._async_session_maker = None
        return self._engine is None

    async def close_async(self) -> bool:
        """Asynchronously closes the database.

        Returns:
            bool: True if the database is closed, False otherwise.
        """
        if self._engine is not None:
            self._engine.dispose()
            self._engine = None
        if self._async_engine is not None:
            await self._async_engine.dispose()
            self._async_engine = None
        self._async_session_maker = None
        return self._engine is None

    # Session
    def build_session_maker(self, **kwargs) -> sessionmaker:
        """Builds the synchronous session maker.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            sessionmaker: The synchronous session maker.
        """
        self._session_maker = sessionmaker(self._engine, **kwargs)
        return self._session_maker

    def build_async_session_maker(self, **kwargs) -> async_sessionmaker:
        """Builds the asynchronous session maker.

        Args:
            **kwargs: Additional keyword arguments.

        Returns:
            async_sessionmaker: The asynchronous session maker.
        """
        self._async_session_maker = async_sessionmaker(self._async_engine, **kwargs)
        return self._async_session_maker

    def create_session(self, *args: Any, **kwargs: Any) -> Session:
        """Creates a synchronous session.

        Args:
            *args: Positional arguments for session creation.
            **kwargs: Keyword arguments for session creation.

        Returns:
            Session: A new synchronous session.

        Raises:
            IOError: If the database is not open.
        """
        if not self.is_open:
            raise IOError("Database not open")
        return Session(self._engine, *args, **kwargs) if args or kwargs else self._session_maker()

    def create_async_session(self, *args: Any, **kwargs: Any) -> AsyncSession:
        """Creates an asynchronous session.

        Args:
            *args: Positional arguments for session creation.
            **kwargs: Keyword arguments for session creation.

        Returns:
            AsyncSession: A new asynchronous session.

        Raises:
            IOError: If the database is not open.
        """
        if not self.is_open:
            raise IOError("Database not open")
        return AsyncSession(self._async_engine, *args, **kwargs) if args or kwargs else self._async_session_maker()

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
        """Builds the tables"""
        for table in self.tables.values():
            table.build()

    def load_tables(self) -> None:
        """Loads the tables."""
        for table in self.tables.values():
            table.build()

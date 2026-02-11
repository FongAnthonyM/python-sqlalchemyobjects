"""databasetestsuite.py
Test suites for the Database class.
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
import copy
import pickle
from collections.abc import Generator
from pathlib import Path
from typing import Any
from unittest.mock import patch
from uuid import UUID

# Third-Party Packages #
import pytest
from baseobjects.testsuite import BaseReducibleTestSuite
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase, Session

# Local Packages #
from ..database import Database
from ..tables import BaseTableSchema, TableManifestation


# Definitions #
# Classes #
class TableSchemaMixin(BaseTableSchema, DeclarativeBase):
    """A Mixin class for testing BaseTableSchema functionality."""


class DatabaseTestSuite(BaseReducibleTestSuite):
    """A Testsuite for the Database class.

    This class tests the functionality of the Database class. It inherits from BaseClassTestSuite to leverage common
    testing functionality.
    """

    # Attributes #
    UnitTestClass: type[Database] = Database
    table_schema: type[TableSchemaMixin]

    # Helper Methods #
    def create_database(self, path: str | Path | None = ":memory:", **kwargs: Any) -> Database:
        """Creates a database at the given path.

        Returns:
            The new database.
        """
        return self.UnitTestClass(path=path, **kwargs)

    # Fixtures #
    @pytest.fixture
    def test_object(self) -> Generator[Database]:
        """Creates a test object.

        Yields:
            Database: A Database instance for testing.
        """
        db = self.create_database()
        yield db
        db.close()

    # Tests #
    @pytest.mark.parametrize("init", [True, False])
    def test_instance_creation(self, tmp_path: Path, init: bool) -> None:
        """Tests that instances of the class can be created.

        Args:
            tmp_path: The temporary path.
            init: The init parameter to pass to the class constructor.
        """
        db_path = tmp_path / "test_instance.db"

        obj = self.UnitTestClass(path=db_path, init=init)
        try:
            assert isinstance(obj, self.UnitTestClass)

            if init:
                assert obj.path == db_path
            else:
                assert not hasattr(obj, "path") or obj.path is None
        finally:
            obj.close()

    def test_pickling(self, test_object: Any) -> None:
        """Tests the pickling of the Database object.

        Args:
            test_object: The test object.
        """
        test_object.open()
        pickled: bytes = pickle.dumps(test_object)
        unpickled = pickle.loads(pickled)
        try:
            assert unpickled is not test_object
            assert isinstance(unpickled, self.UnitTestClass)
            assert unpickled._path == test_object._path
            assert unpickled.is_open
        finally:
            unpickled.close()

    def test_pickling_closed(self, test_object: Any) -> None:
        """Tests the pickling of a closed Database object.

        Args:
            test_object: The test object.
        """
        test_object.close()
        pickled: bytes = pickle.dumps(test_object)
        unpickled = pickle.loads(pickled)
        assert unpickled is not test_object
        assert isinstance(unpickled, self.UnitTestClass)
        assert unpickled._path == test_object._path
        assert not unpickled.is_open

    @pytest.mark.parametrize("method", ["copy", "method"])
    def test_deepcopy_operations(
        self,
        test_object: Any,
        method: str,
        memo: dict[Any, Any] | None = None,
    ) -> None:
        """Tests the deep copy behavior of the object.

        This test verifies that deepcopy creates a new object with the same attributes (state).

        Args:
            test_object: A fixture providing a test object instance.
            method: The method to use for deep copying ('copy' or 'method').
            memo: A memo dictionary to pass to deepcopy.
        """
        if memo is None:
            memo = {}

        if method == "copy":
            obj_deepcopy = copy.deepcopy(test_object, memo=memo)
        else:
            obj_deepcopy = test_object.deepcopy(memo=memo)

        try:
            assert obj_deepcopy is not test_object
            assert isinstance(obj_deepcopy, self.UnitTestClass)
            assert obj_deepcopy._path == test_object._path
        finally:
            obj_deepcopy.close()

    @pytest.mark.parametrize("value", ["test.db", Path("test.db"), None])
    def test_path_setter(self, value: str | Path | None) -> None:
        """Tests the path setter.

        Args:
            value: The value to set the path to.
        """
        with self.create_database() as database:
            database.path = value
            if value is None:
                assert database.path is None
            else:
                assert database.path == Path(value)

    @pytest.mark.parametrize("path", [None, Path("test.db")])
    @pytest.mark.parametrize("url", [None, "sqlite:///:memory:"])
    @pytest.mark.parametrize("async_engine", [True, False])
    def test_create_engine_parameters(
        self,
        path: Path | None,
        url: str | None,
        async_engine: bool,
    ) -> None:
        """Tests the create_engine method with parameters.

        Args:
            path: The path to the database.
            url: The URL to the database.
            async_engine: Whether to create an asynchronous engine.
        """
        with self.create_database() as database:
            if path:
                database.path = path
            elif url is None and database.path is None:
                # If both path and url are None, ensure database has a path
                database.path = ":memory:"

            database.create_engine(path=path, url=url, async_engine=async_engine)

            assert database._engine is not None
            if async_engine:
                assert database._async_engine is not None
            else:
                assert database._async_engine is None

    def test_open_close(self) -> None:
        """Tests the open and close methods of the Database class."""
        with self.create_database() as database:
            database.open(async_engine=False)
            assert database.is_open
            assert not database.is_async

            database.close()
            assert not database.is_open

    @pytest.mark.asyncio
    async def test_open_close_async(self) -> None:
        """Tests the open and close_async methods of the Database class."""
        database: Any = self.create_database()
        database.open(async_engine=True)
        assert database.is_open
        assert database.is_async

        await database.close_async()
        assert not database.is_open
        assert not database.is_async

    def test_open_idempotency(self) -> None:
        """Tests opening the database when it is already open."""
        with self.create_database() as database:
            database.open()
            database.open()
            assert database.is_open
            database.close()
            assert not database.is_open

    @pytest.mark.asyncio
    async def test_open_async_idempotency(self) -> None:
        """Tests opening the database asynchronously when it is already open."""
        async with self.create_database() as database:
            database.open(async_engine=True)
            database.open(async_engine=True)
            assert database.is_open
            await database.close_async()
            assert not database.is_open

    @pytest.mark.asyncio
    async def test_close_async_idempotency(self) -> None:
        """Tests close_async idempotency."""
        db: Any = self.create_database()
        # Ensure async engine is created
        await db.create_database_async()
        assert db.is_open
        assert db.is_async

        # Close first time
        await db.close_async()
        assert not db.is_open

        # Close second time - should cover checks for None
        await db.close_async()
        assert not db.is_open

    @pytest.mark.parametrize("initially_open", [True, False])
    def test_context_manager(self, initially_open: bool) -> None:
        """Tests the context manager.

        Args:
            initially_open: Whether the database is initially open.
        """
        database = self.create_database()
        if initially_open:
            database.open()

        assert database.is_open == initially_open

        with database as db:
            assert db is database
            assert database.is_open

        assert not database.is_open

    @pytest.mark.asyncio
    @pytest.mark.parametrize("initially_open", [True, False])
    async def test_async_context_manager(self, initially_open: bool) -> None:
        """Tests the asynchronous context manager.

        Args:
            initially_open: Whether the database is initially open.
        """
        database = self.create_database()
        if initially_open:
            database.open(async_engine=True)

        assert database.is_open == initially_open
        if initially_open:
            assert database.is_async

        async with database as db:
            assert db is database
            assert database.is_open
            assert database.is_async

        assert not database.is_open

    @pytest.mark.parametrize("kwargs", [{}, {"echo": True}])
    @pytest.mark.parametrize("async_engine", [True, False])
    @pytest.mark.parametrize("path", [None, "test.db"])
    def test_create_database(
        self,
        path: str | None,
        async_engine: bool,
        kwargs: dict[str, Any],
        tmp_path: Path,
    ) -> None:
        """Tests the create_database method.

        Args:
            path: The path to the database.
            async_engine: Whether to create an asynchronous engine.
            kwargs: Additional keyword arguments.
            tmp_path: The temporary path fixture.
        """
        database = self.create_database()
        try:
            db_path = tmp_path / path if path else None
            database.create_database(path=db_path, async_engine=async_engine, **kwargs)
            assert database.is_open
            if async_engine:
                assert database.is_async
            else:
                assert not database.is_async

            if db_path:
                assert database.path == db_path
        finally:
            database.close()

    @pytest.mark.parametrize(
        ("first_name", "second_name"),
        [
            ("test_first.db", "test_second.db"),
            ("test_same.db", "test_same.db"),
        ],
    )
    def test_create_database_reentry(self, tmp_path: Path, first_name: str, second_name: str) -> None:
        """Tests create_database when already open."""
        with self.create_database() as db:
            db_first_path = tmp_path / first_name
            db.create_database(path=db_first_path)
            assert db.path == db_first_path

            db_second_path = tmp_path / second_name
            db.create_database(path=db_second_path)
            assert db.path == db_second_path

    @pytest.mark.asyncio
    @pytest.mark.parametrize("kwargs", [{}, {"echo": True}])
    @pytest.mark.parametrize("path", [None, "test_async.db"])
    async def test_create_database_async(
        self,
        path: str | None,
        kwargs: dict[str, Any],
        tmp_path: Path,
    ) -> None:
        """Tests the create_database_async method.

        Args:
            path: The path to the database.
            kwargs: Additional keyword arguments.
            tmp_path: The temporary path fixture.
        """
        async with self.create_database() as database:
            db_path = tmp_path / path if path else None
            await database.create_database_async(path=db_path, **kwargs)
            assert database.is_open
            assert database.is_async
            if db_path:
                assert database.path == db_path

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        ("first_name", "second_name"),
        [
            ("test_first.db", "test_second.db"),
            ("test_same.db", "test_same.db"),
        ],
    )
    async def test_create_database_async_reentry(self, tmp_path: Path, first_name: str, second_name: str) -> None:
        """Tests create_database_async when already open."""
        async with self.create_database() as db:
            db_first_path = tmp_path / first_name
            await db.create_database_async(path=db_first_path)
            assert db.path == db_first_path

            db_second_path = tmp_path / second_name
            await db.create_database_async(path=db_second_path)
            assert db.path == db_second_path

    @pytest.mark.parametrize("kwargs", [{}, {"autoflush": True}, {"expire_on_commit": False}])
    def test_build_session_maker(self, kwargs: dict[str, Any]) -> None:
        """Tests the build_session_maker method.

        Args:
            kwargs: Keyword arguments for the session maker.
        """
        with self.create_database() as database:
            database.open()
            session_maker = database.build_session_maker(**kwargs)
            assert session_maker is not None
            with session_maker() as session:
                assert isinstance(session, Session)
                for key, value in kwargs.items():
                    assert getattr(session, key) == value

    @pytest.mark.asyncio
    @pytest.mark.parametrize("kwargs", [{}, {"autoflush": True}, {"expire_on_commit": False}])
    async def test_build_async_session_maker(self, kwargs: dict[str, Any]) -> None:
        """Tests the build_async_session_maker method.

        Args:
            kwargs: Keyword arguments for the session maker.
        """
        async with self.create_database() as database:
            database.open(async_engine=True)
            session_maker = database.build_async_session_maker(**kwargs)
            assert session_maker is not None
            async with session_maker() as session:
                assert isinstance(session, AsyncSession)
                for key, value in kwargs.items():
                    assert getattr(session.sync_session, key) == value

    @pytest.mark.parametrize("kwargs", [{}, {"autoflush": True}, {"autoflush": False}, {"expire_on_commit": True}])
    def test_create_session(self, kwargs: dict[str, Any]) -> None:
        """Tests create_session with various parameters.

        Args:
            kwargs: Keyword arguments for the session.
        """
        with self.create_database() as database:
            database.open()
            with database.create_session(**kwargs) as session:
                assert isinstance(session, Session)
                for key, value in kwargs.items():
                    assert getattr(session, key) == value

    def test_create_session_not_open(self) -> None:
        """Tests create_session when the database is not open."""
        database = self.create_database()
        try:
            with pytest.raises(OSError, match="Database not open"):
                database.create_session()
        finally:
            database.close()

    @pytest.mark.asyncio
    @pytest.mark.parametrize("kwargs", [{}, {"autoflush": True}, {"autoflush": False}, {"expire_on_commit": True}])
    async def test_create_async_session(self, kwargs: dict[str, Any]) -> None:
        """Tests create_async_session with various parameters.

        Args:
            kwargs: Keyword arguments for the session.
        """
        async with self.create_database() as database:
            database.open(async_engine=True)
            async with database.create_async_session(**kwargs) as session:
                assert isinstance(session, AsyncSession)
                for key, value in kwargs.items():
                    assert getattr(session.sync_session, key) == value

    def test_create_async_session_no_async_engine(self) -> None:
        """Tests create_async_session when async engine is not available."""
        with self.create_database() as database:
            database.open(async_engine=False)
            with pytest.raises(IOError, match="Async engine is not available"):
                database.create_async_session()

    @pytest.mark.asyncio
    async def test_create_async_session_not_open(self) -> None:
        """Tests create_async_session when the database is not open."""
        database = self.create_database()
        try:
            with pytest.raises(OSError, match="Database not open"):
                database.create_async_session()
        finally:
            await database.close_async()

    @pytest.mark.parametrize("arg_type", ["none_arg", "no_arg", "valid_arg"])
    def test_manifest_tables(self, arg_type: str) -> None:
        """Tests the manifest_tables method with various arguments.

        Args:
            arg_type: The type of argument to test.
        """
        with self.create_database() as database:

            class MockSchema(DeclarativeBase):
                pass

            map_data: dict[str, tuple[type[TableManifestation], type[DeclarativeBase], dict[str, Any]]] = {
                "test": (TableManifestation, MockSchema, {})
            }

            if arg_type == "none_arg":
                database.table_map = {}
                database.tables = {}
                database.manifest_tables(table_map=None)
                assert database.tables == {}
            elif arg_type == "no_arg":
                database.table_map = map_data
                database.manifest_tables()
                assert "test" in database.tables
            elif arg_type == "valid_arg":
                database.manifest_tables(table_map=map_data)
                assert "test" in database.tables
                assert isinstance(database.tables["test"], TableManifestation)

    @pytest.mark.skip(reason="build_tables test not implemented")
    def test_build_tables(self, test_object: Database) -> None:
        """Tests the build_tables method."""
        # Subclasses should define how to test that its tables are built

    @pytest.mark.skip(reason="load_tables test not implemented")
    def test_load_tables(self, test_object: Database) -> None:
        """Tests the load_tables method."""
        # Subclasses should define how to test that its tables are loaded

    @pytest.mark.parametrize("schema", [None])
    @pytest.mark.parametrize("table_map", [None, {}])
    @pytest.mark.parametrize("open_", [True, False])
    @pytest.mark.parametrize("create", [True, False])
    @pytest.mark.parametrize("async_engine", [True, False])
    @pytest.mark.parametrize("init", [True, False])
    def test_instance_full_parameters(
        self,
        tmp_path: Path,
        schema: type[DeclarativeBase] | None,
        table_map: dict[str, tuple[type[TableManifestation], type[DeclarativeBase], dict[str, Any]]] | None,
        create: bool,
        open_: bool,
        async_engine: bool,
        init: bool,
    ) -> None:
        """Tests that instances of the class can be created.

        Args:
            tmp_path: The temporary path.
            schema: The database schema.
            table_map: The table map.
            init: The init parameter to pass to the class constructor.
            create: Whether to create the database.
            open_: Whether to open the database.
            async_engine: Whether to use an asynchronous engine.
        """
        db_path = tmp_path / "test_instance.db"

        obj = self.UnitTestClass(
            path=db_path,
            schema=schema,
            table_map=table_map,
            create=create,
            open_=open_,
            async_engine=async_engine,
            init=init,
        )

        try:
            assert isinstance(obj, self.UnitTestClass)

            if init:
                assert obj.path == db_path

                if create:
                    assert db_path.exists()

                if open_:
                    assert obj.is_open
                    if async_engine:
                        assert obj.is_async
                else:
                    assert not obj.is_open
            else:
                assert not hasattr(obj, "path") or obj.path is None
        finally:
            obj.close()

    @pytest.mark.parametrize("begin", [True, False])
    @pytest.mark.parametrize("use_session", [True, False])
    def test_insert(self, use_session: bool, begin: bool) -> None:
        """Tests the insert method.

        Args:
            use_session: Whether to use a session.
            begin: Whether to begin a transaction.
        """
        with self.create_database(create=True, open_=True) as database:
            item = self.table_schema(id=UUID(int=1))
            if use_session:
                with database.create_session() as session:
                    database.insert(item, session=session, begin=begin)
                    if not begin:
                        session.commit()
            else:
                database.insert(item, begin=begin)

            with database.create_session() as session:
                assert session.get(self.table_schema, UUID(int=1)) is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("begin", [True, False])
    @pytest.mark.parametrize("use_session", [True, False])
    async def test_insert_async(self, use_session: bool, begin: bool) -> None:
        """Tests the insert_async method.

        Args:
            use_session: Whether to use a session.
            begin: Whether to begin a transaction.
        """
        async with self.create_database(create=False, async_engine=True) as database:
            await database.create_database_async()

            item = self.table_schema(id=UUID(int=1))
            if use_session:
                async with database.create_async_session() as session:
                    await database.insert_async(item, session=session, begin=begin)
                    if not begin:
                        await session.commit()
            else:
                await database.insert_async(item, begin=begin)

            async with database.create_async_session() as session:
                assert await session.get(self.table_schema, UUID(int=1)) is not None

    @pytest.mark.parametrize("begin", [True, False])
    @pytest.mark.parametrize("use_session", [True, False])
    def test_insert_all(self, use_session: bool, begin: bool) -> None:
        """Tests the insert_all method.

        Args:
            use_session: Whether to use a session.
            begin: Whether to begin a transaction.
        """
        with self.create_database(create=True, open_=True) as database:
            items = [self.table_schema(id=UUID(int=1)), self.table_schema(id=UUID(int=2))]
            if use_session:
                with database.create_session() as session:
                    database.insert_all(items, session=session, begin=begin)
                    if not begin:
                        session.commit()
            else:
                database.insert_all(items, begin=begin)

            with database.create_session() as session:
                assert session.get(self.table_schema, UUID(int=1)) is not None
                assert session.get(self.table_schema, UUID(int=2)) is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("begin", [True, False])
    @pytest.mark.parametrize("use_session", [True, False])
    async def test_insert_all_async(self, use_session: bool, begin: bool) -> None:
        """Tests the insert_all_async method.

        Args:
            use_session: Whether to use a session.
            begin: Whether to begin a transaction.
        """
        async with self.create_database(create=False, async_engine=True) as database:
            await database.create_database_async()

            items = [self.table_schema(id=UUID(int=1)), self.table_schema(id=UUID(int=2))]
            if use_session:
                async with database.create_async_session() as session:
                    await database.insert_all_async(items, session=session, begin=begin)
                    if not begin:
                        await session.commit()
            else:
                await database.insert_all_async(items, begin=begin)

            async with database.create_async_session() as session:
                assert await session.get(self.table_schema, UUID(int=1)) is not None
                assert await session.get(self.table_schema, UUID(int=2)) is not None

    # Properties Tests #
    def test_mode_setter_getter(self, test_object: Database) -> None:
        """Tests the mode property.

        Args:
            test_object: The test object.
        """
        test_object.close()
        test_object.mode = "ro"
        assert test_object.mode == "ro"
        # Use string to test conversion
        test_object.mode = "rwc"
        assert test_object.mode == "rwc"

        test_object.open()
        with pytest.raises(ValueError, match="Cannot change mode while the database is open"):
            test_object.mode = "ro"
        test_object.close()

    def test_backend_setter_getter(self, test_object: Database) -> None:
        """Tests the backend property.

        Args:
            test_object: The test object.
        """
        # Using string to test conversion
        test_object.backend = "postgresql://"
        assert test_object.backend == "postgresql://"
        test_object.backend = "sqlite://"
        assert test_object.backend == "sqlite://"

    def test_async_backend_setter_getter(self, test_object: Database) -> None:
        """Tests the async_backend property.

        Args:
            test_object: The test object.
        """
        # Using string to test conversion
        test_object.async_backend = "postgresql+asyncpg://"
        assert test_object.async_backend == "postgresql+asyncpg://"
        test_object.async_backend = "sqlite+aiosqlite://"
        assert test_object.async_backend == "sqlite+aiosqlite://"

    def test_full_url_exceptions(self, test_object: Database) -> None:
        """Tests full_url exceptions.

        Args:
            test_object: The test object.
        """
        test_object.path = "test.db"
        test_object.url = "sqlite:///:memory:"
        with pytest.raises(ValueError, match="Cannot have both a path and a URL"):
            _ = test_object.full_url

        test_object.url = None
        test_object.backend = "postgresql://"
        with pytest.raises(ValueError, match="Unsupported backend for path"):
            _ = test_object.full_url

        test_object.path = None
        test_object.url = None
        with pytest.raises(ValueError, match="Path is not set"):
            _ = test_object.full_url

    def test_async_full_url_exceptions(self, test_object: Database) -> None:
        """Tests async_full_url exceptions.

        Args:
            test_object: The test object.
        """
        test_object.path = "test.db"
        test_object.url = "sqlite+aiosqlite:///:memory:"
        with pytest.raises(ValueError, match="Cannot have both a path and a URL"):
            _ = test_object.async_full_url

        test_object.url = None
        test_object.async_backend = "postgresql+asyncpg://"
        with pytest.raises(ValueError, match="Unsupported backend for path"):
            _ = test_object.async_full_url

        test_object.path = None
        test_object.url = None
        with pytest.raises(ValueError, match="Path is not set"):
            _ = test_object.async_full_url

    def test_full_url_variants(self, test_object: Database) -> None:
        """Tests full_url variants.

        Args:
            test_object: The test object.
        """
        test_object.backend = "sqlite://"
        test_object.path = Path("test.db")
        test_object.url = None
        url = test_object.full_url
        assert "mode=" in url
        assert url.startswith("sqlite:///")

        # URL starts with async backend
        test_object.path = None
        test_object.url = "sqlite+aiosqlite:///test.db"
        assert test_object.full_url == "sqlite:///test.db?mode=rwc"

        # URL doesn't have ://
        test_object.url = "test.db"
        assert test_object.full_url == "sqlite:///test.db?mode=rwc"

        # Branch 178->181: "mode=" in url
        test_object.url = "sqlite:///test.db?mode=ro"
        assert "mode=ro" in test_object.full_url
        assert "mode=rwc" not in test_object.full_url

        # Branch 182->184: url.startswith("/")
        test_object.url = "/test.db"
        assert test_object.full_url == "sqlite:///test.db?mode=rwc"

        # Test ? already in url but mode not in url
        test_object.url = "sqlite:///test.db?some_param=value"
        assert test_object.full_url == "sqlite:///test.db?some_param=value&mode=rwc"

    def test_async_full_url_variants(self, test_object: Database) -> None:
        """Tests async_full_url variants.

        Args:
            test_object: The test object.
        """
        test_object.async_backend = "sqlite+aiosqlite://"
        test_object.path = Path("test.db")
        test_object.url = None
        url = test_object.async_full_url
        assert "mode=" in url
        assert url.startswith("sqlite+aiosqlite:///")

        # URL starts with sync backend
        test_object.path = None
        test_object.url = "sqlite:///test.db"
        assert test_object.async_full_url == "sqlite+aiosqlite:///test.db?mode=rwc"

        # URL doesn't have ://
        test_object.url = "test.db"
        assert test_object.async_full_url == "sqlite+aiosqlite:///test.db?mode=rwc"

        # Branch 209->212: "mode=" in url
        test_object.url = "sqlite+aiosqlite:///test.db?mode=ro"
        assert "mode=ro" in test_object.async_full_url
        assert "mode=rwc" not in test_object.async_full_url

        # Branch 213->215: url.startswith("/")
        test_object.url = "/test.db"
        assert test_object.async_full_url == "sqlite+aiosqlite:///test.db?mode=rwc"

        # Test ? already in url but mode not in url
        test_object.url = "sqlite+aiosqlite:///test.db?some_param=value"
        assert test_object.async_full_url == "sqlite+aiosqlite:///test.db?some_param=value&mode=rwc"

    def test_construct_with_mode(self, tmp_path: Path) -> None:
        """Tests construct with mode.

        Args:
            tmp_path: The temporary path.
        """
        db_path = tmp_path / "test_mode.db"
        obj = self.UnitTestClass(path=db_path, mode="ro", init=True)
        assert obj.mode == "ro"

    def test_create_engine_with_mode(self, test_object: Database, tmp_path: Path) -> None:
        """Tests create_engine with mode.

        Args:
            test_object: The test object.
            tmp_path: The temporary path.
        """
        db_path = tmp_path / "test_engine_mode.db"
        test_object.create_engine(path=db_path, mode="ro")
        assert test_object.mode == "ro"

    def test_close_with_running_loop(self, test_object: Database) -> None:
        """Tests close() when an event loop is running.

        Args:
            test_object: The test object.
        """
        test_object.open(async_engine=True)
        # Patch 'sqlalchemyobjects.database.run' because it's imported as 'from asyncio import run' in database.py
        with patch("sqlalchemyobjects.database.run", side_effect=RuntimeError("Event loop is running")):
            with patch("asyncio.get_running_loop") as mock_get_loop:
                mock_loop = mock_get_loop.return_value
                mock_loop.is_running.return_value = True
                test_object.close()
                assert mock_loop.create_task.called
                # Close the coroutine to avoid RuntimeWarning
                coro = mock_loop.create_task.call_args[0][0]
                coro.close()

    def test_close_with_running_loop_already_has_tasks(self, test_object: Database) -> None:
        """Tests close() when an event loop is running and _closing_tasks already exists.

        Args:
            test_object: The test object.
        """
        test_object.open(async_engine=True)
        test_object._closing_tasks = set()
        # Patch 'sqlalchemyobjects.database.run' because it's imported as 'from asyncio import run' in database.py
        with patch("sqlalchemyobjects.database.run", side_effect=RuntimeError("Event loop is running")):
            with patch("asyncio.get_running_loop") as mock_get_loop:
                mock_loop = mock_get_loop.return_value
                mock_loop.is_running.return_value = True
                test_object.close()
                assert mock_loop.create_task.called
                assert len(test_object._closing_tasks) == 1
                # Close the coroutine to avoid RuntimeWarning
                coro = mock_loop.create_task.call_args[0][0]
                coro.close()

    def test_close_with_running_loop_not_running(self, test_object: Database) -> None:
        """Tests close() when get_running_loop returns a loop that is not running.

        Args:
            test_object: The test object.
        """
        test_object.open(async_engine=True)
        with patch("sqlalchemyobjects.database.run", side_effect=RuntimeError("Event loop is running")):
            with patch("asyncio.get_running_loop") as mock_get_loop:
                mock_loop = mock_get_loop.return_value
                mock_loop.is_running.return_value = False
                # To avoid RuntimeWarning, we need to handle the coroutine returned by dispose
                # Database.close() will close it because is_running() is False
                test_object.close()
                assert not mock_loop.create_task.called

    def test_close_with_running_loop_error(self, test_object: Database) -> None:
        """Tests close() when get_running_loop raises RuntimeError.

        Args:
            test_object: The test object.
        """
        test_object.open(async_engine=True)
        with patch("sqlalchemyobjects.database.run", side_effect=RuntimeError("Event loop is running")):
            with patch("asyncio.get_running_loop", side_effect=RuntimeError("No loop")):
                # To avoid RuntimeWarning, we need to handle the coroutine returned by dispose
                # Database.close() will close it because get_running_loop() raises RuntimeError
                test_object.close()
                # Should pass silently

    def test_close_with_exception(self, test_object: Database) -> None:
        """Tests close() when run() raises an exception.

        Args:
            test_object: The test object.
        """
        test_object.open(async_engine=True)
        with patch("sqlalchemyobjects.database.run", side_effect=ValueError("Test exception")):
            with pytest.raises(ValueError, match="Test exception"):
                test_object.close()

    def test_full_url_non_sqlite(self, test_object: Database) -> None:
        """Tests full_url with non-sqlite backend.

        Args:
            test_object: The test object.
        """
        test_object.backend = "postgresql://"
        test_object.path = None
        test_object.url = "localhost/db"
        assert test_object.full_url == "postgresql://localhost/db"

    def test_async_full_url_non_sqlite(self, test_object: Database) -> None:
        """Tests async_full_url with non-sqlite backend.

        Args:
            test_object: The test object.
        """
        test_object.async_backend = "postgresql+asyncpg://"
        test_object.path = None
        test_object.url = "localhost/db"
        assert test_object.async_full_url == "postgresql+asyncpg://localhost/db"


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])

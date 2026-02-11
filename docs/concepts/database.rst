Database
========

For a detailed guide on how the Database class fits into the overall architecture, see the
:doc:`Comprehensive Usage <comprehensive>` guide.

The ``Database`` class brings everything together. It encapsulates the SQLAlchemy engine, session makers, and a
collection of :doc:`TableManifestations <tablemanifestation>`. It serves as the single source of truth for your
database interaction, providing a unified interface for both synchronous and asynchronous operations.

Defining a Database
-------------------

To define a database, you typically create a subclass of ``Database``. Within this subclass, you specify the
database schema and a map of the tables it contains.

The ``schema`` attribute should be the SQLAlchemy `DeclarativeBase`_ class that defines your database structure.
The ``table_map`` is a dictionary where keys are the names you want to use for the tables, and values are tuples
containing the :doc:`TableManifestation <tablemanifestation>` class, the corresponding table schema class, and
a dictionary of any additional keyword arguments for the manifestation.

.. code-block:: python

    from sqlalchemyobjects import Database
    from .schemas import DatabaseSchema, DatabaseUserTableSchema
    from .tables import UserTableManifestation

    class MyDatabase(Database):
        schema = DatabaseSchema
        table_map = {
            "users": (UserTableManifestation, DatabaseUserTableSchema, {}),
        }

Using a Database
----------------

Once defined, you can instantiate and use your database. The ``Database`` class handles the lifecycle of the
underlying SQLAlchemy engine and sessions.

Instantiation and Connection
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

You can instantiate the database by providing the path to the database file. You can also specify if you want
to create the database (and its tables) and if you want to use an asynchronous engine.

.. code-block:: python

    # Synchronous database with table creation and opening
    db = MyDatabase(path="my_database.db", create=True, open_=True)

    # Asynchronous database
    async_db = MyDatabase(path="my_database.db", async_engine=True)
    await async_db.create_database_async()
    await async_db.open()

The ``Database`` class also supports the context manager protocol (and async context manager protocol), ensuring
the database is properly closed after use.

.. code-block:: python

    with MyDatabase(path="my_database.db") as db:
        all_users = db.users.get_all()

Working with Tables
~~~~~~~~~~~~~~~~~~~

Tables defined in the ``table_map`` are instantiated as :doc:`TableManifestations <tablemanifestation>` and stored in
the ``tables`` dictionary. If you defined property shortcuts, you can access them as attributes.

.. code-block:: python

    # Accessing via the tables dictionary
    all_users = db.tables["users"].get_all()

    # Accessing via property shortcut
    all_users = db.users.get_all()

Session Management
~~~~~~~~~~~~~~~~~~

The ``Database`` object provides methods to create sessions, which are automatically bound to the database's engine.

.. code-block:: python

    # Synchronous session
    with db.create_session() as session:
        user = db.users.get_by_id(1, session=session)

    # Asynchronous session
    async with db.create_async_session() as session:
        user = await db.users.get_by_id_async(1, session=session)

Basic Operations
~~~~~~~~~~~~~~~~

For simple operations like inserting a single item or a list of items, the ``Database`` class provides convenience
methods that handle session management internally.

.. code-block:: python

    new_user = UserTableSchema(name="Alice")
    db.insert(new_user)

    # Async insert
    await db.insert_async(new_user)

    # Insert multiple items
    users = [UserTableSchema(name="Alice"), UserTableSchema(name="Bob")]
    db.insert_all(users)

    # Async insert multiple items
    await db.insert_all_async(users)

Backend Features
----------------

The ``Database`` class is designed to be flexible and supports a variety of database backends through SQLAlchemy. It
provides built-in support for both synchronous and asynchronous drivers, and includes specific optimizations for
SQLite.

Supported Backends
~~~~~~~~~~~~~~~~~~

The ``Database`` class can be configured to use any database supported by SQLAlchemy. Common backends include:

*   **SQLite**: The default backend, ideal for local development and embedded applications.
*   **PostgreSQL**: Supported via multiple drivers including ``psycopg2``, ``pg8000``, and ``asyncpg`` for async.
*   **MySQL**: Supported via ``mysqldb``, ``pymysql``, and ``aiomysql`` for async.
*   **Oracle**: Supported via ``oracledb``.
*   **Microsoft SQL Server**: Supported via ``pyodbc``.

You can specify the backend by setting the ``backend`` and ``async_backend`` attributes or properties.

.. code-block:: python

    from sqlalchemyobjects import Database, SQLAlchemyBackends, SQLAlchemyAsyncBackends

    class MyPostgresDatabase(Database):
        _backend = SQLAlchemyBackends.POSTGRESQL_PSYCOPG2
        _async_backend = SQLAlchemyAsyncBackends.POSTGRESQL
        # ... schema and table_map ...

Sync and Async Integration
~~~~~~~~~~~~~~~~~~~~~~~~~~

One of the primary features of the ``Database`` class is its ability to manage both synchronous and asynchronous
engines simultaneously. When ``async_engine=True`` is passed during instantiation, the class creates both a standard
engine and an asynchronous engine, allowing you to use the same database object across different parts of your
application regardless of their execution model.

SQLite Optimizations
~~~~~~~~~~~~~~~~~~~~

For SQLite, the ``Database`` class provides several conveniences:

*   **Path to URL Conversion**: You can simply provide a file path, and the class will automatically generate the
    correct SQLite connection URL.
*   **URI Modes**: It supports SQLite URI modes (``ro``, ``rw``, ``rwc``, ``memory``), which can be set via the
    ``mode`` attribute.
*   **Automated Directory Creation**: When creating a database from a path, it ensures the parent directories exist.

.. code-block:: python

    # The Database object will automatically ensure the 'data' directory exists.
    db = MyDatabase(path="data/my_database.db", create=True)

    # You can also specify the URI mode, such as read-only.
    ro_db = MyDatabase(path="data/my_database.db", mode="ro", open_=True)

Flexible URL Management
~~~~~~~~~~~~~~~~~~~~~~~

If you need to connect to a database using a specific connection string that isn't covered by the default path-based
logic, you can provide a full ``url``. The ``Database`` class will intelligently handle this URL, ensuring it is
correctly adapted for both synchronous and asynchronous engines if necessary.

.. code-block:: python

    # Connecting to a remote MySQL database using a full URL
    db = MyDatabase(url="mysql+pymysql://user:password@host:port/dbname")

Benefits of the Database Object
-------------------------------

Creating and using a ``Database`` object offers several key benefits:

*   **Single Source of Truth**: It provides a central location for all database-related configuration and table
    definitions, making the architecture easier to reason about.
*   **Encapsulated Session Management**: It abstracts away the details of session creation and lifecycle management,
    reducing boilerplate and the risk of session-related errors (e.g., forgotten closes).
*   **Unified Sync and Async Support**: It manages both synchronous and asynchronous engines and session makers
    transparently, allowing you to use the same database object for both types of workflows.
*   **Simplified Dependency Injection**: Instead of passing multiple table manifestations or session factories
    throughout your application, you can simply pass a single ``Database`` instance.
*   **Automated Schema Creation**: By providing a ``schema``, the ``Database`` object can automatically create all
    defined tables in the database via the ``create_database()`` method.

.. _Session: https://docs.sqlalchemy.org/en/20/orm/session_basics.html
.. _AsyncSession: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
.. _DeclarativeBase: https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html

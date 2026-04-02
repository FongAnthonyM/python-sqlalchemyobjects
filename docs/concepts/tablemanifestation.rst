TableManifestations
===================

For a detailed guide on how TableManifestations fit into the overall architecture, see the
:doc:`Comprehensive Usage <comprehensive>` guide.

A ``TableManifestation`` is an object representation of a table. It wraps a :doc:`TableSchema <tableschema>` class
and is bound to a :doc:`Database <database>` instance. It exposes the same CRUD API as the ``TableSchema`` but manages
sessions internally.

This allows for a much cleaner API, as you do not need to pass a `Session`_ to every call:

.. code-block:: python

    user_table = TableManifestation(table_schema=UserTableSchema, database=database)
    user = user_table.get_by_id(1)

Defining a TableManifestation
-----------------------------

It is important to understand that a ``TableManifestation`` is designed to work in tandem with a
:doc:`TableSchema <tableschema>`. While the ``TableSchema`` defines the table's structure (columns) and core logic
(implemented as class methods), the ``TableManifestation`` provides a session-aware instance that exposes this
logic to the rest of the application. This separation allows the schema to remain a pure definition of the data,
while the manifestation handles the operational complexities of database interaction.

While you can use the base ``TableManifestation`` class for standard CRUD operations, you will often want to create
custom manifestations to encapsulate table-specific logic.

To define a custom manifestation, inherit from ``TableManifestation``. It is a common pattern to add methods that
delegate to class methods on the ``TableSchema``, handling session management in the process.

.. code-block:: python

    class UserTableManifestation(TableManifestation):
        """A TableManifestation interface for the UserTableSchema."""

        def get_by_name(
            self, name: str, session: Session | None = None, as_python: bool = False
        ) -> Any:
            """Fetches a user from the table by their name."""
            if session is not None:
                return self.table_schema.get_by_name(session, name, as_python=as_python)
            else:
                with self.create_session() as session:
                    return self.table_schema.get_by_name(session, name, as_python=as_python)

        async def get_by_name_async(
            self, name: str, session: AsyncSession | None = None, as_python: bool = False
        ) -> Any:
            """Asynchronously fetches a user from the table by their name."""
            if session is not None:
                return await self.table_schema.get_by_name_async(session, name, as_python=as_python)
            else:
                async with self.create_async_session() as session:
                    return await self.table_schema.get_by_name_async(session, name, as_python=as_python)

Using a TableManifestation
--------------------------

Once defined, a manifestation is instantiated by passing the corresponding schema and a database instance.

It is important to note that the ``table_schema`` argument must be a class that inherits from both a
:doc:`TableSchema <tableschema>` (``BaseTableSchema`` or its subclasses) and the SQLAlchemy `DeclarativeBase`_.
This ensures the class is both a valid SQLAlchemy model and possesses the required CRUD mixins. Additionally, a
:doc:`Database <database>` instance must be provided to bind the manifestation to a specific database connection.

.. code-block:: python

    # Initialize the manifestation
    user_table = UserTableManifestation(table_schema=UserTableSchema, database=database)

    # Use standard CRUD methods
    user_table.insert({"name": "Alice", "role": "admin"})
    all_users = user_table.get_all()

    # Use custom methods
    bob = user_table.get_by_name("Bob")

Common CRUD Operations
----------------------

``TableManifestation`` exposes the same CRUD API as ``TableSchema``, but it handles the session lifecycle internally.

Insert
~~~~~~

.. code-block:: python

    # Insert using a dictionary
    user_table.insert({"name": "Alice", "email": "alice@example.com"})

    # Insert using an instance
    new_user = UserTableSchema(name="Bob", email="bob@example.com")
    user_table.insert(new_user)

Upsert
~~~~~~

.. code-block:: python

    # Upsert based on the 'id' (default)
    user_table.upsert({"id": 1, "name": "Alice Updated"})

Delete
~~~~~~

.. code-block:: python

    user = user_table.get_by_id(1)
    if user:
        user_table.delete(user)

Count
~~~~~

.. code-block:: python

    total_users = user_table.count()

Asynchronous Operations
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    await user_table.insert_async({"name": "Charlie"})
    count = await user_table.count_async()

Explicit Session Management
---------------------------

While the primary advantage of a ``TableManifestation`` is automated session management, every CRUD method also
accepts an optional ``session`` argument. Providing a session manually is preferable in
several scenarios:

*   **Atomic Transactions**: When you need to perform multiple operations—potentially across different
    manifestations—as a single unit of work. If any operation fails, the entire transaction can be rolled back.
*   **Performance**: If you are performing a large number of operations in sequence, reusing a single session is
    more efficient than creating and closing a new session for every individual call.
*   **External Session Lifecycle**: In some applications (like web frameworks), the session lifecycle might be
    managed externally (e.g., one session per request). In these cases, you should pass the existing session to the
    manifestation methods.

.. code-block:: python

    # Using a single session for multiple operations across different tables
    with database.create_session() as session:
        with session.begin():
            # Operations are part of the same transaction
            user_table.insert({"name": "Eve"}, session=session)
            log_table.insert({"event": "User created", "user": "Eve"}, session=session)

    # The same applies to asynchronous operations
    async with database.create_async_session() as session:
        async with session.begin():
            await user_table.insert_async({"name": "Frank"}, session=session)
            await log_table.insert_async({"event": "User created", "user": "Frank"}, session=session)

Benefits of TableManifestations
-------------------------------

Creating and using ``TableManifestation`` objects offers several advantages:

*   **Automated Session Management**: Manifestations handle the lifecycle of SQLAlchemy `Session`_ objects (creating,
    committing, and closing) for you. This eliminates a common source of errors and boilerplate.
*   **Encapsulation of Logic**: All logic related to a specific table—including custom queries and data
    transformations—is kept in a single, cohesive object.
*   **Simplified API**: Users of the database can interact with tables using a clean, object-oriented API
    without needing to understand the underlying SQLAlchemy session mechanics.
*   **Consistency**: Manifestations provide a unified interface for both synchronous and asynchronous operations,
    making it easier to switch between the two or support both in the same application.
*   **Decoupling**: The business logic of your application interacts with manifestations rather than directly
    with SQLAlchemy models or sessions, leading to a more modular and testable architecture.

.. _Session: https://docs.sqlalchemy.org/en/20/orm/session_basics.html
.. _AsyncSession: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
.. _DeclarativeBase: https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html

Comprehensive Usage
===================

The power of ``sqlalchemyobjects`` is fully realized when :doc:`TableSchema <tableschema>`,
:doc:`TableManifestation <tablemanifestation>`, and :doc:`Database <database>` are used together. This trio provides
a highly structured, maintainable, and session-aware interface for a database.

The Unified Workflow
--------------------

Building a database application with ``sqlalchemyobjects`` typically follows a four-step workflow that promotes
separation of concerns and code reuse.

Step 1: Define TableSchema Mixins
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

First, define a table structure and core logic using mixins that inherit from ``BaseTableSchema``. These mixins should
not inherit from SQLAlchemy's ``DeclarativeBase`` yet; this allows them to be reused across different database schemas
or inheritance patterns.

.. code-block:: python

    from sqlalchemy.orm import Mapped, mapped_column, Session
    from sqlalchemyobjects.tables.base import BaseTableSchema

    class UserTableSchema(BaseTableSchema):
        """A mixin defining the user table structure and logic."""
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column()
        role: Mapped[str] = mapped_column(default="user")

        @classmethod
        def get_by_name(cls, session: Session, name: str) -> "UserMixin | None":
            """Custom logic to find a user by name."""
            return cls.get_by(session, "name", name).scalars().first()

Step 2: Define TableManifestations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Next, define a ``TableManifestation`` to provide a session-managed interface for the schema. This object will delegate
calls to the class methods of the ``TableSchema``.

.. code-block:: python

    from sqlalchemyobjects.tables.base import TableManifestation

    class UserTableManifestation(TableManifestation):
        """A session-aware interface for the User table."""
        def get_by_name(self, name: str) -> Any:
            with self.create_session() as session:
                return self.table_schema.get_by_name(session, name)

Step 3: Define the Database Schema
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Define the standard SQLAlchemy ``DeclarativeBase`` and create the final table classes by combining the mixins
with the base.

.. code-block:: python

    from sqlalchemy.orm import DeclarativeBase
    from sqlalchemy.ext.asyncio import AsyncAttrs


    class DatabaseSchema(AsyncAttrs, DeclarativeBase):
        """The root schema for the application."""


    class DatabaseUserTableSchema(UserTableSchema, MySchema):
        """The actual SQLAlchemy model for the 'user' table."""

Step 4: Combine into a Database Object
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Finally, subclass ``Database`` to tie everything together.

*   Assign the database schema.
*   ``table_map`` should be used to register manifestations.
*   Optionally, add any new methods or properties.

.. code-block:: python

    from sqlalchemyobjects import Database

    class MyDatabase(Database):
        schema = DatabaseSchema
        table_map = {
            "users": (UserTableManifestation, DatabaseUserTableSchema, {}),  # The dictionary is any kwargs to use during Manifestation construction
        }

        @property
        def users(self) -> UserTableManifestation:
            return self.tables["users"]

Putting It All Together
-----------------------

Once the components are defined, interacting with the database becomes simple and expressive.

.. code-block:: python

    # 1. Initialize and open the database
    db = MyDatabase(path="app.db", create=True, open_=True)

    # 2. Get a manifestation through the tables dictionary and use it to interact with data
    db.tables["users"].insert({"name": "Alice", "role": "admin"})

    # 3. Access custom logic through the manifestation
    user = db.users.get_by_name("Alice")  # Use the property shortcut to access user quickly
    if user:
        print(f"Found {user.name} with role {user.role}")

    # 4. Clean up
    db.close()

How They Interact
-----------------

*   **TableSchema**: Acts as the "Blueprint" and "Logic Center." It defines the columns and provides the fundamental
    SQLAlchemy operations as class methods.
*   **TableManifestation**: Acts as the "Interface." It wraps the blueprint and binds it to a database instance,
    handling session lifecycles so the rest of the application doesn't have to.
*   **Database**: Acts as the "Orchestrator." It manages the connection to the physical database and hosts the
    collection of manifestations, serving as the single entry point for all data operations.

Benefits of This Integration
----------------------------

1.  **Strict Separation of Concerns**: Schemas handle data structure, manifestations handle access patterns, and the
    database handles connectivity.
2.  **API Consistency**: You get the same powerful CRUD API across all tables, both synchronously and asynchronously.
3.  **Testability**: Each component can be tested in isolation or mocked easily.
4.  **Scalability**: Adding a new table only requires following the same pattern, ensuring the codebase remains
    organized as the project grows.
5.  **Boilerplate Elimination**: Automated session management and schema creation significantly reduce the amount of
    repetitive code needed to write and maintain.

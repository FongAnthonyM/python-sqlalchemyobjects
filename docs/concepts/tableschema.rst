TableSchema
===========

TableSchema is an extension of SQLAlchemy's Object-Relational Mapping (ORM) inheritance concepts. Specifically,
TableSchema acts as an inheritance mixin to decouple table schema design from the database structure specification.
For example, strictly following SQLAlchemy's table specification leads to creating a table schema which only applies
to the database it is housed in. This means that specified table schema cannot be used in other databases. In fact,
that table schema cannot be used in the same database to specify separate tables with the same structure. The
TableSchema structure described here is an organized implementation of the mixin strategy which SQLAlchemy suggests for
writing decoupled table schemas.

For a detailed guide on how TableSchema fits into the overall SQLAlchemyObjects architecture, see the
:doc:`Comprehensive Usage <comprehensive>` guide.

Inheritance Strategies
----------------------

TableSchema objects are particularly powerful when used as mixins in SQLAlchemy inheritance hierarchies. TableSchema was
primarily designed to make Concrete Table Inheritance easier to define, but TableSchema can be used for Single Table
Inheritance and Joined Table Inheritance as well.

Concrete Table Inheritance
~~~~~~~~~~~~~~~~~~~~~~~~~~

In `Concrete Table Inheritance`_, each subclass has its own table containing all columns. TableSchema is highly
beneficial here because it allows you to define a common schema and CRUD API once and apply it to multiple
independent tables without repeating column definitions. This ensures that all concrete tables have exactly the same
suite of CRUD methods and base columns, maintaining a perfectly consistent API across different data entities
that share a common structure.

.. code-block:: python

    # Base Table Mixin Definitions
    class UserTableSchema(BaseTableSchema):
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str]
        email: Mapped[str]


    # Database Schema Definitions
    class DatabaseRootSchema(DeclarativeBase):
        """The root of the database schema"""


    class Customer(UserTableSchema, DatabaseRootSchema):
        __tablename__ = "customer"
        purchase: Mapped[str]


    class Employee(UserTableSchema, DatabaseRootSchema):
        __tablename__ = "employee"
        task: Mapped[str]

Both ``Customer`` and ``Employee`` now have columns with identical properties, but correspond to their respective
tables. They also have a full suite of CRUD methods defined in ``BaseTableSchema``, operating on their respective
tables.

Single Table Inheritance
~~~~~~~~~~~~~~~~~~~~~~~~

`Single Table Inheritance`_ stores all classes in one table with a discriminator. TableSchema can be applied
to the base class to provide CRUD operations that respect the polymorphic identities.

.. code-block:: python

    # Base Table Mixin Definitions
    class UserTableSchema(BaseTableSchema):
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str]
        email: Mapped[str]
        type: Mapped[str] = mapped_column()


    # Database Schema Definitions
    class DatabaseRoot(DeclarativeBase):
        """The root of the database schema"""


    class User(UserTableSchema, DatabaseRoot):  # The single table
        __tablename__ = "user"
        __mapper_args__ = {"polymorphic_on": "type", "polymorphic_identity": "user"}


    class Admin(User):  # Sub-table in the User table
        __mapper_args__ = {"polymorphic_identity": "admin"}


    class Customer(User):  # Sub-table in the User table
        __mapper_args__ = {"polymorphic_identity": "customer"}

Calling ``Admin.get_all(session)`` will automatically filter for rows where ``type == 'admin'``, leveraging
SQLAlchemy's built-in polymorphism while providing the convenient TableSchema API for the main table and the sub-tables.

Joined Table Inheritance
~~~~~~~~~~~~~~~~~~~~~~~~

In `Joined Table Inheritance`_, columns are spread across multiple tables linked by foreign keys. TableSchema
mixins still provide a consistent interface for these complex structures.

.. code-block:: python

    # Base Table Mixin Definitions
    class UserTableSchema(BaseTableSchema):
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str]
        email: Mapped[str]
        type: Mapped[str] = mapped_column()


    class EngineerTableSchema(UserTableSchema):  # A subclass of UserMixin
        specialty: Mapped[str]


    # Database Schema Definitions
    class DatabaseRoot(DeclarativeBase):
        """The root of the database schema"""


    class Person(UserTableSchema, DatabaseRoot):  # The primary table with columns in User Mixin
        __tablename__ = "person"
        __mapper_args__ = {"polymorphic_on": "type", "polymorphic_identity": "person"}


    class Engineer(Person, EngineerTableSchema):  # The secondary table with columns
        __tablename__ = "engineer"
        __mapper_args__ = {"polymorphic_identity": "engineer"}
        id: Mapped[int] = mapped_column(ForeignKey("person.id"), primary_key=True)  # Specifies that this is a joined table


Even with joined tables, ``Engineer.insert(session, {...})`` handles the necessary multi-table inserts
orchestrated by SQLAlchemy, while maintaining the simplified TableSchema method signature.

Table Methods
-------------

The TableSchema structure also promotes defining table interaction methods.

In SQLAlchemy, the class for a TableSchema represents the table while instances of the TableSchema represent rows of
the table. Furthermore, the TableSchema class specifically represents the schema, not the table itself. Therefore,
table manipulation methods are class methods and must be passed a Session, a link to a real table/database, to perform
a table manipulation.

``BaseTableSchema`` and its subclasses have a suite of common CRUD table manipulation methods. These include
``insert``, ``upsert``, ``delete``, ``count``, and various ``get`` methods (e.g., ``get_by_id``, ``get_all``).

These methods are class methods that take a `Session`_ (or `AsyncSession`_) as an argument:

.. code-block:: python

    with database.create_session() as session:
        user = UserTableSchema.get_by_id(session, 1)

Common CRUD Operations
----------------------

By inheriting from ``BaseTableSchema``, classes gain several methods for interacting with the database. These
methods are designed to be used as class methods, requiring a SQLAlchemy `Session`_ or `AsyncSession`_.

Insert
~~~~~~

Inserts new items into the table by passing a dictionary or an instance of the class.

.. code-block:: python

    with database.create_session() as session:
        # Insert using a dictionary
        UserTableSchema.insert(session, {"name": "Alice", "email": "alice@example.com"}, begin=True)

        # Insert using an instance
        new_user = UserTableSchema(name="Bob", email="bob@example.com")
        UserTableSchema.insert(session, new_user, begin=True)

Upsert
~~~~~~

The ``upsert`` method either inserts a new row or updates an existing one based on a primary key or a unique constraint.

.. code-block:: python

    with database.create_session() as session:
        # Upsert based on the 'id' (default)
        UserTableSchema.upsert(session, {"id": 1, "name": "Alice Updated"}, begin=True)

Delete
~~~~~~

Deleting an item requires an instance of the object.

.. code-block:: python

    with database.create_session() as session:
        user = UserTableSchema.get_by_id(session, 1)
        if user:
            UserTableSchema.delete(session, user, begin=True)

Count
~~~~~

You can easily count the number of rows in the table.

.. code-block:: python

    with database.create_session() as session:
        total_users = UserTableSchema.count(session)

Asynchronous Operations
~~~~~~~~~~~~~~~~~~~~~~~

All CRUD methods have an asynchronous counterpart (e.g., ``insert_async``, ``get_by_id_async``, etc.).

.. code-block:: python

    async with database.create_async_session() as session:
        await UserTableSchema.insert_async(session, {"name": "Charlie"}, begin=True)
        count = await UserTableSchema.count_async(session)



.. _Session: https://docs.sqlalchemy.org/en/20/orm/session_basics.html
.. _AsyncSession: https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html
.. _Joined Table Inheritance: https://docs.sqlalchemy.org/en/20/orm/inheritance.html#joined-table-inheritance
.. _Single Table Inheritance: https://docs.sqlalchemy.org/en/20/orm/inheritance.html#single-table-inheritance
.. _Concrete Table Inheritance: https://docs.sqlalchemy.org/en/20/orm/inheritance.html#concrete-table-inheritance
.. _DeclarativeBase: https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html

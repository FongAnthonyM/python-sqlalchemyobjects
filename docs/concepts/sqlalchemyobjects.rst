SQLAlchemy Objects
==================

The ``sqlalchemyobjects`` package is designed to streamline database interactions by providing a high-level,
object-oriented interface over standard SQLAlchemy. It introduces the concepts of :doc:`TableSchema <tableschema>`
mixins, :doc:`TableManifestations <tablemanifestation>`, and a unified :doc:`Database <database>` object to
simplify common CRUD operations and reduce boilerplate.

SQLAlchemy Core Concepts
------------------------

To understand the value of ``sqlalchemyobjects``, it is first necessary to review how standard SQLAlchemy handles
table interactions and inheritance.

Table Session Interactions
~~~~~~~~~~~~~~~~~~~~~~~~~~

In standard SQLAlchemy ORM, the `Session`_ object is the primary point of interaction. It manages the lifecycle of
objects, handles transactions, and facilitates queries. Users typically interact with the database by:

1.  Creating a `Session`_.
2.  Adding objects to the session (e.g., ``session.add(user)``).
3.  Committing the session (e.g., ``session.commit()``).
4.  Running queries via ``session.query(User)`` or ``select(User)``.

While powerful, this pattern requires the user to manually manage the session's lifecycle and write repetitive
query logic for common operations.

Table Inheritance
~~~~~~~~~~~~~~~~~

SQLAlchemy provides several `inheritance patterns`_ for mapping class hierarchies to database tables:

-   `Joined Table Inheritance`_: Each class in the hierarchy has its own table, and the tables are joined together.
-   `Single Table Inheritance`_: All classes in the hierarchy are stored in a single table, with a
    discriminator column to distinguish between types.
-   `Concrete Table Inheritance`_: Each class has its own table with all columns.

Managing these structures often involves complex mapper configurations and manual handling of polymorphic queries.

The Gap in Standard SQLAlchemy
------------------------------

Standard SQLAlchemy is a versatile toolkit, providing the building blocks for database interaction. However, it
intentionally avoids prescribing specific high-level patterns for common Create, Read, Update, and Delete (CRUD)
operations:

-   **No CRUD Mixins on Models**: Declarative Base models are typically "dumb" data structures. They do not
    natively know how to insert, upsert, or count themselves; these operations must be performed externally using
    a session.
-   **No Table-Bound Objects**: There is no built-in concept of an object that represents a specific table
    *instance* bound to a database connection, providing a high-level API for that specific table.
-   **Manual Session Management**: Users are responsible for ensuring sessions are correctly created, used,
    and closed for every database operation.

SQLAlchemy Objects Extensions
-----------------------------
``sqlalchemyobjects`` offers extensions to the SQLAlchemy paradigm to address these gaps.

-   :doc:`TableSchema <tableschema>`: Base classes that assist in defining SQLAlchemy inheritance structures and
    provide common CRUD methods as mixins.
-   :doc:`TableManifestation <tablemanifestation>`: Object representations of tables that provide a session-managed
    interface for data access and manipulation.
-   :doc:`Database <database>`: A unified object that manages database-wide operations and serves as the single source
    of truth for all database interactions.

For a detailed guide on how these components work together in a real-world application, see the
:doc:`Comprehensive Usage <comprehensive>` guide.

Specialized Tables
~~~~~~~~~~~~~~~~~~
The package also includes specialized table schemas and manifestations for common patterns:

*   **SingletonTable**: For tables that should only contain a single row, such as application configurations.
*   **MetaInformationTable**: For storing arbitrary key-value metadata.
*   **UpdateTable**: For tables that require automated "last updated" timestamp tracking.

Implications
------------

-   **Drastically Reduced Boilerplate**: Common operations that would require multiple lines of SQLAlchemy code
    are reduced to a single, readable method call.
-   **Consistent API**: Both synchronous and asynchronous operations are supported through a consistent
    interface (e.g., ``get_all()`` and ``get_all_async()``).
-   **Improved Readability**: Interactions feel more natural and object-oriented, making the codebase easier to
    understand and maintain.
-   **Better Encapsulation**: Data access logic is kept close to the schema definition or encapsulated within
    manifestations, promoting a cleaner project architecture.
-   **Simplified Inheritance**: By using ``TableSchema`` objects as mixins, you can easily define complex
    inheritance structures while keeping the CRUD API consistent across the entire hierarchy.

.. _Session: https://docs.sqlalchemy.org/en/20/orm/session_basics.html
.. _inheritance patterns: https://docs.sqlalchemy.org/en/20/orm/inheritance.html
.. _Joined Table Inheritance: https://docs.sqlalchemy.org/en/20/orm/inheritance.html#joined-table-inheritance
.. _Single Table Inheritance: https://docs.sqlalchemy.org/en/20/orm/inheritance.html#single-table-inheritance
.. _Concrete Table Inheritance: https://docs.sqlalchemy.org/en/20/orm/inheritance.html#concrete-table-inheritance

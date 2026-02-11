sqlalchemyobjects
=================

|PyPI| |Status| |Python Version| |License|

|Read the Docs| |Tests| |Codecov|

|pre-commit|

.. |PyPI| image:: https://img.shields.io/pypi/v/sqlalchemyobjects.svg
   :target: https://pypi.org/project/sqlalchemyobjects/
   :alt: PyPI
.. |Status| image:: https://img.shields.io/pypi/status/sqlalchemyobjects.svg
   :target: https://pypi.org/project/sqlalchemyobjects/
   :alt: Status
.. |Python Version| image:: https://img.shields.io/pypi/pyversions/sqlalchemyobjects
   :target: https://pypi.org/project/sqlalchemyobjects
   :alt: Python Version
.. |License| image:: https://img.shields.io/pypi/l/sqlalchemyobjects
   :target: https://github.com/AnthonyTechnologies/python-sqlalchemyobjects/blob/main/LICENSE
   :alt: License
.. |Read the Docs| image:: https://img.shields.io/readthedocs/python-sqlalchemyobjects/latest.svg?label=Read%20the%20Docs
   :target: https://python-sqlalchemyobjects.readthedocs.io/
   :alt: Read the documentation at https://python-sqlalchemyobjects.readthedocs.io/
.. |Tests| image:: https://github.com/AnthonyTechnologies/python-sqlalchemyobjects/workflows/Tests/badge.svg
   :target: https://github.com/AnthonyTechnologies/python-sqlalchemyobjects/actions?query=workflow%3ATests
   :alt: Tests
.. |Codecov| image:: https://codecov.io/gh/AnthonyTechnologies/python-sqlalchemyobjects/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/AnthonyTechnologies/python-sqlalchemyobjects
   :alt: Codecov
.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white
   :target: https://github.com/pre-commit/pre-commit
   :alt: pre-commit


Features
--------

*sqlalchemyobjects* provides a high-level, object-oriented interface for SQLAlchemy, designed to streamline database
interactions, simplify inheritance management, and provide a consistent API for both synchronous and asynchronous
workflows.

*   **TableSchema Mixins**: Define SQLAlchemy models with integrated CRUD methods (insert, upsert, delete, count)
    available as class methods for both sync and async sessions.
*   **TableManifestations**: Object-oriented table representations that manage their own session lifecycles and
    encapsulate table-specific business logic.
*   **Unified Database Object**: A central orchestrator that manages engines, session factories, and table
    manifestations, serving as the single source of truth for the application.
*   **Comprehensive Async Support**: Native, first-class support for asynchronous operations using SQLAlchemy's
    asyncio extension.
*   **Specialized Tables**: Built-in support for common patterns like ``SingletonTable`` (for configurations),
    ``MetaInformationTable`` (for metadata), and ``UpdateTable`` (for automated timestamp tracking).
*   **Backend Flexibility**: Easy configuration for SQLite, PostgreSQL, MySQL, Oracle, and MSSQL, with specific
    optimizations for SQLite (automated directory creation and URI modes).


Example
-------

Define a schema, a manifestation, and a database:

.. code:: python

   from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
   from sqlalchemy.ext.asyncio import AsyncAttrs
   from sqlalchemyobjects import Database, BaseTableSchema, TableManifestation

   # 1. Define the Schema
   class UserSchema(BaseTableSchema):
       __tablename__ = "user"
       name: Mapped[str]
       role: Mapped[str] = mapped_column(default="user")

   # 2. Define the Manifestation
   class UserTable(TableManifestation):
       table_schema = UserSchema

   # 3. Create Database Schema
   class DatabaseSchema(AsyncAttrs, DeclarativeBase):
       """The root schema for the application."""

   class DatabaseUserTableSchema(UserSchema, DatabaseSchema):
       """The actual SQLAlchemy model for the 'user' table."""

   # 4. Combine in a Database
   class MyDatabase(Database):
       schema = DatabaseSchema
       table_map = {"users": (UserTable, DatabaseUserTableSchema, {})}

   # 5. Use it
   with MyDatabase(path="my_database.db", create=True) as db:
       db.tables["users"].insert({"name": "Alice"})
       user = db.tables["users].get_by_id(1)
       print(f"Hello, {user.name}!")

Requirements
------------

* Python 3.14 or later
* SQLAlchemy
* aiosqlite

Installation
------------

You can install *sqlalchemyobjects* via pip_ from PyPI_:

.. code:: console

   $ pip install sqlalchemyobjects


Documentation
-------------

For comprehensive guides, see the full documentation on Read the Docs:
https://python-sqlalchemyobjects.readthedocs.io/

The documentation includes a user guide, API reference, tutorials, and examples to help you get productive quickly.

For project-wide conventions and contribution standards, refer to `Anthony's Python Style Guide`_.


Contributing
------------

Contributions are very welcome.
To learn more, see the `Contributor Guide`_.


License
-------

Distributed under the terms of the MIT License, *sqlalchemyobjects* is free and open source software.


Issues
------

If you encounter any problems,
please `file an issue`_ along with a detailed description.


Credits
-------

Project Organization: `Anthony's Python Style Guide`_ based on `The Google Style Guide`_ and
`Hypermodern Python`_ by `Claudio Jolowicz`_.

.. _pip: https://pip.pypa.io/
.. _PyPI: https://pypi.org/
.. _file an issue: https://github.com/AnthonyTechnologies/python-sqlalchemyobjects/issues
.. _Anthony's Python Style Guide: https://github.com/AnthonyTechnologies/python-styleguide
.. _The Google Style Guide: https://google.github.io/styleguide/pyguide.html
.. _Hypermodern Python: https://cjolowicz.github.io/posts/hypermodern-python-01-setup/
.. _Claudio Jolowicz: https://github.com/cjolowicz
.. github-only
.. _Contributor Guide: CONTRIBUTING.rst

"""databaseschema.py
The database schema classes for the comprehensive example.
"""

# Header #
__package_name__ = "sqlalchemyobjects"

__author__ = "Anthony Fong"
__credits__ = ["Anthony Fong"]
__copyright__ = "Copyright 2026, Anthony Fong"
__license__ = "MIT"

__version__ = "0.1.0"


# Imports #
# Third-Party Packages #
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

# Local Packages #
from .tables import AppMetaTableSchema, ConfigurationTableSchema, DepartmentTableSchema, EmployeeTableSchema


# Definitions #
# Classes #
class DatabaseAsyncSchema(AsyncAttrs, DeclarativeBase):
    """The root of the database schema which the whole database is built from."""


class DatabaseAppMetaTableSchema(AppMetaTableSchema, DatabaseAsyncSchema):
    """The schema for the database meta information table."""


class DatabaseConfigurationTableSchema(ConfigurationTableSchema, DatabaseAsyncSchema):
    """The schema for the database configuration table."""


class DatabaseDepartmentTableSchema(DepartmentTableSchema, DatabaseAsyncSchema):
    """The schema for the database department table."""


class DatabaseAEmployeeTableSchema(EmployeeTableSchema, DatabaseAsyncSchema):
    """The schema for the database A employee table."""

    # Class Attributes #
    __tablename__ = "a_employee"


class DatabaseBEmployeeTableSchema(EmployeeTableSchema, DatabaseAsyncSchema):
    """The schema for the database B employee table."""

    # Class Attributes #
    __tablename__ = "b_employee"

"""__init__.py
Tables for the comprehensive example.
"""

# Header #
__package_name__ = "sqlalchemyobjects"

__author__ = "Anthony Fong"
__credits__ = ["Anthony Fong"]
__copyright__ = "Copyright 2026, Anthony Fong"
__license__ = "MIT"

__version__ = "0.1.0"


# Imports #
# Local Packages #
from .app_meta import AppMetaTableManifestation, AppMetaTableSchema
from .configuration import ConfigurationTableManifestation, ConfigurationTableSchema
from .department import DepartmentTableManifestation, DepartmentTableSchema
from .employee import EmployeeTableManifestation, EmployeeTableSchema

__all__ = [
    "AppMetaTableManifestation",
    "AppMetaTableSchema",
    "ConfigurationTableManifestation",
    "ConfigurationTableSchema",
    "DepartmentTableManifestation",
    "DepartmentTableSchema",
    "EmployeeTableManifestation",
    "EmployeeTableSchema",
]

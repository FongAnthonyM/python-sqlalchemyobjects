"""__init__.py
Comprehensive example package.
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
from .comprehensivedatabase import ComprehensiveDatabase
from .tables import (
    AppMetaTableManifestation,
    AppMetaTableSchema,
    ConfigurationTableManifestation,
    ConfigurationTableSchema,
    DepartmentTableManifestation,
    DepartmentTableSchema,
    EmployeeTableManifestation,
    EmployeeTableSchema,
)

__all__ = [
    "AppMetaTableManifestation",
    "AppMetaTableSchema",
    "ComprehensiveDatabase",
    "ConfigurationTableManifestation",
    "ConfigurationTableSchema",
    "DepartmentTableManifestation",
    "DepartmentTableSchema",
    "EmployeeTableManifestation",
    "EmployeeTableSchema",
]

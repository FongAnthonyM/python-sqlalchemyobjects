"""database.py
Custom database definition for the comprehensive example.
"""

# Header #
__package_name__ = "sqlalchemyobjects"

__author__ = "Anthony Fong"
__credits__ = ["Anthony Fong"]
__copyright__ = "Copyright 2026, Anthony Fong"
__license__ = "MIT"

__version__ = "0.1.0"


# Imports #
# Source Packages #
from sqlalchemyobjects import Database

# Local Packages #
from .databaseschema import (
    DatabaseAEmployeeTableSchema,
    DatabaseAppMetaTableSchema,
    DatabaseAsyncSchema,
    DatabaseBEmployeeTableSchema,
    DatabaseConfigurationTableSchema,
    DatabaseDepartmentTableSchema,
)
from .tables import (
    AppMetaTableManifestation,
    ConfigurationTableManifestation,
    DepartmentTableManifestation,
    EmployeeTableManifestation,
)


# Definitions #
# Classes #
class ComprehensiveDatabase(Database):
    """A custom database for the comprehensive example."""

    # Attributes #
    schema = DatabaseAsyncSchema  # Set the schema for the database.
    table_map = {  # Map the tables to their manifestations, schemas, and kwargs for the manifestations.
        "app_meta": (AppMetaTableManifestation, DatabaseAppMetaTableSchema, {}),
        "configuration": (ConfigurationTableManifestation, DatabaseConfigurationTableSchema, {}),
        "a_employees": (EmployeeTableManifestation, DatabaseAEmployeeTableSchema, {}),
        "b_employees": (EmployeeTableManifestation, DatabaseBEmployeeTableSchema, {}),
        "departments": (DepartmentTableManifestation, DatabaseDepartmentTableSchema, {}),
    }

    # Properties #
    # The properties below are shortcuts for accessing the tables and are not required.
    @property
    def app_meta(self) -> AppMetaTableManifestation:
        """Access the app_meta table."""
        return self.tables["app_meta"]  # type: ignore[return-value]

    @property
    def configuration(self) -> ConfigurationTableManifestation:
        """Access the configuration table."""
        return self.tables["configuration"]  # type: ignore[return-value]

    @property
    def departments(self) -> DepartmentTableManifestation:
        """Access the departments table."""
        return self.tables["departments"]  # type: ignore[return-value]

    @property
    def a_employees(self) -> EmployeeTableManifestation:
        """Access the employees table."""
        return self.tables["a_employees"]  # type: ignore[return-value]

    @property
    def b_employees(self) -> EmployeeTableManifestation:
        """Access the employees table."""
        return self.tables["b_employees"]  # type: ignore[return-value]

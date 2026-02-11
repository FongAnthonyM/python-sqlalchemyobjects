"""employee.py
Employee table schema and manifestation for the comprehensive example.
"""

# Header #
__package_name__ = "sqlalchemyobjects"

__author__ = "Anthony Fong"
__credits__ = ["Anthony Fong"]
__copyright__ = "Copyright 2026, Anthony Fong"
__license__ = "MIT"

__version__ = "0.1.0"


# Imports #
# Standard Libraries #
from typing import Any

# Third-Party Packages #
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

# Source Packages #
from sqlalchemyobjects.tables.base import BaseTableSchema, TableManifestation


# Definitions #
# Classes #
class EmployeeTableSchema(BaseTableSchema):
    """A custom table schema for employees."""

    # Class Attributes #
    __tablename__ = "employee"
    __mapper_args__ = {"polymorphic_identity": "employee"}
    name: Mapped[str] = mapped_column(String)
    position: Mapped[str] = mapped_column(String)


class EmployeeTableManifestation(TableManifestation):
    """A custom manifestation for the employee table."""

    # Attributes #
    table_schema: type[EmployeeTableSchema]  # Not necessary but helpful for type checking

    # Instance Methods #
    def get_by_name(self, name: str, as_python: bool = True) -> Any:
        """Fetches an employee by name.

        Returns:
            The employee with the given name, or None if not found.
        """
        with self.create_session() as session:
            # Note: In a real app, you'd use a more efficient query.
            # Here we demonstrate using get_all and filtering.
            employees = self.get_all(session=session, as_python=as_python)
            if isinstance(employees, list):
                for emp in employees:
                    if emp["name"] == name:
                        return emp
            else:
                for emp in employees.scalars():
                    if emp.name == name:
                        return emp
        return None

    async def get_by_name_async(self, name: str, as_python: bool = True) -> Any:
        """Fetches an employee by name asynchronously.

        Returns:
            The employee with the given name, or None if not found.
        """
        async with self.create_async_session() as session:
            # Note: In a real app, you'd use a more efficient query.
            # Here we demonstrate using get_all and filtering.
            employees = await self.get_all_async(session=session, as_python=as_python)
            if isinstance(employees, list):
                for emp in employees:
                    if emp["name"] == name:
                        return emp
            else:
                async for emp in employees.scalars():
                    if emp.name == name:
                        return emp
        return None

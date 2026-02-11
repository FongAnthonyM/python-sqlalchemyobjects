"""department.py
Department table schema and manifestation for the comprehensive example.
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
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

# Source Packages #
from sqlalchemyobjects.tables.base import BaseUpdateTableSchema, UpdateTableManifestation


# Definitions #
# Classes #
class DepartmentTableSchema(BaseUpdateTableSchema):
    """A custom update table schema for departments."""

    # Class Attributes #
    __tablename__ = "department"
    __mapper_args__ = {"polymorphic_identity": "department"}
    name: Mapped[str] = mapped_column(String)
    budget: Mapped[int] = mapped_column(Integer)


class DepartmentTableManifestation(UpdateTableManifestation):
    """A custom manifestation for the department table."""

    # Attributes #
    table_schema: type[DepartmentTableSchema]  # Not necessary but helpful for type checking

    # Instance Methods #
    def get_large_budget_departments(self, threshold: int, as_python: bool = True) -> list[Any]:
        """Fetches departments with a budget larger than the threshold.

        Returns:
            The departments with a budget larger than the threshold.
        """
        with self.create_session() as session:
            departments = self.get_all(session=session, as_python=as_python)
            if isinstance(departments, list):
                return [d for d in departments if d["budget"] > threshold]
            else:
                return [d for d in departments.scalars() if d.budget > threshold]

    async def get_large_budget_departments_async(self, threshold: int, as_python: bool = True) -> list[Any]:
        """Fetches departments with a budget larger than the threshold asynchronously.

        Returns:
            The departments with a budget larger than the threshold.
        """
        async with self.create_async_session() as session:
            departments = await self.get_all_async(session=session, as_python=as_python)
            if isinstance(departments, list):
                return [d for d in departments if d["budget"] > threshold]
            else:
                return [d async for d in departments.scalars() if d.budget > threshold]

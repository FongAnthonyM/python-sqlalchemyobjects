"""app_meta.py
App meta table schema and manifestation for the comprehensive example.
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
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

# Source Packages #
from sqlalchemyobjects.tables.base import BaseMetaInformationTableSchema, MetaInformationTableManifestation


# Definitions #
# Classes #
class AppMetaTableSchema(BaseMetaInformationTableSchema):
    """A custom meta information table schema for application metadata."""

    # Class Attributes #
    __tablename__ = "app_meta"
    __mapper_args__ = {"polymorphic_identity": "app_meta"}
    version: Mapped[str] = mapped_column(String, default="1.0.0")
    last_run: Mapped[str | None] = mapped_column(String, nullable=True)


class AppMetaTableManifestation(MetaInformationTableManifestation):
    """A custom manifestation for the app meta table."""

    # Attributes #
    table_schema: type[AppMetaTableSchema]  # Not necessary but helpful for type checking

    # Instance Methods #
    def update_last_run(self, timestamp: str) -> None:
        """Updates the last run timestamp."""
        self.set_meta_information(last_run=timestamp)

    async def update_last_run_async(self, timestamp: str) -> None:
        """Updates the last run timestamp asynchronously."""
        await self.set_meta_information_async(last_run=timestamp)

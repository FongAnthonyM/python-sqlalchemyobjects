"""configuration.py
Configuration table schema and manifestation for the comprehensive example.
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
from sqlalchemyobjects.tables.base import BaseSingletonTableSchema, SingletonTableManifestation


# Definitions #
# Classes #
class ConfigurationTableSchema(BaseSingletonTableSchema):
    """A custom singleton table schema for system configuration."""

    # Class Attributes #
    __tablename__ = "configuration"
    __mapper_args__ = {"polymorphic_identity": "configuration"}
    app_name: Mapped[str] = mapped_column(String, default="Comprehensive Example App")
    debug_mode: Mapped[bool] = mapped_column(default=False)


class ConfigurationTableManifestation(SingletonTableManifestation):
    """A custom manifestation for the configuration table."""

    # Attributes #
    table_schema: type[ConfigurationTableSchema]  # Not necessary but helpful for type checking

    # Instance Methods #
    def toggle_debug_mode(self) -> bool:
        """Toggles the debug mode in the configuration.

        Returns:
            The new debug mode state.
        """
        config = self.get_item(as_python=False)
        if isinstance(config, ConfigurationTableSchema):
            new_mode = not config.debug_mode
            self.set_item(debug_mode=new_mode)
            return new_mode
        return False

    async def toggle_debug_mode_async(self) -> bool:
        """Toggles the debug mode in the configuration asynchronously.

        Returns:
            The new debug mode state.
        """
        config = await self.get_item_async(as_python=False)
        if isinstance(config, ConfigurationTableSchema):
            new_mode = not config.debug_mode
            await self.set_item_async(debug_mode=new_mode)
            return new_mode
        return False

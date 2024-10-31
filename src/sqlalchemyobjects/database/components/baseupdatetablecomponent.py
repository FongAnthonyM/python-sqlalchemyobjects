"""basedatabasecomponent.py.py

"""
# Package Header #
from ...header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
from typing import Any, Iterable

# Third-Party Packages #
from sqlalchemy import Result
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

# Local Packages #
from ...tables import BaseUpdateTable
from .basetablecomponent import BaseTableComponent


# Definitions #
# Classes #
class BaseUpdateTableComponent(BaseTableComponent):
    """A basic component for a database which is meant to interact with an update table.

    Attributes:
        _composite: A weak reference to the object which this object is a component of.
        table_name: The name of the table.
        _table: The table class.

    Args:
        composite: The object which this object is a component of.
        table_name: The name of the table.
        init: Determines if this object will construct.
        **kwargs: Keyword arguments for inheritance.
    """

    # Instance Methods #
    # Table
    def get_last_update_id(self, session: Session | None = None) -> int | None:
        """Gets the last update ID from the table.

        Args:
            session: The SQLAlchemy session to use for the query. Defaults to None.

        Returns:
            int | None: The last update ID.
        """
        if session is not None:
            return self.table.get_last_update_id(session)
        else:
            with self.create_session() as session:
                return self.table.get_last_update_id(session)

    async def get_last_update_id_async(self, session: AsyncSession | None = None) -> int | None:
        """Asynchronously gets the last update ID from the table.

        Args:
            session: The SQLAlchemy session to use for the query. Defaults to None.

        Returns:
            int | None: The last update ID.
        """
        if session is not None:
            return await self.table.get_last_update_id_async(session)
        else:
            async with self.create_async_session() as session:
                return await self.table.get_last_update_id_async(session)

    def get_from_update(
        self,
        update_id: int,
        session: Session | None = None,
        inclusive: bool = True,
        as_entries: bool = False,
    ) -> Result | list[dict[str, Any]]:
        """Gets entries from the table based on the update ID.

        Args:
            update_id: The update ID to filter entries.
            session: The SQLAlchemy session to use for the query. Defaults to None.
            inclusive: If True, includes the entry with the given update ID. Defaults to True.
            as_entries: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            Result | list[dict[str, Any]]: The result of the query, either as a Result object or as a list of dictionaries.
        """
        if session is not None:
            return self.table.get_from_update(session, update_id, inclusive, as_entries)
        else:
            with self.create_session() as session:
                return self.table.get_from_update(session, update_id, inclusive, as_entries)

    async def get_from_update_async(
        self,
        update_id: int,
        session: AsyncSession | None = None,
        inclusive: bool = True,
        as_entries: bool = False,
    ) -> Result | list[dict[str, Any]]:
        """Asynchronously gets entries from the table based on the update ID.

        Args:
            update_id: The update ID to filter entries.
            session: The SQLAlchemy session to use for the query. Defaults to None.
            inclusive: If True, includes the entry with the given update ID. Defaults to True.
            as_entries: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            Result | list[dict[str, Any]]: The result of the query, either as a Result object or as a list of dictionaries.
        """
        if session is not None:
            return await self.table.get_from_update_async(session, update_id, inclusive, as_entries)
        else:
            async with self.create_async_session() as session:
                return await self.table.get_from_update_async(session, update_id, inclusive, as_entries)

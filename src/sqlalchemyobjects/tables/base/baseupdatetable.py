"""basetable.py
An abstract base class which outlines a table to be used in a SQLAlchemy ORM model.
"""
# Package Header #
from src.sqlalchemyobjects.header import *

# Header #
__author__ = __author__
__credits__ = __credits__
__maintainer__ = __maintainer__
__email__ = __email__


# Imports #
# Standard Libraries #
from typing import Any

# Third-Party Packages #
from sqlalchemy import Result, select, lambda_stmt, func
from sqlalchemy.orm import mapped_column, Session
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.types import BigInteger

# Local Packages #
from src.sqlalchemyobjects.tables.base.basetable import BaseTable


# Definitions #
# Classes #
class BaseUpdateTable(BaseTable):
    """A base table for tracking updates in a SQLAlchemy ORM model.

    Class Attributes:
        __tablename__: The name of the table.
        __mapper_args__: Mapper arguments for SQLAlchemy ORM configurations.

    Columns:
        id: The primary key column of the table, using UUIDs.
        update_id: A column to track updates, using big integers.
    """

    # Class Attributes #
    __tablename__: str = "baseupdate"
    __mapper_args__: dict[str, str] = {"polymorphic_identity": "base"}

    # Columns #
    update_id = mapped_column(BigInteger, default=0)

    # Class Methods #
    @classmethod
    def get_last_update_id(cls, session: Session) -> int | None:
        """Gets the last update ID from the table.

        Args:
            session: The SQLAlchemy session to use for the query.

        Returns:
            int | None: The last update ID, or None if no updates exist.
        """
        return session.execute(lambda_stmt(lambda: select(func.max(cls.update_id)))).one_or_none()[0]

    @classmethod
    async def get_last_update_id_async(cls, session: AsyncSession) -> int | None:
        """Gets the last update ID from the table asynchronously.

        Args:
            session: The SQLAlchemy async session to use for the query.

        Returns:
            int | None: The last update ID, or None if no updates exist.
        """
        return (await session.execute(lambda_stmt(lambda: select(func.max(cls.update_id))))).one_or_none()[0]

    @classmethod
    def get_from_update(
        cls,
        session: Session,
        update_id: int,
        inclusive: bool = True,
        as_entries: bool = False,
    ) -> Result | list[dict[str, Any]]:
        """Gets entries from the table based on the update ID.

        Args:
            session: The SQLAlchemy session to use for the query.
            update_id: The update ID to filter by.
            inclusive: If True, includes entries with the specified update ID. Defaults to True.
            as_entries: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            Result | list[dict[str, Any]]: The result of the query, either as a Result object or as a list of dictionaries.
        """
        update_statement = lambda_stmt(lambda: select(cls))
        if inclusive:
            update_statement += lambda s: s.where(cls.update_id >= update_id)
        else:
            update_statement += lambda s: s.where(cls.update_id > update_id)

        results = session.execute(update_statement)
        return [r.as_entry() for r in results.scalars()] if as_entries else results

    @classmethod
    async def get_from_update_async(
        cls,
        session: AsyncSession,
        update_id: int,
        inclusive: bool = True,
        as_entries: bool = False,
    ) -> Result | list[dict[str, Any]]:
        """Gets entries from the table based on the update ID asynchronously.

        Args:
            session: The SQLAlchemy async session to use for the query.
            update_id: The update ID to filter by.
            inclusive: If True, includes entries with the specified update ID. Defaults to True.
            as_entries: If True, returns a list of dictionaries representing the entries; otherwise, returns a Result.

        Returns:
            Result | list[dict[str, Any]]: The result of the query, either as a Result object or as a list of dictionaries.
        """
        update_statement = lambda_stmt(lambda: select(cls))
        if inclusive:
            update_statement += lambda s: s.where(cls.update_id >= update_id)
        else:
            update_statement += lambda s: s.where(cls.update_id > update_id)

        results = await session.execute(update_statement)
        return [r.as_entry() for r in results.scalars()] if as_entries else results

    # Instance Methods #
    def update(self, dict_: dict[str, Any] | None = None, /, **kwargs) -> None:
        """Updates the row of the table with the provided dictionary or keyword arguments.

        Args:
            dict_: A dictionary of attributes/columns to update. Defaults to None.
            **kwargs: Additional keyword arguments for the attributes to update.
        """
        dict_ = ({} if dict_ is None else dict_) | kwargs
        if (update_id := dict_.get("update_id", None)) is not None:
            self.update_id = update_id

    def as_dict(self) -> dict[str, Any]:
        """Creates a dictionary with all the contents of the row.

        Returns:
            dict[str, Any]: A dictionary representation of the row.
        """
        dict_ = super().as_dict()
        dict_.update(update_id=self.update_id)
        return dict_

    def as_entry(self) -> dict[str, Any]:
        """Creates a dictionary with the entry contents of the row.

        Returns:
            dict[str, Any]: A dictionary representation of the entry.
        """
        entry = super().as_entry()
        entry.update(update_id=self.update_id)
        return entry

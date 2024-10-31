"""basedatasecomponent.py.py

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
from typing import Any

# Third-Party Packages #
from baseobjects import BaseComponent
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

# Local Packages #
from ...tables import BaseTable


# Definitions #
# Classes #
class BaseDatabaseComponent(BaseComponent):
    """A base class for database components.

    Attributes:
        _composite: A weak reference to the object which this object is a component of.

    Args:
        composite: The object which this object is a component of.
        init: Determines if this object will construct.
        **kwargs: Keyword arguments for inheritance.
    """

    # Properties #
    @property
    def tables(self) -> dict[str, type[BaseTable]] | None:
        """The tables of the database."""
        try:
            return self._composite().tables
        except TypeError:
            return None

    # Instance Methods #
    # Construction/Destruction
    def build(self, *args: Any, **kwargs: Any) -> None:
        """Build the component."""

    # File
    def load(self, *args: Any, **kwargs: Any) -> None:
        """Load the component."""

    # Session
    def create_session(self, *args: Any, **kwargs: Any) -> Session:
        """Creates a new SQLAlchemy session.

        Args:
            *args: Positional arguments for session creation.
            **kwargs: Keyword arguments for session creation.

        Returns:
            Session: A new SQLAlchemy session.
        """
        return self._composite().create_session(*args, **kwargs)

    def create_async_session(self, *args: Any, **kwargs: Any) -> AsyncSession:
        """Creates a new asynchronous SQLAlchemy session.

        Args:
            *args : Positional arguments for session creation.
            **kwargs: Keyword arguments for session creation.

        Returns:
            AsyncSession: A new asynchronous SQLAlchemy session.
        """
        return self._composite().create_async_session(*args, **kwargs)

    # Table
    def build_tables(self, *args: Any, **kwargs: Any) -> None:
        """Build the table for the component."""

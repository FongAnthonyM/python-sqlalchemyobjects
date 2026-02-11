"""__init__.py
Package initialization for sqlalchemyobjects.

This module initializes the sqlalchemyobjects package, which provides a set of objects for working with SQLAlchemy. It
also provides a central location for package metadata.
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
from .database import Database as Database
from .database import SQLAlchemyAsyncBackends as SQLAlchemyAsyncBackends
from .database import SQLAlchemyBackends as SQLAlchemyBackends
from .database import SQLiteModes as SQLiteModes
from .tables import *

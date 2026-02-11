"""__init__.py
ConcreteDatabaseSchema tables for sqlalchemyobjects.

This module contains the base table manifestations and schemas for the sqlalchemyobjects package.
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
from .basetable import BaseTableSchema as BaseTableSchema
from .basetable import TableManifestation as TableManifestation
from .metainformationtable import BaseMetaInformationTableSchema as BaseMetaInformationTableSchema
from .metainformationtable import MetaInformationTableManifestation as MetaInformationTableManifestation
from .singletontable import BaseSingletonTableSchema as BaseSingletonTableSchema
from .singletontable import SingletonTableManifestation as SingletonTableManifestation
from .updatetable import BaseUpdateTableSchema as BaseUpdateTableSchema
from .updatetable import UpdateTableManifestation as UpdateTableManifestation

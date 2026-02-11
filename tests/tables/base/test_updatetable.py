"""test_updatetable.py
Tests for the updatetable module.
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

# Third-Party Packages #
import pytest

# Source Packages #
from sqlalchemyobjects.testsuite import UpdateTableManifestationTestSuite, UpdateTableSchemaTestSuite


# Definitions #
# Classes #
class TestUpdateTableSchema(UpdateTableSchemaTestSuite):
    """Tests the BaseUpdateTableSchema class."""


class TestUpdateTableManifestation(UpdateTableManifestationTestSuite):
    """Tests the UpdateTableManifestation class."""

    # Instance Methods #
    # Tests #
    def test_build(self) -> None:
        """Tests the build method."""
        table_manifestation = self.create_new_table_manifestation()
        try:
            table_manifestation.database.create_database()
            table_manifestation.build()
            # build is a placeholder in base, just ensure it runs
            assert True
        finally:
            table_manifestation.database.close()

    def test_load(self) -> None:
        """Tests the load method."""
        table_manifestation = self.create_new_table_manifestation()
        try:
            table_manifestation.database.create_database()
            table_manifestation.load()
            # load is a placeholder in base, just ensure it runs
            assert True
        finally:
            table_manifestation.database.close()


# Main #
if __name__ == "__main__":
    pytest.main(["-v", "-s"])

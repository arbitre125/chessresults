# resultsdatabase.py
# Copyright 2011 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database using Sqlite3 database via apsw.
"""

from solentware_base import apsw_database

from ..core.filespec import FileSpec
from ..basecore import database


class ResultsDatabase(database.Database, apsw_database.Database):
    """Methods and data structures to create, open, and close database"""

    _datasourceset_modulename = "solentware_grid.core.datasourceset"
    _knownnames_modulename = "chessresults.basecore.knownnamesds"

    def __init__(self, sqlite3file, **kargs):

        names = FileSpec(**kargs)

        super(ResultsDatabase, self).__init__(names, sqlite3file, **kargs)

    def delete_database(self):
        """Close and delete the open chess results database."""
        return super().delete_database((self.database_file,))

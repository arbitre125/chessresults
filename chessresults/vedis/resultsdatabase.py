# resultsdatabase.py
# Copyright 2019 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database using a NoSQL database via vedis.
"""

from solentware_base import vedis_database

from ..core.filespec import FileSpec
from ..basecore import database


class ResultsDatabase(database.Database, vedis_database.Database):
    """Methods and data structures to create, open, and close database"""

    _datasourceset_modulename = "solentware_grid.core.datasourceset"
    _knownnames_modulename = "chessresults.basecore.knownnamesds"

    def __init__(self, nosqlfile, **kargs):

        names = FileSpec(**kargs)

        super(ResultsDatabase, self).__init__(names, nosqlfile, **kargs)

    def delete_database(self):
        """Close and delete the open chess results database."""
        return super().delete_database((self.database_file,))

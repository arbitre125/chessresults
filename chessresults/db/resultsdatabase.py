# resultsdatabase.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database using Berkeley DB database via bsddb3.
"""

from bsddb3.db import (
    DB_BTREE,
    DB_HASH,
    DB_RECNO,
    DB_DUPSORT,
    DB_CREATE,
    DB_RECOVER,
    DB_INIT_MPOOL,
    DB_INIT_LOCK,
    DB_INIT_LOG,
    DB_INIT_TXN,
    DB_PRIVATE,
    )

from solentware_base import bsddb3_database

from ..core.filespec import FileSpec
from ..basecore import database


class ResultsDatabase(database.Database, bsddb3_database.Database):
    """Methods and data structures to create, open, and close database."""

    _datasourceset_modulename = 'solentware_grid.core.datasourceset'
    _knownnames_modulename = 'chessresults.basecore.knownnamesds'

    def __init__(self, DBfile, **kargs):

        dbnames = FileSpec(**kargs)

        environment = {
            'flags': (DB_CREATE |
                      DB_RECOVER |
                      DB_INIT_MPOOL |
                      DB_INIT_LOCK |
                      DB_INIT_LOG |
                      DB_INIT_TXN |
                      DB_PRIVATE),
            }

        super(ResultsDatabase, self).__init__(
            dbnames,
            DBfile,
            environment,
            **kargs)

    def delete_database(self):
        """Close and delete the open chess results database."""
        return super().delete_database((self.database_file,
                                        self.dbenv.get_lg_dir().decode()))

    # Not clear why _keyify is necessary or just returns value for Berkeley DB.
    def _keyify(self, value):
        """Tranform a value from an ECF DbaseIII file for database key search.

        Overrides the default in database.Database which decodes value.

        """
        return value

    # Not clear why _keybyteify is necessary except it is same as for _keyify.
    # See version in db.resultsdatabase.
    def _keybyteify(self, value):
        """Tranform a value from an ECF json download for database key search.

        Overrides the default in database.Database which returns value.

        """
        return value.encode('iso-8859-1')

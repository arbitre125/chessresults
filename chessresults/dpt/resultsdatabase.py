# resultsdatabase.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database using DPT database via dptdb.dptapi.
"""

import os
import shutil

from solentware_base import dpt_database

from ..core.filespec import FileSpec
from ..basecore import database
from .. import APPLICATION_NAME


class ResultsDatabase(database.Database, dpt_database.Database):
    """Provide access to a database of results of games of chess."""

    _datasourceset_modulename = "solentware_grid.dpt.dptdatasourceset"
    _knownnames_modulename = "chessresults.dpt.knownnames"

    def __init__(self, databasefolder, **kargs):

        try:
            sysprint = kargs.pop("sysprint")
        except KeyError:
            sysprint = "CONSOLE"
        ddnames = FileSpec(**kargs)

        super(ResultsDatabase, self).__init__(
            ddnames, databasefolder, sysprint=sysprint, **kargs
        )

    def delete_database(self):
        """Close and delete the open chess results database."""
        names = [self.sysfolder]
        for k, v in self.table.items():
            names.append(v.file)
        return super().delete_database(names)

    def open_database(self, files=None):
        """Return '' if all files are opened in Normal mode (FISTAT == 0),
        or a message explaining why it remains closed.
        """
        super().open_database(files=files)
        fistat = dict()
        for dbo in self.table.values():
            fistat[dbo] = dbo.get_file_parameters(self.dbenv)["FISTAT"]
        for dbo in self.table.values():
            if fistat[dbo][0] != 0:
                break
        else:
            self.increase_database_size(files=None)
            return ""

        # At least one file is not in Normal state
        r = "\n".join(
            [
                "\t".join((os.path.basename(dbo.file), fistat[dbo][1]))
                for dbo in self.table.values()
            ]
        )
        self.close_database()
        return "".join(
            (
                APPLICATION_NAME,
                " opened the database but found some of the files are ",
                "not in the Normal state.\n\n",
                r,
                "\n\n",
                APPLICATION_NAME,
                " has closed the database.\n\nRestore the database from ",
                "backups, or source data, before trying again.",
            )
        )

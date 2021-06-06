# database.py
# Copyright 2019 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ChessResults database methods common to all database engine interfaces.
"""

import os
import shutil

from .. import APPLICATION_NAME, ERROR_LOG
from ..core import constants


class Database:

    """ """

    def open_database(self, files=None):
        """Return '' to fit behaviour of dpt version of this method."""
        super().open_database(files=files)
        return ""

    def delete_database(self, names):
        """Delete results database and return message about items not deleted."""
        listnames = set(n for n in os.listdir(self.home_directory))
        homenames = set(n for n in names if os.path.basename(n) in listnames)
        if ERROR_LOG in listnames:
            homenames.add(os.path.join(self.home_directory, ERROR_LOG))
        default = os.path.basename(self.home_directory).join(
            (constants.URL_NAMES, ".txt")
        )
        if default in listnames:
            homenames.add(os.path.join(self.home_directory, default))
        if len(listnames - set(os.path.basename(h) for h in homenames)):
            message = "".join(
                (
                    "There is at least one file or folder in\n\n",
                    self.home_directory,
                    "\n\nwhich may not be part of the database.  These items ",
                    "have not been deleted by ",
                    APPLICATION_NAME,
                    ".",
                )
            )
        else:
            message = None
        self.close_database()
        for h in homenames:
            if os.path.isdir(h):
                shutil.rmtree(h, ignore_errors=True)
            else:
                os.remove(h)
        try:
            os.rmdir(self.home_directory)
        except:
            pass
        return message

    def _strify(self, value):
        """Tranform a value from an ECF DbaseIII file to str.

        Assume iso-8859-1 encoding for value.

        """
        return value.decode("iso-8859-1")

    # Not clear why _keyify is necessary.  See version in db.resultsdatabase.
    def _keyify(self, value):
        """Tranform a value from an ECF DbaseIII file for database key search."""
        return self._strify(value)

    # Not clear why _keybyteify is necessary except it is same as for _keyify.
    # See version in db.resultsdatabase.
    def _keybyteify(self, value):
        """Tranform a value from an ECF json download for database key search."""
        return value

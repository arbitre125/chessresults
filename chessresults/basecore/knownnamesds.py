# knownnamesds.py
# Copyright 2017 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Interface to results database for player names known in other editions of
event.

The KnownNamesDS class in this module supports the apsw, db, and sqlite3,
intefaces to a database.

See the ..dpt.knownnames module for the KnownNamesDS class for DPT.

"""

from solentware_grid.core.datasourcecursor import DataSourceCursor

from .knownnames import KnownNames


class KnownNamesDS(DataSourceCursor, KnownNames):

    """Combine player names known in other editions of event using the apsw,
    db, or sqlite3, interfaces to a database.
    """

# knownnamesds.py
# Copyright 2017 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Interface to DPT results database for player names known in other editions
of event.

The KnownNamesDS class in this module supports the DPT inteface to a database.

See the ..basecore.knownnames module for the KnownNamesDS class for the apsw,
db, and sqlite3, intefaces to a database.

"""

from solentware_grid.dpt.datasourcecursor import DataSourceCursor

from ..basecore.knownnames import KnownNames


class KnownNamesDS(DataSourceCursor, KnownNames):
    
    """Combine player names known in other editions of event with DPT
    interface.
    """

# eventplayergrids.py
# Copyright 2017 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database datagrid classes for new players in an event.
"""

import tkinter

from solentware_grid.core import dataclient

from . import eventgrids
from . import resultsrow
from ..core import filespec
from ..core import resultsrecord


class EventPlayerBaseGrid(eventgrids.EventBaseGrid):

    """Base class for grid widgets used on event page."""


class EventPlayerGrid(EventPlayerBaseGrid):

    """Grid for players in an event whose names have been used in other
    editions of the event.

    These are still new players: they have not been linked to a known player
    nor marked as 'known new players'.  Known players do not appear in this
    grid.

    There is a very high chance the implied link to a known player is the
    correct one.
    """

    def __init__(self, panel, **kwargs):
        """Extend and link to data source."""
        super(EventPlayerGrid, self).__init__(panel, **kwargs)
        self.make_header(resultsrow.ResultsDBrowNewPlayer.header_specification)
        appsys = self.appsyspanel.get_appsys()
        db = appsys.get_results_database()
        ds = appsys.get_knownnamesdatasource_module().KnownNamesDS(
            db,
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYER_FILE_DEF,
            newrow=resultsrow.ResultsDBrowNewPlayer,
        )
        eventrecord = resultsrecord.get_event_from_record_value(
            db.get_primary_record(
                filespec.EVENT_FILE_DEF,
                appsys.get_event_detail_context().eventgrid.selection[0][-1],
            )
        )
        ds.get_known_names(eventrecord)
        self.set_data_source(ds)
        appsys.get_data_register().register_in(self, self.on_data_change)

# ecfeventgrids.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database datagrid classes for event's ECF detail and submission.
"""

import tkinter

from solentware_grid.core.dataclient import DataSource

from .. import eventgrids
from ..resultsrow import ResultsDBrowEvent
from ...core import filespec


class ECFEventBaseGrid(eventgrids.EventBaseGrid):

    """Base class for grid widgets used on ECF event page."""


class ECFEventGrid(ECFEventBaseGrid):

    """Grid for events to be submitted to ECF for grading."""

    def __init__(self, panel, **kwargs):
        """Extend and note sibling grids."""
        super(ECFEventGrid, self).__init__(panel, **kwargs)
        self.make_header(ResultsDBrowEvent.header_specification)
        ds = DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.EVENT_FILE_DEF,
            filespec.EVENTNAME_FIELD_DEF,
            ResultsDBrowEvent,
        )
        self.set_data_source(ds)
        self.appsyspanel.get_appsys().get_data_register().register_in(
            self, self.on_data_change
        )

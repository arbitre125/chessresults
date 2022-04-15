# leagues_lite.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Leagues frame class.
"""

from .. import leagues_database
from . import control_lite
from . import events_lite
from . import newplayers_lite


class Leagues(leagues_database.Leagues):

    """The Results frame for a Results database."""

    def define_state_switch_table(self):
        """Return dict of tuple(<state>, <action>):list(<state>, <tab>)."""
        switch_table = super().define_state_switch_table()
        switch_table.update(
            {
                (self._state_dbopen, events_lite.Events._btn_performance): [
                    self._state_dbopen_report_event,
                    self._tab_reportevent,
                ],
                (self._state_dbopen, events_lite.Events._btn_prediction): [
                    self._state_dbopen_report_event,
                    self._tab_reportevent,
                ],
                (self._state_dbopen, events_lite.Events._btn_population): [
                    self._state_dbopen_report_event,
                    self._tab_reportevent,
                ],
            }
        )
        return switch_table

    def results_control(self, **kargs):
        """Return control_lite.Control class instance."""
        return control_lite.Control(**kargs)

    def results_events(self, **kargs):
        """Return events_lite.Events class instance."""
        return events_lite.Events(**kargs)

    def results_newplayers(self, **kargs):
        """Return newplayers_lite.NewPlayers class instance."""
        return newplayers_lite.NewPlayers(**kargs)

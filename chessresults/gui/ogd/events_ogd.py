# events_ogd.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Event panel class.
"""

from ..lite import events_lite
from ...core.ogd import ecfgcodemaprecord
from ...core.ogd import ecfogdrecord
from ...core import resultsrecord


class Events(events_lite.Events):

    """The Events panel for a Results database."""

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database events panel."""
        super(Events, self).__init__(parent=parent, cnf=cnf, **kargs)

    def get_gradingcodes(self, database):
        """Return dict of ECF codes for players, default empty dict."""
        return {
            p: ecfgcodemaprecord.get_grading_code_for_person(database, person)
            for p, person in resultsrecord.get_persons(
                database, players
            ).items()
        }

    def get_ecfplayernames(self, database, gradingcodes):
        """Return dict of player names for ECF codes, default empty dict."""
        ecfplayers = {
            p: ecfogdrecord.get_ecf_ogd_player_for_grading_code(
                database, gradingcodes[p]
            ).value.ECFOGDname
            if gradingcodes[p]
            else ""
            for p in gradingcodes
        }
        return ecfplayers

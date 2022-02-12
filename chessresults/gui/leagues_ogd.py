# leagues_ogd.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Leagues frame class.
"""

import os
import importlib

from . import control_ogd
from . import events_ogd
from . import newplayers_ogd
from . import players
from . import ogdgradingcodes
from . import leagues_lite
from . import importecfogd
from .. import ECF_OGD_DATA_IMPORT_MODULE


class Leagues(leagues_lite.Leagues):

    """The Results frame for a Results database.

    Use as
    Leagues(..., database_modulenname=results._dbresults, ...)
    for runtime "from <db|dpt>results import ResultsDatabase".

    """

    _tab_ecfogdgradingcodes = "leagues_ogd_tab_ecfogdgradingcodes"
    _tab_importecfogd = "leagues_ogd_tab_importecfogd"

    _state_importecfogd = "leagues_ogd_state_importecfogd"

    def __init__(self, master=None, cnf=dict(), **kargs):
        """Extend and define the results database results frame."""
        super(Leagues, self).__init__(master=master, cnf=cnf, **kargs)

        self._show_grading_list_grading_codes = True

        self.define_tab(
            self._tab_control,
            text="Administration",
            tooltip="Open and close databases and import data.",
            underline=0,
            tabclass=lambda **k: control_ogd.Control(**k),
            create_actions=(control_ogd.Control._btn_opendatabase,),
            destroy_actions=(control_ogd.Control._btn_closedatabase,),
        )
        self.define_tab(
            self._tab_events,
            text="Events",
            tooltip="Export event data",
            underline=0,
            tabclass=lambda **k: events_ogd.Events(gridhorizontal=False, **k),
            destroy_actions=(control_ogd.Control._btn_closedatabase,),
        )
        self.define_tab(
            self._tab_newplayers,
            text="NewPlayers",
            tooltip="Identify new players and merge with existing players.",
            underline=0,
            tabclass=lambda **k: newplayers_ogd.NewPlayers(
                gridhorizontal=False, **k
            ),
            destroy_actions=(control_ogd.Control._btn_closedatabase,),
        )
        self.define_tab(
            self._tab_players,
            text="Players",
            tooltip="Merge or separate existing players.",
            underline=0,
            tabclass=lambda **k: players.Players(gridhorizontal=False, **k),
            destroy_actions=(control_ogd.Control._btn_closedatabase,),
        )
        self.define_tab(
            self._tab_ecfogdgradingcodes,
            text="Grading Codes",
            tooltip="Associate player with ECF grading code.",
            underline=0,
            tabclass=lambda **k: ogdgradingcodes.ECFGradingCodes(
                gridhorizontal=False, **k
            ),
            destroy_actions=(control_ogd.Control._btn_closedatabase,),
        )
        self.define_tab(
            self._tab_importecfogd,
            text="Import ECF Online Grading Database",
            tooltip="Import ECF Online Grading Database from zipped files.",
            underline=-1,
            tabclass=lambda **k: importecfogd.ImportECFOGD(**k),
            destroy_actions=(
                importecfogd.ImportECFOGD._btn_closeecfogdimport,
            ),
        )

        self.define_state_transitions(
            tab_state={
                self._state_dbopen: (
                    self._tab_control,
                    self._tab_events,
                    self._tab_newplayers,
                    self._tab_players,
                    self._tab_ecfogdgradingcodes,
                ),
                self._state_importecfogd: (self._tab_importecfogd,),
            },
            switch_state={
                (
                    self._state_dbopen,
                    control_ogd.Control._btn_copyecfogdgradingfile,
                ): [self._state_importecfogd, self._tab_importecfogd],
                (
                    self._state_importecfogd,
                    importecfogd.ImportECFOGD._btn_closeecfogdimport,
                ): [self._state_dbopen, self._tab_control],
            },
        )

    def set_ecfogddataimport_module(self, enginename):
        """Import the ECF reference data import module."""
        self._ecfogddataimport_module = importlib.import_module(
            ECF_OGD_DATA_IMPORT_MODULE[enginename], "chessresults.gui"
        )

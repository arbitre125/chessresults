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
from . import ogdgradingcodes
from . import importecfogd
from .. import leagues_database
from ... import ECF_OGD_DATA_IMPORT_MODULE


class Leagues(leagues_database.Leagues):

    """The Results frame for a Results database.

    Use as
    Leagues(..., database_modulenname=results._dbresults, ...)
    for runtime "from <db|dpt>results import ResultsDatabase".

    """

    _tab_ecfogdgradingcodes = "leagues_ogd_tab_ecfogdgradingcodes"
    _tab_importecfogd_grading = "leagues_ogd_tab_importecfogdgrading"
    _tab_importecfogd_rating = "leagues_ogd_tab_importecfogdrating"

    _state_importecfogd_grading = "leagues_ogd_state_importecfogdgrading"
    _state_importecfogd_rating = "leagues_ogd_state_importecfogdrating"

    def __init__(self, master=None, cnf=dict(), **kargs):
        """Extend and define the results database results frame."""
        super(Leagues, self).__init__(master=master, cnf=cnf, **kargs)

    def define_tabs(self):
        """Define the application tabs."""
        super().define_tabs()
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
            self._tab_importecfogd_grading,
            text="Import ECF Online Grading Database",
            tooltip="Import ECF Online Grading Database from zipped files.",
            underline=-1,
            tabclass=lambda **k: importecfogd.ImportECFOGD(**k),
            destroy_actions=(
                importecfogd.ImportECFOGD._btn_closeecfogdimport,
                control_ogd.Control._btn_closedatabase,
            ),
        )
        self.define_tab(
            self._tab_importecfogd_rating,
            text="Import ECF Online Rating Database",
            tooltip="Import ECF Online Rating Database from zipped files.",
            underline=-1,
            tabclass=lambda **k: importecfogd.ImportECFOGD(**k),
            destroy_actions=(
                importecfogd.ImportECFOGD._btn_closeecfogdimport,
                control_ogd.Control._btn_closedatabase,
            ),
        )

    def define_tab_states(self):
        """Return dict of <state>:tuple(<tab>, ...)."""
        tab_states = super().define_tab_states()
        tab_states.update(
            {
                self._state_dbopen: (
                    self._tab_control,
                    self._tab_events,
                    self._tab_newplayers,
                    self._tab_players,
                    self._tab_ecfogdgradingcodes,
                ),
                self._state_dataopen_dbopen: (self._tab_sourceedit,),
                self._state_importecfogd_grading: (
                    self._tab_importecfogd_grading,
                ),
                self._state_importecfogd_rating: (
                    self._tab_importecfogd_rating,
                ),
            }
        )
        return tab_states

    def define_state_switch_table(self):
        """Return dict of tuple(<state>, <action>):list(<state>, <tab>)."""
        switch_table = super().define_state_switch_table()
        switch_table.update(
            {
                (
                    self._state_dbopen,
                    control_ogd.Control._btn_copyecfogdgradingfile,
                ): [
                    self._state_importecfogd_grading,
                    self._tab_importecfogd_grading,
                ],
                (
                    self._state_importecfogd_grading,
                    importecfogd.ImportECFOGD._btn_closeecfogdimport,
                ): [self._state_dbopen, self._tab_control],
                (
                    self._state_importecfogd_grading,
                    control_ogd.Control._btn_closedatabase,
                ): [self._state_dbclosed, None],
                (
                    self._state_dbopen,
                    control_ogd.Control._btn_copyecfogdratingfile,
                ): [
                    self._state_importecfogd_rating,
                    self._tab_importecfogd_rating,
                ],
                (
                    self._state_importecfogd_rating,
                    importecfogd.ImportECFOGD._btn_closeecfogdimport,
                ): [self._state_dbopen, self._tab_control],
                (
                    self._state_importecfogd_rating,
                    control_ogd.Control._btn_closedatabase,
                ): [self._state_dbclosed, None],
            }
        )
        return switch_table

    def set_ecfogddataimport_module(self, enginename):
        """Import the ECF reference data import module."""
        self._ecfogddataimport_module = importlib.import_module(
            ECF_OGD_DATA_IMPORT_MODULE[enginename], "chessresults.gui"
        )

    def results_control(self, **kargs):
        """Return control_ogd.Control class instance."""
        return control_ogd.Control(**kargs)

    def results_events(self, **kargs):
        """Return events_ogd.Events class instance."""
        return events_ogd.Events(**kargs)

    def results_newplayers(self, **kargs):
        """Return newplayers_ogd.NewPlayers class instance."""
        return newplayers_ogd.NewPlayers(**kargs)

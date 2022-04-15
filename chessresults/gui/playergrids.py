# playergrids.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database datagrid classes for identifying players.
"""

import tkinter

from solentware_grid.datagrid import DataGridReadOnly
from solentware_grid.core import dataclient

from solentware_misc.core.utilities import AppSysPersonNameParts
from solentware_misc.gui import gridbindings

from . import resultsrow
from ..core import filespec


class PlayerGrid(gridbindings.SelectorGridBindings, DataGridReadOnly):

    """Base class for grid widgets used on new player and player pages."""

    def __init__(self, panel, focus_selector=None, **kwargs):
        """Extend and bind grid navigation within page commands to events."""
        DataGridReadOnly.__init__(self, panel)
        gridbindings.SelectorGridBindings.__init__(
            self, focus_selector=focus_selector, **kwargs
        )
        self.bindings(function=self.on_focus_in)

    def show_popup_menu_no_row(self, event=None):
        """Override superclass to do nothing."""
        # Added when DataGridBase changed to assume a popup menu is available
        # when right-click done on empty part of data drid frame.  The popup is
        # used to show all navigation available from grid: but this is not done
        # in results, at least yet, so avoid the temporary loss of focus to an
        # empty popup menu.


class AliasGrid(PlayerGrid):

    """Grid for all players."""

    def __init__(self, panel, **kwargs):
        """Custom PlayerGrid for the playeralias index."""
        super(AliasGrid, self).__init__(panel, **kwargs)
        dr = self.appsyspanel.get_appsys().get_data_register()
        self.make_header(resultsrow.ResultsDBrowAlias.header_specification)
        ds = dataclient.DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYERNAME_FIELD_DEF,
            newrow=resultsrow.ResultsDBrowAlias,
        )
        self.set_data_source(ds)
        dr.register_in(self, self.on_data_change)


class IdentityGrid(PlayerGrid):

    """Grid for identified players."""

    def __init__(self, panel, **kwargs):
        """Custom PlayerGrid for the playeridentity index."""
        super(IdentityGrid, self).__init__(panel, **kwargs)
        dr = self.appsyspanel.get_appsys().get_data_register()
        self.make_header(resultsrow.ResultsDBrowIdentity.header_specification)
        ds = dataclient.DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYERNAMEIDENTITY_FIELD_DEF,
            newrow=resultsrow.ResultsDBrowIdentity,
        )
        self.set_data_source(ds)
        dr.register_in(self, self.on_data_change)


class NewGrid(PlayerGrid):

    """Grid for new players."""

    def __init__(self, panel, **kwargs):
        """Custom PlayerGrid for the playernew index."""
        super(NewGrid, self).__init__(panel, **kwargs)
        dr = self.appsyspanel.get_appsys().get_data_register()
        self.make_header(resultsrow.ResultsDBrowNewPlayer.header_specification)
        ds = dataclient.DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYERPARTIALNEW_FIELD_DEF,
            newrow=resultsrow.ResultsDBrowNewPlayer,
        )
        self.set_data_source(ds)
        dr.register_in(self, self.on_data_change)

    def bookmark_down(self):
        """Extend to adjust Identified grid."""
        super(NewGrid, self).bookmark_down()
        # not implemented
        # self.appsyspanel.playergrid.display_identified_players_for_selection()

    def bookmark_up(self):
        """Extend to adjust Identified grid."""
        super(NewGrid, self).bookmark_up()
        # not implemented
        # self.appsyspanel.playergrid.display_identified_players_for_selection()

# ogdplayergrids.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Datagrid classes for allocating ECF online grading codes to players.
"""

import tkinter

from solentware_grid.core import dataclient

from . import ecfogdrow
from . import ecfgcodemaprow
from .. import playergrids
from ...core import filespec


class ECFOGDPlayerGrid(playergrids.PlayerGrid):

    """Base class for grid widgets used on ECF grading code page."""


class OGDPersonGrid(ECFOGDPlayerGrid):

    """Grid for players linked to ECF grading code on Online Grading Database."""

    def __init__(self, panel, **kwargs):
        """Extend, customise record selection widget, and note sibling grids."""
        super(OGDPersonGrid, self).__init__(panel, **kwargs)
        self.make_header(
            ecfgcodemaprow.ECFmapOGDrowPlayer.header_specification
        )
        ds = dataclient.DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYERIDENTITY_FIELD_DEF,
            ecfgcodemaprow.ECFmapOGDrowPlayer,
        )
        self.set_data_source(ds)
        self.appsyspanel.get_appsys().get_data_register().register_in(
            self, self.on_data_change
        )

    def encode_navigate_grid_key(self, key):
        """Return key after formatting and delegating encoding to superclass.

        This method is used to process text entered by the user.
        It is not used by the standard navigation functions (page up and so on).

        This method converts key to look like the start of a <key> held on the
        database after a repr(<key>) call.

        """
        k = repr((key,))
        return super().encode_navigate_grid_key(k[: k.index(key) + len(key)])


class ECFOGDPersonGrid(ECFOGDPlayerGrid):

    """Grid for players on Online Grading Database with ECF grading codes."""

    def __init__(self, panel, **kwargs):
        """Extend, customise record selection widget, and note sibling grids."""
        super(ECFOGDPersonGrid, self).__init__(panel, **kwargs)
        self.make_header(ecfogdrow.ECFrefOGDrowPlayer.header_specification)
        ds = dataclient.DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.ECFOGDPLAYER_FILE_DEF,
            filespec.OGDPLAYERNAME_FIELD_DEF,
            ecfogdrow.ECFrefOGDrowPlayer,
        )
        self.set_data_source(ds)
        self.appsyspanel.get_appsys().get_data_register().register_in(
            self, self.on_data_change
        )

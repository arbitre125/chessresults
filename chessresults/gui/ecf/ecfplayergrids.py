# ecfplayergrids.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database datagrid classes for assigning ECF grading codes to players.
"""

import tkinter

from solentware_grid.core import dataclient

from . import ecfrow
from . import ecfmaprow
from .. import playergrids
from ...core import filespec


class ECFPlayerGrid(playergrids.PlayerGrid):

    """Base class for grid widgets used on ECF grading code page."""


class NewPersonGrid(ECFPlayerGrid):

    """Grid for players with no ECF grading code recorded."""

    def __init__(self, panel, **kwargs):
        """Extend, customise record selection widget, and note sibling grids."""
        super(NewPersonGrid, self).__init__(panel, **kwargs)
        self.make_header(ecfmaprow.ECFmapDBrowNewPerson.header_specification)
        ds = dataclient.DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.MAPECFPLAYER_FILE_DEF,
            filespec.PERSONMAP_FIELD_DEF,
            newrow=ecfmaprow.ECFmapDBrowNewPerson,
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


class PersonGrid(ECFPlayerGrid):

    """Grid for players linked to ECF grading code."""

    def __init__(self, panel, **kwargs):
        """Extend, customise record selection widget, and note sibling grids."""
        super(PersonGrid, self).__init__(panel, **kwargs)
        self.make_header(ecfmaprow.ECFmapDBrowPerson.header_specification)
        ds = dataclient.DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYERNAME_FIELD_DEF,
            newrow=ecfmaprow.ECFmapDBrowPerson,
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


class ECFPersonGrid(ECFPlayerGrid):

    """Grid for players on master list with ECF grading codes."""

    def __init__(self, panel, **kwargs):
        """Extend, customise record selection widget, and note sibling grids."""
        super(ECFPersonGrid, self).__init__(panel, **kwargs)
        self.make_header(ecfrow.ECFrefDBrowECFPlayer.header_specification)
        ds = dataclient.DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.ECFPLAYER_FILE_DEF,
            filespec.ECFPLAYERNAME_FIELD_DEF,
            newrow=ecfrow.ECFrefDBrowECFPlayer,
        )
        self.set_data_source(ds)
        self.appsyspanel.get_appsys().get_data_register().register_in(
            self, self.on_data_change
        )


class NewPlayerClubGrid(ECFPlayerGrid):

    """Grid for players with no ECF club affiliation recorded."""

    def __init__(self, panel, **kwargs):
        """Extend, customise record selection widget, and note sibling grids."""
        super(NewPlayerClubGrid, self).__init__(panel, **kwargs)
        self.make_header(ecfmaprow.ECFmapDBrowNewPlayer.header_specification)
        ds = dataclient.DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.MAPECFCLUB_FILE_DEF,
            filespec.PLAYERALIASMAP_FIELD_DEF,
            newrow=ecfmaprow.ECFmapDBrowNewPlayer,
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


class PlayerECFDetailGrid(ECFPlayerGrid):

    """Grid for ECF detail of identified players."""

    def __init__(self, panel, **kwargs):
        """Extend, customise record selection widget, and note sibling grids."""
        super(PlayerECFDetailGrid, self).__init__(panel, **kwargs)
        self.make_header(ecfmaprow.ECFmapDBrowPlayer.header_specification)
        ds = dataclient.DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYERNAME_FIELD_DEF,
            newrow=ecfmaprow.ECFmapDBrowPlayer,
        )
        self.set_data_source(ds)
        self.appsyspanel.get_appsys().get_data_register().register_in(
            self, self.on_data_change
        )


class ECFClubCodeGrid(ECFPlayerGrid):

    """Grid for ECF clubs available for affiliation."""

    def __init__(self, panel, **kwargs):
        """Extend, customise record selection widget, and note sibling grids."""
        super(ECFClubCodeGrid, self).__init__(panel, **kwargs)
        self.make_header(ecfrow.ECFrefDBrowECFClub.header_specification)
        ds = dataclient.DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.ECFCLUB_FILE_DEF,
            filespec.ECFCLUBNAME_FIELD_DEF,
            newrow=ecfrow.ECFrefDBrowECFClub,
        )
        self.set_data_source(ds)
        self.appsyspanel.get_appsys().get_data_register().register_in(
            self, self.on_data_change
        )

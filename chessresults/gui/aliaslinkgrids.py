# aliaslinkgrids.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database datagrid classes for identifying players.

ResultsDBrowAliasLink is separated from the similar classes in resultsrow
module because it depends additionally on record definitions from the ECF
and OGD variants of chessresults.

The existence of an ECF code, formerly Grading code, link to either the
ECF or OGD tables of ECF codes is important even if the Database or Lite
variant of chessresults is being used.  This is to prevent a destructive
adjustment of the alias links, which may wreck ECF code links set up by
the ECF or OGD variants.

"""

from solentware_grid.core import dataclient

from . import aliaslinkrow
from . import playergrids
from ..core import filespec


class AliasLinkGrid(playergrids.PlayerGrid):

    """Grid for all players with grading code link."""

    def __init__(self, panel, **kwargs):
        """Custom PlayerGrid for the playeralias index."""
        super(AliasLinkGrid, self).__init__(panel, **kwargs)
        dr = self.appsyspanel.get_appsys().get_data_register()
        self.make_header(
            aliaslinkrow.ResultsDBrowAliasLink.header_specification
        )
        ds = dataclient.DataSource(
            self.appsyspanel.get_appsys().get_results_database(),
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYERNAME_FIELD_DEF,
            newrow=aliaslinkrow.ResultsDBrowAliasLink,
        )
        self.set_data_source(ds)
        dr.register_in(self, self.on_data_change)

# aliaslinkrow.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Create widgets that display details of events and players.

ResultsDBrowAliasLink is separated from the similar classes in resultsrow
module because it depends additionally on record definitions from the ECF
and OGD variants of chessresults.

The existence of an ECF code, formerly Grading code, link to either the
ECF or OGD tables of ECF codes is important even if the Database or Lite
variant of chessresults is being used.  This is to prevent a destructive
adjustment of the alias links, which may wreck ECF code links set up by
the ECF or OGD variants.

"""

import tkinter

from solentware_grid.gui.datarow import (
    GRID_COLUMNCONFIGURE,
    GRID_CONFIGURE,
    WIDGET_CONFIGURE,
    WIDGET,
    ROW,
)

from .datarow import DataRow
from ..core import resultsrecord
from ..core.ecf import ecfmaprecord
from ..core.ogd import ecfgcodemaprecord


class ResultsDBrowAliasLink(resultsrecord.ResultsDBrecordPlayer, DataRow):

    """Display an alias record with grading code link."""

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Name", anchor=tkinter.CENTER),
            GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="npname"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Event details", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="npevent"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="npsection"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Association", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=3, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="npaff"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(
                text="Linked Grading Code", anchor=tkinter.W
            ),
            GRID_CONFIGURE: dict(column=4, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="nplink"),
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link new player record to database."""
        super(ResultsDBrowAliasLink, self).__init__()
        self.set_database(database)
        self.row_specification = [
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: dict(anchor=tkinter.CENTER),
                GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
                ROW: 0,
            },
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: dict(anchor=tkinter.W),
                GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
                ROW: 0,
            },
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: dict(anchor=tkinter.W),
                GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
                ROW: 0,
            },
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: dict(anchor=tkinter.W),
                GRID_CONFIGURE: dict(column=3, sticky=tkinter.EW),
                ROW: 0,
            },
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: dict(anchor=tkinter.W),
                GRID_CONFIGURE: dict(column=4, sticky=tkinter.EW),
                ROW: 0,
            },
        ]

    def grid_row(self, **kargs):
        """Return super(ResultsDBrowAliasLink).grid_row(textitems=(.), **kargs).

        Create textitems argument for ResultsDBrowAliasLink instance.

        """
        person = resultsrecord.get_person_from_player(self.database, self)
        grading_code = ecfmaprecord.get_grading_code_for_person(
            self.database, person
        )
        if not grading_code:
            grading_code = ecfgcodemaprecord.get_grading_code_for_person(
                self.database, person
            )
        return super(ResultsDBrowAliasLink, self).grid_row(
            textitems=(
                self.value.name,
                resultsrecord.get_event_details(
                    self.database, self.value.event
                ),
                resultsrecord.get_section_details(
                    self.database, self.value.section, self.value.pin
                ),
                resultsrecord.get_affiliation_details(
                    self.database, self.value.affiliation
                ),
                grading_code,
            ),
            **kargs
        )

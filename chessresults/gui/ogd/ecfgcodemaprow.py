# ecfgcodemaprow.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Create widgets that display player details with Online Grading List data.
"""
# class names need to be tidied up

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
from ..core import ecfogdrecord
from ..core import ecfgcodemaprecord


class ECFmapOGDrowPlayer(resultsrecord.ResultsDBrecordPlayer, DataRow):

    """Display a player record."""

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="ECF code", anchor=tkinter.CENTER),
            GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="pecfcode"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Name", anchor=tkinter.CENTER),
            GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="pname"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Event details", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="pevent"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=3, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="psection"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Association", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=4, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="paff"),
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link player record to database."""
        super(ECFmapOGDrowPlayer, self).__init__()
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
                WIDGET_CONFIGURE: dict(anchor=tkinter.CENTER),
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
        """Return super(ECFmapOGDrowPlayer,).grid_row(textitems=(..), **kargs).

        Create textitems argument for ECFmapOGDrowPlayer instance.

        """
        mapcode = ecfgcodemaprecord.get_grading_code_for_person(
            self.database,
            resultsrecord.get_person_from_alias(self.database, self),
        )
        if mapcode:
            ogdrec = ecfogdrecord.get_ecf_ogd_player_for_grading_code(
                self.database, mapcode
            )
            if ogdrec is None:
                mapcode = "*"
            elif ogdrec.value.ECFOGDname is None:
                mapcode = "*"
        else:
            mapcode = ""
        return super(ECFmapOGDrowPlayer, self).grid_row(
            textitems=(
                mapcode,
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
            ),
            **kargs
        )

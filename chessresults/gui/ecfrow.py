# ecfrow.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Create widgets that display ECF club and player details.
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
from ..core import ecfrecord
from ..core import ecfmaprecord


class ECFrefDBrowECFClub(ecfrecord.ECFrefDBrecordECFclub, DataRow):

    """Display an ECF Club record.

    Note that this is the subset of fields copied from master file.

    """
    header_specification = [
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Status', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='cactive'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Club code', anchor=tkinter.CENTER),
         GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=0, uniform='ccode'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Name', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='cname'),
         ROW: 0,
         },
        ]

    def __init__(self, database=None):
        """Extend, link ECF club record from master file to database."""
        super(ECFrefDBrowECFClub, self).__init__()
        self.set_database(database)
        self.row_specification = [
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.W),
             GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
             ROW: 0,
             },
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.CENTER),
             GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
             ROW: 0,
             },
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.W),
             GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
             ROW: 0,
             },
            ]
        
    def grid_row(self, **kargs):
        """Return super(ECFrefDBrowECFClub,).grid_row(textitems=(...), **kargs).

        Create textitems argument for ECFrefDBrowECFClub instance.

        """
        return super(ECFrefDBrowECFClub, self).grid_row(
            textitems=(
                'Inactive' if not self.value.ECFactive else '',
                self.value.ECFcode,
                self.value.ECFname),
            **kargs)


class ECFrefDBrowECFPlayer(ecfrecord.ECFrefDBrecordECFplayer, DataRow):

    """Display an ECF player record.

    Note that this is the subset of fields copied from master file.

    """
    header_specification = [
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Merge status', anchor=tkinter.CENTER),
         GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=0, uniform='pmerge'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Grading code', anchor=tkinter.CENTER),
         GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=0, uniform='pcode'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Name (ECF)', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='pname'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(
             text="Clubs (if grading code listed in 'Player ECF Detail')",
             anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=3, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='pclubs'),
         ROW: 0,
         },
        ]

    def __init__(self, database=None):
        """Extend, link ECF player record from master file to database."""
        super(ECFrefDBrowECFPlayer, self).__init__()
        self.set_database(database)
        self.row_specification = [
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.CENTER),
             GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
             ROW: 0,
             },
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.CENTER),
             GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
             ROW: 0,
             },
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.W),
             GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
             ROW: 0,
             },
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.W),
             GRID_CONFIGURE: dict(column=3, sticky=tkinter.EW),
             ROW: 0,
             },
            ]
        
    def grid_row(self, **kargs):
        """Return super(ECFrefDBrowECFPlayer,).grid_row(textitems=(.), **kargs).

        Create textitems argument for ECFrefDBrowECFPlayer instance.

        """
        if self.value.ECFactive:
            merged_into = ''
            person = ecfmaprecord.get_person_for_grading_code(
                self.database, self.value.ECFcode)
            if person is None:
                clubs = ''
            elif self.value.ECFclubcodes:
                clubs = '\t\t'.join(ecfrecord.get_ecf_clubs_for_player(
                    self.database, self.value.ECFclubcodes))
            else:
                clubs = 'No clubs listed by ECF'
        elif self.value.ECFmerge:
            merged_into = self.value.ECFmerge
            clubs = (
                'ECF list of clubs not available because grading code merged')
        else:
            merged_into = 'Inactive'
            clubs = ''
        return super(ECFrefDBrowECFPlayer, self).grid_row(
            textitems=(
                merged_into,
                self.value.ECFcode,
                self.value.ECFname,
                clubs),
            **kargs)

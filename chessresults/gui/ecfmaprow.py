# ecfmaprow.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Create widgets that display various sets of player details.
"""
#class names need to be tidied up

import tkinter

from solentware_grid.gui.datarow import (
    GRID_COLUMNCONFIGURE,
    GRID_CONFIGURE,
    WIDGET_CONFIGURE,
    WIDGET,
    ROW,
    )

from .datarow import DataRow
from ..core import ecfmaprecord
from ..core import resultsrecord
from ..core import ecfrecord


class ECFmapDBrowNewPlayer(ecfmaprecord.ECFmapDBrecordClub, DataRow):

    """Display a Player record without club affiliation.
    """
    header_specification = [
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='ECF club detail', anchor=tkinter.CENTER),
         GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='enpeccode'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Name', anchor=tkinter.CENTER),
         GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='enpname'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Event details', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='enpevent'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=3, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='enpsection'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Association', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=4, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='enpaff'),
         ROW: 0,
         },
        ]

    def __init__(self, database=None):
        """Extend, link player club record without affiliation to database."""
        super(ECFmapDBrowNewPlayer, self).__init__()
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
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.W),
             GRID_CONFIGURE: dict(column=4, sticky=tkinter.EW),
             ROW: 0,
             },
            ]
        
    def grid_row(self, **kargs):
        """Return super(ECFmapDBrowNewPlayer,).grid_row(textitems=(.), **kargs).

        Create textitems argument for ECFmapDBrowNewPlayer instance.

        """
        v = self.value
        cc = cn = ''
        if v.clubecfcode is not None:
            cc = v.clubecfcode
        if v.clubecfname is not None:
            cn = v.clubecfname
        ecfclubdetails = ['\t'.join((cc, cn))]
        ecfclubdetails.extend(
            resultsrecord.get_alias_details(
                self.database,
                self.value.playerkey))
        return super(ECFmapDBrowNewPlayer, self).grid_row(
            textitems=tuple(ecfclubdetails),
            **kargs)


class ECFmapDBrowPlayer(resultsrecord.ResultsDBrecordPlayer, DataRow):

    """Display a Player record with club affiliation.
    """
    header_specification = [
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Grading code', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='epgcode'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='ECF club affiliation', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='epccode'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Name', anchor=tkinter.CENTER),
         GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='epname'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Event details', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=3, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='epevent'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=4, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='epsection'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Association', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=5, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='epaff'),
         ROW: 0,
         },
        ]

    def __init__(self, database=None):
        """Extend, link player club record with affiliation to database."""
        super(ECFmapDBrowPlayer, self).__init__()
        self.set_database(database)
        self.row_specification = [
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.W),
             GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
             ROW: 0,
             },
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.W),
             GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
             ROW: 0,
             },
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.CENTER),
             GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
             ROW: 0,
             },
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.W),
             GRID_CONFIGURE: dict(column=3, sticky=tkinter.EW),
             ROW: 0,
             },
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.W),
             GRID_CONFIGURE: dict(column=4, sticky=tkinter.EW),
             ROW: 0,
             },
            {WIDGET: tkinter.Label,
             WIDGET_CONFIGURE: dict(anchor=tkinter.W),
             GRID_CONFIGURE: dict(column=5, sticky=tkinter.EW),
             ROW: 0,
             },
            ]
        
    def grid_row(self, **kargs):
        """Return super(ECFmapDBrowPlayer,).grid_row(textitems=(...), **kargs).

        Create textitems argument for ECFmapDBrowPlayer instance.

        """
        return super(ECFmapDBrowPlayer, self).grid_row(
            textitems=(
                ecfmaprecord.get_grading_code_for_person(
                    self.database,
                    resultsrecord.get_person_from_alias(
                        self.database, self)),
                ecfmaprecord.get_club_details_for_player(self.database, self),
                self.value.name,
                resultsrecord.get_event_details(
                    self.database, self.value.event),
                resultsrecord.get_section_details(
                    self.database, self.value.section, self.value.pin),
                resultsrecord.get_affiliation_details(
                    self.database, self.value.affiliation)
                ),
            **kargs)


class ECFmapDBrowNewPerson(ecfmaprecord.ECFmapDBrecordPlayer, DataRow):

    """Display a Player record without ECF grading code.
    """
    header_specification = [
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='New ECF detail', anchor=tkinter.CENTER),
         GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='enpeccode'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(
             text='Name', anchor=tkinter.CENTER),
         GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='enpename'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(
             text='Event details', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='enpeevent'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=3, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='enpesection'),
         ROW: 0,
         },
        ]

    def __init__(self, database=None):
        """Extend, link player record without grading code to database."""
        super(ECFmapDBrowNewPerson, self).__init__()
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
        """Return super(ECFmapDBrowNewPerson,).grid_row(textitems=(.), **kargs).

        Create textitems argument for ECFmapDBrowNewPerson instance.

        """
        if self.value.playercode:
            code = self.value.playerecfname
        elif self.value.playerecfcode:
            code = self.value.playerecfcode
        elif self.value.playerecfname:
            code = self.value.playerecfname
        else:
            code = ''
        name, event, section, affiliation = resultsrecord.get_alias_details(
            self.database, self.value.playerkey)
        return super(ECFmapDBrowNewPerson, self).grid_row(
            textitems=(code, name, event, section),
            **kargs)


class ECFmapDBrowPerson(resultsrecord.ResultsDBrecordPlayer, DataRow):

    """Display a Player record with ECF grading code.
    """
    header_specification = [
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Grading code', anchor=tkinter.CENTER),
         GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='epeccode'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='Name', anchor=tkinter.CENTER),
         GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='epename'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(
             text='Event details', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='epeevent'),
         ROW: 0,
         },
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text='', anchor=tkinter.W),
         GRID_CONFIGURE: dict(column=3, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1, uniform='epesection'),
         ROW: 0,
         },
        ]

    def __init__(self, database=None):
        """Extend, link player record without grading code to database."""
        super(ECFmapDBrowPerson, self).__init__()
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
        """Return super(ECFmapDBrowPerson,).grid_row(textitems=(...), **kargs).

        Create textitems argument for ECFmapDBrowPerson instance.

        """
        return super(ECFmapDBrowPerson, self).grid_row(
            textitems=(
                ecfmaprecord.get_grading_code_for_person(
                    self.database,
                    resultsrecord.get_person_from_alias(
                        self.database, self)),
                self.value.name,
                resultsrecord.get_event_details(
                    self.database, self.value.event),
                resultsrecord.get_section_details(
                    self.database,
                    self.value.section,
                    self.value.pin)),
            **kargs)

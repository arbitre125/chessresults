# resultsrow.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Create widgets that display details of events and players.
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
from ..core import filespec


class ResultsDBrowEvent(resultsrecord.ResultsDBrecordEvent, DataRow):

    """Display an Event record."""

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Start date", anchor=tkinter.CENTER),
            GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=0, uniform="edate"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="End date", anchor=tkinter.CENTER),
            GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=0, uniform="edate"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Name", anchor=tkinter.CENTER),
            GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="ename"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Sections", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=3, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="esections"),
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link event record without affiliation to database."""
        super(ResultsDBrowEvent, self).__init__()
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
                WIDGET_CONFIGURE: dict(anchor=tkinter.CENTER),
                GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
                ROW: 0,
            },
            {
                WIDGET: tkinter.Label,
                WIDGET_CONFIGURE: dict(anchor=tkinter.W),
                GRID_CONFIGURE: dict(column=3, sticky=tkinter.EW),
                ROW: 0,
            },
        ]

    def grid_row(self, **kargs):
        """Return super(ResultsDBrowEvent,).grid_row(textitems=(...), **kargs).

        Create textitems argument for ResultsDBrowEvent instance.

        """
        st = []
        for s in self.value.sections:
            st.append(
                resultsrecord.get_name_from_record_value(
                    self.database.get_primary_record(filespec.NAME_FILE_DEF, s)
                )
            )

        return super(ResultsDBrowEvent, self).grid_row(
            textitems=(
                "".join((self.value.startdate, "\t")),
                "".join((self.value.enddate, "\t")),
                self.value.name,
                "\t".join([s.value.name.strip() for s in st]),
            ),
            **kargs
        )


class ResultsDBrowIdentity(resultsrecord.ResultsDBrecordPlayer, DataRow):

    """Display an identified player record."""

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Name", anchor=tkinter.CENTER),
            GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="iname"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Event details", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="ievent"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="isection"),
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link identified player record to database."""
        super(ResultsDBrowIdentity, self).__init__()
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
        ]

    def grid_row(self, **kargs):
        """Return super(ResultsDBrowIdentity,).grid_row(textitems=(.), **kargs).

        Create textitems argument for ResultsDBrowIdentity instance.

        """
        return super(ResultsDBrowIdentity, self).grid_row(
            textitems=(
                self.value.name,
                resultsrecord.get_event_details(
                    self.database, self.value.event
                ),
                resultsrecord.get_section_details(
                    self.database, self.value.section, self.value.pin
                ),
            ),
            **kargs
        )


class ResultsDBrowNewPlayer(resultsrecord.ResultsDBrecordPlayer, DataRow):

    """Display a new player record."""

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
            WIDGET_CONFIGURE: dict(text="Reported Codes", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=4, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="npcodes"),
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link new player record to database."""
        super(ResultsDBrowNewPlayer, self).__init__()
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
        """Return super(ResultsDBrowNewPlayer).grid_row(textitems=(.), **kargs).

        Create textitems argument for ResultsDBrowNewPlayer instance.

        """
        if self.value.reported_codes:
            reportedcodes = "   ".join(self.value.reported_codes)
        else:
            reportedcodes = ""
        return super(ResultsDBrowNewPlayer, self).grid_row(
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
                reportedcodes,
            ),
            **kargs
        )


class ResultsDBrowAlias(resultsrecord.ResultsDBrecordPlayer, DataRow):

    """Display an alias record."""

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
    ]

    def __init__(self, database=None):
        """Extend, link new player record to database."""
        super(ResultsDBrowAlias, self).__init__()
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
        ]

    def grid_row(self, **kargs):
        """Return super(ResultsDBrowAlias).grid_row(textitems=(.), **kargs).

        Create textitems argument for ResultsDBrowAlias instance.

        """
        return super(ResultsDBrowAlias, self).grid_row(
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
            ),
            **kargs
        )


class ResultsDBrowPlayer(resultsrecord.ResultsDBrecordPlayer, DataRow):

    """Display a player record."""

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Name", anchor=tkinter.CENTER),
            GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="pname"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Event details", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="pevent"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="psection"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Association", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=3, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="paff"),
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link player record to database."""
        super(ResultsDBrowPlayer, self).__init__()
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
        ]

    def grid_row(self, **kargs):
        """Return super(ResultsDBrowPlayer,).grid_row(textitems=(...), **kargs).

        Create textitems argument for ResultsDBrowPlayer instance.

        """
        items = (
            (
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
        )
        return super(ResultsDBrowPlayer, self).grid_row(
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
            ),
            **kargs
        )

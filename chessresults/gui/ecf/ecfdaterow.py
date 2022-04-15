# ecfdaterow.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Create widgets that display dates of data from ECF.
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
from ..core.ecfrecord import ECFrefDBrecordECFdate


class ECFrefDBrowECFdate(ECFrefDBrecordECFdate, DataRow):

    """Display an ECF date record."""

    header_specification = [
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Date", anchor=tkinter.CENTER),
            GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="etdate"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Data Type", anchor=tkinter.CENTER),
            GRID_CONFIGURE: dict(column=1, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="ettype"),
            ROW: 0,
        },
        {
            WIDGET: tkinter.Label,
            WIDGET_CONFIGURE: dict(text="Action", anchor=tkinter.W),
            GRID_CONFIGURE: dict(column=2, sticky=tkinter.EW),
            GRID_COLUMNCONFIGURE: dict(weight=1, uniform="etaction"),
            ROW: 0,
        },
    ]

    def __init__(self, database=None):
        """Extend, link ECF master file date record to database."""
        super(ECFrefDBrowECFdate, self).__init__()
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
        ]

    def grid_row(self, **kargs):
        """Return super(ECFrefDBrowECFdate,).grid_row(textitems=(...), **kargs).

        Create textitems argument for ECFrefDBrowECFdate instance.

        """
        return super(ECFrefDBrowECFdate, self).grid_row(
            textitems=(
                self.key.ECFdate,
                self.value.ECFobjtype,
                self.value.ECFtxntype,
            ),
            **kargs
        )

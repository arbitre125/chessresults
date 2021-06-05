# dbasedatarow.py
# Copyright 2007 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Define a row from a dBaseIII file.

"""

import tkinter

from solentware_base.core.record import KeydBaseIII, Value, RecorddBaseIII

from solentware_grid.gui.datarow import (
    DataHeader,
    GRID_COLUMNCONFIGURE,
    GRID_CONFIGURE,
    WIDGET_CONFIGURE,
    WIDGET,
    ROW,
    )

from ..datarow import DataRow


class dBaseDataHeader(DataHeader):
    
    """Provide methods to create a new header and configure its widgets.

    """

    @staticmethod
    def make_header_specification(fieldnames=None):
        """Return dbase file header specification.
        """
        if fieldnames is None:
            return dBaseDataRow.header_specification
        else:
            hs = []
            for col, fn in enumerate(fieldnames):
                hs.append(dBaseDataRow.header_specification[0].copy())
                hs[-1][GRID_CONFIGURE] = dict(
                    column=col, sticky=tkinter.EW)
                hs[-1][WIDGET_CONFIGURE] = dict(text=fn)
            return hs


class dBaseDataRow(RecorddBaseIII, DataRow):
    
    """Provide methods to create, for display, a row from a dBaseIII file.
    
    """
    # The header is derived from file so define a null header here
    header_specification = (
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(text=''),
         GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
         GRID_COLUMNCONFIGURE: dict(weight=1),
         ROW: 0,
         },
        )
    # The row is derived from file so define a null row here
    row_specification = (
        {WIDGET: tkinter.Label,
         WIDGET_CONFIGURE: dict(),
         GRID_CONFIGURE: dict(column=0, sticky=tkinter.EW),
         ROW: 0,
         },
        )

    def __init__(self, database=None):
        """Create a dBaseIII row definition attatched to database."""
        super().__init__(keyclass=KeydBaseIII,
                         valueclass=Value)
        self.set_database(database)
        self.row_specification = []
        
    def grid_row(self, **kargs):
        """Return super(dBaseDataRow, self).grid_row(textitems=(...), **kargs).

        Create row specification from dBase file fieldnames.
        Create textitems argument for dBaseDataRow instance.

        """
        fn = self.database.dBasefiles[self.dbname]._dbaseobject.fieldnames
        self.row_specification = self.make_row_specification(fn)
        v = self.value.__dict__
        return super(dBaseDataRow, self).grid_row(
            textitems=tuple([v.get(f, '') for f in fn]),
            **kargs)

    @staticmethod
    def make_row_specification(fieldnames=None):
        """Return dbase file row specification.
        """
        if fieldnames is None:
            return dBaseDataRow.row_specification
        else:
            hs = []
            for col, fn in enumerate(fieldnames):
                hs.append(dBaseDataRow.row_specification[0].copy())
                hs[-1][GRID_CONFIGURE] = dict(
                    column=col, sticky=tkinter.EW)
            return hs


# newidentitydss.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Provide bsddb style access to a list of DPT record sets and lists.

Each record set in the list is displayed in record number order but the
records will not appear in an obvious sort order like alphabetical.  There
will be an application specific reason for the list of record sets to be in
the given order.

Typical use is:
Find the records that match each of the forenames initials and surname in a
given name.  Build sets that match as many as possible of the name elements
and display the reords with those that match most at start.

"""

from solentware_grid.core.dataclient import DataSource

from ..core import filespec


class NewIdentityDSS(DataSource):
    
    """Define an interface between a database and user interface.
    
    The database is an instance of a subclass of
    solentware_base/sqlite3api.Sqlite3api.
    
    """

    def __init__(
        self,
        dbhome,
        dbset=None,
        dbname=None,
        newrow=None):
        """Define an interface between sqlite3 database and GUI controls.
        
        See superclass for description of arguments.

        """
        super(NewIdentityDSS, self).__init__(
            dbhome,
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYER_FIELD_DEF,
            newrow=newrow)

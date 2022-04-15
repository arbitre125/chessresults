# ecfclubdb.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Classes to open ECF club files and extract records.
"""

import io
from os.path import split

from solentware_base.core.record import KeydBaseIII, Value, RecorddBaseIII

from ...minorbases.dbaseapi import (
    dBaseapi,
    FOLDER,
    FIELDS,
    FILE,
    C,
    N,
    L,
    D,
    F,
    LENGTH,
    TYPE,
    START,
)

CLUBS = "clubs"

# The RECTYPE values on an ECF club update file and interpretation
_addclub = "A"  # add a new club
_updateclub = "U"  # update details of existing club
_deleteclub = "D"  # delete a club


class ECFclubsDB(dBaseapi):

    """Access a club master file published by ECF."""

    def __init__(self, DBpath):

        if isinstance(DBpath, io.BytesIO):
            d, f = False, DBpath
        else:
            d, f = split(DBpath)

        dbnames = {
            CLUBS: {
                FILE: f,
                FIELDS: {
                    "CODE": {START: 1, LENGTH: 4, TYPE: C},
                    "CLUB": {LENGTH: 40, TYPE: C},
                    "COUNTY": {START: 45, LENGTH: 4, TYPE: C},
                },
            },
        }

        dBaseapi.__init__(self, dbnames, d)


class ECFclubsUpdateDB(dBaseapi):

    """Access a club update file published by ECF."""

    def __init__(self, DBpath):

        if isinstance(DBpath, io.BytesIO):
            d, f = False, DBpath
        else:
            d, f = split(DBpath)

        dbnames = {
            CLUBS: {
                FILE: f,
                FIELDS: {
                    "RECTYPE": {START: 1, LENGTH: 1, TYPE: C},
                    "CODE": {START: 2, LENGTH: 4, TYPE: C},
                    "CLUB": {LENGTH: 40, TYPE: C},
                    "COUNTY": {START: 46, LENGTH: 4, TYPE: C},
                },
            },
        }

        dBaseapi.__init__(self, dbnames, d)


class ECFclubsDBkey(KeydBaseIII):

    """Club key."""

    pass


class ECFclubsDBvalue(Value):

    """Club data."""

    # def load(self, value):
    #    """Convert bytes values from dbaseIII record to string"""
    #    super(ECFclubsDBvalue, self).load(value)
    #    for a in self.__dict__:
    #        self.__dict__[a] = self.__dict__[a]


class ECFclubsDBrecord(RecorddBaseIII):

    """Club record."""

    def __init__(self, keyclass=ECFclubsDBkey, valueclass=ECFclubsDBvalue):

        super(ECFclubsDBrecord, self).__init__(keyclass, valueclass)

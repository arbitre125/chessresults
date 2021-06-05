# ecfplayerdb.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Classes to open ECF player files and extract records.
"""

import io
from os.path import split

from solentware_base.core.record import KeydBaseIII, Value, RecorddBaseIII

from ..minorbases.dbaseapi import (
    dBaseapi,
    FOLDER, FIELDS, FILE,
    C, N, L, D, F, LENGTH, TYPE, START,
    )

PLAYERS = 'players'

# The RECTYPE values on an ECF player update file and interpretation
_addplayer = 'A'      # add a new player
_updateplayer = 'U'   # update details of existing player
_deleteplayer = 'D'   # delete a player


class ECFplayersDB(dBaseapi):

    """Access a player master file published by ECF.
    """

    def __init__(self, DBpath):

        if isinstance(DBpath, io.BytesIO):
            d, f = False, DBpath
        else:
            d, f = split(DBpath)

        dbnames = {
            PLAYERS: {
                FILE: f,
                FIELDS: {
                    'REF': {START:1, LENGTH:7, TYPE:C},
                    'NAME': {START:8, LENGTH:60, TYPE:C},
                    'CLUB1': {LENGTH:4, TYPE:C},
                    'CLUB2': {LENGTH:4, TYPE:C},
                    'CLUB3': {LENGTH:4, TYPE:C},
                    'CLUB4': {LENGTH:4, TYPE:C},
                    'CLUB5': {LENGTH:4, TYPE:C},
                    'CLUB6': {LENGTH:4, TYPE:C},
                    'CAT': {LENGTH:1, TYPE:C},
                    'RCAT': {LENGTH:1, TYPE:C},
                    },
                },
            }

        dBaseapi.__init__(self, dbnames, d)


class ECFplayersUpdateDB(dBaseapi):

    """Access a player update file published by ECF.
    """

    def __init__(self, DBpath):

        if isinstance(DBpath, io.BytesIO):
            d, f = False, DBpath
        else:
            d, f = split(DBpath)

        dbnames = {
            PLAYERS: {
                FILE: f,
                FIELDS: {
                    'RECTYPE': {START:1, LENGTH:1, TYPE:C},
                    'REF': {START:2, LENGTH:7, TYPE:C},
                    'NAME': {START:9, LENGTH:60, TYPE:C},
                    'CLUB1': {LENGTH:4, TYPE:C},
                    'CLUB2': {LENGTH:4, TYPE:C},
                    'CLUB3': {LENGTH:4, TYPE:C},
                    'CLUB4': {LENGTH:4, TYPE:C},
                    'CLUB5': {LENGTH:4, TYPE:C},
                    'CLUB6': {LENGTH:4, TYPE:C},
                    'CAT': {LENGTH:1, TYPE:C},
                    'RCAT': {LENGTH:1, TYPE:C},
                    },
                },
            }

        dBaseapi.__init__(self, dbnames, d)


class ECFplayersDBkey(KeydBaseIII):

    """Player key.
    """

    pass


class ECFplayersDBvalue(Value):

    """Player data.
    """

    #def load(self, value):
    #    """Convert bytes values from dbaseIII record to string"""
    #    super(ECFplayersDBvalue, self).load(value)
    #    for a in self.__dict__:
    #        self.__dict__[a] = self.__dict__[a]


class ECFplayersDBrecord(RecorddBaseIII):

    """Player record.
    """

    def __init__(self,
                 keyclass=ECFplayersDBkey,
                 valueclass=ECFplayersDBvalue):

        super(ECFplayersDBrecord, self).__init__(
            keyclass,
            valueclass)

# ecfgcodemaprecord.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Record definition classes for linking players to online ECF grading codes.
"""

from solentware_base.core.record import KeyData
from solentware_base.core.record import ValueList, Record

from . import filespec


class ECFmapOGDkeyPlayer(KeyData):

    """Primary key of player."""

    pass


class ECFmapOGDvaluePlayer(ValueList):

    """ECF name and grading code for player in event."""

    attributes = dict(
        playerkey=None,
        playercode=None,
    )
    _attribute_order = (
        "playercode",  # ecf grading code from ecf online grading database
        "playerkey",  # internal key for player on current database
    )

    def empty(self):
        """(Re)Initialize value attribute."""
        self.playerkey = ""
        # self.playername = ''
        self.playercode = None
        # self.ecfname = ''

    def pack(self):
        """Extend, return player to ECF grading code record and index data."""
        v = super(ECFmapOGDvaluePlayer, self).pack()
        index = v[1]
        index[filespec.OGDPERSONID_FIELD_DEF] = [self.playerkey]
        index[filespec.OGDPERSONCODE_FIELD_DEF] = [self.playercode]
        return v


class ECFmapOGDrecordPlayer(Record):
    """Player in event linked to ECF grading code.

    For each ResultsDBrecordPlayer record where merge is False
    there are 0 or 1 ECFmapOGDrecordPlayer records.
    The merge and alias attributes of other ResultsDBrecordPlayer
    instances may imply a link to this record.

    """

    def __init__(
        self, keyclass=ECFmapOGDkeyPlayer, valueclass=ECFmapOGDvaluePlayer
    ):

        super(ECFmapOGDrecordPlayer, self).__init__(keyclass, valueclass)


def get_grading_code_for_person(database, person):
    """Return Online Grading Database grading code for person or ''.

    Caller must ensure person is a resultsrecord.ResultsDBrecordPlayer with
    value.merge equal False as these are the ones with an ECFmapOGDrecordPlayer
    record for key.

    """
    if person is None:
        return ""
    identity = database.encode_record_number(person.key.recno)
    cursor = database.database_cursor(
        filespec.MAPECFOGDPLAYER_FILE_DEF, filespec.OGDPERSONID_FIELD_DEF
    )
    try:
        r = cursor.nearest(identity)
    finally:
        cursor.close()
    if r:
        if database.encode_record_selector(r[0]) == identity:
            p = get_person(database, r[-1])
            if p:
                if p.value.playercode:
                    return p.value.playercode
    return ""


def get_person(database, key):
    """Return ECFmapOGDrecordPlayer() for code or None."""
    a = database.get_primary_record(filespec.MAPECFOGDPLAYER_FILE_DEF, key)
    if a:
        ar = ECFmapOGDrecordPlayer()
        ar.load_record(a)
        return ar


def get_person_for_grading_code(database, code):
    """Return ECFmapOGDrecordPlayer() for code or None"""
    encoded_record_number = database.encode_record_number(code)
    cursor = database.database_cursor(
        filespec.MAPECFOGDPLAYER_FILE_DEF, filespec.OGDPERSONCODE_FIELD_DEF
    )
    try:
        r = cursor.nearest(encoded_record_number)
    finally:
        cursor.close()
    if r is not None:
        if database.encode_record_selector(r[0]) != encoded_record_number:
            return None
        p = database.get_primary_record(
            filespec.MAPECFOGDPLAYER_FILE_DEF, r[-1]
        )
        if p is not None:
            pr = ECFmapOGDrecordPlayer()
            pr.load_record(p)
            return pr


def get_person_for_player(database, code):
    """Return ECFmapOGDrecordPlayer() for code or None."""
    encoded_record_number = database.encode_record_number(code)
    cursor = database.database_cursor(
        filespec.MAPECFOGDPLAYER_FILE_DEF, filespec.OGDPERSONID_FIELD_DEF
    )
    try:
        r = cursor.nearest(encoded_record_number)
    finally:
        cursor.close()
    if r is not None:
        if database.encode_record_selector(r[0]) != encoded_record_number:
            return None
        p = database.get_primary_record(
            filespec.MAPECFOGDPLAYER_FILE_DEF, r[-1]
        )
        if p is not None:
            pr = ECFmapOGDrecordPlayer()
            pr.load_record(p)
            return pr

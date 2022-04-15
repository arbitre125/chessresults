# ecfmaprecord.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Record definition classes for linking players to ECF grading and club codes.
"""

from ast import literal_eval

from solentware_base.core.record import KeyData
from solentware_base.core.record import ValueList, Record, Value

from .. import filespec
from . import ecfrecord
from ..resultsrecord import get_unpacked_player_identity


class ECFmapDBkeyClub(KeyData):

    """Primary key of club data for player in event."""

    pass


class ECFmapDBvalueClub(ValueList):

    """ECF club for player in event."""

    attributes = dict(
        playerkey=None,
        playername=None,
        clubcode=None,
        clubecfname=None,
        clubecfcode=None,
    )
    _attribute_order = (
        "clubcode",  # ecf club code from ecf club file
        "playerkey",  # internal key for player on current database
        "playername",  # name reported on results input
        "clubecfname",  # ecf club name entered for new club
        "clubecfcode",  # ecf club code entered for new club
    )

    def empty(self):
        """(Re)Initialize value attribute."""
        self.playerkey = ""
        self.playername = ""
        self.clubcode = None
        self.clubecfname = None
        self.clubecfcode = None

    def pack(self):
        """Extend, return player to ECF club record and index data."""
        v = super(ECFmapDBvalueClub, self).pack()
        index = v[1]
        index[filespec.PLAYERALIASID_FIELD_DEF] = [self.playerkey]
        if self.clubcode is None:
            index[filespec.PLAYERALIASMAP_FIELD_DEF] = [self.playername]
        elif self.clubcode is False:
            pass
        else:
            index[filespec.CLUBCODE_FIELD_DEF] = [self.clubcode]
        return v

    def get_unpacked_playername(self):
        """Return playername unpacked into ResultsDBvaluePlayer components."""
        return get_unpacked_player_identity(self.playername)


class ECFmapDBrecordClub(Record):

    """Player in event associated with ECF club.

    For each ResultsDBrecordPlayer record there are 0 or 1
    ECFmapDBrecordClub records.

    """

    def __init__(self, keyclass=ECFmapDBkeyClub, valueclass=ECFmapDBvalueClub):

        super(ECFmapDBrecordClub, self).__init__(keyclass, valueclass)


class ECFmapDBkeyEvent(KeyData):

    """Primary key of event."""

    pass


class ECFmapDBvalueEvent(ValueList):

    """Event data."""

    attributes = dict(
        eventkey=None,
        eventname=None,
        eventcode=None,
    )
    _attribute_order = (
        "eventcode",  # event code reported on results input
        "eventkey",  # internal key for event on current database
        "eventname",  # name reported on results input
    )

    def empty(self):
        """(Re)Initialize value attribute"""
        self.eventkey = ""
        self.eventname = None
        self.eventcode = ""


class ECFmapDBrecordEvent(Record):

    """Event record"""

    def __init__(
        self, keyclass=ECFmapDBkeyEvent, valueclass=ECFmapDBvalueEvent
    ):

        super(ECFmapDBrecordEvent, self).__init__(keyclass, valueclass)


class ECFmapDBkeyPlayer(KeyData):

    """Primary key of player."""

    pass


class ECFmapDBvaluePlayer(ValueList):

    """ECF name and grading code for player in event."""

    attributes = dict(
        playerkey=None,
        playername=None,
        playercode=None,
        playerecfname=None,
        playerecfcode=None,
    )
    _attribute_order = (
        "playercode",  # ecf grading code from ecf master file
        "playerkey",  # internal key for player on current database
        "playername",  # name reported on results input
        "playerecfname",  # ecf version of name entered for new player
        "playerecfcode",  # ecf grading code for new player from feedback
    )

    def empty(self):
        """(Re)Initialize value attribute."""
        self.playerkey = ""
        self.playername = ""
        self.playercode = None
        self.playerecfname = None
        self.playerecfcode = None

    def pack(self):
        """Extend, return player to ECF grading code record and index data."""
        v = super(ECFmapDBvaluePlayer, self).pack()
        index = v[1]
        index[filespec.PERSONID_FIELD_DEF] = [self.playerkey]
        if self.playercode is None:
            index[filespec.PERSONMAP_FIELD_DEF] = [self.playername]
        else:
            index[filespec.PERSONCODE_FIELD_DEF] = [self.playercode]
            if self.playerecfcode is not None:
                index[filespec.PERSONMAP_FIELD_DEF] = [self.playername]
        return v

    def get_unpacked_playername(self):
        """Return playername unpacked into ResultsDBvaluePlayer components."""
        return get_unpacked_player_identity(self.playername)

    # This may be a hack: I did not want to put this in Value definition
    # because everything else is happy without it at Python3.  But there should
    # not be much wrong with putting it there as Value was hashable at Python2.
    __hash__ = object.__hash__


class ECFmapDBrecordPlayer(Record):
    """Player in event linked to ECF name and grading code.

    For each ResultsDBrecordPlayer record where merge is False
    there are 0 or 1 ECFmapDBrecordPlayer records.
    The merge and alias attributes of other ResultsDBrecordPlayer
    instances may imply a link to this record.

    """

    def __init__(
        self, keyclass=ECFmapDBkeyPlayer, valueclass=ECFmapDBvaluePlayer
    ):

        super(ECFmapDBrecordPlayer, self).__init__(keyclass, valueclass)


def get_club_details_for_player(database, player):
    """Return ECF Club details for player or ''.

    Caller must ensure player is a resultsrecord.ResultsDBrecordPlayer with
    value.merge equal False or value.alias equal False as these are the ones
    with an ECFmapDBrecordClub record for key.

    """
    if player is None:
        return ""
    identity = database.encode_record_number(player.key.recno)
    cursor = database.database_cursor(
        filespec.MAPECFCLUB_FILE_DEF, filespec.PLAYERALIASID_FIELD_DEF
    )
    try:
        r = cursor.nearest(identity)
    finally:
        cursor.close()
    if r:
        if database.encode_record_selector(r[0]) == identity:
            p = get_player(database, r[-1])
            if p:
                if p.value.clubcode:
                    return ecfrecord.get_ecf_club_details(
                        database, p.value.clubcode
                    )
    return ""


def get_grading_code_for_person(database, person):
    """Return ECF Grading Code for person or ''.

    Caller must ensure person is a resultsrecord.ResultsDBrecordPlayer with
    value.merge equal False as these are the ones with an ECFmapDBrecordPlayer
    record for key.

    """
    if person is None:
        return ""
    identity = database.encode_record_number(person.key.recno)
    cursor = database.database_cursor(
        filespec.MAPECFPLAYER_FILE_DEF, filespec.PERSONID_FIELD_DEF
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
                if p.value.playerecfcode:
                    return p.value.playerecfcode
    return ""


def get_merge_grading_code_for_person(database, person):
    """Return ECF Grading Code with which person's code is merged or ''.

    Find grading code using get_grading_code_for_person then lookup to get
    merged code if there is one.

    """
    grading_code = get_grading_code_for_person(database, person)
    if grading_code == "":
        return grading_code
    return ecfrecord.get_merge_for_grading_code(database, grading_code)


def get_new_person_for_identity(database, identity):
    """Return ECFmapDBrecordPlayer() for key or None."""
    pr = ECFmapDBrecordPlayer()
    identity = literal_eval(
        database.encode_record_number(identity.identity_packed())
    )
    cursor = database.database_cursor(
        filespec.MAPECFPLAYER_FILE_DEF, filespec.PERSONMAP_FIELD_DEF
    )
    try:
        r = cursor.nearest(identity)
        if r is not None:
            if database.encode_record_selector(r[0]) == identity:
                p = database.get_primary_record(
                    filespec.MAPECFPLAYER_FILE_DEF, r[-1]
                )
                if p is not None:
                    pr.load_record(p)
                    return pr
    finally:
        cursor.close()


def get_new_person_for_grading_code(database, code):
    """Return ECFmapDBrecordPlayer() for code or None."""
    pr = ECFmapDBrecordPlayer()
    cursor = database.database_cursor(
        filespec.MAPECFPLAYER_FILE_DEF, filespec.PERSONMAP_FIELD_DEF
    )
    try:
        r = cursor.first()
        while r is not None:
            p = database.get_primary_record(
                filespec.MAPECFPLAYER_FILE_DEF, r[-1]
            )
            if p is not None:
                pr.load_record(p)
                if code == pr.value.playerecfcode:
                    return pr
            r = cursor.next()
    finally:
        cursor.close()


def get_person(database, key):
    """Return ECFmapDBrecordPlayer() for key or None."""
    a = database.get_primary_record(filespec.MAPECFPLAYER_FILE_DEF, key)
    if a is not None:
        ar = ECFmapDBrecordPlayer()
        ar.load_record(a)
        return ar


def get_person_for_alias(database, aliaskey):
    """Return ECFmapDBrecordPlayer() for aliaskey or None.

    aliaskey should be key of resultsrecord.ResultsDBrecordPlayer with
    value.merge equal False as these are the ones which can be linked to an
    ECFmapDBrecordPlayer record.

    """
    aliaskey = database.encode_record_number(aliaskey)
    cursor = database.database_cursor(
        filespec.MAPECFPLAYER_FILE_DEF, filespec.PERSONID_FIELD_DEF
    )
    try:
        r = cursor.nearest(aliaskey)
    finally:
        cursor.close()
    if r is not None:
        if database.encode_record_selector(r[0]) == aliaskey:
            p = database.get_primary_record(
                filespec.MAPECFPLAYER_FILE_DEF, r[-1]
            )
            if p is not None:
                pr = ECFmapDBrecordPlayer()
                pr.load_record(p)
                return pr


def get_person_for_grading_code(database, code):
    """Return ECFmapDBrecordPlayer() for code or None."""
    code = database.encode_record_selector(code)
    cursor = database.database_cursor(
        filespec.MAPECFPLAYER_FILE_DEF, filespec.PERSONCODE_FIELD_DEF
    )
    try:
        r = cursor.nearest(code)
    finally:
        cursor.close()
    if r is not None:
        if database.encode_record_selector(r[0]) != code:
            return None
        p = database.get_primary_record(filespec.MAPECFPLAYER_FILE_DEF, r[-1])
        if p is not None:
            pr = ECFmapDBrecordPlayer()
            pr.load_record(p)
            return pr


def get_person_for_player(database, code):
    """Return ECFmapDBrecordPlayer() for code or None."""
    code = database.encode_record_number(code)
    cursor = database.database_cursor(
        filespec.MAPECFPLAYER_FILE_DEF, filespec.PERSONID_FIELD_DEF
    )
    try:
        r = cursor.nearest(code)
    finally:
        cursor.close()
    if r is not None:
        if database.encode_record_selector(r[0]) != code:
            return None
        p = database.get_primary_record(filespec.MAPECFPLAYER_FILE_DEF, r[-1])
        if p is not None:
            pr = ECFmapDBrecordPlayer()
            pr.load_record(p)
            return pr


def get_player(database, key):
    """Return ECFmapDBrecordClub() for code or None."""
    a = database.get_primary_record(filespec.MAPECFCLUB_FILE_DEF, key)
    if a is not None:
        ar = ECFmapDBrecordClub()
        ar.load_record(a)
        return ar


def get_player_for_alias(database, aliaskey):
    """Return ECFmapDBrecordClub() for aliaskey or None.

    aliaskey should be key of resultsrecord.ResultsDBrecordPlayer with
    value.merge or value.alias equal False as these are the ones which can be
    linked to an ECFmapDBrecordClub record.

    """
    ak = database.encode_record_number(aliaskey)
    cursor = database.database_cursor(
        filespec.MAPECFCLUB_FILE_DEF, filespec.PLAYERALIASID_FIELD_DEF
    )
    try:
        r = cursor.nearest(ak)
    finally:
        cursor.close()
    if r is not None:
        if database.encode_record_selector(r[0]) == ak:
            p = database.get_primary_record(
                filespec.MAPECFCLUB_FILE_DEF, r[-1]
            )
            if p is not None:
                pr = ECFmapDBrecordClub()
                pr.load_record(p)
                return pr


def get_player_clubs_for_games(database, games):
    """Return {record key : ECFmapDBrecordClub(), ...} for games."""
    players = dict()
    cursor = database.database_cursor(
        filespec.MAPECFCLUB_FILE_DEF, filespec.PLAYERALIASID_FIELD_DEF
    )
    try:
        for g in games:
            for pk in (g.value.homeplayer, g.value.awayplayer):
                if pk not in players:
                    pkc = database.encode_record_number(pk)
                    r = cursor.nearest(pkc)
                    if r is not None:
                        if database.encode_record_selector(r[0]) != pkc:
                            continue
                        p = database.get_primary_record(
                            filespec.MAPECFCLUB_FILE_DEF, r[-1]
                        )
                        if p is not None:
                            players[pk] = ECFmapDBrecordClub()
                            players[pk].load_record(p)
    finally:
        cursor.close()
    return players

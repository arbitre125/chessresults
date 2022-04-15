# ecfogdrecord.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Record definition classes for data from ECF Online Grading Database.

Two download formats exist: the grading list produced up to mid-2020, and
the rating list produced after mid-2020.

ecfrating.org.uk/v2/help/help_api.php on 20 March 2022 states rating list
format downloads are available for all grading and rating lists since 1994.

Grading list format downloads are no longer available but downloaded copies
may still exist.

"""

from solentware_base.core.record import KeyData
from solentware_base.core.record import Value, ValueList, Record

from .. import filespec


class ECFrefOGDkeyPlayer(KeyData):
    """Primary key of player from ECF."""


class ECFrefOGDvaluePlayer(ValueList):
    """Player data from ECF."""

    attributes = dict(
        ECFOGDcode=None,
        ECFOGDname=None,
        ECFOGDclubs=list,
    )
    _attribute_order = tuple(sorted(attributes.keys()))

    def pack(self):
        """Extend, return ECF player record and index data."""
        v = super(ECFrefOGDvaluePlayer, self).pack()
        index = v[1]
        index[filespec.OGDPLAYERCODE_FIELD_DEF] = [self.ECFOGDcode]
        if self.ECFOGDname:
            index[filespec.OGDPLAYERNAME_FIELD_DEF] = [self.ECFOGDname]
            index[filespec.OGDPLAYERCODEPUBLISHED_FIELD_DEF] = [
                self.ECFOGDcode
            ]
        return v


class ECFrefOGDrecordPlayer(Record):
    """Player record from ECF."""

    def __init__(
        self, keyclass=ECFrefOGDkeyPlayer, valueclass=ECFrefOGDvaluePlayer
    ):

        super(ECFrefOGDrecordPlayer, self).__init__(keyclass, valueclass)


def get_ecf_ogd_player(database, key):
    """Return ECFrefOGDrecordPlayer instance for dbrecord[key]."""
    p = database.get_primary_record(filespec.ECFOGDPLAYER_FILE_DEF, key)
    pr = ECFrefOGDrecordPlayer()
    pr.load_record(p)
    return pr


def get_ecf_ogd_player_for_grading_code(database, key):
    """Return ECFrefOGDrecordPlayer instance for key on index or None."""
    r = database.get_primary_record(
        filespec.ECFOGDPLAYER_FILE_DEF,
        database.database_cursor(
            filespec.ECFOGDPLAYER_FILE_DEF, filespec.OGDPLAYERCODE_FIELD_DEF
        ).get_unique_primary_for_index_key(
            database.encode_record_selector(key)
        ),
    )
    if r is not None:
        pr = ECFrefOGDrecordPlayer()
        pr.load_record(r)
        return pr

# mergeplayers.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Merge player functions.
"""

from . import resultsrecord
from . import filespec


def get_new_player_for_alias_key(database, key):
    """Return the Alias record for the new player.

    Allow for value.merge on the record with key srkey being any value.
    Return the record if it has value.merge is False.  If value.merge is
    neither None nor True (assumed to be integer) use it to retreive a
    record; and return this if its value.merge is False.  Otherwise
    return None.

    """
    r = resultsrecord.get_alias(database, key[-1])
    if r is None:
        return
    elif r.value.merge is None:
        return r
    elif r.value.merge is True:
        return r


def get_new_players_for_alias_keys(database, keys):
    """Return the Alias records for the new players."""
    return _get_records(database, keys, get_new_player_for_alias_key)


def get_person_for_alias_key(database, key):
    """Return the Alias record for the identified player.

    Step up the merge chain for a player key until value.merge is None True
    or False.
    Return this record if value.merge is False (identified player).
    Return None if value.merge is None or True (unidentified player).
    Return None if _get_merge_for_alias_key() returns None. 

    """
    r = _get_merge_for_alias_key(database, key[-1])
    while r:
        if r.value.merge is False:
            return r
        elif r.value.merge is True:
            return
        elif r.value.merge is None:
            return
        r = _get_merge_for_alias_key(database, r.value.merge)


def get_persons_for_alias_keys(database, keys):
    """Return the Alias records for the identified players."""
    return _get_records(database, keys, get_person_for_alias_key)


def join_merged_players(database, playerrecord, joins):
    """Link joins records into playerrecord record and return True if ok.

    playerrecord.merge must be None True or False ==> alias is list
    joins[*].merge must be None True or False ==> alias is list.

    These restrictions are because caller is expected to resolve selection
    of playerrecord and joins to person records.

    get_alias_list() is used to allow direct joins for records imported
    from peer databases.

    This method assumes a single level of join but a planned change is to
    allow multi-level merges to support merges within an event as well as
    across events.

    """
    database.start_transaction()
    newplayerrecord = playerrecord.clone()
    for joinrecord in joins:
        newjoinrecord = joinrecord.clone()
        newplayerrecord.value.alias.append(
            joinrecord.key.recno)
        newjoinrecord.value.merge = playerrecord.key.recno
        if newplayerrecord.value.merge is None:
            newjoinrecord.value.alias = False
        elif newplayerrecord.value.merge is True:
            newjoinrecord.value.alias = False
        elif newplayerrecord.value.merge is False:
            newjoinrecord.value.alias = False
        else:
            newjoinrecord.value.alias = []
        for alias in joinrecord.value.alias:
            aliasrecord = resultsrecord.get_alias(database, alias)
            if aliasrecord is None:
                database.backout()
                return ''.join(
                    ('Record for player\n',
                     resultsrecord.get_player_name_text(
                         database,
                         aliasrecord.value.identity()),
                     '\ndoes not exist.'))
            newplayerrecord.value.alias.append(
                aliasrecord.key.recno)
            for ak in aliasrecord.value.get_alias_list():
                r = database.get_primary_record(filespec.PLAYER_FILE_DEF, ak)
                if r is None:
                    database.backout()
                    return ''.join(
                        ('An imported alias for player\n',
                         resultsrecord.get_player_name_text(
                             database,
                             joinrecord.value.identity()),
                         '\ndoes not exist.'))
            newplayerrecord.value.alias.extend(
                aliasrecord.value.get_alias_list())
            newaliasrecord = aliasrecord.clone()
            newaliasrecord.value.merge = playerrecord.key.recno
            if newplayerrecord.value.merge is None:
                newaliasrecord.value.alias = False
            elif newplayerrecord.value.merge is True:
                newaliasrecord.value.alias = False
            elif newplayerrecord.value.merge is False:
                newaliasrecord.value.alias = False
            else:
                newaliasrecord.value.alias = []
            aliasrecord.edit_record(
                database,
                filespec.PLAYER_FILE_DEF,
                filespec.PLAYER_FIELD_DEF,
                newaliasrecord)
        joinrecord.edit_record(
            database,
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYER_FIELD_DEF,
            newjoinrecord)
    if newplayerrecord.value.merge is None:
        newplayerrecord.value.merge = False
    elif newplayerrecord.value.merge is True:
        newplayerrecord.value.merge = False
    playerrecord.edit_record(
        database,
        filespec.PLAYER_FILE_DEF,
        filespec.PLAYER_FIELD_DEF,
        newplayerrecord)
    database.commit()

    return None
    

def merge_new_players(database, playerrecord, merges):
    """Link merges records into playerrecord record and return True if ok.

    playerrecord.merge must be None True or False ==> alias is list
    merges[*].merge must be None True or False ==> alias is list.

    These restrictions are because caller is expected to resolve selection
    of playerrecord to a person record and a new player will have merge
    equal None or True but False is allowed as well.

    Strictly an integer value for merges[*].merge should raise an exception
    but a planned change is to allow aliases to be merged within an event as
    well as across events. So get_alias_list() is used.
        
    """
    database.start_transaction()
    newplayerrecord = playerrecord.clone()
    for aliasrecord in merges:
        newplayerrecord.value.alias.append(
            aliasrecord.key.recno)
        for ak in aliasrecord.value.get_alias_list():
            r = database.get_primary_record(filespec.PLAYER_FILE_DEF, ak)
            if r is None:
                database.backout()
                return ''.join(
                    ('An imported alias for player\n',
                     resultsrecord.get_player_name_text(
                         database,
                         aliasrecord.value.identity()),
                     '\ndoes not exist.'))
        newplayerrecord.value.alias.extend(
            aliasrecord.value.get_alias_list())
        newaliasrecord = aliasrecord.clone()
        newaliasrecord.value.merge = playerrecord.key.recno
        if newplayerrecord.value.merge is None:
            newaliasrecord.value.alias = False
        elif newplayerrecord.value.merge is True:
            newaliasrecord.value.alias = False
        elif newplayerrecord.value.merge is False:
            newaliasrecord.value.alias = False
        else:
            newaliasrecord.value.alias = []
        aliasrecord.edit_record(
            database,
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYER_FIELD_DEF,
            newaliasrecord)
    if newplayerrecord.value.merge is None:
        newplayerrecord.value.merge = False
    elif newplayerrecord.value.merge is True:
        newplayerrecord.value.merge = False
    playerrecord.edit_record(
        database,
        filespec.PLAYER_FILE_DEF,
        filespec.PLAYER_FIELD_DEF,
        newplayerrecord)
    database.commit()

    return None


def _get_merge_for_alias_key(database, key):
    """Return the Alias record of the merged player.

    Allow for value.merge on the record with key srkey being any value.
    Return the record if value.merge is None True or False.
    Otherwise assume value.merge is integer and use it to retreive and
    return a record.
    return None if get_alias() returns None.

    """
    r = resultsrecord.get_alias(database, key)
    if r is None:
        return
    elif r.value.merge is None:
        return r
    elif r.value.merge is True:
        return r
    elif r.value.merge is False:
        return r
    r = resultsrecord.get_alias(database, r.value.merge)
    if r is None:
        return
    return r


def _get_records(database, keys, function):
    """Return records on database for keys using function."""
    records = dict()
    for k in keys:
        r = function(database, k)
        if r is None:
            records.setdefault(None, []).append(k)
        else:
            kp = r.key.pack()
            if kp not in records:
                records[kp] = r
    return records

# ecfdataimport.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Extract player and club data from ECF reference files.

Provide the database engine independant ecfdata import module functions apart
from the two implementing the current rules.

ECF (formerly BCF) provided reference files on CD from the end of the 1998
season as a matter of routine.  These contained the active players from the
most recent three seasons.  From the end of the 2006 season smaller updates
were provided during the season but these were soon replaced by more frequent
issuing of reference files including new, or re-activated, players.  From the
middle of the 2011 season the reference files included all players who had
ever played a graded game (since early 1990s in practice).

"""

from ..basecore import ecfdataimport
from ..core import filespec
from ..core import ecfrecord
from ..core import ecfclubdb
from ..core import ecfplayerdb
from ..core import ecfmaprecord


def copy_ecf_players_post_2020_rules(
    results,
    logwidget=None,
    ecffile=None,
    ecfdate=None,
    parent=None,
    datecontrol=None,
    **kwargs
    ):
    """Import a new ECF player file.

    widget - the manager object for the ecf data import tab

    """
    
    # DPT database engine code to ensure ECFPLAYER_FILE_DEF file is large
    # enough for any extra records.

    if logwidget:
        logwidget.append_text('', timestamp=False)
        logwidget.append_text(''.join(
            ('Ensure ',
             filespec.ECFPLAYER_FILE_DEF,
             ' is large enough for any extra records on Master player file.',
             )))
    players = ecffile.database_cursor(ecfplayerdb.PLAYERS, ecfplayerdb.PLAYERS)
    ecfimp = ecfplayerdb.ECFplayersDBrecord()

    # Get all ECF grading codes mapped to dBaseIII record numbers.
    data = players.first()
    oldrefs = set()
    bothrefs = dict()
    newrefs = dict()
    while data:
        ecfimp.load_instance(
            ecffile, ecfplayerdb.PLAYERS, ecfplayerdb.PLAYERS, data)
        newrefs[ecfimp.value.REF] = ecfimp.key.recno
        data = players.next()
    ecfcursor = results.database_cursor(
        filespec.ECFPLAYER_FILE_DEF, filespec.ECFPLAYER_FIELD_DEF)
    ecfrec = ecfrecord.ECFrefDBrecordECFplayer()

    # Go through existing records for equivalents to master list records
    r = ecfcursor.first()
    while r:
        ecfrec.load_instance(
            results,
            filespec.ECFPLAYER_FILE_DEF,
            filespec.ECFPLAYER_FIELD_DEF,
            r)
        ref = ecfrec.value.ECFcode
        if ref in newrefs:
            bothrefs[ref] = newrefs[ref]
            del newrefs[ref]
        else:
            oldrefs.add(ref)
        r = ecfcursor.next()
    extra_records = max(len(newrefs) - len(oldrefs), 0)

    # Close record sets, cursors, etc, to allow increase_database_size.
    ecfcursor.close()
    players.close()
    del oldrefs, bothrefs, newrefs

    # Increase file size if necessary.
    results.increase_database_size(
        {filespec.ECFPLAYER_FILE_DEF: (extra_records, extra_records)})

    # Import data (identical to other database engine versions).

    return ecfdataimport.copy_ecf_players_post_2020_rules(
        results,
        logwidget=logwidget,
        ecffile=ecffile,
        ecfdate=ecfdate,
        parent=parent,
        datecontrol=datecontrol,
        **kwargs)


def copy_ecf_clubs_post_2020_rules(
    results,
    logwidget=None,
    ecffile=None,
    ecfdate=None,
    parent=None,
    datecontrol=None,
    **kwargs
    ):
    """Import a new ECF club file

    widget - the manager object for the ecf data import tab

    """

    # DPT datebase engine code to ensure ECFPLAYER_FILE_DEF file is large
    # enough for any extra records.

    if logwidget:
        logwidget.append_text('', timestamp=False)
        logwidget.append_text(''.join(
            ('Ensure ',
             filespec.ECFCLUB_FILE_DEF,
             ' is large enough for any extra records on Master club file.',
             )))
    clubs = ecffile.database_cursor(ecfclubdb.CLUBS, ecfclubdb.CLUBS)
    ecfimp = ecfclubdb.ECFclubsDBrecord()

    # Get all ECF club codes mapped to dBaseIII record numbers.
    data = clubs.first()
    oldrefs = set()
    bothrefs = dict()
    newrefs = dict()
    while data:
        ecfimp.load_instance(
            ecffile, ecfclubdb.CLUBS, ecfclubdb.CLUBS, data)
        newrefs[ecfimp.value.CODE] = ecfimp.key.recno
        data = clubs.next()
    ecfcursor = results.database_cursor(
        filespec.ECFCLUB_FILE_DEF, filespec.ECFCLUB_FIELD_DEF)
    ecfrec = ecfrecord.ECFrefDBrecordECFclub()
    
    # Go through existing records for equivalents to master list records.
    r = ecfcursor.first()
    while r:
        ecfrec.load_instance(
            results,
            filespec.ECFCLUB_FILE_DEF,
            filespec.ECFCLUB_FIELD_DEF,
            r)
        ref = ecfrec.value.ECFcode
        if ref in newrefs:
            bothrefs[ref] = newrefs[ref]
            del newrefs[ref]
        else:
            oldrefs.add(ref)
        r = ecfcursor.next()
    extra_records = max(len(newrefs) - len(oldrefs), 0)

    # Close record sets, cursors, etc, to allow increase_database_size.
    ecfcursor.close()
    clubs.close()
    del oldrefs, bothrefs, newrefs

    # Increase file size if necessary.
    results.increase_database_size(
        {filespec.ECFCLUB_FILE_DEF: (extra_records, extra_records)})

    # Import data (identical to other database engine versions).

    return ecfdataimport.copy_ecf_clubs_post_2020_rules(
        results,
        logwidget=logwidget,
        ecffile=ecffile,
        ecfdate=ecfdate,
        parent=parent,
        datecontrol=datecontrol,
        **kwargs)


def copy_ecf_players_post_2011_rules(
    results,
    logwidget=None,
    ecffile=None,
    ecfdate=None,
    parent=None,
    datecontrol=None,
    **kwargs
    ):
    """Import a new ECF player file.

    widget - the manager object for the ecf data import tab

    """
    
    # DPT database engine code to ensure ECFPLAYER_FILE_DEF file is large
    # enough for any extra records.

    if logwidget:
        logwidget.append_text('', timestamp=False)
        logwidget.append_text(''.join(
            ('Ensure ',
             filespec.ECFPLAYER_FILE_DEF,
             ' is large enough for any extra records on Master player file.',
             )))
    players = ecffile.database_cursor(ecfplayerdb.PLAYERS, ecfplayerdb.PLAYERS)
    ecfimp = ecfplayerdb.ECFplayersDBrecord()

    # Get all ECF grading codes mapped to dBaseIII record numbers.
    data = players.first()
    oldrefs = set()
    bothrefs = dict()
    newrefs = dict()
    while data:
        ecfimp.load_instance(
            ecffile, ecfplayerdb.PLAYERS, ecfplayerdb.PLAYERS, data)
        newrefs[ecfimp.value.REF] = ecfimp.key.recno
        data = players.next()
    ecfcursor = results.database_cursor(
        filespec.ECFPLAYER_FILE_DEF, filespec.ECFPLAYER_FIELD_DEF)
    ecfrec = ecfrecord.ECFrefDBrecordECFplayer()

    # Go through existing records for equivalents to master list records
    r = ecfcursor.first()
    while r:
        ecfrec.load_instance(
            results,
            filespec.ECFPLAYER_FILE_DEF,
            filespec.ECFPLAYER_FIELD_DEF,
            r)
        ref = ecfrec.value.ECFcode
        if ref in newrefs:
            bothrefs[ref] = newrefs[ref]
            del newrefs[ref]
        else:
            oldrefs.add(ref)
        r = ecfcursor.next()
    extra_records = max(len(newrefs) - len(oldrefs), 0)

    # Close record sets, cursors, etc, to allow increase_database_size.
    ecfcursor.close()
    players.close()
    del oldrefs, bothrefs, newrefs

    # Increase file size if necessary.
    results.increase_database_size(
        {filespec.ECFPLAYER_FILE_DEF: (extra_records, extra_records)})

    # Import data (identical to other database engine versions).

    return ecfdataimport.copy_ecf_players_post_2011_rules(
        results,
        logwidget=logwidget,
        ecffile=ecffile,
        ecfdate=ecfdate,
        parent=parent,
        datecontrol=datecontrol,
        **kwargs)


def copy_ecf_clubs_post_2011_rules(
    results,
    logwidget=None,
    ecffile=None,
    ecfdate=None,
    parent=None,
    datecontrol=None,
    **kwargs
    ):
    """Import a new ECF club file

    widget - the manager object for the ecf data import tab

    """

    # DPT datebase engine code to ensure ECFPLAYER_FILE_DEF file is large
    # enough for any extra records.

    if logwidget:
        logwidget.append_text('', timestamp=False)
        logwidget.append_text(''.join(
            ('Ensure ',
             filespec.ECFCLUB_FILE_DEF,
             ' is large enough for any extra records on Master club file.',
             )))
    clubs = ecffile.database_cursor(ecfclubdb.CLUBS, ecfclubdb.CLUBS)
    ecfimp = ecfclubdb.ECFclubsDBrecord()

    # Get all ECF club codes mapped to dBaseIII record numbers.
    data = clubs.first()
    oldrefs = set()
    bothrefs = dict()
    newrefs = dict()
    while data:
        ecfimp.load_instance(
            ecffile, ecfclubdb.CLUBS, ecfclubdb.CLUBS, data)
        newrefs[ecfimp.value.CODE] = ecfimp.key.recno
        data = clubs.next()
    ecfcursor = results.database_cursor(
        filespec.ECFCLUB_FILE_DEF, filespec.ECFCLUB_FIELD_DEF)
    ecfrec = ecfrecord.ECFrefDBrecordECFclub()
    
    # Go through existing records for equivalents to master list records.
    r = ecfcursor.first()
    while r:
        ecfrec.load_instance(
            results,
            filespec.ECFCLUB_FILE_DEF,
            filespec.ECFCLUB_FIELD_DEF,
            r)
        ref = ecfrec.value.ECFcode
        if ref in newrefs:
            bothrefs[ref] = newrefs[ref]
            del newrefs[ref]
        else:
            oldrefs.add(ref)
        r = ecfcursor.next()
    extra_records = max(len(newrefs) - len(oldrefs), 0)

    # Close record sets, cursors, etc, to allow increase_database_size.
    ecfcursor.close()
    clubs.close()
    del oldrefs, bothrefs, newrefs

    # Increase file size if necessary.
    results.increase_database_size(
        {filespec.ECFCLUB_FILE_DEF: (extra_records, extra_records)})

    # Import data (identical to other database engine versions).

    return ecfdataimport.copy_ecf_clubs_post_2011_rules(
        results,
        logwidget=logwidget,
        ecffile=ecffile,
        ecfdate=ecfdate,
        parent=parent,
        datecontrol=datecontrol,
        **kwargs)

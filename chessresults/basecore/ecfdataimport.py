# ecfdataimport.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Extract player and club data from ECF reference files or downloads.

ECF (formerly BCF) provided reference files on CD from the end of the 1998
season as a matter of routine.  These contained the active players from the
most recent three seasons.  From the end of the 2006 season smaller updates
were provided during the season but these were soon replaced by more frequent
issuing of reference files including new, or re-activated, players.  From the
middle of the 2011 season the reference files included all players who had
ever played a graded game (since early 1990s in practice).

The ECF introduced a rating system, calculated monthly, which replaced the
grading system.  The old reference files are not included in the rating system,
and are replaced by downloads published monthly which include all players who
have a rating.  Six-monthly downloads prior to 2020 have been made available
as far back as information is available.

A significant number of players on the old reference files are not shown in
any download.

"""

from ..core import filespec
from ..core import ecfrecord
from ..core import ecfclubdb
from ..core import ecfplayerdb
from ..core import ecfmaprecord


def copy_ecf_clubs_post_2020_rules(
    results, logwidget=None, ecfdata=None, downloaddate=None, **kwargs
):
    """ """
    keybyteify = results._keybyteify

    # downloaddate replaces the datecontrol and ecfdate arguments.
    # Keep the original names within the procedure.
    datecontrol = downloaddate
    ecfdate = downloaddate

    # The _strify method of the Database instance is not needed because the
    # source is not a DBF file but from a json.loads() call.
    # Assume any encoding problems caused the json.loads() call to fail.

    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            "".join(
                [
                    "Start processing all active clubs list downloaded on ",
                    datecontrol,
                    ".",
                ]
            )
        )
    results.start_transaction()

    # Update Master file date record.
    # There is no publication date associated with all clubs download so
    # use date of download to avoid design changes in clubs area.
    datecursor = results.database_cursor(
        filespec.ECFTXN_FILE_DEF, filespec.ECFDATE_FIELD_DEF
    )
    try:
        r = datecursor.first()
        ecfdateexists = False
        while r:
            daterecord = ecfrecord.ECFrefDBrecordECFdate()
            daterecord.load_instance(
                results,
                filespec.ECFTXN_FILE_DEF,
                filespec.ECFDATE_FIELD_DEF,
                r,
            )
            if daterecord.value.ECFobjtype == ecfrecord.objtypeClub:
                if ecfdate != daterecord.value.appliedECFdate:
                    newdaterecord = daterecord.clone()
                    newdaterecord.value.appliedECFdate = ecfdate
                    newdaterecord.edit_record(
                        results,
                        filespec.ECFTXN_FILE_DEF,
                        filespec.ECFDATE_FIELD_DEF,
                        newdaterecord,
                    )
                if ecfdate == daterecord.value.ECFdate:
                    ecfdateexists = True
            r = datecursor.next()
        if not ecfdateexists:
            txndaterec = ecfrecord.ECFrefDBrecordECFdate()
            txndaterec.value.ECFdate = ecfdate
            txndaterec.value.ECFtxntype = ecfrecord.txnNew
            txndaterec.value.ECFobjtype = ecfrecord.objtypeClub
            txndaterec.value.appliedECFdate = ecfdate
            txndaterec.key.recno = None
            txndaterec.put_record(results, filespec.ECFTXN_FILE_DEF)
            ecfrecord.ECFrefDBrecordECFdate.set_most_recent_master_dates(
                results
            )
    finally:
        datecursor.close()

    # Load the ECF data.
    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            "Add or edit ECF Club Code references to Master club file."
        )
    ecf_codes = set()
    ecfcursor = results.database_cursor(
        filespec.ECFCLUB_FILE_DEF, filespec.ECFCLUBCODE_FIELD_DEF
    )
    try:
        for data in ecfdata["clubs"]:
            club_code = data.get("club_code")
            if club_code is None:
                club_code = ""
            club_name = data.get("club_name")
            if club_name is None:
                club_name = ""
            assoc_code = data.get("assoc_code")
            if assoc_code is None:
                assoc_code = ""
            ecfrec = ecfrecord.ECFrefDBrecordECFclub()
            record = ecfcursor.nearest(keybyteify(club_code))
            if record == None:
                ecfrec.key.recno = None
                ecfrec.value.ECFcode = club_code
                ecfrec.value.ECFactive = True
                ecfrec.value.ECFname = club_name
                ecfrec.value.ECFcountycode = assoc_code
                ecf_codes.add(ecfrec.value.ECFcode)
                ecfrec.put_record(results, filespec.ECFCLUB_FILE_DEF)
            elif record[0] != club_code:
                ecfrec.key.recno = None
                ecfrec.value.ECFcode = club_code
                ecfrec.value.ECFactive = True
                ecfrec.value.ECFname = club_name
                ecfrec.value.ECFcountycode = assoc_code
                ecf_codes.add(ecfrec.value.ECFcode)
                ecfrec.put_record(results, filespec.ECFCLUB_FILE_DEF)
            else:
                ecfrec.load_instance(
                    results,
                    filespec.ECFCLUB_FILE_DEF,
                    filespec.ECFCLUBCODE_FIELD_DEF,
                    record,
                )
                ecfnew = ecfrec.clone()
                ecfnew.value.ECFactive = True
                ecfnew.value.ECFname = club_name
                ecfnew.value.ECFcountycode = assoc_code
                ecf_codes.add(ecfrec.value.ECFcode)
                ecfrec.edit_record(
                    results,
                    filespec.ECFCLUB_FILE_DEF,
                    filespec.ECFCLUBCODE_FIELD_DEF,
                    ecfnew,
                )

        # Mark ECF codes not in download as inactive.
        # Meaning of inactive depends on which download is loaded, latest or
        # earlier.
        if logwidget:
            logwidget.append_text(
                "Delete ECF Club Code references not in all active clubs."
            )
        record = ecfcursor.first()
        while record:
            ecfrec = ecfrecord.ECFrefDBrecordECFclub()
            ecfrec.load_instance(
                results,
                filespec.ECFCLUB_FILE_DEF,
                filespec.ECFCLUBCODE_FIELD_DEF,
                record,
            )
            if ecfrec.value.ECFcode not in ecf_codes:
                ecfnew = ecfrec.clone()
                ecfnew.value.ECFactive = False
                ecfrec.edit_record(
                    results,
                    filespec.ECFCLUB_FILE_DEF,
                    filespec.ECFCLUBCODE_FIELD_DEF,
                    ecfnew,
                )
            record = ecfcursor.next()

    finally:
        ecfcursor.close()
    results.commit()
    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            " ".join(
                [
                    "All active clubs list downloaded on",
                    datecontrol,
                    "has been processed.",
                ]
            )
        )
    return True


def copy_ecf_players_post_2020_rules(
    results, logwidget=None, ecfdata=None, downloaddate=None, **kwargs
):
    """ """
    keybyteify = results._keybyteify

    # downloaddate replaces the datecontrol argument.
    # ecfdate is replaced by ... in ecfdata.
    # Keep the original names within the procedure.
    datecontrol = downloaddate
    ecfdate = ecfdata["rating_effective_date"]

    # The _strify method of the Database instance is not needed because the
    # source is not a DBF file but from a json.loads() call.
    # Assume any encoding problems caused the json.loads() call to fail.
    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            "".join(
                [
                    "Start processing players list downloaded on ",
                    datecontrol,
                    " published on ",
                    ecfdate,
                    ".",
                ]
            )
        )
    results.start_transaction()

    # Update Master file date record.
    datecursor = results.database_cursor(
        filespec.ECFTXN_FILE_DEF, filespec.ECFDATE_FIELD_DEF
    )
    try:
        r = datecursor.first()
        ecfdateexists = False
        while r:
            daterecord = ecfrecord.ECFrefDBrecordECFdate()
            daterecord.load_instance(
                results,
                filespec.ECFTXN_FILE_DEF,
                filespec.ECFDATE_FIELD_DEF,
                r,
            )
            if daterecord.value.ECFobjtype == ecfrecord.objtypePlayer:
                if ecfdate != daterecord.value.appliedECFdate:
                    newdaterecord = daterecord.clone()
                    newdaterecord.value.appliedECFdate = ecfdate
                    newdaterecord.edit_record(
                        results,
                        filespec.ECFTXN_FILE_DEF,
                        filespec.ECFDATE_FIELD_DEF,
                        newdaterecord,
                    )
                if ecfdate == daterecord.value.ECFdate:
                    ecfdateexists = True
            r = datecursor.next()
        if not ecfdateexists:
            txndaterec = ecfrecord.ECFrefDBrecordECFdate()
            txndaterec.value.ECFdate = ecfdate
            txndaterec.value.ECFtxntype = ecfrecord.txnNew
            txndaterec.value.ECFobjtype = ecfrecord.objtypePlayer
            txndaterec.value.appliedECFdate = ecfdate
            txndaterec.key.recno = None
            txndaterec.put_record(results, filespec.ECFTXN_FILE_DEF)
            ecfrecord.ECFrefDBrecordECFdate.set_most_recent_master_dates(
                results
            )
    finally:
        datecursor.close()

    # Load the ECF data.
    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            "Add or edit ECF Grading Code references to Master player file."
        )
    ecf_codes = set()
    ecfcursor = results.database_cursor(
        filespec.ECFPLAYER_FILE_DEF, filespec.ECFPLAYERCODE_FIELD_DEF
    )
    try:
        code_index = ecfdata["column_names"].index("ECF_code")
        name_index = ecfdata["column_names"].index("full_name")
        club_code_index = (ecfdata["column_names"].index("club_code"),)
        for data in ecfdata["players"]:
            ECF_code = data[code_index]
            if ECF_code is None:
                ECF_code = ""
            full_name = data[name_index]
            if full_name is None:
                full_name = ""
            clubcodes = []
            for i in club_code_index:
                c = data[i]
                if isinstance(c, str):
                    clubcodes.append(c)
                else:
                    clubcodes.append(str(c).zfill(4))
            clubcodes.sort()
            ecfrec = ecfrecord.ECFrefDBrecordECFplayer()
            record = ecfcursor.nearest(keybyteify(ECF_code))
            if record == None:
                ecfrec.key.recno = None
                ecfrec.value.ECFcode = ECF_code
                ecfrec.value.ECFactive = True
                ecfrec.value.ECFname = full_name
                ecfrec.value.ECFclubcodes = clubcodes
                ecf_codes.add(ecfrec.value.ECFcode)
                ecfrec.put_record(results, filespec.ECFPLAYER_FILE_DEF)
            elif record[0] != ECF_code:
                ecfrec.key.recno = None
                ecfrec.value.ECFcode = ECF_code
                ecfrec.value.ECFactive = True
                ecfrec.value.ECFname = full_name
                ecfrec.value.ECFclubcodes = clubcodes
                ecf_codes.add(ecfrec.value.ECFcode)
                ecfrec.put_record(results, filespec.ECFPLAYER_FILE_DEF)
            else:
                ecfrec.load_instance(
                    results,
                    filespec.ECFPLAYER_FILE_DEF,
                    filespec.ECFPLAYERCODE_FIELD_DEF,
                    record,
                )
                ecfnew = ecfrec.clone()
                ecfnew.value.ECFactive = True
                ecfnew.value.ECFname = full_name
                ecfnew.value.ECFclubcodes = clubcodes
                ecf_codes.add(ecfrec.value.ECFcode)
                ecfrec.edit_record(
                    results,
                    filespec.ECFPLAYER_FILE_DEF,
                    filespec.ECFPLAYERCODE_FIELD_DEF,
                    ecfnew,
                )

        # Mark ECF codes not in download as inactive.
        # Meaning of inactive depends on which download is loaded, latest or
        # earlier.
        if logwidget:
            logwidget.append_text(
                "Mark ECF Grading Codes not in player download inactive."
            )
        clubcodes = []
        record = ecfcursor.first()
        while record:
            ecfrec = ecfrecord.ECFrefDBrecordECFplayer()
            ecfrec.load_instance(
                results,
                filespec.ECFPLAYER_FILE_DEF,
                filespec.ECFPLAYERCODE_FIELD_DEF,
                record,
            )
            if ecfrec.value.ECFcode not in ecf_codes:
                ecfnew = ecfrec.clone()
                ecfnew.value.ECFactive = False
                ecfnew.value.ECFclubcodes = clubcodes
                ecfrec.edit_record(
                    results,
                    filespec.ECFPLAYER_FILE_DEF,
                    filespec.ECFPLAYERCODE_FIELD_DEF,
                    ecfnew,
                )
            record = ecfcursor.next()
    finally:
        ecfcursor.close()

    # Match grading codes for new players to copied master list
    # Any left unlinked are probably merged before master list published
    # if publication after results submission
    if logwidget:
        logwidget.append_text(
            "Reconcile new player Grading Codes with player download."
        )
    ecfmapcursor = results.database_cursor(
        filespec.MAPECFPLAYER_FILE_DEF, filespec.MAPECFPLAYER_FIELD_DEF
    )
    try:
        mapdata = ecfmapcursor.first()
        while mapdata:
            mr = ecfmaprecord.ECFmapDBrecordPlayer()
            mr.load_record(mapdata)

            # mapdata values like (key, None) occur sometimes, origin unknown
            # but seen only when mixing event imports and ecf reference data
            # imports.
            # Ignoring them should be correct, and seems ok too.
            # Find and delete them offline.
            # See gui.events_lite too.
            if mr.value.__dict__:

                if mr.value.playercode is None:
                    if mr.value.playerecfcode is not None:
                        if ecfrecord.get_ecf_player_for_grading_code(
                            results, mr.value.playerecfcode
                        ):
                            newmr = mr.clone()
                            newmr.value.playerecfcode = None
                            newmr.value.playercode = mr.value.playerecfcode
                            mr.edit_record(
                                results,
                                filespec.MAPECFPLAYER_FILE_DEF,
                                filespec.MAPECFPLAYER_FIELD_DEF,
                                newmr,
                            )
            mapdata = ecfmapcursor.next()
    finally:
        ecfmapcursor.close()

    results.commit()
    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            "".join(
                [
                    "Player list downloaded on ",
                    datecontrol,
                    " has been processed.",
                ]
            )
        )
    return True


def copy_ecf_players_post_2011_rules(
    results,
    logwidget=None,
    ecffile=None,
    ecfdate=None,
    parent=None,
    datecontrol=None,
    **kwargs
):
    """Import a new ECF player file

    widget - the manager object for the ecf data import tab

    """
    strify = results._strify
    keyify = results._keyify
    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            "".join(
                ["Start processing Master player file for ", datecontrol, "."]
            )
        )
    results.start_transaction()

    # Update Master file date record.
    datecursor = results.database_cursor(
        filespec.ECFTXN_FILE_DEF, filespec.ECFDATE_FIELD_DEF
    )
    try:
        r = datecursor.first()
        ecfdateexists = False
        while r:
            daterecord = ecfrecord.ECFrefDBrecordECFdate()
            daterecord.load_instance(
                results,
                filespec.ECFTXN_FILE_DEF,
                filespec.ECFDATE_FIELD_DEF,
                r,
            )
            if daterecord.value.ECFobjtype == ecfrecord.objtypePlayer:
                if ecfdate != daterecord.value.appliedECFdate:
                    newdaterecord = daterecord.clone()
                    newdaterecord.value.appliedECFdate = ecfdate
                    newdaterecord.edit_record(
                        results,
                        filespec.ECFTXN_FILE_DEF,
                        filespec.ECFDATE_FIELD_DEF,
                        newdaterecord,
                    )
                if ecfdate == daterecord.value.ECFdate:
                    ecfdateexists = True
            r = datecursor.next()
        if not ecfdateexists:
            txndaterec = ecfrecord.ECFrefDBrecordECFdate()
            txndaterec.value.ECFdate = ecfdate
            txndaterec.value.ECFtxntype = ecfrecord.txnNew
            txndaterec.value.ECFobjtype = ecfrecord.objtypePlayer
            txndaterec.value.appliedECFdate = ecfdate
            txndaterec.key.recno = None
            txndaterec.put_record(results, filespec.ECFTXN_FILE_DEF)
            ecfrecord.ECFrefDBrecordECFdate.set_most_recent_master_dates(
                results
            )
    finally:
        datecursor.close()

    # Load the ECF data.
    ecfimp = ecfplayerdb.ECFplayersDBrecord()
    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            "Add or edit ECF Grading Code references to Master player file."
        )
    ecf_codes = set()
    ecfcursor = results.database_cursor(
        filespec.ECFPLAYER_FILE_DEF, filespec.ECFPLAYERCODE_FIELD_DEF
    )
    try:
        players = ecffile.database_cursor(
            ecfplayerdb.PLAYERS, ecfplayerdb.PLAYERS
        )
        try:
            data = players.first()
            while data:
                ecfimp.load_instance(
                    ecffile, ecfplayerdb.PLAYERS, ecfplayerdb.PLAYERS, data
                )
                clubcodes = []
                for f in ecfrecord._ECFplayerclubsfields:
                    c = ecfimp.value.__dict__.get(f)
                    if c:
                        clubcodes.append(strify(c))
                clubcodes.sort()
                ecfrec = ecfrecord.ECFrefDBrecordECFplayer()
                record = ecfcursor.nearest(keyify(ecfimp.value.REF))
                if record == None:
                    ecfrec.key.recno = None
                    ecfrec.value.ECFcode = strify(ecfimp.value.REF)
                    ecfrec.value.ECFactive = True
                    ecfrec.value.ECFname = strify(ecfimp.value.NAME)
                    ecfrec.value.ECFclubcodes = clubcodes
                    ecf_codes.add(ecfrec.value.ECFcode)
                    ecfrec.put_record(results, filespec.ECFPLAYER_FILE_DEF)
                elif record[0] != strify(ecfimp.value.REF):
                    ecfrec.key.recno = None
                    ecfrec.value.ECFcode = strify(ecfimp.value.REF)
                    ecfrec.value.ECFactive = True
                    ecfrec.value.ECFname = strify(ecfimp.value.NAME)
                    ecfrec.value.ECFclubcodes = clubcodes
                    ecf_codes.add(ecfrec.value.ECFcode)
                    ecfrec.put_record(results, filespec.ECFPLAYER_FILE_DEF)
                else:
                    ecfrec.load_instance(
                        results,
                        filespec.ECFPLAYER_FILE_DEF,
                        filespec.ECFPLAYERCODE_FIELD_DEF,
                        record,
                    )
                    ecfnew = ecfrec.clone()
                    ecfnew.value.ECFactive = True
                    ecfnew.value.ECFname = strify(ecfimp.value.NAME)
                    ecfnew.value.ECFclubcodes = clubcodes
                    ecf_codes.add(ecfrec.value.ECFcode)
                    ecfrec.edit_record(
                        results,
                        filespec.ECFPLAYER_FILE_DEF,
                        filespec.ECFPLAYERCODE_FIELD_DEF,
                        ecfnew,
                    )
                data = players.next()
        finally:
            players.close()

        # Mark ECF codes not in download as inactive.
        # Meaning of inactive depends on which download is loaded, latest or
        # earlier.
        if logwidget:
            logwidget.append_text(
                "Mark ECF Grading Codes not on Master player file inactive."
            )
        clubcodes = []
        record = ecfcursor.first()
        while record:
            ecfrec = ecfrecord.ECFrefDBrecordECFplayer()
            ecfrec.load_instance(
                results,
                filespec.ECFPLAYER_FILE_DEF,
                filespec.ECFPLAYERCODE_FIELD_DEF,
                record,
            )
            if ecfrec.value.ECFcode not in ecf_codes:
                ecfnew = ecfrec.clone()
                ecfnew.value.ECFactive = False
                ecfnew.value.ECFclubcodes = clubcodes
                ecfrec.edit_record(
                    results,
                    filespec.ECFPLAYER_FILE_DEF,
                    filespec.ECFPLAYERCODE_FIELD_DEF,
                    ecfnew,
                )
            record = ecfcursor.next()
    finally:
        ecfcursor.close()

    # Match grading codes for new players to copied master list
    # Any left unlinked are probably merged before master list published
    # if publication after results submission
    if logwidget:
        logwidget.append_text(
            "Reconcile new player Grading Codes with Master player file."
        )
    ecfmapcursor = results.database_cursor(
        filespec.MAPECFPLAYER_FILE_DEF, filespec.MAPECFPLAYER_FIELD_DEF
    )
    try:
        mapdata = ecfmapcursor.first()
        while mapdata:
            mr = ecfmaprecord.ECFmapDBrecordPlayer()
            mr.load_record(mapdata)

            # mapdata values like (key, None) occur sometimes, origin unknown
            # but seen only when mixing event imports and ecf reference data
            # imports.
            # Ignoring them should be correct, and seems ok too.
            # Find and delete them offline.
            # See gui.events_lite too.
            if mr.value.__dict__:

                if mr.value.playercode is None:
                    if mr.value.playerecfcode is not None:
                        if ecfrecord.get_ecf_player_for_grading_code(
                            results, mr.value.playerecfcode
                        ):
                            newmr = mr.clone()
                            newmr.value.playerecfcode = None
                            newmr.value.playercode = mr.value.playerecfcode
                            mr.edit_record(
                                results,
                                filespec.MAPECFPLAYER_FILE_DEF,
                                filespec.MAPECFPLAYER_FIELD_DEF,
                                newmr,
                            )
            mapdata = ecfmapcursor.next()
    finally:
        ecfmapcursor.close()

    results.commit()
    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            "".join(
                [
                    "Master player file for ",
                    datecontrol,
                    " has been processed.",
                ]
            )
        )
    return True


def copy_ecf_clubs_post_2011_rules(
    results,
    logwidget=None,
    ecffile=None,
    ecfdate=None,
    parent=None,
    datecontrol=None,
    datekey=lambda d: d,
    **kwargs
):
    """Import a new ECF club file

    widget - the manager object for the ecf data import tab

    """
    strify = results._strify
    keyify = results._keyify
    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            "".join(
                ["Start processing Master club file for ", datecontrol, "."]
            )
        )
    results.start_transaction()

    # Update Master file date record.
    datecursor = results.database_cursor(
        filespec.ECFTXN_FILE_DEF, filespec.ECFDATE_FIELD_DEF
    )
    try:
        r = datecursor.first()
        ecfdateexists = False
        while r:
            daterecord = ecfrecord.ECFrefDBrecordECFdate()
            daterecord.load_instance(
                results,
                filespec.ECFTXN_FILE_DEF,
                filespec.ECFDATE_FIELD_DEF,
                r,
            )
            if daterecord.value.ECFobjtype == ecfrecord.objtypeClub:
                if ecfdate != daterecord.value.appliedECFdate:
                    newdaterecord = daterecord.clone()
                    newdaterecord.value.appliedECFdate = ecfdate
                    newdaterecord.edit_record(
                        results,
                        filespec.ECFTXN_FILE_DEF,
                        filespec.ECFDATE_FIELD_DEF,
                        newdaterecord,
                    )
                if ecfdate == daterecord.value.ECFdate:
                    ecfdateexists = True
            r = datecursor.next()
        if not ecfdateexists:
            txndaterec = ecfrecord.ECFrefDBrecordECFdate()
            txndaterec.value.ECFdate = ecfdate
            txndaterec.value.ECFtxntype = ecfrecord.txnNew
            txndaterec.value.ECFobjtype = ecfrecord.objtypeClub
            txndaterec.value.appliedECFdate = ecfdate
            txndaterec.key.recno = None
            txndaterec.put_record(results, filespec.ECFTXN_FILE_DEF)
            ecfrecord.ECFrefDBrecordECFdate.set_most_recent_master_dates(
                results
            )
    finally:
        datecursor.close()

    # Load the ECF data.
    ecfimp = ecfclubdb.ECFclubsDBrecord()
    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            "Add or edit ECF Club Code references to Master club file."
        )
    ecf_codes = set()
    ecfcursor = results.database_cursor(
        filespec.ECFCLUB_FILE_DEF, filespec.ECFCLUBCODE_FIELD_DEF
    )
    try:
        clubs = ecffile.database_cursor(ecfclubdb.CLUBS, ecfclubdb.CLUBS)
        try:
            data = clubs.first()
            while data:
                ecfimp.load_instance(
                    ecffile, ecfclubdb.CLUBS, ecfclubdb.CLUBS, data
                )
                ecfrec = ecfrecord.ECFrefDBrecordECFclub()
                record = ecfcursor.nearest(keyify(ecfimp.value.CODE))
                if record == None:
                    ecfrec.key.recno = None
                    ecfrec.value.ECFcode = strify(ecfimp.value.CODE)
                    ecfrec.value.ECFactive = True
                    ecfrec.value.ECFname = strify(ecfimp.value.CLUB)
                    ecfrec.value.ECFcountycode = strify(ecfimp.value.COUNTY)
                    ecf_codes.add(ecfrec.value.ECFcode)
                    ecfrec.put_record(results, filespec.ECFCLUB_FILE_DEF)
                elif record[0] != strify(ecfimp.value.CODE):
                    ecfrec.key.recno = None
                    ecfrec.value.ECFcode = strify(ecfimp.value.CODE)
                    ecfrec.value.ECFactive = True
                    ecfrec.value.ECFname = strify(ecfimp.value.CLUB)
                    ecfrec.value.ECFcountycode = strify(ecfimp.value.COUNTY)
                    ecf_codes.add(ecfrec.value.ECFcode)
                    ecfrec.put_record(results, filespec.ECFCLUB_FILE_DEF)
                else:
                    ecfrec.load_instance(
                        results,
                        filespec.ECFCLUB_FILE_DEF,
                        filespec.ECFCLUBCODE_FIELD_DEF,
                        record,
                    )
                    ecfnew = ecfrec.clone()
                    ecfnew.value.ECFactive = True
                    ecfnew.value.ECFname = strify(ecfimp.value.CLUB)
                    ecfnew.value.ECFcountycode = strify(ecfimp.value.COUNTY)
                    ecf_codes.add(ecfrec.value.ECFcode)
                    ecfrec.edit_record(
                        results,
                        filespec.ECFCLUB_FILE_DEF,
                        filespec.ECFCLUBCODE_FIELD_DEF,
                        ecfnew,
                    )
                data = clubs.next()
        finally:
            clubs.close()

        # Mark ECF codes not in download as inactive.
        # Meaning of inactive depends on which download is loaded, latest or
        # earlier.
        if logwidget:
            logwidget.append_text(
                "Mark ECF Club Codes not on clubs download inactive."
            )
        record = ecfcursor.first()
        while record:
            ecfrec = ecfrecord.ECFrefDBrecordECFclub()
            ecfrec.load_instance(
                results,
                filespec.ECFCLUB_FILE_DEF,
                filespec.ECFCLUBCODE_FIELD_DEF,
                record,
            )
            if ecfrec.value.ECFcode not in ecf_codes:
                ecfnew = ecfrec.clone()
                ecfnew.value.ECFactive = False
                ecfrec.edit_record(
                    results,
                    filespec.ECFCLUB_FILE_DEF,
                    filespec.ECFCLUBCODE_FIELD_DEF,
                    ecfnew,
                )
            record = ecfcursor.next()
    finally:
        ecfcursor.close()

    results.commit()
    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            " ".join(
                ["Master club file for", datecontrol, "has been processed."]
            )
        )
    return True


def copy_single_ecf_club_post_2020_rules(results, ecfdata=None, **kwargs):
    """ """
    keybyteify = results._keybyteify

    # The _strify method of the Database instance is not needed because the
    # source is not a DBF file but from a json.loads() call.
    # Assume any encoding problems caused the json.loads() call to fail.

    results.start_transaction()

    # Load the ECF data.
    ecfcursor = results.database_cursor(
        filespec.ECFCLUB_FILE_DEF, filespec.ECFCLUBCODE_FIELD_DEF
    )
    try:
        club_code = ecfdata.get("club_code")
        if club_code is None:
            club_code = ""
        club_name = ecfdata.get("club_name")
        if club_name is None:
            club_name = ""
        assoc_code = ecfdata.get("assoc_code")
        if assoc_code is None:
            assoc_code = ""
        ecfrec = ecfrecord.ECFrefDBrecordECFclub()
        record = ecfcursor.nearest(keybyteify(club_code))
        if record == None:
            ecfrec.key.recno = None
            ecfrec.value.ECFcode = club_code
            ecfrec.value.ECFactive = False
            ecfrec.value.ECFname = club_name
            ecfrec.value.ECFcountycode = assoc_code
            ecfrec.put_record(results, filespec.ECFCLUB_FILE_DEF)
        elif record[0] != club_code:
            ecfrec.key.recno = None
            ecfrec.value.ECFcode = club_code
            ecfrec.value.ECFactive = False
            ecfrec.value.ECFname = club_name
            ecfrec.value.ECFcountycode = assoc_code
            ecfrec.put_record(results, filespec.ECFCLUB_FILE_DEF)
        else:
            ecfrec.load_instance(
                results,
                filespec.ECFCLUB_FILE_DEF,
                filespec.ECFCLUBCODE_FIELD_DEF,
                record,
            )
            ecfnew = ecfrec.clone()
            ecfnew.value.ECFactive = False
            ecfnew.value.ECFname = club_name
            ecfnew.value.ECFcountycode = assoc_code
            ecfrec.edit_record(
                results,
                filespec.ECFCLUB_FILE_DEF,
                filespec.ECFCLUBCODE_FIELD_DEF,
                ecfnew,
            )

    finally:
        ecfcursor.close()
    results.commit()
    return True


def copy_single_ecf_players_post_2020_rules(results, ecfdata=None, **kwargs):
    """ """
    keybyteify = results._keybyteify

    # The _strify method of the Database instance is not needed because the
    # source is not a DBF file but from a json.loads() call.
    # Assume any encoding problems caused the json.loads() call to fail.
    results.start_transaction()

    # Load the ECF data.
    ecfcursor = results.database_cursor(
        filespec.ECFPLAYER_FILE_DEF, filespec.ECFPLAYERCODE_FIELD_DEF
    )
    try:
        ECF_code = ecfdata["ECF_code"]
        if ECF_code is None:
            ECF_code = ""
        full_name = ecfdata["full_name"]
        if full_name is None:
            full_name = ""
        clubcodes = [str(ecfdata["club_code"]).zfill(4)]
        ecfrec = ecfrecord.ECFrefDBrecordECFplayer()
        record = ecfcursor.nearest(keybyteify(ECF_code))
        if record == None:
            ecfrec.key.recno = None
            ecfrec.value.ECFcode = ECF_code
            ecfrec.value.ECFactive = False
            ecfrec.value.ECFname = full_name
            ecfrec.value.ECFclubcodes = clubcodes
            ecfrec.put_record(results, filespec.ECFPLAYER_FILE_DEF)
        elif record[0] != ECF_code:
            ecfrec.key.recno = None
            ecfrec.value.ECFcode = ECF_code
            ecfrec.value.ECFactive = False
            ecfrec.value.ECFname = full_name
            ecfrec.value.ECFclubcodes = clubcodes
            ecfrec.put_record(results, filespec.ECFPLAYER_FILE_DEF)
        else:
            ecfrec.load_instance(
                results,
                filespec.ECFPLAYER_FILE_DEF,
                filespec.ECFPLAYERCODE_FIELD_DEF,
                record,
            )
            ecfnew = ecfrec.clone()
            ecfnew.value.ECFactive = False
            ecfnew.value.ECFname = full_name
            ecfnew.value.ECFclubcodes = clubcodes
            ecfrec.edit_record(
                results,
                filespec.ECFPLAYER_FILE_DEF,
                filespec.ECFPLAYERCODE_FIELD_DEF,
                ecfnew,
            )
    finally:
        ecfcursor.close()

    results.commit()
    return True

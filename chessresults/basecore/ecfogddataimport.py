# ecfogddataimport.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Extract player and club data from ECF Online Grading Database files.

The Online Grading Database download file is roughly equivalent in content to
the printed Grading List.  It contains all players who have played at least
one graded game in the most recent three completed seasons.  Toward the end of
the 2012-2013 season the downloadable online membership list became available
in a reliable form.  This module follows the ecfdataimport.py style to allow
addition of this source to the menu.

"""

import csv

from ..core import filespec
from ..core.ogd import ecfogddb
from ..core.ogd import ecfogdrecord


def validate_and_copy_ecf_ogd_players_post_2006_rules(
    results, logwidget=None, ecffile=None, parent=None, **kwargs
):
    """Import a new ECF downloadable OGD player file.

    widget - the manager object for the ecf data import tab

    """
    gcodes = validate_ecf_ogd_players_post_2006_rules(
        logwidget, ecffile, **kwargs
    )
    if gcodes is False:
        return
    return copy_ecf_ogd_players_post_2006_rules(results, logwidget, gcodes)


def validate_ecf_ogd_players_post_2006_rules(
    logwidget,
    ecffile,
    playercode_field=None,
    playername_field=None,
    playerclubs_fields=None,
    **kwargs
):
    """Return dict of update records if valid, or False if not."""
    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            "Start processing Online Grading Database player file."
        )

    # Get all ECF grading codes in Online Grading Database download file.
    ogdfile = ecffile.main[ecfogddb.PLAYERS]
    gcodes = dict()
    duplicates = []
    checkfails = []
    r = csv.DictReader(
        [o.decode("iso-8859-1") for o in ogdfile.textlines], ogdfile.fieldnames
    )
    for row in r:
        try:
            gcodes.setdefault(row[playercode_field], []).append(
                (row[playername_field], [row[c] for c in playerclubs_fields])
            )
        except:
            if logwidget:
                logwidget.append_text_only("")
                logwidget.append_text_only(
                    "Exception while reading a row from Grading List."
                )
                logwidget.append_text_only(
                    "".join((str(len(gcodes)), " rows read successfully."))
                )
                logwidget.append_text_only("")
            return False
    for k, v in gcodes.items():
        if len(v) > 1:
            duplicates.append(k)
        if len(k) != 7:
            checkfails.append(k)
        else:
            tokens = list(k)
            checkdigit = 0
            for i in range(6):
                if not tokens[i].isdigit():
                    checkfails.append(k)
                    break
                checkdigit += int(tokens[5 - i]) * (i + 2)
            else:
                if tokens[-1] != "ABCDEFGHJKL"[checkdigit % 11]:
                    checkfails.append(k)
    if len(duplicates) or len(checkfails):
        if logwidget:
            logwidget.append_text(
                "Import from Online Grading Database abandonned."
            )
            if len(duplicates):
                logwidget.append_text_only("Duplicate grading codes exist.")
            if len(checkfails):
                logwidget.append_text_only(
                    "Grading codes exist that fail the checkdigit test."
                )
            logwidget.append_text_only("")
        return False
    return gcodes


def copy_ecf_ogd_players_post_2006_rules(results, logwidget, gcodes):
    """Copy update in gcodes to database using record definition results."""

    # Load the ECF data.
    if logwidget:
        logwidget.append_text(
            "Update existing records from Online Grading Database file."
        )
    startlengcodes = len(gcodes)
    ogdplayerrec = ecfogdrecord.ECFrefOGDrecordPlayer()
    results.start_transaction()
    ogdplayers = results.database_cursor(
        filespec.ECFOGDPLAYER_FILE_DEF, filespec.ECFOGDPLAYER_FIELD_DEF
    )
    try:
        data = ogdplayers.first()
        while data:
            ogdplayerrec.load_record(data)
            code = ogdplayerrec.value.ECFOGDcode
            newrec = ogdplayerrec.clone()
            if code in gcodes:
                newrec.value.ECFOGDname = gcodes[code][0][0]
                newrec.value.ECFOGDclubs = [c for c in gcodes[code][0][1]]
                del gcodes[code]
            else:
                newrec.value.ECFOGDname = None
                newrec.value.ECFOGDclubs = []
            ogdplayerrec.edit_record(
                results,
                filespec.ECFOGDPLAYER_FILE_DEF,
                filespec.ECFOGDPLAYER_FIELD_DEF,
                newrec,
            )
            data = ogdplayers.next()

            # Avoid possible RecursionError on next ogdplayerrec.clone() call.
            del ogdplayerrec.newrecord

    finally:
        ogdplayers.close()
    if logwidget:
        logwidget.append_text_only(
            "".join(
                (
                    str(startlengcodes - len(gcodes)),
                    " records were updated.",
                )
            )
        )

    if logwidget:
        logwidget.append_text(
            "Create new records from Online Grading Database file."
        )
        logwidget.append_text_only(
            "".join(
                (
                    str(len(gcodes)),
                    " records will be created.",
                )
            )
        )
    for k, v in gcodes.items():
        ogdplayerrec = ecfogdrecord.ECFrefOGDrecordPlayer()
        ogdplayerrec.key.recno = None
        ogdplayerrec.value.ECFOGDcode = k
        ogdplayerrec.value.ECFOGDname = v[0][0]
        ogdplayerrec.value.ECFOGDclubs = [c for c in v[0][1]]
        ogdplayerrec.put_record(results, filespec.ECFOGDPLAYER_FILE_DEF)
    if logwidget:
        logwidget.append_text("Commit database update.")
        logwidget.append_text_only("")
    results.commit()
    if logwidget:
        logwidget.append_text(
            "".join(
                (
                    "Grading Codes and names imported from ",
                    "Online Grading database.",
                )
            )
        )
        logwidget.append_text_only("")
    return True

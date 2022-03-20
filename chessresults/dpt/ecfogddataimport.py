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

from ..core import filespec
from ..core import ecfogdrecord
from ..basecore.ecfogddataimport import (
    validate_ecf_ogd_players_post_2006_rules,
    copy_ecf_ogd_players_post_2006_rules,
)


def validate_and_copy_ecf_ogd_players_post_2006_rules(
    results, logwidget=None, ecffile=None, parent=None, **kwargs
):
    """Import a new ECF downloadable OGD player file.

    widget - the manager object for the ecf data import tab

    """
    gcodes = validate_ecf_ogd_players_post_2006_rules(logwidget, ecffile)
    if gcodes is False:
        return

    # Ensure ECFOGDPLAYER_FILE_DEF file is large enough for any extra records.
    if logwidget:
        logwidget.append_text("", timestamp=False)
        logwidget.append_text(
            "".join(
                (
                    "Ensure ",
                    filespec.ECFOGDPLAYER_FILE_DEF,
                    " is large enough for any extra records on Master player file.",
                )
            )
        )
    oldrefs = set()
    bothrefs = set()
    newrefs = set(gcodes)
    ecfcursor = results.database_cursor(
        filespec.ECFOGDPLAYER_FILE_DEF, filespec.ECFOGDPLAYER_FIELD_DEF
    )
    ecfrec = ecfogdrecord.ECFrefOGDrecordPlayer()

    # Go through existing records for equivalents to OGD records.
    r = ecfcursor.first()
    while r:
        ecfrec.load_instance(
            results,
            filespec.ECFOGDPLAYER_FILE_DEF,
            filespec.ECFOGDPLAYER_FIELD_DEF,
            r,
        )
        ref = ecfrec.value.ECFOGDcode
        if ref in newrefs:
            bothrefs.add(ref)
            newrefs.discard(ref)
        else:
            oldrefs.add(ref)
        r = ecfcursor.next()
    extra_records = max(len(newrefs) - len(oldrefs), 0)

    # Close record sets, cursors, etc, to allow increase_database_size.
    ecfcursor.close()

    # Increase file size if necessary.
    results.increase_database_size(
        {filespec.ECFOGDPLAYER_FILE_DEF: (extra_records, extra_records)}
    )

    # Import data.
    return copy_ecf_ogd_players_post_2006_rules(results, logwidget, gcodes)

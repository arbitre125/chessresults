# newplayers.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database NewPlayers panel class for ECF monthly rating.

Identify new players.  Declare the new player to be the same as one already
on database or to be new to this database.

This module did the job of newplayers_lite before version 5.1 of ChessResults.

This module now customises newplayers_lite for use with the ECF monthly
rating system.

"""
import tkinter
import tkinter.messagebox
import re
import os
import urllib.request
import json

from solentware_misc.core.getconfigurationitem import get_configuration_item

from . import newplayers_lite
from ..core import resultsrecord
from ..core import ecfrecord
from ..core import ecfmaprecord
from ..core import constants
from ..basecore.ecfdataimport import copy_single_ecf_players_post_2020_rules


class NewPlayers(newplayers_lite.NewPlayers):

    """New Players panel for Results database with ECF monthly rating.

    Customise user interface for use with ECF monthly rating system.

    """

    _btn_download_ecf_codes = "newplayers_ecf_codes"

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database new player panel."""
        super(NewPlayers, self).__init__(parent=parent, cnf=cnf, **kargs)

    def on_download_ecf_codes(self, event=None):
        """Do processing for on_download_ecf_codes button."""
        self.download_ecf_codes()
        return "break"

    def describe_buttons(self):
        """Define all action buttons that may appear on new players page."""
        self.define_button(
            self._btn_merge,
            text="Merge",
            tooltip="Merge the selected players under the chosen reference.",
            underline=0,
            command=self.on_merge,
        )
        self.define_button(
            self._btn_join,
            text="Join",
            tooltip="Join selected merged players under chosen reference.",
            underline=0,
            command=self.on_join,
        )
        self.define_button(
            self._btn_person_details,
            text="Players Details",
            tooltip="Show details for bookmarked and selected players.",
            underline=1,
            command=self.on_person_details,
        )
        self.define_button(
            self._btn_download_ecf_codes,
            text="Download ECF codes",
            tooltip="Download ECF code for one of reported codes.",
            underline=1,
            command=self.on_download_ecf_codes,
        )

    def download_ecf_codes(self):
        """Attempt to download ECF codes for new player's reported codes."""
        title = "Download ECF codes"
        nsel = self.newplayergrid.selection
        nbkm = self.newplayergrid.bookmarks
        if len(nsel) + len(nbkm) == 0:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Please select or bookmark the new players for whom",
                        "download of ECF codes for reported codes should be",
                        "attempted",
                    )
                ),
                title=title,
            )
            return
        db = self.get_appsys().get_results_database()
        aliaskeys = {n[-1] for n in nsel + nbkm}
        reportedcodes = set()
        for name, key in nsel + nbkm:
            if key not in aliaskeys:
                continue
            aliaskeys.remove(key)
            aliasrecord = resultsrecord.get_alias(db, key)
            if aliasrecord is None:
                continue
            self._download_ecf_codes_for_player_reported_codes(
                aliasrecord,
                db,
                title,
                reportedcodes=reportedcodes,
            )

    def _download_ecf_codes_for_player_reported_codes(
        self, aliasrecord, db, title, reportedcodes=None
    ):
        """Attempt to download ECF codes for aliasrecord player.

        There may be several reported codes for a player.  Look for an
        ECF code for each of them.

        """
        if reportedcodes is None:
            reportedcodes = set()
        for rc in aliasrecord.value.reported_codes:
            if rc in reportedcodes:
                continue
            reportedcodes.add(rc)

            # The regular expression prevents malformed ECF codes with
            # an invalid check digit being treated as ECF membership
            # numbers.  However, for example, a 12 digit numberic code is
            # treated as two ECF membership numbers.
            # The interpretation of '123456B012345' depends on whether
            # 'B' is the valid check digit for '123456' as an ECF code.
            for match in re.finditer(
                "|".join(
                    (
                        r"(?P<ec>[1-9][0-9]{5}[a-hjklA-HJKL])",  # code
                        r"(?P<mno>[0-9]{6})(?![a-zA-Z])",  # membership
                    )
                ),
                rc,
            ):
                groups = match.groupdict()
                if groups["mno"]:
                    ecfdata = self._ecf_data_for_reported_membership_number(
                        aliasrecord, db, title, groups["mno"]
                    )
                    if ecfdata is None:
                        continue
                    if self._is_reported_ecf_code_on_database(
                        aliasrecord, db, title, ecfdata["ECF_code"]
                    ):
                        continue
                    if not self._store_ecf_data_for_reported_membership_number(
                        aliasrecord, db, title, ecfdata, groups["mno"]
                    ):
                        continue
                    self._copy_ecf_data_to_database(
                        aliasrecord, db, title, ecfdata
                    )
                    continue
                ecfcode = groups["ec"]
                if ecfcode:
                    tokens = list(ecfcode)
                    checkdigit = 0
                    for i in range(6):
                        checkdigit += int(tokens[5 - i]) * (i + 2)
                    if tokens[-1] != "ABCDEFGHJKL"[checkdigit % 11]:
                        tkinter.messagebox.showinfo(
                            parent=self.get_widget(),
                            message="".join(
                                (
                                    ecfcode,
                                    " for\n",
                                    aliasrecord.value.name,
                                    "\ndoes not have the correct check ",
                                    "character for the six digits so cannot ",
                                    "be an ECF Grading Code",
                                )
                            ),
                            title=title,
                        )
                        continue
                    if self._is_reported_ecf_code_on_database(
                        aliasrecord, db, title, ecfcode
                    ):
                        continue
                    ecfdata = self._ecf_data_for_reported_ecf_code(
                        aliasrecord, db, title, ecfcode
                    )
                    if ecfdata is None:
                        continue
                    if not self._store_ecf_data_for_reported_ecf_code(
                        aliasrecord, db, title, ecfdata, ecfcode
                    ):
                        continue
                    self._copy_ecf_data_to_database(
                        aliasrecord, db, title, ecfdata
                    )
                    continue

    def _is_reported_ecf_code_on_database(
        self, aliasrecord, db, title, reported_ecf_code
    ):
        """Attempt to find reported ECF code on database."""
        ecfrec = ecfrecord.get_ecf_player_for_grading_code(
            db, reported_ecf_code
        )
        if ecfrec is None:
            return False
        ecfmaprec = ecfmaprecord.get_person_for_grading_code(
            db, reported_ecf_code
        )
        if ecfmaprec:
            # Perhaps ask if the merge should be done?
            playerrecord = resultsrecord.get_alias(
                db, ecfmaprec.value.playerkey
            )

            # Attribute alias can be None, but not for a valid playerrecord.
            aliases = len(playerrecord.value.alias)

            eventrecord = resultsrecord.get_event(db, playerrecord.value.event)
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Reported ECF code ",
                        reported_ecf_code,
                        " for\n",
                        aliasrecord.value.name,
                        "\nis already linked to\n",
                        playerrecord.value.name,
                        "\nin\n",
                        eventrecord.value.name,
                        "\nfrom ",
                        eventrecord.value.startdate,
                        " to ",
                        eventrecord.value.enddate,
                        "\nwith ",
                        str(aliases),
                        " other events.\n\nUse 'Merge' to extend ",
                        "this link if reported code is correct.",
                    )
                ),
                title=title,
            )
            return True
        eventrecord = resultsrecord.get_event(db, aliasrecord.value.event)
        tkinter.messagebox.showinfo(
            parent=self.get_widget(),
            message="".join(
                (
                    "ECF code ",
                    reported_ecf_code,
                    " for\n\n",
                    ecfrec.value.ECFname,
                    "\n\nis not linked to any player.\n\n",
                    aliasrecord.value.name,
                    "\n\nreported in\n",
                    eventrecord.value.name,
                    "\nfrom ",
                    eventrecord.value.startdate,
                    " to ",
                    eventrecord.value.enddate,
                    "\n\ncan be linked to this ECF code when presented ",
                    "on the Grading Codes tab.",
                )
            ),
            title=title,
        )
        return True

    def _ecf_data_for_reported_membership_number(
        self, aliasrecord, db, title, reported_code
    ):
        """Attempt to download ECF code for reported membership number."""
        return self._get_ecf_data_for_reported_code(
            aliasrecord,
            db,
            title,
            reported_code,
            constants.MEMBER_INFO_URL,
            "".join(("ME", reported_code)),
        )

    def _ecf_data_for_reported_ecf_code(
        self, aliasrecord, db, title, reported_code
    ):
        """Attempt to download ECF code for reported ecf code."""
        return self._get_ecf_data_for_reported_code(
            aliasrecord,
            db,
            title,
            reported_code,
            constants.PLAYER_INFO_URL,
            reported_code[:6],
        )

    def _get_ecf_data_for_reported_code(
        self, aliasrecord, db, title, reported_code, url_name, request_value
    ):
        """Attempt to download ECF data for reported code."""
        urlname = get_configuration_item(
            os.path.expanduser(os.path.join("~", constants.RESULTS_CONF)),
            url_name,
            constants.DEFAULT_URLS,
        )
        try:
            url = urllib.request.urlopen("".join((urlname, request_value)))
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title=title,
                message="".join(
                    (
                        "Exception raised trying to open URL to ",
                        "fetch\n",
                        reported_code,
                        " for\n",
                        aliasrecord.value.name,
                        ".\n\n",
                        str(exc),
                    )
                ),
            )
            return None
        try:
            urldata = url.read()
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title=title,
                message="".join(
                    (
                        "Exception raised trying to read data ",
                        "from URL for\n",
                        reported_code,
                        " for\n",
                        aliasrecord.value.name,
                        "\n\n",
                        str(exc),
                    )
                ),
            )
            return None
        try:
            return json.loads(urldata)
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title=title,
                message="".join(
                    (
                        "Exception raised trying to access data ",
                        "returned from URL for\n",
                        reported_code,
                        " for\n",
                        aliasrecord.value.name,
                        "\n\n",
                        str(exc),
                    )
                ),
            )
            return None

    def _store_ecf_data_for_reported_membership_number(
        self, aliasrecord, db, title, ecfdata, reportedcode
    ):
        """Confirm ECF data for membership number is stored on database."""
        if not tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="".join(
                (
                    "The reported membership number refers to ",
                    "ECF code and name\n\n",
                    ecfdata["ECF_code"],
                    "\n",
                    ecfdata["full_name"],
                    "\n\nThe reported name and membership number are\n\n",
                    aliasrecord.value.name,
                    "\n",
                    reportedcode,
                    "\n\nShould ECF data be added to database?",
                )
            ),
            title=title,
        ):
            return False
        return True

    def _store_ecf_data_for_reported_ecf_code(
        self, aliasrecord, db, title, ecfdata, reportedcode
    ):
        """Confirm ECF data for ECF code is stored on database."""
        if not tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="".join(
                (
                    "ECF code  ",
                    ecfdata["ECF_code"],
                    "\nECF name  ",
                    ecfdata["full_name"],
                    "\n\nReported name  ",
                    aliasrecord.value.name,
                    "\nReported ECF code  ",
                    reportedcode,
                    "\n\nShould ECF data be added to database?",
                )
            ),
            title=title,
        ):
            return False
        return True

    def _copy_ecf_data_to_database(self, aliasrecord, db, title, ecfdata):
        """Copy ECF code and player name downloaded from ECF to database."""
        try:
            copy_single_ecf_players_post_2020_rules(db, ecfdata)
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title=title,
                message="".join(
                    (
                        "Exception raised trying to save data ",
                        "returned from URL for\n",
                        reported_code,
                        " for\n",
                        aliasrecord.value.name,
                        "\non database.\n\n",
                        str(exc),
                    )
                ),
            )

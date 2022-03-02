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
from ..core.players_html import PlayersHTML, PlayersHTMLTooManyECFCodes


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
            self._download_player_ecf_code(
                aliasrecord,
                db,
                title,
                reportedcodes=reportedcodes,
            )

    def _download_player_ecf_code(
        self, aliasrecord, db, title, reportedcodes=None
    ):
        """Attempt to download ECF code for aliasrecord player."""
        if reportedcodes is None:
            reportedcodes = set()
        for rc in aliasrecord.value.reported_codes:
            if rc in reportedcodes:
                continue
            reportedcodes.add(rc)

            # The regular expression prevents malformed ECF codes with
            # an invalid check digit being treated as ECF membership
            # numbers.  However a 12 digit numberic code is treated as
            # two ECF membership numbers, for example.
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
                    ecfcode = None
                    urlname = get_configuration_item(
                        os.path.join(
                            db.home_directory,
                            os.path.basename(db.home_directory).join(
                                (constants.URL_NAMES, ".txt")
                            ),
                        ),
                        constants.PLAYER_SEARCH_URL,
                        constants.DEFAULT_URLS,
                    )
                    try:
                        url = urllib.request.urlopen(
                            "".join((urlname, groups["mno"]))
                        )
                    except Exception as exc:
                        tkinter.messagebox.showinfo(
                            parent=self.get_widget(),
                            title=title,
                            message="".join(
                                (
                                    "Exception raised trying to open URL ",
                                    "to fetch ",
                                    groups["mno"],
                                    ".\n\n",
                                    str(exc),
                                )
                            ),
                        )
                        continue
                    try:
                        urldata = url.read()
                    except Exception as exc:
                        tkinter.messagebox.showinfo(
                            parent=self.get_widget(),
                            title=title,
                            message="".join(
                                (
                                    "Exception raised trying to read URL\n\n",
                                    str(exc),
                                )
                            ),
                        )
                        continue
                    parser = PlayersHTML(groups["mno"])
                    parser.feed(urldata.decode())
                    try:
                        ecfcode = parser.get_ecf_code()
                    except PlayersHTMLTooManyECFCodes as error:
                        tkinter.messagebox.showinfo(
                            parent=self.get_widget(),
                            message=str(error),
                            title=title,
                        )
                        continue
                    if ecfcode is None:
                        tkinter.messagebox.showinfo(
                            parent=self.get_widget(),
                            message=" ".join(
                                (
                                    "No ECF code found for membership number",
                                    groups["mno"],
                                )
                            ),
                            title=title,
                        )
                        continue
                else:
                    ecfcode = groups["ec"]
                ecfrec = ecfrecord.get_ecf_player_for_grading_code(db, ecfcode)
                if ecfrec is None:
                    ecfname = None
                    ecfmerge = None
                    # Cannot download record from ECF yet.
                    # If ecfname remains None it should mean the player
                    # needs a new ECF code.
                    tokens = list(ecfcode)
                    checkdigit = 0
                    for i in range(6):
                        checkdigit += int(tokens[5 - i]) * (i + 2)
                    if tokens[-1] != "ABCDEFGHJKL"[checkdigit % 11]:
                        tkinter.messagebox.showinfo(
                            parent=self.get_widget(),
                            message=" ".join(
                                (
                                    ecfcode,
                                    "does not have the correct check",
                                    "character for the six digits so cannot",
                                    "be an ECF Grading Code",
                                )
                            ),
                            title=title,
                        )
                        continue
                    urlname = get_configuration_item(
                        os.path.join(
                            db.home_directory,
                            os.path.basename(db.home_directory).join(
                                (constants.URL_NAMES, ".txt")
                            ),
                        ),
                        constants.PLAYER_INFO_URL,
                        constants.DEFAULT_URLS,
                    )
                    try:
                        url = urllib.request.urlopen(
                            "".join((urlname, ecfcode[:6]))
                        )
                    except Exception as exc:
                        tkinter.messagebox.showinfo(
                            parent=self.get_widget(),
                            title=title,
                            message="".join(
                                (
                                    "Exception raised trying to open URL to ",
                                    "fetch ",
                                    ecfcode,
                                    ".\n\n",
                                    str(exc),
                                )
                            ),
                        )
                        continue
                    try:
                        urldata = url.read()
                    except Exception as exc:
                        tkinter.messagebox.showinfo(
                            parent=self.get_widget(),
                            title=title,
                            message="".join(
                                (
                                    "Exception raised trying to read URL\n\n",
                                    str(exc),
                                )
                            ),
                        )
                        continue
                    if groups["mno"]:
                        mem_no_rep = " ".join(
                            ("\nReported membership number", groups["mno"])
                        )
                    else:
                        mem_no_rep = ""
                    ecfdata = json.loads(urldata)
                    if not tkinter.messagebox.askyesno(
                        parent=self.get_widget(),
                        message="".join(
                            (
                                "ECF code  ",
                                ecfdata["ECF_code"],
                                "\nECF name  ",
                                ecfdata["full_name"],
                                "\nReported name  ",
                                aliasrecord.value.name,
                                mem_no_rep,
                                "\n\nShould ECF code be stored?",
                            )
                        ),
                        title=title,
                    ):
                        continue
                    try:
                        copy_single_ecf_players_post_2020_rules(db, ecfdata)
                    except Exception as exc:
                        tkinter.messagebox.showinfo(
                            parent=self.get_widget(),
                            title=title,
                            message="".join(
                                (
                                    "Exception raised trying to extract ",
                                    "grading code from URL\n\n",
                                    str(exc),
                                )
                            ),
                        )
                        continue
                    continue
                else:
                    ecfname = ecfrec.value.ECFname
                    ecfmerge = ecfrec.value.ECFmerge
                ecfmaprec = ecfmaprecord.get_person_for_grading_code(
                    db, ecfcode
                )
                if ecfmaprec:
                    # Perhaps ask if the merge should be done?
                    playerrecord = resultsrecord.get_alias(
                        db, ecfmaprec.value.playerkey
                    )
                    try:
                        aliases = len(playerrecord.value.alias)
                    except:
                        aliases = 0
                    playername = playerrecord.value.name
                    eventrecord = resultsrecord.get_event(
                        db, playerrecord.value.event
                    )
                    eventname = eventrecord.value.name
                    eventstart = eventrecord.value.startdate
                    eventend = eventrecord.value.enddate
                    tkinter.messagebox.showinfo(
                        parent=self.get_widget(),
                        message="".join(
                            (
                                "ECF code ",
                                ecfcode,
                                " is already linked to\n",
                                playername,
                                "\nin\n",
                                eventname,
                                "\nfrom ",
                                eventstart,
                                " to ",
                                eventend,
                                "\nwith ",
                                str(aliases),
                                " other events.\n\nUse 'Merge' to extend ",
                                "this link if reported code is correct.",
                            )
                        ),
                        title=title,
                    )
                    continue
                playername = aliasrecord.value.name
                eventrecord = resultsrecord.get_event(
                    db, aliasrecord.value.event
                )
                eventname = eventrecord.value.name
                eventstart = eventrecord.value.startdate
                eventend = eventrecord.value.enddate
                if ecfname is None:
                    tkinter.messagebox.showinfo(
                        parent=self.get_widget(),
                        message="".join(
                            (
                                "ECF code ",
                                ecfcode,
                                " does not exist.\n",
                                playername,
                                "\nin\n",
                                eventname,
                                "\nfrom ",
                                eventstart,
                                " to ",
                                eventend,
                                "\nshould be allocated an ECF code without ",
                                "relying on the reported code ",
                                ecfcode,
                                ".",
                            )
                        ),
                        title=title,
                    )
                else:
                    tkinter.messagebox.showinfo(
                        parent=self.get_widget(),
                        message="".join(
                            (
                                "ECF code ",
                                ecfcode,
                                " for\n\n",
                                ecfname,
                                "\n\nis not linked to any player.\n\n",
                                playername,
                                "\n\nreported in\n",
                                eventname,
                                "\nfrom ",
                                eventstart,
                                " to ",
                                eventend,
                                "\ncan be linked using the reported code ",
                                ecfcode,
                                " if the two names are consistent.",
                            )
                        ),
                        title=title,
                    )

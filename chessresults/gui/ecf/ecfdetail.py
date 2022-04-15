# ecfdetail.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Dialogue for updating ECF grading code and ECF version of player's name.
"""

import tkinter
import tkinter.messagebox
import json
import urllib.request
import os

from solentware_misc.gui.exceptionhandler import ExceptionHandler, FOCUS_ERROR
from solentware_misc.core.getconfigurationitem import get_configuration_item

from ...core import (
    resultsrecord,
    constants,
    configuration,
)
from ...core.ecf import (
    ecfrecord,
    ecfmaprecord,
)
from ...basecore import ecfdataimport


class ECFDetailDialog(ExceptionHandler):

    """Dialogue to display locally entered ECF details for player.

    Update methods are defined but do not change database.  Subclasses must
    override as needed.

    """

    def __init__(
        self, parent, title, header, items, edititems, cnf=dict(), **kargs
    ):
        """Create dialogue to display locally entered ECF detail for player."""

        super(ECFDetailDialog, self).__init__()
        self.edit_ctrl = []
        self.yes = False
        self.dialog = tkinter.Toplevel(master=parent)
        self.restore_focus = self.dialog.focus_get()
        self.dialog.wm_title(title)
        self.header = tkinter.Label(master=self.dialog, text=header)
        self.buttons_frame = tkinter.Frame(master=self.dialog)
        self.buttons_frame.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        buttonrow = self.buttons_frame.pack_info()["side"] in ("top", "bottom")
        for i, b in enumerate(
            (
                (
                    "Cancel",
                    "Quit edit without updating database",
                    True,
                    0,
                    self.on_cancel,
                ),
                (
                    "Update",
                    "Apply edit to database and quit",
                    True,
                    0,
                    self.on_update,
                ),
            )
        ):
            button = tkinter.Button(
                master=self.buttons_frame,
                text=b[0],
                underline=b[3],
                command=self.try_command(b[4], self.buttons_frame),
            )
            if buttonrow:
                self.buttons_frame.grid_columnconfigure(i * 2, weight=1)
                button.grid_configure(column=i * 2 + 1, row=0)
            else:
                self.buttons_frame.grid_rowconfigure(i * 2, weight=1)
                button.grid_configure(row=i * 2 + 1, column=0)
        if buttonrow:
            self.buttons_frame.grid_columnconfigure(len(b * 2), weight=1)
        else:
            self.buttons_frame.grid_rowconfigure(len(b * 2), weight=1)

        self.header.pack(side=tkinter.TOP, fill=tkinter.X)

        self.edit_frame = tkinter.Frame(master=self.dialog)
        self.edit_frame.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        for c in range(2):
            self.edit_frame.grid_columnconfigure(
                c, uniform="col", weight=c + 1
            )
        for r, item in enumerate(items):
            st, tc = item
            st_ctrl = tkinter.Label(master=self.edit_frame, text=st)
            tc_ctrl = tkinter.Label(master=self.edit_frame, text=tc)
            self.edit_frame.grid_rowconfigure(r, uniform="row", weight=1)
            st_ctrl.grid(row=r, column=0, sticky=tkinter.E)
            tc_ctrl.grid(row=r, column=1, sticky=tkinter.W)

        for r, item in enumerate(edititems):
            st, tc = item
            st_ctrl = tkinter.Label(master=self.edit_frame, text=st)
            te_ctrl = tkinter.Entry(master=self.edit_frame)
            te_ctrl.delete(0, tkinter.END)
            te_ctrl.insert(tkinter.END, tc)
            re = r + len(items)
            self.edit_frame.grid_rowconfigure(re, uniform="row", weight=2)
            st_ctrl.grid(row=re, column=0, sticky=tkinter.E)
            te_ctrl.grid(row=re, column=1, sticky=tkinter.EW)
            self.edit_ctrl.append(te_ctrl)

        self.dialog.wait_visibility()
        self.dialog.grab_set()
        self.dialog.wait_window()

    def is_yes(self):
        """Return True if tkMessageBox.askyesno closed by clicking Yes."""
        return self.yes

    def on_cancel(self, event=None):
        """Show dialogue to confirm cancellation of edit."""
        if tkinter.messagebox.askyesno(
            parent=self.dialog,
            message="Confirm cancellation of edit",
            title="ECF detail Edit",
        ):
            self.dialog.destroy()

    def on_update(self, event=None):
        """Show dialogue to confirm application of edit.

        Subclass must override this method.

        """
        if tkinter.messagebox.askyesno(
            parent=self.dialog,
            message="Confirm application of edit",
            title="ECF detail Edit",
        ):
            self.dialog.destroy()
            self.set_yes()

    def set_yes(self):
        """Set state such that is_yes() call returns True."""
        self.yes = True

    def __del__(self):
        """Restore focus to widget with focus before modal interaction."""
        try:
            # restore focus on dismissing dialogue
            self.restore_focus.focus_set()
        except tkinter._tkinter.TclError as error:
            # application destroyed while confirm dialogue exists
            if str(error) != FOCUS_ERROR:
                raise


class ECFClubDialog(ECFDetailDialog):

    """Dialogue to amend locally entered ECF club details for player.

    A club record must exist on the Central Grading Database before the club
    code can be used in result submission files.  But an ECF club file with
    this club code may not be available for some time afterwards.  This
    dialogue allows the club code to be used until then.  If applied an ECF
    results feedback file will update the ECF references so that the club code
    can be used normally.

    This dialogue cannot be used to inform ECF about a new club.

    """

    def __init__(self, parent, record, cnf=dict(), **kargs):
        """Extend, allow update of ECF formatted player name."""
        self.record = record
        if record.value.clubecfname is None:
            ecfname = ""
        else:
            ecfname = record.value.clubecfname
        if record.value.clubecfcode is None:
            ecfcode = ""
        else:
            ecfcode = record.value.clubecfcode
        items = (
            (
                "Name:",
                resultsrecord.get_player_name_text(
                    record.database, record.value.get_unpacked_playername()
                ),
            ),
            ("ECF Club Name:", ecfname),
            ("Club Code:", ecfcode),
        )
        edititems = (
            ("Edit ECF Club Name", ecfname),
            ("Edit ECF Club Code", ecfcode),
        )

        super(ECFClubDialog, self).__init__(
            parent,
            "ECF club detail Edit",
            "Edit ECF club detail for Player",
            items,
            edititems,
            cnf=cnf,
            **kargs
        )

    def on_update(self, event=None):
        """Validate and apply update to ECF club detail for player."""
        clubname = self.edit_ctrl[0].get()
        clubcode = self.edit_ctrl[1].get()
        if len(clubname) == 0:
            if len(clubcode) == 0:
                if tkinter.messagebox.askyesno(
                    parent=self.dialog,
                    message="".join(
                        (
                            "Neither club name nor club code specified.\n\n",
                            "Confirm ECF club details for player to be deleted.",
                        )
                    ),
                    title="ECF club detail Edit",
                ):
                    newrecord = self.record.clone()
                    newrecord.value.clubecfname = None
                    newrecord.value.clubecfcode = None
                    self.record.database.start_transaction()
                    self.record.edit_record(
                        self.record.database,
                        self.record.dbname,
                        self.record.dbname,
                        newrecord,
                    )
                    self.record.database.commit()
                    self.set_yes()
                    self.dialog.destroy()
                return
        if len(clubcode) != 4:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                message="".join(
                    ("ECF club code (", clubcode, ") must be 4 characters.")
                ),
                title="ECF club detail Edit",
            )
            return
        if len(clubname) == 0:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                message="ECF club name must be specified.",
                title="ECF club detail Edit",
            )
            return
        if len(clubname) > 40:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                message="".join(
                    (
                        "ECF club name (",
                        clubname,
                        ") must be 1 to 40 characters.",
                    )
                ),
                title="ECF club detail Edit",
            )
            return
        ecfclub = ecfrecord.get_ecf_club_for_club_code(
            self.record.database, clubcode
        )
        if ecfclub:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                message="".join(
                    (
                        "ECF club code (",
                        clubcode,
                        ") already exists on ECF club file for:\n",
                        ecfclub.value.ECFname,
                        '\n\nUse "Affiliate" to select this club or change the ',
                        "club code entered.",
                    )
                ),
                title="ECF club detail Edit",
            )
            return
        if tkinter.messagebox.askyesno(
            parent=self.dialog,
            message="".join(
                (
                    "Confirm change ECF club code to:\n",
                    clubcode,
                    "\n\nand ECF club name to:\n",
                    clubname,
                    "\n",
                )
            ),
            title="ECF club detail Edit",
        ):
            newrecord = self.record.clone()
            newrecord.value.clubecfname = clubname
            newrecord.value.clubecfcode = clubcode
            self.record.database.start_transaction()
            self.record.edit_record(
                self.record.database,
                self.record.dbname,
                self.record.dbname,
                newrecord,
            )
            self.record.database.commit()
            self.set_yes()
            self.dialog.destroy()


class ECFNameDialog(ECFDetailDialog):

    """Dialogue to amend locally entered ECF formatted name for player."""

    def __init__(self, parent, record, cnf=dict(), **kargs):
        """Extend, allow update of ECF formatted player name."""
        self.record = record
        if record.value.playerecfname is None:
            ecfname = ""
        else:
            ecfname = record.value.playerecfname
        if record.value.playerecfcode is None:
            ecfcode = ""
        else:
            ecfcode = record.value.playerecfcode
        items = (
            (
                "Name:",
                resultsrecord.get_player_name_text(
                    record.database, record.value.get_unpacked_playername()
                ),
            ),
            ("ECF Name:", ecfname),
            ("Grading Code:", ecfcode),
        )
        edititems = (("Edit ECF Name", ecfname),)

        super(ECFNameDialog, self).__init__(
            parent,
            "ECF detail Edit",
            "Edit ECF name for New Player",
            items,
            edititems,
            cnf=cnf,
            **kargs
        )

    def on_update(self, event=None):
        """Validate and apply update to ECF formatted player name."""
        text = self.edit_ctrl[0].get()
        if "," in text:
            tokens = text.split(",", 1)
            tokens[1:1] = ", "
            text = "".join(tokens)
        tokens = text.split()
        text = " ".join(tokens)
        if len(text) == 0:
            if self.record.value.playerecfname:
                if tkinter.messagebox.askyesno(
                    parent=self.dialog,
                    message="Confirm ECF version of new player name to be deleted",
                    title="ECF detail Edit",
                ):
                    newrecord = self.record.clone()
                    newrecord.value.playerecfname = None
                    self.record.database.start_transaction()
                    self.record.edit_record(
                        self.record.database,
                        self.record.dbname,
                        self.record.dbname,
                        newrecord,
                    )
                    self.record.database.commit()
                    self.set_yes()
                    self.dialog.destroy()
            else:
                dlg = tkinter.messagebox.showinfo(
                    parent=self.dialog,
                    message="No name specified",
                    title="ECF detail Edit",
                )
            return
        onecase = text.isupper() or text.islower()
        if onecase:
            tokens = [t.title() for t in tokens]
        else:

            def charcase(t):
                if len(t) == 1:
                    return t.upper()
                else:
                    return t

            tokens = [charcase(t) for t in tokens]
        ecfname = " ".join(tokens)
        if len(ecfname) > 60:
            dlg = tkinter.messagebox.showinfo(
                parent=self.dialog,
                message=" ".join(
                    (ecfname, "is too long for ECF version of name (max 60)")
                ),
                title="ECF detail Edit",
            )
            return
        if tkinter.messagebox.askyesno(
            parent=self.dialog,
            message=" ".join(
                (
                    "Confirm ECF version of new player name to be changed to",
                    ecfname,
                )
            ),
            title="ECF detail Edit",
        ):
            newrecord = self.record.clone()
            newrecord.value.playerecfname = ecfname
            self.record.database.start_transaction()
            self.record.edit_record(
                self.record.database,
                self.record.dbname,
                self.record.dbname,
                newrecord,
            )
            self.record.database.commit()
            self.set_yes()
            self.dialog.destroy()


class ECFGradingCodeDialog(ECFDetailDialog):

    """Dialogue to amend locally entered ECF grading code for player."""

    def __init__(self, parent, record, cnf=dict(), **kargs):
        """Extend, allow update of ECF grading code for player."""
        self.record = record
        if record.value.playerecfname is None:
            ecfname = ""
        else:
            ecfname = record.value.playerecfname
        if record.value.playerecfcode is None:
            ecfcode = ""
        else:
            ecfcode = record.value.playerecfcode
        items = (
            (
                "Name:",
                resultsrecord.get_player_name_text(
                    record.database, record.value.get_unpacked_playername()
                ),
            ),
            ("ECF Name:", ecfname),
            ("Grading Code:", ecfcode),
        )
        edititems = (("Edit Grading Code", ecfcode),)

        super(ECFGradingCodeDialog, self).__init__(
            parent,
            "ECF detail Edit",
            "Edit Grading Code for New Player",
            items,
            edititems,
            cnf=cnf,
            **kargs
        )

    def on_update(self, event=None):
        """Validate and apply update to ECF grading code for player."""
        ecfcode = "".join(self.edit_ctrl[0].get().strip().split())

        if len(ecfcode) == 0:
            if self.record.value.playerecfcode:
                if tkinter.messagebox.askyesno(
                    parent=self.dialog,
                    message="Confirm Grading Code for new player to be deleted",
                    title="ECF detail Edit",
                ):
                    newrecord = self.record.clone()
                    newrecord.value.playerecfcode = None
                    self.record.database.start_transaction()
                    self.record.edit_record(
                        self.record.database,
                        self.record.dbname,
                        self.record.dbname,
                        newrecord,
                    )
                    self.record.database.commit()
                    self.set_yes()
                    self.dialog.destroy()
                return

        if len(ecfcode) != 7:
            dlg = tkinter.messagebox.showinfo(
                parent=self.dialog,
                message=" ".join(
                    (
                        ecfcode,
                        "is not 7 characters so cannot be an ECF Grading Code",
                    )
                ),
                title="ECF detail Edit",
            )
            return
        tokens = list(ecfcode)
        checkdigit = 0
        for i in range(6):
            if not tokens[i].isdigit():
                dlg = tkinter.messagebox.showinfo(
                    parent=self.dialog,
                    message=" ".join(
                        (
                            ecfcode,
                            "is not 6 digits followed by a check",
                            "character so cannot be an ECF Grading Code",
                        )
                    ),
                    title="ECF detail Edit",
                )
                return
            checkdigit += int(tokens[5 - i]) * (i + 2)
        if tokens[-1] != "ABCDEFGHJKL"[checkdigit % 11]:
            dlg = tkinter.messagebox.showinfo(
                parent=self.dialog,
                message=" ".join(
                    (
                        ecfcode,
                        "does not have the correct check character for the",
                        "six digits so cannot be an ECF Grading Code",
                    )
                ),
                title="ECF detail Edit",
            )
            return
        ecfplayer = ecfrecord.get_ecf_player_for_grading_code(
            self.record.database, ecfcode
        )
        if ecfplayer is not None:
            if not ecfplayer.value.ECFactive:
                mapperson = ecfmaprecord.get_person_for_grading_code(
                    self.record.database, ecfcode
                )
                if mapperson is not None:
                    dlg = tkinter.messagebox.showinfo(
                        parent=self.dialog,
                        message=" ".join(
                            (
                                ecfcode,
                                "is already specified as the ECF Grading",
                                "Code for",
                                "".join(
                                    (
                                        mapperson.value.playername.split(
                                            "\t", 1
                                        )[0],
                                        ".",
                                    )
                                ),
                                "If the Grading Code is correct for the new",
                                "player then the existing player on the master",
                                "list should not have this grading code or these",
                                "should be the same person.",
                            )
                        ),
                        title="ECF detail Edit",
                    )
                else:
                    if tkinter.messagebox.askyesno(
                        parent=self.dialog,
                        message=" ".join(
                            (
                                "Confirm Grading Code of new player is",
                                "".join((ecfcode, ".\n\n")),
                                "This grading code is on an old master list for",
                                "".join((ecfplayer.value.ECFname, ".")),
                            )
                        ),
                        title="ECF detail Edit",
                    ):
                        newrecord = self.record.clone()
                        newrecord.value.playerecfcode = None
                        newrecord.value.playerecfname = None
                        newrecord.value.playercode = ecfcode
                        self.record.database.start_transaction()
                        self.record.edit_record(
                            self.record.database,
                            self.record.dbname,
                            self.record.dbname,
                            newrecord,
                        )
                        self.record.database.commit()
                        self.set_yes()
                        self.dialog.destroy()
                return
            dlg = tkinter.messagebox.showinfo(
                parent=self.dialog,
                message=" ".join(
                    (
                        ecfcode,
                        "is already on the master list as the ECF Grading",
                        "Code for",
                        "".join((ecfplayer.value.ECFname, ".")),
                        "If the Grading Code is correct for the new player then",
                        "the existing player on the master list should not have",
                        "this grading code or these should be the same person.",
                    )
                ),
                title="ECF detail Edit",
            )
            return

        mapplayer = ecfmaprecord.get_new_person_for_grading_code(
            self.record.database, ecfcode
        )
        if mapplayer is not None:
            if self.record.value.playername != mapplayer.value.playername:
                dlg = tkinter.messagebox.showinfo(
                    parent=self.dialog,
                    message=" ".join(
                        (
                            ecfcode,
                            "is already specified as the ECF Grading",
                            "Code for",
                            "".join(
                                (
                                    mapplayer.value.playerecfname,
                                    " (another new player).",
                                )
                            ),
                            "If the Grading Code is correct for",
                            self.record.value.playerecfname,
                            "then the other person should not have this grading",
                            "code or these should be the same person.",
                        )
                    ),
                    title="ECF detail Edit",
                )
                return

        if tkinter.messagebox.askyesno(
            parent=self.dialog,
            message=" ".join(
                (
                    "Confirm Grading Code of new player to be changed to",
                    ecfcode,
                )
            ),
            title="ECF detail Edit",
        ):
            newrecord = self.record.clone()
            newrecord.value.playerecfcode = ecfcode
            self.record.database.start_transaction()
            self.record.edit_record(
                self.record.database,
                self.record.dbname,
                self.record.dbname,
                newrecord,
            )
            self.record.database.commit()
            self.set_yes()
            self.dialog.destroy()


class ECFDownloadGradingCodeDialog(ECFDetailDialog):

    """Dialogue to download ECF grading code for player."""

    def __init__(self, parent, database, cnf=dict(), **kargs):
        """Extend, allow download of ECF grading code."""
        self.database = database
        items = ()
        edititems = (
            ("Download ECF Grading Code", ""),
            (
                "URL",
                get_configuration_item(
                    configuration.Configuration().get_configuration_file_name(),
                    constants.PLAYER_INFO_URL,
                    constants.DEFAULT_URLS,
                ),
            ),
        )

        super().__init__(
            parent,
            "ECF Grading Code Download",
            "Download ECF Grading Code from URL",
            items,
            edititems,
            cnf=cnf,
            **kargs
        )

    # Implemented by ecfdataimport.copy_single_ecf_players_post_2020_rules()
    # call, like in ECFDownloadPlayerNameDialog but with different rules to
    # allow call to occur.
    def on_update(self, event=None):
        """Validate and apply download to ECF code list."""
        ecfcode = "".join(self.edit_ctrl[0].get().strip().split())
        urlname = self.edit_ctrl[1].get().strip()
        if len(ecfcode) != 7:
            dlg = tkinter.messagebox.showinfo(
                parent=self.dialog,
                message="".join(
                    (
                        "'",
                        ecfcode,
                        "' is not 7 characters so cannot be an ECF Grading Code",
                    )
                ),
                title="ECF Grading Code Download",
            )
            return
        tokens = list(ecfcode)
        checkdigit = 0
        for i in range(6):
            if not tokens[i].isdigit():
                dlg = tkinter.messagebox.showinfo(
                    parent=self.dialog,
                    message=" ".join(
                        (
                            ecfcode,
                            "is not 6 digits followed by a check",
                            "character so cannot be an ECF Grading Code",
                        )
                    ),
                    title="ECF Grading Code Download",
                )
                return
            checkdigit += int(tokens[5 - i]) * (i + 2)
        if tokens[-1] != "ABCDEFGHJKL"[checkdigit % 11]:
            dlg = tkinter.messagebox.showinfo(
                parent=self.dialog,
                message=" ".join(
                    (
                        ecfcode,
                        "does not have the correct check character for the",
                        "six digits so cannot be an ECF Grading Code",
                    )
                ),
                title="ECF Grading Code Download",
            )
            return
        ecfplayer = ecfrecord.get_ecf_player_for_grading_code(
            self.database, ecfcode
        )
        if ecfplayer is not None:
            dlg = tkinter.messagebox.showinfo(
                parent=self.dialog,
                message="".join(
                    (
                        ecfcode,
                        "\n\nis already on the master list as the ECF Grading ",
                        "Code for\n\n",
                        "".join((ecfplayer.value.ECFname, ".")),
                    )
                ),
                title="ECF Grading Code Download",
            )
            return

        mapplayer = ecfmaprecord.get_new_person_for_grading_code(
            self.database, ecfcode
        )
        if mapplayer is not None:
            dlg = tkinter.messagebox.showinfo(
                parent=self.dialog,
                message="".join(
                    (
                        ecfcode,
                        "\n\nis already specified as the ECF Grading ",
                        "Code for\n\n",
                        "".join(
                            (
                                mapplayer.value.playerecfname,
                                "\n\n(a new player).  ",
                            )
                        ),
                        "Delete the grading code from the new player, download ",
                        "the grading code, and link it to the player.",
                    )
                ),
                title="ECF Grading Code Download",
            )
            return
        try:
            url = urllib.request.urlopen("".join((urlname, ecfcode[:6])))
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                title="ECF Grading Code Download",
                message="".join(
                    ("Exception raised trying to open URL\n\n", str(exc))
                ),
            )
            return
        try:
            urldata = url.read()
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                title="ECF Grading Code Download",
                message="".join(
                    ("Exception raised trying to read URL\n\n", str(exc))
                ),
            )
            return
        try:
            ecfdataimport.copy_single_ecf_players_post_2020_rules(
                self.database, json.loads(urldata)
            )
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                title="ECF Grading Code Download",
                message="".join(
                    (
                        "Exception raised trying to extract grading code ",
                        "from URL\n\n",
                        str(exc),
                    )
                ),
            )
            return
        self.set_yes()
        self.dialog.destroy()
        return


class ECFDownloadPlayerNameDialog(ECFDetailDialog):

    """Dialogue to download ECF name for player."""

    def __init__(self, parent, database, cnf=dict(), **kargs):
        """Extend, allow download of ECF name for existing ECF code."""
        self.database = database
        items = ()
        edititems = (
            ("Download ECF name for ECF code", ""),
            (
                "URL",
                get_configuration_item(
                    configuration.Configuration().get_configuration_file_name(),
                    constants.PLAYER_INFO_URL,
                    constants.DEFAULT_URLS,
                ),
            ),
        )

        super().__init__(
            parent,
            "ECF Player Name Download",
            "Download ECF name for ECF code from URL",
            items,
            edititems,
            cnf=cnf,
            **kargs
        )

    # Implemented by ecfdataimport.copy_single_ecf_players_post_2020_rules()
    # call, like in ECFDownloadGradingCodeDialog but with different rules to
    # allow call to occur.
    def on_update(self, event=None):
        """Validate and apply download to grading code list."""
        ecfcode = "".join(self.edit_ctrl[0].get().strip().split())
        urlname = self.edit_ctrl[1].get().strip()
        if len(ecfcode) != 7:
            dlg = tkinter.messagebox.showinfo(
                parent=self.dialog,
                message="".join(
                    (
                        "'",
                        ecfcode,
                        "' is not 7 characters so cannot be an ECF Grading Code",
                    )
                ),
                title="ECF Player Name Download",
            )
            return
        tokens = list(ecfcode)
        checkdigit = 0
        for i in range(6):
            if not tokens[i].isdigit():
                dlg = tkinter.messagebox.showinfo(
                    parent=self.dialog,
                    message=" ".join(
                        (
                            ecfcode,
                            "is not 6 digits followed by a check",
                            "character so cannot be an ECF Grading Code",
                        )
                    ),
                    title="ECF Player Name Download",
                )
                return
            checkdigit += int(tokens[5 - i]) * (i + 2)
        if tokens[-1] != "ABCDEFGHJKL"[checkdigit % 11]:
            dlg = tkinter.messagebox.showinfo(
                parent=self.dialog,
                message=" ".join(
                    (
                        ecfcode,
                        "does not have the correct check character for the",
                        "six digits so cannot be an ECF Grading Code",
                    )
                ),
                title="ECF Player Name Download",
            )
            return
        ecfplayer = ecfrecord.get_ecf_player_for_grading_code(
            self.database, ecfcode
        )
        if ecfplayer is None:
            dlg = tkinter.messagebox.showinfo(
                parent=self.dialog,
                message="".join(
                    (
                        ecfcode,
                        "\n\nis not on the master list.\n\n",
                        "Use 'Download ECF Code' instead.",
                    )
                ),
                title="ECF Player Name Download",
            )
            return

        mapplayer = ecfmaprecord.get_new_person_for_grading_code(
            self.database, ecfcode
        )
        if mapplayer is not None:
            dlg = tkinter.messagebox.showinfo(
                parent=self.dialog,
                message="".join(
                    (
                        ecfcode,
                        "\n\nis already specified as the ECF Grading ",
                        "Code for\n\n",
                        "".join(
                            (
                                mapplayer.value.playerecfname,
                                "\n\n(a new player).  ",
                            )
                        ),
                        "Delete the grading code from the new player, download ",
                        "the grading code, and link it to the player.",
                    )
                ),
                title="ECF Player Name Download",
            )
            return
        try:
            url = urllib.request.urlopen("".join((urlname, ecfcode[:6])))
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                title="ECF Player Name Download",
                message="".join(
                    ("Exception raised trying to open URL\n\n", str(exc))
                ),
            )
            return
        try:
            urldata = url.read()
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                title="ECF Player Name Download",
                message="".join(
                    ("Exception raised trying to read URL\n\n", str(exc))
                ),
            )
            return
        try:
            ecfdataimport.copy_single_ecf_players_post_2020_rules(
                self.database, json.loads(urldata)
            )
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                title="ECF Player Name Download",
                message="".join(
                    (
                        "Exception raised trying to extract grading code ",
                        "from URL\n\n",
                        str(exc),
                    )
                ),
            )
            return
        self.set_yes()
        self.dialog.destroy()
        return


class ECFDownloadClubCodeDialog(ECFDetailDialog):

    """Dialogue to download ECF club code."""

    def __init__(self, parent, database, cnf=dict(), **kargs):
        """Extend, allow download of ECF club code."""
        self.database = database
        items = ()
        edititems = (
            ("Download ECF Club Code", ""),
            (
                "URL",
                get_configuration_item(
                    configuration.Configuration().get_configuration_file_name(),
                    constants.CLUB_INFO_URL,
                    constants.DEFAULT_URLS,
                ),
            ),
        )

        super().__init__(
            parent,
            "ECF Club Code Download",
            "Download ECF Club Code from URL",
            items,
            edititems,
            cnf=cnf,
            **kargs
        )

    def on_update(self, event=None):
        """Validate and apply download to club code list and player."""
        clubcode = self.edit_ctrl[0].get()
        urlname = self.edit_ctrl[1].get().strip()
        if len(clubcode) != 4:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                message="".join(
                    ("ECF club code '", clubcode, "' must be 4 characters.")
                ),
                title="ECF Club Code Download",
            )
            return
        ecfclub = ecfrecord.get_ecf_club_for_club_code(self.database, clubcode)
        if ecfclub:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                message="".join(
                    (
                        "ECF club code '",
                        clubcode,
                        "' already exists on ECF club file for:\n\n",
                        ecfclub.value.ECFname,
                    )
                ),
                title="ECF Club Code Download",
            )
            return
        try:
            url = urllib.request.urlopen("".join((urlname, clubcode)))
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                title="ECF Grading Code Download",
                message="".join(
                    ("Exception raised trying to open URL\n\n", str(exc))
                ),
            )
            return
        try:
            urldata = url.read()
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                title="ECF Grading Code Download",
                message="".join(
                    ("Exception raised trying to read URL\n\n", str(exc))
                ),
            )
            return
        try:
            ecfdataimport.copy_single_ecf_club_post_2020_rules(
                self.database, json.loads(urldata)
            )
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.dialog,
                title="ECF Grading Code Download",
                message="".join(
                    (
                        "Exception raised trying to extract grading code ",
                        "from URL\n\n",
                        str(exc),
                    )
                ),
            )
            return
        self.set_yes()
        self.dialog.destroy()
        return

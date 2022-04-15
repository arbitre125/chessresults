# feedback_monthly.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ECF results feedback database update class.

Display a feedback document from ECF alongside the grading code updates
for new players deduced from the content.  The selected updates are applied
to the database.

"""

import tkinter
import datetime
import re
import email
import os

from solentware_misc.gui import panel
from solentware_misc.gui import textreadonly
from solentware_misc.gui import tasklog

from ...core.ecf import ecfmaprecord
from ...core.ecf import ecfrecord
from ...core.ecf import feedback_html
from ...core import resultsrecord
from ...core import filespec
from ...core import constants
from ...core import configuration

_remove_dates_re = re.compile(r"\d{4}-\d{2}-\d{2}")
_exact_re = re.compile(r"\s+Exact\s+match\s+(\d{6}[A-L])\s*\Z")
_merge_re = re.compile(r"\s+(\d{6}[A-L])\s+was\s+(\d{6}[A-L])\s+")

# The '... Revoke ...' version was expected in response to a 'commit'
# submission, but the '...$' version is returned by the delayed 'check
# and report' submission.  The chance to revoke has long expired.
_match_to_re = re.compile(
    r"\s+Matched\s+to\s+:\s+(\d{6}[A-L])(?:\s+-\s+Revoke\s+|$)"
)

_new_re = re.compile(r"\s+New\s+:\s+(\d{6}[A-L])\s*\Z")
_no_code_re = re.compile(
    r"\s+\d+\s+-\s+Issue:\s+ECFCode\s+not\s+submitted\.\s+"
)
_submission_player_re = re.compile(r"#Name=([^#]*)(?:#|/Z)", flags=re.DOTALL)


class FeedbackMonthly(panel.PlainPanel):

    """The Feedback panel for a Results database with monthly rating emails."""

    _btn_closefeedbackmonthly = "feedback_monthly_close"
    _btn_applyfeedbackmonthly = "feedback_monthly_apply"

    def __init__(self, parent=None, datafile=None, cnf=dict(), **kargs):
        """Extend and define the results database feedback panel."""
        super().__init__(parent=parent, cnf=cnf, **kargs)

        datafilename, feedbacktext = datafile

        self.show_buttons_for_start_import()
        self.create_buttons()

        self.resultsdbfolder = tkinter.Label(master=self.get_widget(), text="")
        self.resultsdbfolder.pack(side=tkinter.TOP, fill=tkinter.X)

        self.datafilepath = tkinter.Label(
            master=self.get_widget(), text=datafilename
        )
        self.datafilepath.pack(side=tkinter.TOP, fill=tkinter.X)

        pw = tkinter.PanedWindow(
            self.get_widget(),
            opaqueresize=tkinter.FALSE,
            orient=tkinter.VERTICAL,
        )
        pw.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.TRUE)

        self.allowapplycodes = None
        self.updateplayers = None
        self.updateclubs = None
        self.newecfcodes = None
        self.mergeecfcodes = None
        toppane = tkinter.PanedWindow(
            master=pw, opaqueresize=tkinter.FALSE, orient=tkinter.HORIZONTAL
        )
        feedbackpane = tkinter.PanedWindow(
            master=toppane, opaqueresize=tkinter.FALSE, orient=tkinter.VERTICAL
        )
        applypane = tkinter.PanedWindow(
            master=toppane, opaqueresize=tkinter.FALSE, orient=tkinter.VERTICAL
        )
        fbf, feedbackctrl = textreadonly.make_scrolling_text_readonly(
            master=feedbackpane, wrap=tkinter.WORD, undo=tkinter.FALSE
        )
        af, self.applyctrl = textreadonly.make_scrolling_text_readonly(
            master=applypane, wrap=tkinter.WORD, undo=tkinter.FALSE
        )
        applypane.add(af)
        feedbackpane.add(fbf)
        toppane.add(feedbackpane)
        toppane.add(applypane)
        pw.paneconfigure(toppane, stretch=tkinter.FIRST)

        rf = tkinter.Frame(master=pw)
        self.tasklog = tasklog.TaskLog(
            # threadqueue=self.get_appsys().get_thread_queue(),
            logwidget=tasklog.LogText(
                master=rf, wrap=tkinter.WORD, undo=tkinter.FALSE
            ),
        )
        pw.add(toppane)
        pw.add(rf)
        pw.paneconfigure(toppane, stretch=tkinter.FIRST)
        pw.paneconfigure(rf, stretch="never")

        self.feedbackctrl = feedbackctrl
        self.response = self.process_response(feedbacktext)

    def process_response(self, response):
        database = self.get_appsys().get_results_database()
        gepfgc = ecfrecord.get_ecf_player_for_grading_code
        gecfcc = ecfrecord.get_ecf_club_for_club_code
        self.allowapplycodes = None
        fb = feedback_html.FeedbackHTML()
        fb.submission_file_name = "@@@@@@@@"
        fb.responsestring = response
        fb.feed(response)
        fb.insert_whitespace_and_redact_dates()
        fb.find_player_lists()
        self.insert_text_feedbackctrl("\n\n")
        if (
            fb.feedbacknumbers is None
            or fb.feedbackplayers is None
            or fb.submissionpins is None
            or fb.submissionplayers is None
        ):
            message = "".join(
                (
                    "The upload for this feedback is assumed to have failed ",
                    " because the player lists cannot be found",
                )
            )
            self.insert_text_feedbackctrl(message + ".")
            tkinter.messagebox.showinfo(
                title="Apply Feedback", message=message
            )
            return fb
        pknames = {"ECFCode", "Name"}
        cknames = {"ClubName", "ClubCode"}
        knames = pknames.union(cknames)
        updateplayers = []
        updateclubs = []
        newecfcodes = []
        mergeecfcodes = []
        playerset = set()
        clubset = set()
        for sp in fb.submissionplayers[1:]:
            elements = [e.strip() for e in sp.split("\t")]
            ed = dict()
            for e in elements:
                f = e.split("=")
                if len(f) != 2:
                    continue
                k = f[0].strip("#")
                if k in knames:
                    ed[k] = f[1].strip()
            if len(pknames.intersection(ed)) == 2:
                if ed["ECFCode"] not in playerset:
                    if gepfgc(database, ed["ECFCode"]) is None:
                        updateplayers.append(ed)
                        playerset.add(ed["ECFCode"])
            if len(cknames.intersection(ed)) == 2:
                if ed["ClubCode"] not in clubset:
                    if gecfcc(database, ed["ClubCode"]) is None:
                        updateclubs.append(ed)
                        clubset.add(ed["ClubCode"])

        # Commented code displays the two blocks from which PINs and grading
        # codes are fitted together.

        # self.insert_text_feedbackctrl(
        #    'List of players generated in response to submission\n\n')
        # self.insert_text_feedbackctrl(fb.feedbackplayers[0])
        # self.insert_text_feedbackctrl('\n')
        # for n, p in zip(fb.feedbacknumbers, fb.feedbackplayers[1:]):
        #    self.insert_text_feedbackctrl(''.join((n, p, '\n')))
        # self.insert_text_feedbackctrl(
        #    '\n\nList of players in the submission\n\n')
        # self.insert_text_feedbackctrl(fb.submissionplayers[0])
        # for n, p in zip(fb.submissionpins, fb.submissionplayers[1:]):
        #    self.insert_text_feedbackctrl(''.join((n, p)))

        if updateplayers:
            self.insert_text_applyctrl(
                "Grading codes to be added to local list of Players.\n\n"
            )
            for up in updateplayers:
                self.insert_text_applyctrl(
                    "  ".join(("Add", up["ECFCode"], up["Name"]))
                )
                self.insert_text_applyctrl("\n")
            self.insert_text_applyctrl("\n")
        if updateclubs:
            self.insert_text_applyctrl(
                "Club codes to be added to local list of Clubs.\n\n"
            )
            for uc in updateclubs:
                self.insert_text_applyctrl(
                    "  ".join(("Add", uc["ClubCode"], uc["ClubName"]))
                )
                self.insert_text_applyctrl("\n")
            self.insert_text_applyctrl("\n")
        self.insert_text_feedbackctrl(
            "".join(
                (
                    "\n\nThe submission PINs and feedback players in display order ",
                    "match up as follows (all dates removed):\n\n",
                )
            )
        )
        for fbn, spin, sp, fbp in zip(
            fb.feedbacknumbers,
            fb.submissionpins,
            fb.submissionplayers[1:],
            fb.feedbackplayers[1:],
        ):
            self.insert_text_feedbackctrl(
                "".join(
                    (
                        fbn.strip(),
                        "\t",
                        spin[1:],
                        "\t\t",
                        _remove_dates_re.sub("", fbp),
                        "\n",
                    )
                )
            )
            n = _submission_player_re.search(sp)
            m = _no_code_re.search(fbp)
            if m:
                self.insert_allowapply_header()
                self.allowapplycodes = False
                self.insert_text_applyctrl(
                    "".join(
                        (
                            "Pin ",
                            spin.split("=")[1],
                            ": ",
                            n.group(1).strip(),
                            " : no grading code assigned.\n\n",
                        )
                    )
                )
                continue
            m = _exact_re.search(fbp)
            if m:
                newecfcodes.append((spin.split("=")[1], m.group(1)))
                self.insert_allowapply_header()
                self.insert_text_applyctrl(
                    "".join(
                        (
                            "Pin ",
                            spin.split("=")[1],
                            ": ",
                            n.group(1).strip(),
                            " : grading code ",
                            m.group(1),
                            " assigned.\n\n",
                        )
                    )
                )
                continue
            m = _match_to_re.search(fbp)
            if m:
                newecfcodes.append((spin.split("=")[1], m.group(1)))
                self.insert_allowapply_header()
                self.insert_text_applyctrl(
                    "".join(
                        (
                            "Pin ",
                            spin.split("=")[1],
                            ": ",
                            n.group(1).strip(),
                            " : grading code ",
                            m.group(1),
                            " assigned.\n\n",
                        )
                    )
                )
                continue
            m = _new_re.search(fbp)
            if m:
                newecfcodes.append((spin.split("=")[1], m.group(1)))
                self.insert_allowapply_header()
                self.insert_text_applyctrl(
                    "".join(
                        (
                            "Pin ",
                            spin.split("=")[1],
                            ": ",
                            n.group(1).strip(),
                            " : grading code ",
                            m.group(1),
                            " assigned.\n\n",
                        )
                    )
                )
                continue
            m = _merge_re.search(fbp)
            if m:
                mergeecfcodes.append(
                    (spin.split("=")[1], m.group(2), m.group(1))
                )
                self.insert_allowapply_header()
                self.insert_text_applyctrl(
                    "".join(
                        (
                            "Pin ",
                            spin.split("=")[1],
                            ": ",
                            n.group(1).strip(),
                            " : grading code ",
                            m.group(2),
                            " merged into ",
                            m.group(1),
                            ".\n\n",
                        )
                    )
                )
                continue
        self.insert_text_feedbackctrl("\n\n")
        if self.allowapplycodes is None:
            self.insert_text_applyctrl(
                "".join(
                    (
                        "There are no new or merged grading codes ",
                        "to be processed.\n\n",
                    )
                )
            )
        elif not self.allowapplycodes:
            self.insert_text_applyctrl(
                "".join(
                    (
                        "New or merged grading codes will not be processed ",
                        "because a grading code is missing.",
                        "\n\n",
                    )
                )
            )
        self.updateplayers = updateplayers
        self.updateclubs = updateclubs
        self.newecfcodes = newecfcodes
        self.mergeecfcodes = mergeecfcodes
        return fb

    def insert_text_feedbackctrl(self, text):
        self.feedbackctrl.insert(tkinter.END, text)

    def insert_text_applyctrl(self, text):
        self.applyctrl.insert(tkinter.END, text)

    def insert_allowapply_header(self):
        if self.allowapplycodes is not None:
            return
        self.allowapplycodes = True
        self.insert_text_applyctrl(
            "Grading codes for Apply Feedback to process:\n\n"
        )

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """
        pass

    def apply_new_grading_codes(self, *args, **kargs):
        """Apply new grading codes from feedback and return report.

        args and kargs soak up arguments set by threading or multiprocessing
        when running this method.

        """
        updateplayers = self.updateplayers
        updateclubs = self.updateclubs
        newecfcodes = self.newecfcodes
        mergeecfcodes = self.mergeecfcodes
        if (
            not updateclubs
            and not updateplayers
            and not newecfcodes
            and not mergeecfcodes
        ):
            self.insert_text_applyctrl(
                "\n\nThere were no updates for Apply Feedback to do.\n\n",
            )
            return False

        database = self.get_appsys().get_results_database()
        database.start_transaction()

        if updateplayers:
            record = ecfrecord.ECFrefDBrecordECFplayer()
            gepfgc = ecfrecord.get_ecf_player_for_grading_code
            self.insert_text_applyctrl("Add ECF codes and player names.\n\n")
            for up in updateplayers:
                if gepfgc(database, up["ECFCode"]):
                    continue
                record.key.recno = None
                record.value.ECFcode = up["ECFCode"]
                record.value.ECFname = up["Name"]
                record.value.ECFactive = True
                record.value.ECFclubcodes = []
                record.put_record(database, filespec.ECFPLAYER_FILE_DEF)
                self.insert_text_applyctrl(
                    "  ".join(("Added", up["ECFCode"], up["Name"]))
                )
                self.insert_text_applyctrl("\n")
            self.insert_text_applyctrl("\n")

            # An almost exact copy of code in copy_ecf_players_post_2020_rules
            # function in ecfdataimport module.  (mr.value replaced by v).
            ecfmapcursor = database.database_cursor(
                filespec.MAPECFPLAYER_FILE_DEF, filespec.MAPECFPLAYER_FIELD_DEF
            )
            try:
                mapdata = ecfmapcursor.first()
                while mapdata:
                    mr = ecfmaprecord.ECFmapDBrecordPlayer()
                    mr.load_record(mapdata)
                    v = mr.value

                    # mapdata values like (key, None) occur sometimes, origin
                    # unknown but seen only when mixing event imports and ecf
                    # reference data imports.
                    # Ignoring them should be correct, and seems ok too.
                    # Find and delete them offline.
                    # See gui.events_lite too.
                    if v.__dict__:

                        if v.playercode is None:
                            if v.playerecfcode is not None:
                                if ecfrecord.get_ecf_player_for_grading_code(
                                    database, v.playerecfcode
                                ):
                                    newmr = mr.clone()
                                    newmr.value.playerecfcode = None
                                    newmr.value.playercode = v.playerecfcode
                                    mr.edit_record(
                                        database,
                                        filespec.MAPECFPLAYER_FILE_DEF,
                                        filespec.MAPECFPLAYER_FIELD_DEF,
                                        newmr,
                                    )
                    mapdata = ecfmapcursor.next()
            finally:
                ecfmapcursor.close()

        if updateclubs:
            ecfrec = ecfrecord.ECFrefDBrecordECFclub()
            gecfcc = ecfrecord.get_ecf_club_for_club_code
            self.insert_text_applyctrl("Add ECF codes and club names.\n\n")
            for uc in updateclubs:
                if gecfcc(database, uc["ClubCode"]):
                    continue
                ecfrec.key.recno = None
                ecfrec.value.ECFcode = uc["ClubCode"]
                ecfrec.value.ECFactive = True
                ecfrec.value.ECFname = uc["ClubName"]
                ecfrec.value.ECFcountycode = ""
                ecfrec.put_record(database, filespec.ECFCLUB_FILE_DEF)
                self.insert_text_applyctrl(
                    "  ".join(("Added", uc["ClubCode"], uc["ClubName"]))
                )
                self.insert_text_applyctrl("\n")
            self.insert_text_applyctrl("\n")

            # The ecfdataimport import module does not have this code analogous
            # to the updateplayers code.  It probably should now, but far less
            # happened for clubs than players and should be same in future.
            # Possibly MAPECFCLUB_FIELD_DEF should be PLAYERALIASMAP_FIELD_DEF
            # because that index selects player records which need processing.
            ecfmapcursor = database.database_cursor(
                filespec.MAPECFCLUB_FILE_DEF, filespec.MAPECFCLUB_FIELD_DEF
            )
            try:
                mapdata = ecfmapcursor.first()
                while mapdata:
                    mr = ecfmaprecord.ECFmapDBrecordClub()
                    mr.load_record(mapdata)
                    v = mr.value

                    # mapdata values like (key, None) occur sometimes, origin
                    # unknown but seen only when mixing event imports and ecf
                    # reference data imports.
                    # Ignoring them should be correct, and seems ok too.
                    # Find and delete them offline.
                    # See gui.events_lite too.
                    if v.__dict__:

                        if v.clubcode is None:
                            if v.clubecfcode is not None:
                                if ecfrecord.get_ecf_club_for_club_code(
                                    database, v.clubecfcode
                                ):
                                    newmr = mr.clone()
                                    newmr.value.clubecfcode = None
                                    newmr.value.clubcode = v.clubecfcode
                                    mr.edit_record(
                                        database,
                                        filespec.MAPECFCLUB_FILE_DEF,
                                        filespec.MAPECFCLUB_FIELD_DEF,
                                        newmr,
                                    )
                    mapdata = ecfmapcursor.next()
            finally:
                ecfmapcursor.close()

        if newecfcodes:
            for spin, newcode in newecfcodes:
                person = self._get_ecfmaprecord_for_new_person(database, spin)
                if person is None:
                    self.insert_text_applyctrl(
                        "".join(
                            (
                                newcode,
                                " is not consistent with code provided locally (",
                                "try removing code for player in 'Grading Codes'",
                                " tab)",
                            )
                        )
                    )
                    self.insert_text_applyctrl("\n")
                    continue
                personclone = person.clone()
                personclone.value.playerecfcode = None
                personclone.value.playerecfname = None
                personclone.value.playercode = newcode
                person.edit_record(
                    database,
                    filespec.MAPECFPLAYER_FILE_DEF,
                    filespec.MAPECFPLAYER_FIELD_DEF,
                    personclone,
                )
                self.insert_text_applyctrl(
                    "".join(
                        (
                            newcode,
                            " added as feedback update to ECF player list",
                        )
                    )
                )
                self.insert_text_applyctrl("\n")
            self.insert_text_applyctrl("\n")

        if mergeecfcodes:
            for spin, usedcode, mergecode in mergeecfcodes:
                ecfplayer = ecfrecord.get_ecf_player_for_grading_code(
                    database, usedcode
                )
                if ecfplayer is None:
                    continue
                if mergecode == ecfplayer.value.ECFmerge:
                    if not ecfplayer.value.ECFactive:
                        continue
                if ecfplayer.value.ECFmerge:
                    repmerge = "  ".join(
                        (
                            " replacing noted merge into",
                            ecfplayer.value.ECFmerge,
                        )
                    )
                else:
                    repmerge = ""
                ecfplayerclone = ecfplayer.clone()
                ecfplayerclone.value.ECFmerge = mergecode
                ecfplayerclone.value.ECFactive = False
                ecfplayer.edit_record(
                    database,
                    filespec.ECFPLAYER_FILE_DEF,
                    filespec.ECFPLAYER_FIELD_DEF,
                    ecfplayerclone,
                )
                self.insert_text_applyctrl(
                    "".join(
                        (
                            usedcode,
                            "  noted as merged into  ",
                            mergecode,
                            "  in feedback update",
                            repmerge,
                        )
                    )
                )
                self.insert_text_applyctrl("\n")
            self.insert_text_applyctrl("\n")

        database.commit()
        self.newcodesapply = []
        self.refresh_controls(
            (
                (
                    database,
                    filespec.MAPECFPLAYER_FILE_DEF,
                    filespec.PERSONMAP_FIELD_DEF,
                ),
                (
                    database,
                    filespec.ECFPLAYER_FILE_DEF,
                    filespec.ECFPLAYERNAME_FIELD_DEF,
                ),
                (
                    database,
                    filespec.MAPECFCLUB_FILE_DEF,
                    filespec.PLAYERALIASMAP_FIELD_DEF,
                ),
                (
                    database,
                    filespec.ECFCLUB_FILE_DEF,
                    filespec.ECFCLUBNAME_FIELD_DEF,
                ),
                (
                    database,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYERNAME_FIELD_DEF,
                ),
            )
        )
        self.insert_text_applyctrl("Apply feedback update completed.\n\n")
        return True

    def describe_buttons(self):
        """Define all action buttons that may appear on Feedback page."""
        super().describe_buttons()
        self.define_button(
            self._btn_closefeedbackmonthly,
            text="Cancel Apply Feedback",
            tooltip="Cancel the feedback update.",
            underline=0,
            switchpanel=True,
            command=self.on_cancel_apply_feedback,
        )
        self.define_button(
            self._btn_applyfeedbackmonthly,
            text="Apply Feedback",
            tooltip="Apply feedback updates to database.",
            underline=0,
            command=self.on_apply_feedback,
        )

    def on_cancel_apply_feedback(self, event=None):
        """Do any tidy up before switching to next panel."""
        pass

    def on_apply_feedback(self, event=None):
        """Run apply_new_grading_codes in separate thread."""
        if not self.allowapplycodes:
            tkinter.messagebox.showinfo(
                title="Apply Feedback", message="Feedback not applied"
            )
        self.tasklog.run_method(method=self.apply_new_grading_codes)

    def show_buttons_for_cancel_import(self):
        """Show buttons for actions allowed at start of import process."""
        self.hide_panel_buttons()
        self.show_panel_buttons((self._btn_closefeedbackmonthly,))

    def show_buttons_for_start_import(self):
        """Show buttons for actions allowed at start of import process."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (self._btn_closefeedbackmonthly, self._btn_applyfeedbackmonthly)
        )

    def _get_ecfmaprecord_for_new_person(self, database, pin):
        """Return ECFmapDBrecordPlayer() for pin or None.

        None is returned if the value attributes make it inappropriate to
        update with a grading code extracted from ECF feedback.  For example
        a grading code has been supplied by editing from the Grading Codes tab.

        """
        rec = resultsrecord.get_alias(database, pin)
        if rec:
            maprec = ecfmaprecord.get_new_person_for_identity(
                database, rec.value
            )
            if maprec:
                if maprec.value.playercode is None:
                    if maprec.value.playerecfcode is None:
                        if maprec.value.playerecfname is not None:
                            return maprec


def show_ecf_results_feedback_monthly_tab(tab, button):
    """Show monthly feedback panel to do ECF feedback actions.

    tab is the tab instance containing the button initiating the action.
    button is the button which initiated the action.

    The button has a different name, for state purposes, on each tab.

    """
    conf = configuration.Configuration()
    filepath = tkinter.filedialog.askopenfilename(
        parent=tab.get_widget(),
        title="Open Saved ECF Feedback",
        # defaultextension='.txt',
        # filetypes=(('ECF feedback', '*.txt'),),
        initialdir=conf.get_configuration_value(constants.RECENT_FEEDBACK),
    )
    if not filepath:
        tab.inhibit_context_switch(button)
        return
    conf.set_configuration_value(
        constants.RECENT_FEEDBACK,
        conf.convert_home_directory_to_tilde(os.path.dirname(filepath)),
    )
    try:
        feedbackfile = open(filepath, "rb")
        try:
            tab.get_appsys().set_kwargs_for_next_tabclass_call(
                dict(
                    datafile=(
                        filepath,
                        _get_feedback_monthly_text(feedbackfile),
                    )
                )
            )
        finally:
            feedbackfile.close()
    except:
        tkinter.messagebox.showinfo(
            parent=tab.get_widget(),
            message="".join(
                ("File\n", os.path.split(dlg)[-1], "\ndoes not exist")
            ),
            title=" ".join(["Open ECF feedback email or attachment"]),
        )
        return


def _get_feedback_monthly_text(file):
    """Return feedback text from open binary file.

    Required text is assumed to be either in 'text/html' parts of an email,
    but not an 'application/ms-tnef' attachment, or in a text file containing
    the saved response from a submission to the ECF ratings website.

    """
    m = email.message_from_binary_file(file)

    # Assume feedback is a saved response file if no message keys are found.
    if not m.keys():
        file.seek(0)
        return file.read().decode()

    # Assume feedback is in body of email, with no attachments.
    return m.get_payload()

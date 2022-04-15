# ecfevents.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database panel for submitting events to ECF for grading.
"""

import tkinter
import tkinter.messagebox
import tkinter.filedialog
import os

from solentware_misc.gui import panel

from chessvalidate.core import gameresults

from . import ecfeventgrids
from . import uploadresults
from .feedback_monthly import show_ecf_results_feedback_monthly_tab
from ...core.ecf import ecfmaprecord
from ...core.ecf import ecfrecord
from ...core import resultsrecord
from ...core import constants
from ...core import filespec
from ...core import configuration
from . import ecferrors


class ECFEvents(panel.PanelGridSelector):

    """The ECF Events panel for a Results database."""

    _btn_ecf_save = "ecfevents_save"
    _btn_ecf_submit = "ecfevents_submit"
    _btn_ecf_check_and_report = "ecfevents_check_and_report"
    _btn_ecfeventdetail = "ecfevents_detail"
    _btn_ecf_feedback_monthly = "ecfevents_feedback_monthly"

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database ECF events panel"""
        self.eventgrid = None
        super(ECFEvents, self).__init__(parent=parent, cnf=cnf, **kargs)
        self.show_panel_buttons(
            (
                self._btn_ecfeventdetail,
                self._btn_ecf_save,
                self._btn_ecf_check_and_report,
                self._btn_ecf_submit,
                self._btn_ecf_feedback_monthly,
            )
        )
        self.create_buttons()
        (self.eventgrid,) = self.make_grids(
            (
                dict(
                    grid=ecfeventgrids.ECFEventGrid,
                    gridfocuskey="<KeyPress-F7>",
                ),
            )
        )

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """
        pass

    def describe_buttons(self):
        """Define all action buttons that may appear on ECF events page."""
        super().describe_buttons()
        self.define_button(
            self._btn_ecfeventdetail,
            text="Update Event Detail",
            tooltip="Update details for selected event.",
            switchpanel=True,
            underline=0,
            command=self.on_ecf_event_detail,
        )
        self.define_button(
            self._btn_ecf_save,
            text="Create file",
            tooltip="Create results file for selected events.",
            underline=7,
            command=self.on_ecf_save,
        )
        self.define_button(
            self._btn_ecf_check_and_report,
            text="Check and Report file",
            tooltip="Check and report previouly created results file to ECF.",
            underline=13,
            command=self.on_ecf_check_and_report,
        )
        self.define_button(
            self._btn_ecf_submit,
            text="Submit file",
            tooltip="Submit previouly created results file to ECF.",
            underline=2,
            command=self.on_ecf_submit,
        )
        self.define_button(
            self._btn_ecf_feedback_monthly,
            text="Feedback",
            tooltip="Display saved feedback for an upload to ECF.",
            underline=7,
            switchpanel=True,
            command=self.on_ecf_results_feedback_monthly,
        )

    def is_event_selected(self):
        """Return True if events selected.  Otherwise False."""
        if len(self.eventgrid.selection) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="No event selected for amendment of detail",
                title="ECF Events",
            )
            return False
        return True

    def on_ecf_event_detail(self, event=None):
        """Do processing for buttons with command set to on_ecf_event_detail.

        Abandon processing if no record selected.

        """
        if not self.is_event_selected():
            return "break"

    def on_ecf_save(self, event=None):
        """Create an ECF Results Submission File."""
        self.write_results_file_for_ecf()

    def on_ecf_check_and_report(self, event=None):
        """Check and report created ECF Results Submission File to ECF."""
        if not uploadresults.curl and not uploadresults.requests:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "'Check and Report' action cannot be done because",
                        "both 'curl' and 'requests' are not available.\n\nA",
                        "browser can be used to upload the submission file to",
                        "https://www.ecfrating.org.uk/v2/submit/",
                    )
                ),
                title="ECF Events",
            )
            return
        upload = uploadresults.CheckAndReportResults()
        upload.root.wait_visibility()
        upload.root.grab_set()
        upload.root.wait_window()
        return

    def on_ecf_submit(self, event=None):
        """Submit created ECF Results Submission File to ECF."""
        if not uploadresults.curl and not uploadresults.requests:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "'Submit' action cannot be done because",
                        "both 'curl' and 'requests' are not available.\n\nA",
                        "browser can be used to upload the submission file to",
                        "https://www.ecfrating.org.uk/v2/submit/",
                    )
                ),
                title="ECF Events",
            )
            return
        upload = uploadresults.SubmitResults()
        upload.root.wait_visibility()
        upload.root.grab_set()
        upload.root.wait_window()
        return

    def on_ecf_results_feedback_monthly(self, event=None):
        """Do ECF feedback actions."""
        show_ecf_results_feedback_monthly_tab(
            self, self._btn_ecf_feedback_monthly
        )

    def write_results_file_for_ecf(self):
        """Write results for selected events to ECF submission file.

        Submission file format is defined at www.ecfrating.org.uk/doc/.

        """
        esel = self.eventgrid.selection
        ebkm = self.eventgrid.bookmarks
        submit_events = dict()
        submit_games = dict()
        db = self.get_appsys().get_results_database()

        for e in ebkm:
            submit_events[e[-1]] = resultsrecord.get_event_from_record_value(
                db.get_primary_record(filespec.EVENT_FILE_DEF, e[-1])
            )
        for e in esel:
            if e not in ebkm:
                submit_events[
                    e[-1]
                ] = resultsrecord.get_event_from_record_value(
                    db.get_primary_record(filespec.EVENT_FILE_DEF, e[-1])
                )

        if len(submit_events) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="No events selected for submission of results to ECF",
                title="ECF Events",
            )
            return

        for s in submit_events:
            startdate = submit_events[s].value.startdate
            enddate = submit_events[s].value.enddate
            name = submit_events[s].value.name
            reference_event = submit_events[s]
            break

        ecfeventrecord = ecfrecord.get_ecf_event(
            db.get_primary_record(
                filespec.ECFEVENT_FILE_DEF,
                db.database_cursor(
                    filespec.ECFEVENT_FILE_DEF,
                    filespec.ECFEVENTIDENTITY_FIELD_DEF,
                ).get_unique_primary_for_index_key(
                    db.encode_record_number(
                        reference_event.value.get_event_identity()
                    )
                ),
            )
        )

        if ecfeventrecord is None:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "No event details available for inclusion",
                        "in submission of results to ECF. Click the",
                        '"Event Details" button to get the form for',
                        "providing them.",
                    )
                ),
                title="ECF Events",
            )
            return

        for s in submit_events:
            if (
                startdate != submit_events[s].value.startdate
                or enddate != submit_events[s].value.enddate
                or name != submit_events[s].value.name
            ):
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message=" ".join(
                        (
                            "Cannot submit the selected events to ECF in",
                            "same file because the start dates end dates",
                            "and names are not all the same.",
                        )
                    ),
                    title="ECF Events",
                )
                return

        all_events = resultsrecord.get_events_matching_event_identity(
            db, reference_event.value.get_event_identity()
        )
        msg = []
        for ae in all_events:
            if ae not in submit_events:
                for s in all_events[ae].value.sections:
                    msg.append(resultsrecord.get_section_details(db, s, False))
        if len(msg):
            resp = tkinter.messagebox.askquestion(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "The following sections in event",
                        name,
                        "start date:",
                        startdate,
                        "end date:",
                        enddate,
                        "will not be included in the submission because",
                        "their event record(s) are not selected:\n\n",
                        "; ".join(msg),
                        "\n\n",
                        'Click "Yes" to include them all.\n',
                        'Click "No" to use the selection already made.',
                    )
                ),
                title="ECF Events",
            )
            if resp == tkinter.messagebox.YES:
                submit_events.update(all_events)
                msg = " ".join(
                    (
                        "A results submission file for ECF will be created",
                        "for all events with same name and dates as the",
                        "selected event(s).",
                    )
                )
            elif resp == tkinter.messagebox.NO:
                msg = " ".join(
                    (
                        "A results submission file for ECF will be created",
                        "using the selected event(s) only.",
                    )
                )
            else:
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="Creation of submission file for ECF abandoned",
                    title="ECF Events",
                )
                return
        else:
            msg = " ".join(
                (
                    "A results submission file for ECF will be created",
                    "for the selected event(s).",
                )
            )

        del all_events

        if not tkinter.messagebox.askyesno(
            parent=self.get_widget(), message=msg, title="ECF Events"
        ):
            return

        games = []
        for se in submit_events:
            games.extend(
                resultsrecord.get_games_for_event(db, submit_events[se])
            )
        for g in games:
            v = g.value
            if v.hometeam and v.awayteam:
                ecfsection = (v.hometeam, v.awayteam)
            elif v.section:
                ecfsection = v.section
            else:
                ecfsection = (v.event,)
            if ecfsection not in submit_games:
                submit_games[ecfsection] = [g]
            else:
                submit_games[ecfsection].append(g)
        aliases = resultsrecord.get_persons(
            db, resultsrecord.get_aliases_for_games(db, games)
        )
        submit_players = self._get_ecf_players_for_alias_map(db, aliases)
        submit_player_clubs = ecfmaprecord.get_player_clubs_for_games(
            db, games
        )
        submit_clubs = self._get_ecf_clubs_for_alias_map(
            db, submit_player_clubs
        )
        submit_counties = dict()
        for sc in submit_clubs:
            # this needs pick relevant txn date I think
            v = submit_clubs[sc].value
            if v.ECFcode not in submit_counties:
                submit_counties[v.ECFcode] = v.ECFcountycode
        submit_names = resultsrecord.get_names_for_games(db, games)
        del games

        list0 = []
        for sp, spc in submit_player_clubs.items():
            if spc.value.clubcode is None and spc.value.clubecfcode is None:
                list0.append(
                    resultsrecord.get_player_name_text_tabs(
                        db, spc.value.get_unpacked_playername()
                    )
                )
        if len(list0):
            reports = [("Player has no ECF club code", list0)]
            errors = ecferrors.ECFErrorFrame(
                None, "ECF Errors", "Sample club", reports
            )
            return

        list1 = []
        list2 = []
        list3 = []
        for sp in submit_players:
            if isinstance(
                submit_players[sp], ecfmaprecord.ECFmapDBvaluePlayer
            ):
                if submit_players[sp].playerecfname is None:
                    list2.append(
                        resultsrecord.get_player_name_text_tabs(
                            db, submit_players[sp].get_unpacked_playername()
                        )
                    )
                elif submit_players[sp].playerecfcode is None:
                    list3.append(
                        resultsrecord.get_player_name_text_tabs(
                            db, submit_players[sp].get_unpacked_playername()
                        )
                    )
            elif submit_players[sp] is None:
                list1.append(
                    resultsrecord.get_player_name_text_tabs(
                        db, aliases[sp].value.identity()
                    )
                )
        if len(list1) + len(list2) > 0:
            if len(list3) == 0:
                msg = " ".join(
                    (
                        "A number of players in this event do not have",
                        "an ECF grading code on the Master List or have",
                        "not been given a name in the style accepted by",
                        "ECF. The lists will be displayed on closing",
                        "this message.",
                    )
                )
            else:
                msg = " ".join(
                    (
                        "A number of players in this event do not have",
                        "an ECF grading code on the Master List or have",
                        "not been given a name in the style accepted by",
                        "ECF. The lists will be displayed on closing",
                        "this message.\n",
                        "Also included is a list of new players who",
                        "have not been given an ECF grading code. If,"
                        "you have got feedback files from the ECF for",
                        "this event it means you have not edited these",
                        "records to hold the allocated grading code.",
                    )
                )
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(), message=msg, title="ECF Events"
            )
            reports = []
            if len(list1):
                reports.append(("Player not in event list", list1))
            if len(list2):
                reports.append(("Player has no ECF name", list2))
            if len(list3):
                reports.append(("Player has no ECF code", list3))
            errors = ecferrors.ECFErrorFrame(
                None, "ECF Errors", "Sample", reports
            )
            return
        if len(list3) > 0:
            reports = [("Player has no ECF code", list3)]
            errors = ecferrors.ECFErrorFrame(
                None, "ECF Grading Code Check", "Sample", reports
            )
            if tkinter.messagebox.YES != tkinter.messagebox.askquestion(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "A list of players without an ECF grading code has",
                        "been displayed.\n\nPlease be sure that submitting these",
                        "results without ECF grading codes for these players is",
                        "correct before you do so, to avoid extra work merging any",
                        "new grading codes allocated.",
                    )
                ),
                title="ECF Events - create submission file",
            ):
                return

        def dcc(ecf_field_name):
            # Hack to make things work at Python 3
            # Probably correct is making all ecfeventrecord.value attributes
            # bytes and coping with that at the interface with Text widgets.
            # This is consistent with strategy elsewhere.
            # Only thing in favour of technique used here is the need to
            # translate from utf-8 to ascii, or iso-8859-1 or some other 256
            # code point map while ECF system expects that.
            # Change to str in application code may make this hack redundant.
            # return ecf_field_name.decode('ascii')
            return ecf_field_name

        def ecf_line(data):
            return "".join(("#", "=".join(data)))

        def pin_convention(pin):
            if pin in pin_to_ecf_code:
                return pin_to_ecf_code[pin]
            spin = str(pin)
            if spin == str(0):
                return constants.ECF_ZERO_NOT_0
            else:
                return spin

        v = ecfeventrecord.value
        if v.eventcode:
            submission = v.submission + 1
            subfilename = "".join(
                (v.eventcode, str(submission).zfill(2), ".txt")
            )
        else:
            subfilename = "ecf00.txt"
            submission = 0
        lines = [ecf_line((dcc(constants.EVENT_DETAILS),))]
        lines.append(ecf_line((dcc(constants.EVENT_CODE), v.eventcode)))
        lines.append(ecf_line((dcc(constants.EVENT_NAME), v.eventname)))
        lines.append(
            ecf_line((dcc(constants.SUBMISSION_INDEX), str(submission)))
        )
        d = v.eventstartdate.split("-")
        d.reverse()
        lines.append(ecf_line((dcc(constants.EVENT_DATE), "/".join(d))))
        d = v.eventenddate.split("-")
        d.reverse()
        lines.append(ecf_line((dcc(constants.FINAL_RESULT_DATE), "/".join(d))))
        lines.append(ecf_line((dcc(constants.RESULTS_OFFICER), v.gradername)))
        if len(v.graderemail):
            lines.append(
                ecf_line(
                    (dcc(constants.RESULTS_OFFICER_ADDRESS), v.graderemail)
                )
            )
        else:
            addr = v.graderaddress.split("\n")
            for a in addr:
                lines.append(
                    ecf_line((dcc(constants.RESULTS_OFFICER_ADDRESS), a))
                )
            if len(v.graderpostcode):
                lines.append(
                    ecf_line(
                        (
                            dcc(constants.RESULTS_OFFICER_ADDRESS),
                            v.graderpostcode,
                        )
                    )
                )
        lines.append(ecf_line((dcc(constants.TREASURER), v.treasurername)))
        addr = v.treasureraddress.split("\n")
        for a in addr:
            lines.append(ecf_line((dcc(constants.TREASURER_ADDRESS), a)))
        if len(v.treasurerpostcode):
            lines.append(
                ecf_line(
                    (dcc(constants.TREASURER_ADDRESS), v.treasurerpostcode)
                )
            )
        if len(v.movesfirst):
            lines.append(
                ecf_line((dcc(constants.MOVES_FIRST_SESSION), v.movesfirst))
            )
        if len(v.minutesfirst):
            lines.append(
                ecf_line(
                    (dcc(constants.MINUTES_FIRST_SESSION), v.minutesfirst)
                )
            )
        if len(v.moveslater):
            lines.append(
                ecf_line((dcc(constants.MOVES_SECOND_SESSION), v.moveslater))
            )
        if len(v.minuteslater):
            lines.append(
                ecf_line(
                    (dcc(constants.MINUTES_SECOND_SESSION), v.minuteslater)
                )
            )
        if len(v.minuteslast):
            lines.append(
                ecf_line((dcc(constants.MINUTES_REST_OF_GAME), v.minuteslast))
            )
        if len(v.minutesonly):
            lines.append(
                ecf_line((dcc(constants.MINUTES_FOR_GAME), v.minutesonly))
            )
        if len(v.secondspermove):
            lines.append(
                ecf_line((dcc(constants.SECONDS_PER_MOVE), v.secondspermove))
            )
        if v.adjudication == 0:
            lines.append(ecf_line((dcc(constants.ADJUDICATED), "Maybe")))
        elif v.adjudication == 1:
            lines.append(ecf_line((dcc(constants.ADJUDICATED), "Yes")))
        elif v.adjudication == 2:
            lines.append(ecf_line((dcc(constants.ADJUDICATED), "No")))
        if v.informgrandprix:
            lines.append(ecf_line((dcc(constants.INFORM_GRAND_PRIX),)))
        if v.informfide:
            lines.append(ecf_line((dcc(constants.INFORM_FIDE),)))
        if v.informchessmoves:
            lines.append(ecf_line((dcc(constants.INFORM_CHESSMOVES),)))
        if v.informeast:
            lines.append(ecf_line((dcc(constants.INFORM_UNION), "EAST")))
        if v.informmidlands:
            lines.append(ecf_line((dcc(constants.INFORM_UNION), "MIDLANDS")))
        if v.informnorth:
            lines.append(ecf_line((dcc(constants.INFORM_UNION), "NORTH")))
        if v.informsouth:
            lines.append(ecf_line((dcc(constants.INFORM_UNION), "SOUTH")))
        if v.informwest:
            lines.append(ecf_line((dcc(constants.INFORM_UNION), "WEST")))
        if len(submit_players):
            lines.append(ecf_line((dcc(constants.PLAYER_LIST),)))
        # Decorate PLAYER LIST data to sort players by name and grading code.
        # The comparison operators defined for ECFmapDBvaluePlayer may not be
        # suitable for alphabetic sorting.
        sorted_submit_players = []
        # pin_to_ecf_code and ecf_code_to_pin are used to implement a hack
        # which causes league results for players to be presented one block per
        # player on the ECF Online Grading Database as found at 02 March 2016
        # even when multiple spellings of player names occur in reports from
        # leagues.  It was assumed the blocking should ignore PINs if grading
        # codes are present.
        # club_code is added to the decoration in sorted_submit_players so that
        # duplicate entries can be ignored later.
        pin_to_ecf_code = dict()
        ecf_code_to_pin = dict()
        for pk, pv in submit_players.items():
            if isinstance(pv, ecfmaprecord.ECFmapDBvaluePlayer):
                ssp_code = dcc(pv.playerecfcode) if pv.playerecfcode else ""
                ssp_player = pv.playerecfname if pv.playerecfname else ""
            elif pv is not None:
                ssp_code = dcc(pv.value.ECFcode)
                ssp_player = dcc(pv.value.ECFname)
            else:
                continue
            if pk in submit_clubs:
                club_code = submit_clubs[pk].value.ECFcode
            elif pk in submit_player_clubs:
                club_code = submit_player_clubs[pk].value.clubecfcode
            else:
                club_code = None
            if ssp_code:
                pin_to_ecf_code[pk] = ecf_code_to_pin.setdefault(
                    (ssp_code, club_code), str(pk)
                )
            sorted_submit_players.append(
                (
                    ssp_player,
                    ssp_code,
                    club_code,
                    pk,
                    pv,
                )
            )
        # Original for statement now populates sorted_submit_players.
        # The original no longer generates output in the same order across runs
        # of the program when the data has not changed.
        # sspp and sspc were sinks to absorb the sort decorators, but now allow
        # duplicate entries to be ignored.
        # pin_to_person_pin extends the blocking hack done with pin_to_ecf_code
        # and ecf_code_to_pin to players where a grading code is not available.
        pin_to_person_pin = {None: None}
        prev_sspc = None
        prev_cc = None
        prev_pk = None
        for sspp, sspc, cc, pk, pv in sorted(sorted_submit_players):
            if prev_sspc == sspc and prev_cc == cc:
                if pk in pin_to_ecf_code:
                    continue
                if aliases[prev_pk] == aliases[pk]:
                    pin_to_person_pin[pk] = prev_pk
                    continue
            prev_sspc = sspc
            prev_cc = cc
            prev_pk = pk
            playerline = [ecf_line((dcc(constants.PIN), pin_convention(pk)))]
            if isinstance(pv, ecfmaprecord.ECFmapDBvaluePlayer):
                if pv.playerecfcode:
                    playerline.append(
                        ecf_line(
                            (dcc(constants.BCF_CODE), dcc(pv.playerecfcode))
                        )
                    )
                if pv.playerecfname:
                    playerline.append(
                        ecf_line((dcc(constants.NAME), pv.playerecfname))
                    )
            elif pv is not None:
                playerline.append(
                    ecf_line((dcc(constants.BCF_CODE), dcc(pv.value.ECFcode)))
                )
                playerline.append(
                    ecf_line((dcc(constants.NAME), dcc(pv.value.ECFname)))
                )
            else:
                continue
            if pk in submit_clubs:
                v = submit_clubs[pk].value
                playerline.append(
                    ecf_line((dcc(constants.CLUB), dcc(v.ECFname)))
                )
                playerline.append(
                    ecf_line((dcc(constants.CLUB_CODE), dcc(v.ECFcode)))
                )
                playerline.append(
                    ecf_line(
                        (
                            dcc(constants.CLUB_COUNTY),
                            dcc(submit_counties[v.ECFcode]),
                        )
                    )
                )
            elif pk in submit_player_clubs:
                v = submit_player_clubs[pk].value
                if (
                    v.clubcode is None
                    and v.clubecfname is not None
                    and v.clubecfcode is not None
                ):
                    playerline.append(
                        ecf_line((dcc(constants.CLUB), dcc(v.clubecfname)))
                    )
                    playerline.append(
                        ecf_line(
                            (dcc(constants.CLUB_CODE), dcc(v.clubecfcode))
                        )
                    )
            lines.append("".join(playerline))
        del aliases
        del pin_to_person_pin[None]

        # Quoted from "Grading Results File Layout"

        # BOARD - One may be present if this sequence is in a Match Results
        # part of the results file, otherwise none
        # ROUND - One must be present if this sequence is in a Section Results
        # part of the results file, otherwise none
        # GAME DATE - One must be present if this sequence is in an Other
        # Results part of the results file, otherwise one may be present.

        # These rules are applied as follows:

        # Thus the presence of board in ResultsDBvalueGame means the game can
        # be reported under a MATCH RESULTS header; the absence of board and
        # presence of round means the game can be reported under a SECTION
        # RESULTS header; the absence of board and round and presence of
        # GAME DATE means the game can be reported under an OTHER RESULTS
        # header.

        # The type and value of section in ResultsDBvalueGame determines
        # which possibility is used. If this is tuple length 2 report under
        # MATCH RESULTS header if possible and OTHER RESULTS header if not.
        # Otherwise report under a SECTION RESULTS header if possible and
        # OTHER RESULTS if not.

        # Decorate MATCH RESULTS, SECTION RESULTS, and OTHER RESULTS data to
        # sort sections by name.
        # The objects in submit_games are no longer in the same order across
        # runs of the program ever.  In particular when the data is the same.
        sorted_submit_games = []
        for gs in submit_games:
            if isinstance(gs, tuple):
                ssgh = " - ".join([submit_names[n].value.name for n in gs])
            else:
                ssgh = dcc(submit_names[gs].value.name)
            sorted_submit_games.append((ssgh, gs))
        # Original for statement now populates sorted_submit_games.
        # The original no longer generates output in the same order across runs
        # of the program when the data has not changed.
        # ssgh is the sink to absorb the sort decorator.
        for ssgh, gs in sorted(sorted_submit_games):
            match = False
            other = False
            if isinstance(gs, tuple):
                header = " - ".join([submit_names[n].value.name for n in gs])
                if len(gs) == 2:
                    match = True
            else:
                header = dcc(submit_names[gs].value.name)
            if not match:
                section = True
                for g in submit_games[gs]:
                    v = g.value
                    if v.round is None:
                        section = False
                        other = True
                        break
                    # Validate round value by ECF submission rules to allow
                    # removal of round validation on input to this program.
                    elif not str(v.round).isdecimal():
                        section = False
                        other = True
                        break
                    elif int(v.round) < 1 or int(v.round) > 99:
                        section = False
                        other = True
                        break
            else:
                section = False
            if not (match or section or other):
                other = True
            header_games = []
            for g in submit_games[gs]:
                v = g.value
                # Add round, date, and board to sort decorator in preparation
                # for ECF publishing match details on Online Grading Database.
                # Board identifiers are integers usually so give priority to
                # length of board string in the sort.
                header_games.append(
                    (
                        v.section,
                        v.round if v.round else "",
                        v.date if v.date else "",
                        (len(v.board), v.board) if v.board else (),
                        v,
                    )
                )
            header_games.sort()
            prev_game_header = (None,)
            for g in header_games:
                v = g[-1]
                # Adjust header line generation for more accurate reconstruction
                # of original match details, for planned ECF publication, based
                # on round and date information added to sort decorator.
                # Board is part of the sort decorator because the ECF Database
                # Administrator thinks the games will not be sorted by board
                # following the example of existing Central Database process.
                if match:
                    if prev_game_header != g[:-2]:
                        lines.append(
                            ecf_line((dcc(constants.MATCH_RESULTS), header))
                        )
                        lines.append(
                            ecf_line((dcc(constants.WHITE_ON), "Unknown"))
                        )
                elif section:
                    if prev_game_header[:-2] != g[:-4]:
                        lines.append(
                            ecf_line((dcc(constants.SECTION_RESULTS), header))
                        )
                        lines.append(
                            ecf_line((dcc(constants.WHITE_ON), "Unknown"))
                        )
                elif other:
                    if prev_game_header[:-2] != g[:-4]:
                        lines.append(
                            ecf_line((dcc(constants.OTHER_RESULTS), header))
                        )
                        lines.append(
                            ecf_line((dcc(constants.WHITE_ON), "Unknown"))
                        )
                prev_game_header = g[:-2]
                score = gameresults.ecfresult.get(v.result)
                if score is not None:
                    gameline = [
                        ecf_line(
                            (
                                dcc(constants.PIN1),
                                pin_convention(
                                    pin_to_person_pin.get(
                                        v.homeplayer, v.homeplayer
                                    )
                                ),
                            )
                        )
                    ]
                    gameline.append(ecf_line((dcc(constants.SCORE), score)))
                    gameline.append(
                        ecf_line(
                            (
                                dcc(constants.PIN2),
                                pin_convention(
                                    pin_to_person_pin.get(
                                        v.awayplayer, v.awayplayer
                                    )
                                ),
                            )
                        )
                    )
                    if section:
                        gameline.append(
                            ecf_line(
                                (dcc(constants.ROUND), str(int(dcc(v.round))))
                            )
                        )
                    d = v.date.split("-")
                    d.reverse()
                    gameline.append(
                        ecf_line((dcc(constants.GAME_DATE), "/".join(d)))
                    )
                    if match:
                        if v.board is not None:
                            gameline.append(
                                ecf_line((dcc(constants.BOARD), str(v.board)))
                            )
                    colour = v.homeplayerwhite
                    if colour == True:
                        gameline.append(
                            ecf_line((dcc(constants.COLOUR), "WHITE"))
                        )
                    elif colour == False:
                        gameline.append(
                            ecf_line((dcc(constants.COLOUR), "BLACK"))
                        )
                    lines.append("".join(gameline))

        lines.append(ecf_line((dcc(constants.FINISH),)))

        conf = configuration.Configuration()
        filepath = tkinter.filedialog.asksaveasfilename(
            parent=self.get_widget(),
            title="Save ECF Results submission file",
            initialfile=subfilename,
            initialdir=conf.get_configuration_value(
                constants.RECENT_SUBMISSION
            ),
        )
        if not filepath:
            return
        conf.set_configuration_value(
            constants.RECENT_SUBMISSION,
            conf.convert_home_directory_to_tilde(os.path.dirname(filepath)),
        )

        of = open(filepath, "wb")
        of.write(os.linesep.join(lines).encode("ascii"))
        of.close()

        newrecord = ecfeventrecord.clone()
        if newrecord.value.eventcode:
            newrecord.value.submission += 1
        db.start_transaction()
        ecfeventrecord.edit_record(
            db,
            filespec.ECFEVENT_FILE_DEF,
            filespec.ECFEVENT_FIELD_DEF,
            newrecord,
        )
        db.commit()

    def _get_ecf_clubs_for_alias_map(self, database, aliasmap):
        """Return {player: ECFrefDBrecordECFclub(), ...}."""
        ecfclubs = dict()
        codes = dict()
        for a in aliasmap:
            clubcode = aliasmap[a].value.clubcode
            if clubcode:
                if clubcode not in codes:
                    codes[clubcode] = ecfrecord.get_ecf_club_for_club_code(
                        database, clubcode
                    )
                if codes[clubcode] is not None:
                    ecfclubs[a] = codes[clubcode]
        return ecfclubs

    def _get_ecf_players_for_alias_map(self, database, aliasmap):
        """Return {player: ECFrefDBrecordECFplayer(), ...}."""
        ecfplayers = dict()
        ecfmap = dict()
        codes = dict()
        get_ecf = ecfrecord.get_ecf_player_for_grading_code

        cursorid = database.database_cursor(
            filespec.MAPECFPLAYER_FILE_DEF, filespec.PERSONID_FIELD_DEF
        )
        try:
            for a in aliasmap:
                gc = None
                identity = database.encode_record_number(aliasmap[a].key.recno)
                if identity not in ecfmap:
                    r = cursorid.nearest(identity)
                    if r:
                        if database.encode_record_selector(r[0]) != identity:
                            continue
                        maprec = ecfmaprecord.get_person(database, r[-1])
                        if maprec:
                            gc = maprec.value.playercode
                            if gc:
                                if gc not in codes:
                                    codes[gc] = get_ecf(database, gc)
                                ecfmap[identity] = codes[gc]
                            else:
                                gc = maprec.value
                                if gc not in codes:
                                    codes[gc] = gc
                                ecfmap[identity] = codes[gc]
                if identity not in ecfmap:
                    ecfmap[identity] = None
                ecfplayers[a] = ecfmap[identity]

        finally:
            cursorid.close()
        return ecfplayers

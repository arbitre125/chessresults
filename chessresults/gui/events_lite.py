# events_lite.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Event panel class.
"""

import tkinter
import tkinter.messagebox
import tkinter.filedialog
import bz2
import csv
import os
import io

from solentware_misc.gui import panel, dialogue
from solentware_misc.core.utilities import AppSysPersonName

from chesscalc.gui import performance, prediction, population

from ..core import (
    constants,
    filespec,
    resultsrecord,
    ecfmaprecord,
    ecfrecord,
    gameresults,
    ecfgcodemaprecord,
    ecfogdrecord,
)
from ..core.importreports import convert_alias_to_transfer_format
from . import (
    eventgrids,
    gamesummary,
)
from .taskpanel import TaskPanel

# Move to constants.py or gameresults.py, along with ecfevent.py equivalents
HOME_PLAYER_COLOUR = {True: "White", False: "Black"}
EVENT_SUMMARY_HEADER = (
    (
        "Event",
        "Start Date",
        "End Date",
        "Section",
        "Home Team",
        "Away Team",
        "Round",
        "Date Played",
        "Board",
        "ECF Name Home Player",
        "ECF Name Away Player",
        "Home Player",
        "Away Player",
        "Result",
        "Home Player Colour",
        "Home Person Number",
        "Away Person Number",
        "Event Number",
    ),
    (
        "Grading Code",
        "ECF Name",
        "Player",
        "Game Count",
        "Person Number",
        "Event Number",
    ),
)


class Events(panel.PanelGridSelector):

    """The Events panel for a Results database."""

    _btn_dropevent = "eventslite_drop"
    _btn_exportevents = "eventslite_export"
    _btn_performance = "eventslite_performance"
    _btn_game_summary = "eventslite_game_summary"
    _btn_prediction = "eventslite_prediction"
    _btn_save = "eventslite_save"
    _btn_event_summary = "eventslite_event_summary"
    _btn_population = "eventslite_population"

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database events panel."""
        self.eventgrid = None
        super(Events, self).__init__(parent=parent, cnf=cnf, **kargs)
        self.show_event_panel_actions_allowed_buttons()
        self.create_buttons()
        (self.eventgrid,) = self.make_grids(
            (
                dict(
                    grid=eventgrids.EventGrid,
                    gridfocuskey="<KeyPress-F7>",
                ),
            )
        )

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """
        pass

    def generate_event_export(self, database, logwidget):
        """Write events selected for export to serial file."""

        def add_name_to_export(key, valuekey):
            exportdata.append(
                "=".join(
                    (
                        key,
                        resultsrecord.get_name_from_record_value(
                            database.get_primary_record(
                                filespec.NAME_FILE_DEF, valuekey
                            )
                        ).value.name,
                    )
                )
            )

        def add_game_player_to_export(
            cname, cpin, cpinfalse, caffiliation, creportedcodes
        ):
            def agpte(player):
                aliastext, m, a, affiliation, reportedcodes = player
                exportdata.append("=".join((cname, aliastext[0])))
                if aliastext[6]:
                    exportdata.append("=".join((cpin, str(aliastext[6]))))
                elif aliastext[6] is False:
                    exportdata.append("=".join((cpinfalse, "true")))
                if affiliation:
                    add_name_to_export(caffiliation, affiliation)
                if reportedcodes:
                    for rc in reportedcodes:
                        exportdata.append("=".join((creportedcodes, rc)))

            return agpte

        add_game_homeplayer_to_export = add_game_player_to_export(
            constants._homename,
            constants._homepin,
            constants._homepinfalse,
            constants._homeaffiliation,
            constants._homereportedcodes,
        )
        add_game_awayplayer_to_export = add_game_player_to_export(
            constants._awayname,
            constants._awaypin,
            constants._awaypinfalse,
            constants._awayaffiliation,
            constants._awayreportedcodes,
        )

        def add_game_to_export(game):
            v = game.value
            if gameplayers[v.homeplayer] not in eventplayers:
                return False
            if gameplayers[v.awayplayer] not in eventplayers:
                return False
            event = resultsrecord.get_event_from_record_value(
                database.get_primary_record(filespec.EVENT_FILE_DEF, v.event)
            ).value
            exportdata.append("=".join((constants._event, event.name)))
            exportdata.append(
                "=".join((constants._startdate, event.startdate))
            )
            exportdata.append("=".join((constants._enddate, event.enddate)))
            for s in event.sections:
                add_name_to_export(constants._eventsection, s)
            if v.homeplayerwhite is True:
                exportdata.append(
                    "=".join((constants._homeplayerwhite, constants._yes))
                )
            elif v.homeplayerwhite is False:
                exportdata.append(
                    "=".join((constants._homeplayerwhite, constants._no))
                )
            else:
                exportdata.append(
                    "=".join((constants._homeplayerwhite, constants._nocolor))
                )
            exportdata.append("=".join((constants._date, v.date)))
            if v.board:
                exportdata.append("=".join((constants._board, v.board)))
            if v.round:
                exportdata.append("=".join((constants._round, v.round)))
            if v.hometeam:
                add_name_to_export(constants._hometeam, v.hometeam)
            if v.awayteam:
                add_name_to_export(constants._awayteam, v.awayteam)
            if v.section:
                add_name_to_export(constants._section, v.section)
            add_game_homeplayer_to_export(players[gameplayers[v.homeplayer]])
            add_game_awayplayer_to_export(players[gameplayers[v.awayplayer]])
            exportdata.append("=".join((constants._result, v.result)))
            return True

        esel = self.eventgrid.selection
        ebkm = self.eventgrid.bookmarks
        export_events = []
        for e in ebkm:
            export_events.append(e)
        for e in esel:
            if e not in ebkm:
                export_events.append(e)

        if len(export_events) == 0:
            if logwidget:
                logwidget.append_text(
                    " ".join(
                        (
                            "Cannot export results and players",
                            "when no events selected.",
                        )
                    )
                )
                logwidget.append_text_only("")
                return
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot export results and players",
                        "when no events selected.",
                    )
                ),
                title="Events",
            )
            return

        for e in export_events:
            rv = resultsrecord.get_event_from_record_value(
                database.get_primary_record(filespec.EVENT_FILE_DEF, e[-1])
            ).value
            er = [rv.startdate, rv.enddate, rv.name]
            er.extend(
                [
                    resultsrecord.get_name_from_record_value(
                        database.get_primary_record(filespec.NAME_FILE_DEF, s)
                    ).value.name
                    for s in rv.sections
                ]
            )
            if logwidget:
                logwidget.append_text_only("\t".join(er))

        # get all aliases on exporting database
        # note identity with embedded keys translated and merge structure
        if logwidget:
            logwidget.append_text("Finding all player names on the database.")
            logwidget.append_text_only("")
        players = dict()
        gai = resultsrecord.get_alias_identity
        pr = resultsrecord.ResultsDBrecordPlayer()
        pk = pr.key
        pv = pr.value
        pr.set_database(database)
        rset = database.recordlist_ebm(filespec.PLAYER_FILE_DEF)
        cursor = rset.create_recordset_cursor()
        try:
            r = cursor.first()
            while r:
                pr.load_record(r)
                players[pk.recno] = (
                    gai(pr),
                    pv.merge,
                    pv.alias,
                    pv.affiliation,
                    pv.reported_codes,
                )
                r = cursor.next()
        finally:
            cursor.close()
            rset.close()

        # get all games for events being exported
        if logwidget:
            logwidget.append_text("Finding all games in the events.")
            logwidget.append_text_only("")
        games = []
        for event in export_events:
            eventgames = resultsrecord.get_games_for_event(
                database, resultsrecord.get_event(database, event[-1])
            )
            games.extend(eventgames)

        # get all alias keys for games being exported and map coded to decoded
        if logwidget:
            logwidget.append_text_only("")
            logwidget.append_text("Finding all player names in the events.")
        eventplayers = set()
        gameplayers = dict()
        for g in games:
            for ak in (g.value.homeplayer, g.value.awayplayer):
                k = ak  # Legacy of {coded:decoded} mapping.
                eventplayers.add(k)
                gameplayers[ak] = k
        if logwidget:
            logwidget.append_text("Preparing data for export.")
            logwidget.append_text_only("")

        # add all aliases to export data with identity last
        main_alias_values = {type(True), type(False), type(None)}
        exportdata = []
        for k, v in players.items():
            pi, pm, pa, paff, prc = v
            if type(pm) in main_alias_values:
                for a in pa:
                    if a != k:
                        exportdata.extend(
                            convert_alias_to_transfer_format(
                                players[a][0], constants._name
                            )
                        )
                exportdata.extend(
                    convert_alias_to_transfer_format(pi, constants._name)
                )
                exportdata.append(
                    "=".join((constants._exportedeventplayer, "true"))
                )

        # add all games being exported to export data
        allmerged = True
        for g in games:
            allmerged = allmerged and add_game_to_export(g)
        if not allmerged:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot generate an export file when some players in the",
                        "events being exported have not been merged or joined.",
                    )
                ),
                title="Events",
            )
            return
        self.__exportdata = exportdata
        if logwidget:
            logwidget.append_text("Ready to save export file.")
            logwidget.append_text_only("")

    def on_drop_event(self, event=None):
        """Delete selecte events."""
        self.delete_events()
        return "break"

    def on_export_events(self, event=None):
        """Export selected events."""
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            dict(
                runmethod=self.get_appsys()
                .get_results_database()
                .do_database_task,
                starttaskmsg="Export events task started",
                tabtitle="Export Events",
                runmethodargs=dict(taskmethod=self.generate_event_export),
                taskbuttons={
                    TaskPanel._btn_closebackgroundtask: dict(
                        text="Cancel",
                        tooltip="Dismiss the Export Events task log.",
                        underline=0,
                        switchpanel=True,
                        command=self._on_dismiss_exported_events,
                    ),
                    Events._btn_save: dict(
                        text="Save Exported Events",
                        tooltip="Save the Export Events.",
                        underline=2,
                        command=self._on_save_exported_events,
                    ),
                },
                starttaskbuttons=(
                    TaskPanel._btn_closebackgroundtask,
                    Events._btn_save,
                ),
            )
        )

    def on_performance(self, event=None):
        """Calculate player performances in selected events."""
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            dict(
                runmethod=self.get_appsys()
                .get_results_database()
                .do_database_task,
                starttaskmsg="Player performances task started",
                tabtitle="Performances",
                runmethodargs=dict(
                    taskmethod=self.calculate_player_performances
                ),
                taskbuttons={
                    TaskPanel._btn_closebackgroundtask: dict(
                        text="Cancel",
                        tooltip="Dismiss the Performance task log.",
                        underline=0,
                        switchpanel=True,
                        command=False,  # use default on_dismiss
                    ),
                },
                starttaskbuttons=(TaskPanel._btn_closebackgroundtask,),
            )
        )

    def on_prediction(self, event=None):
        """Calculate predicted performances for selected events over seasons."""
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            dict(
                runmethod=self.get_appsys()
                .get_results_database()
                .do_database_task,
                starttaskmsg="Predictions task started",
                tabtitle="Predictions",
                runmethodargs=dict(
                    taskmethod=self.calculate_performance_predictions
                ),
                taskbuttons={
                    TaskPanel._btn_closebackgroundtask: dict(
                        text="Cancel",
                        tooltip="Dismiss the Predictions task log.",
                        underline=0,
                        switchpanel=True,
                        command=False,  # use default on_dismiss
                    ),
                },
                starttaskbuttons=(TaskPanel._btn_closebackgroundtask,),
            )
        )

    def on_population(self, event=None):
        """Calculate populations."""
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            dict(
                runmethod=self.get_appsys()
                .get_results_database()
                .do_database_task,
                starttaskmsg="Population map analysis task started",
                tabtitle="Populations",
                runmethodargs=dict(
                    taskmethod=self.calculate_population_map_analysis
                ),
                taskbuttons={
                    TaskPanel._btn_closebackgroundtask: dict(
                        text="Cancel",
                        tooltip=(
                            "Dismiss the Population map analysis task log."
                        ),
                        underline=0,
                        switchpanel=True,
                        command=False,  # use default on_dismiss
                    ),
                },
                starttaskbuttons=(TaskPanel._btn_closebackgroundtask,),
            )
        )

    def on_game_summary(self, event=None):
        """Display game summary for each selected event."""
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            dict(
                runmethod=self.get_appsys()
                .get_results_database()
                .do_database_task,
                starttaskmsg="Game Summary by event task started",
                tabtitle="Game Summary",
                runmethodargs=dict(taskmethod=self.display_game_summary),
                taskbuttons={
                    TaskPanel._btn_closebackgroundtask: dict(
                        text="Cancel",
                        tooltip="Dismiss the Game Summary task log.",
                        underline=0,
                        switchpanel=True,
                        command=False,  # use default on_dismiss
                    ),
                },
                starttaskbuttons=(TaskPanel._btn_closebackgroundtask,),
            )
        )

    def on_event_summary(self, event=None):
        """Display event summary for selected events."""
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            dict(
                runmethod=self.get_appsys()
                .get_results_database()
                .do_database_task,
                starttaskmsg="Event summary task started",
                tabtitle="Event Summary",
                runmethodargs=dict(taskmethod=self.generate_event_summary),
                taskbuttons={
                    TaskPanel._btn_closebackgroundtask: dict(
                        text="Cancel",
                        tooltip="Dismiss the Event Summary task log.",
                        underline=0,
                        switchpanel=True,
                        command=self._on_dismiss_event_summary,
                    ),
                    Events._btn_save: dict(
                        text="Save Event Summary",
                        tooltip="Save the Event Summary.",
                        underline=2,
                        command=self._on_save_event_summary,
                    ),
                },
                starttaskbuttons=(
                    TaskPanel._btn_closebackgroundtask,
                    Events._btn_save,
                ),
            )
        )

    def _on_dismiss_exported_events(self, event=None):
        """Tidy up when finished with export event task log."""
        self.__exportdata = None

    def _on_dismiss_event_summary(self, event=None):
        """Tidy up when finished with event summary task log."""
        self.__eventsummary = None

    def _on_save_exported_events(self, event=None):
        """Save exported events dialogue."""
        if self.__exportdata is None:
            return
        filename = tkinter.filedialog.asksaveasfilename(
            parent=self.get_widget(),
            title="Export Event Results",
            defaultextension=".bz2",
            filetypes=(("bz2 compressed", "*.bz2"),),
        )
        if not filename:
            tkinter.messagebox.showwarning(
                parent=self.get_widget(),
                title="Export Event Results",
                message="Event Results export file not saved",
            )
            return
        outputfile = bz2.open(filename, mode="wt", encoding="utf8")
        outputfile.write("\n".join(self.__exportdata))
        outputfile.close()
        tkinter.messagebox.showinfo(
            parent=self.get_widget(),
            title="Export Event Results",
            message="\n".join(("Event Results saved for export in", filename)),
        )

    def _on_save_event_summary(self, event=None):
        """Save event_summary dialogue."""
        if self.__eventsummary is None:
            return
        filename = tkinter.filedialog.asksaveasfilename(
            parent=self.get_widget(),
            title="Event Summary - Filename Prefix",
            defaultextension=".bz2",
            filetypes=(("bz2 compressed", "*.bz2"),),
        )
        if not filename:
            tkinter.messagebox.showwarning(
                parent=self.get_widget(),
                title="Event Summary",
                message="Event Summary files not saved",
            )
            return
        prefix = os.path.splitext(os.path.basename(filename))[0]
        if prefix.endswith(".csv"):
            prefix = prefix[:-4]
        listfile = os.path.join(
            os.path.dirname(filename),
            ".".join(("_".join((prefix, "gamelist")), "csv", "bz2")),
        )
        countsfile = os.path.join(
            os.path.dirname(filename),
            ".".join(("_".join((prefix, "gamecounts")), "csv", "bz2")),
        )
        if not tkinter.messagebox.askokcancel(
            parent=self.get_widget(),
            message="".join(
                (
                    "The list of games will be saved in\n",
                    ".".join(
                        (
                            os.path.join(
                                "...", "_".join((prefix, "gamelist"))
                            ),
                            "csv",
                            "bz2",
                        )
                    ),
                    "\n\n",
                    "The count of games per player will be saved in\n",
                    ".".join(
                        (
                            os.path.join(
                                "...", "_".join((prefix, "gamecounts"))
                            ),
                            "csv",
                            "bz2",
                        )
                    ),
                )
            ),
            title="Event Summary - Confirm Filenames",
        ):
            return

        for f, data, header in (
            (listfile, self.__eventsummary[0], EVENT_SUMMARY_HEADER[0]),
            (countsfile, self.__eventsummary[1], EVENT_SUMMARY_HEADER[1]),
        ):
            with io.StringIO() as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(header)
                for d in data:
                    writer.writerow(d)
                bz2file = bz2.open(f, "wt")
                try:
                    bz2file.write(csvfile.getvalue())
                finally:
                    bz2file.close()
                csvfile.close()

        tkinter.messagebox.showinfo(
            parent=self.get_widget(),
            title="Event Summary",
            message="".join(
                (
                    "Game list saved in\n",
                    listfile,
                    "\n\nGame counts per player saved in\n",
                    countsfile,
                )
            ),
        )

    def delete_events(self):
        """Delete all data for selected events."""
        esel = self.eventgrid.selection
        ebkm = self.eventgrid.bookmarks
        delete_events = []
        for e in ebkm:
            delete_events.append(e)
        for e in esel:
            if e not in ebkm:
                delete_events.append(e)

        if len(delete_events) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="Cannot delete events when no events selected.",
                title="Events",
            )
            return

        db = self.get_appsys().get_results_database()
        event_report = []
        identity_report = []
        for e in delete_events:
            rec = resultsrecord.get_event_from_record_value(
                db.get_primary_record(filespec.EVENT_FILE_DEF, e[-1])
            )
            identity_report.extend(
                self.player_identification_dependant_on_event(db, rec)
            )
            rv = rec.value
            er = [rv.startdate, rv.enddate, rv.name]
            er.extend(
                [
                    resultsrecord.get_name_from_record_value(
                        db.get_primary_record(filespec.NAME_FILE_DEF, s)
                    ).value.name
                    for s in rv.sections
                ]
            )
            event_report.append("\t".join(er))
        if identity_report:
            head = "".join(
                (
                    " ".join(
                        (
                            "The following events cannot be deleted because the",
                            "players listed below use one, or more, of them as",
                            "part of their main identification:",
                        )
                    ),
                    "\n\n",
                    "\n".join(event_report),
                    "\n\n",
                    " ".join(
                        (
                            "Any events not mentioned in the list of players can",
                            "be deleted by adjusting the event selection.",
                        )
                    ),
                )
            )
            dialogue.Report(
                parent=self,
                title="Delete Events",
                action_titles={"Save": "Save Event Details"},
                wrap=tkinter.WORD,
                tabstyle="tabular",
            ).append(
                "\n\n".join(
                    (
                        head,
                        "\n".join(
                            [
                                resultsrecord.get_player_name_text_tabs(
                                    db, i.value.identity()
                                )
                                for i in identity_report
                            ]
                        ),
                    )
                )
            )
            return
        else:
            dlg = dialogue.ModalConfirm(
                parent=self,
                title="Confirm Delete Events",
                text="\n\n".join(
                    (
                        "The events listed below will be deleted",
                        "\n".join(event_report),
                    )
                ),
                action_titles={
                    "Cancel": "Cancel Delete Events",
                    "Ok": "Delete Events",
                },
                # close=('Cancel', 'Cancel Delete Events', 'Tooltip',),
                # ok=('Ok', 'Delete Events', 'Tooltip',),
                wrap=tkinter.WORD,
                tabstyle="tabular",
            )
            if not dlg.ok_pressed():
                return

        def unset_name(skey):
            """Get name record and decrement reference count."""
            if skey not in names:
                names[skey] = resultsrecord.get_name_from_record_value(
                    db.get_primary_record(filespec.NAME_FILE_DEF, skey)
                )
                namesamend[skey] = names[skey].clone()
            namesamend[skey].value.reference_count -= 1

        def unset_player(skey):
            """Get player record and decrement reference counts for names."""
            if skey not in players:
                players[skey] = resultsrecord.get_alias(db, skey)
                a = players[skey].value.affiliation
                if a is not None:
                    unset_name(a)
                if players[skey].value.section:
                    unset_name(players[skey].value.section)

        events = dict()
        games = []
        players = dict()
        names = dict()
        namesamend = dict()

        db.start_transaction()
        for e in delete_events:
            events[e[-1]] = resultsrecord.get_event_from_record_value(
                db.get_primary_record(filespec.EVENT_FILE_DEF, e[-1])
            )
            for s in events[e[-1]].value.sections:
                unset_name(s)
            games.extend(
                resultsrecord.get_games_for_event(
                    db, self.eventgrid.objects[e]
                )
            )
        for g in games:
            for s in (g.value.awayteam, g.value.hometeam, g.value.section):
                if s is not None:
                    unset_name(s)
            for p in (g.value.homeplayer, g.value.awayplayer):
                unset_player(p)

        for g in games:
            g.delete_record(db, filespec.GAME_FILE_DEF)
        for n in names:
            if n in namesamend:
                rc = namesamend[n].value.reference_count
                if rc <= 0:
                    names[n].delete_record(db, filespec.NAME_FILE_DEF)
                elif names[n].value.reference_count != rc:
                    names[n].edit_record(
                        db,
                        filespec.NAME_FILE_DEF,
                        filespec.NAME_FIELD_DEF,
                        namesamend[n],
                    )
        for p in players:
            if isinstance(players[p].value.merge, int):
                prforp = resultsrecord.get_person_from_alias(db, players[p])
                prforpamend = prforp.clone()
                prforpamend.value.alias.remove(p)
                prforp.edit_record(
                    db,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYER_FIELD_DEF,
                    prforpamend,
                )
            players[p].delete_record(db, filespec.PLAYER_FILE_DEF)
        for e in events:
            events[e].delete_record(db, filespec.EVENT_FILE_DEF)
        db.commit()
        self.refresh_controls((self.eventgrid,))

    def describe_buttons(self):
        """Define all action buttons that may appear on events page."""
        self.define_button(
            self._btn_dropevent,
            text="Delete Event",
            tooltip="Delete the selected event from the database.",
            underline=2,
            command=self.on_drop_event,
        )
        self.define_button(
            self._btn_exportevents,
            text="Export Events",
            tooltip=" ".join(
                (
                    "Export event data in text format recognised by Import",
                    "Events.",
                )
            ),
            underline=1,
            switchpanel=True,
            command=self.on_export_events,
        )
        self.define_button(
            self._btn_performance,
            text="Performances",
            tooltip="Calculate player performances in selected events.",
            underline=3,
            switchpanel=True,
            command=self.on_performance,
        )
        self.define_button(
            self._btn_prediction,
            text="Predictions",
            tooltip="Calculate performance predictions in selected events.",
            underline=5,
            switchpanel=True,
            command=self.on_prediction,
        )
        self.define_button(
            self._btn_population,
            text="Population",
            tooltip="Calculate population map analysis in selected events.",
            underline=1,
            switchpanel=True,
            command=self.on_population,
        )
        self.define_button(
            self._btn_game_summary,
            text="Game Summary",
            tooltip="Show game summary for selected events.",
            underline=2,
            switchpanel=True,
            command=self.on_game_summary,
        )
        self.define_button(
            self._btn_event_summary,
            text="Event Summary",
            tooltip="Show event summary for selected events.",
            underline=-1,
            switchpanel=True,
            command=self.on_event_summary,
        )

    def player_identification_dependant_on_event(self, database, event):
        """Return list of players in event used as main identifier of person."""
        players = set()
        identifiers = []
        for g in resultsrecord.get_games_for_event(database, event):
            for p in (g.value.homeplayer, g.value.awayplayer):
                players.add(p)
        for p in players:
            a = resultsrecord.get_alias(database, p)
            if len(a.value.get_alias_list()):
                identifiers.append(a)
            elif a.value.merge is False:
                identifiers.append(a)
            elif a.value.merge is True:
                identifiers.append(a)
        return identifiers

    def show_event_panel_actions_allowed_buttons(self):
        """Specify buttons to show on events panel."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (
                self._btn_dropevent,
                self._btn_exportevents,
                self._btn_performance,
                self._btn_prediction,
                self._btn_population,
                self._btn_game_summary,
                self._btn_event_summary,
            )
        )

    def calculate_performance_predictions(self, database, logwidget):
        """Display performance predictions for selected events."""
        esel = self.eventgrid.selection
        ebkm = self.eventgrid.bookmarks
        calculate_events = []
        for e in ebkm:
            calculate_events.append(e)
        for e in esel:
            if e not in ebkm:
                calculate_events.append(e)

        if len(calculate_events) == 0:
            if logwidget:
                logwidget.append_text(
                    " ".join(
                        (
                            "Cannot calculate performance predictions",
                            "when no events selected.",
                        )
                    )
                )
                logwidget.append_text_only("")
                return
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot calculate performance predictions",
                        "when no events selected.",
                    )
                ),
                title="Events",
            )
            return

        ro = []
        for e in calculate_events:
            rv = resultsrecord.get_event_from_record_value(
                database.get_primary_record(filespec.EVENT_FILE_DEF, e[-1])
            ).value
            er = [rv.name, rv.startdate, rv.enddate, rv.name]
            er.extend(
                [
                    resultsrecord.get_name_from_record_value(
                        database.get_primary_record(filespec.NAME_FILE_DEF, s)
                    ).value.name
                    for s in rv.sections
                ]
            )
            ro.append(er)
        event_report = []
        for er in sorted(ro):
            event_report.append("\t".join(er[1:]))
        if logwidget:
            logwidget.append_text(
                "Finding players and game results for selected events"
            )
            logwidget.append_text_only("")
        gefpc = resultsrecord.get_events_for_performance_prediction(
            database, calculate_events
        )
        if gefpc is None:
            if logwidget:
                logwidget.append_text(
                    " ".join(
                        (
                            "Cannot resolve all player identities.  This may be ",
                            "because one or more players in the selected events have ",
                            "not been merged on the New Players tab.",
                        )
                    )
                )
                logwidget.append_text_only("")
                return
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot resolve all player identities.  This may be ",
                        "because one or more players in the selected events have ",
                        "not been merged on the New Players tab.",
                    )
                ),
                title="Events",
            )
            return
        names = gefpc[-1]
        for k in names.keys():
            aspn = AppSysPersonName(names[k])
            names[k] = (aspn.name, names[k])
        if logwidget:
            logwidget.append_text(
                "Calculating performances and season comparisions."
            )
            logwidget.append_text_only("")
        prediction.Prediction(
            self,
            "Calculate Performance Distributions",
            "\n".join(event_report),
            *gefpc
        )
        if logwidget:
            logwidget.append_text("Calculations completed.")
            logwidget.append_text_only("")
        return

    def calculate_player_performances(self, database, logwidget):
        """Display player performances for selected events."""
        esel = self.eventgrid.selection
        ebkm = self.eventgrid.bookmarks
        calculate_events = []
        for e in ebkm:
            calculate_events.append(e)
        for e in esel:
            if e not in ebkm:
                calculate_events.append(e)

        if len(calculate_events) == 0:
            if logwidget:
                logwidget.append_text(
                    " ".join(
                        (
                            "Cannot calculate player performances",
                            "when no events selected.",
                        )
                    )
                )
                logwidget.append_text_only("")
                return
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot calculate player performances",
                        "when no events selected.",
                    )
                ),
                title="Events",
            )
            return

        event_report = []
        for e in calculate_events:
            rv = resultsrecord.get_event_from_record_value(
                database.get_primary_record(filespec.EVENT_FILE_DEF, e[-1])
            ).value
            er = [rv.startdate, rv.enddate, rv.name]
            er.extend(
                [
                    resultsrecord.get_name_from_record_value(
                        database.get_primary_record(filespec.NAME_FILE_DEF, s)
                    ).value.name
                    for s in rv.sections
                ]
            )
            event_report.append("\t".join(er))
        if logwidget:
            logwidget.append_text(
                "Finding players and game results for selected events"
            )
            logwidget.append_text_only("")
        gefpc = resultsrecord.get_events_for_performance_calculation(
            database, calculate_events
        )
        if gefpc is None:
            if logwidget:
                logwidget.append_text_only("")
                logwidget.append_text(
                    " ".join(
                        (
                            "Cannot resolve all player identities.  This may be ",
                            "because one or more players in the selected events have ",
                            "not been merged on the New Players tab.",
                        )
                    )
                )
                logwidget.append_text_only("")
                return
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot resolve all player identities.  This may be ",
                        "because one or more players in the selected events have ",
                        "not been merged on the New Players tab.",
                    )
                ),
                title="Events",
            )
            return
        if logwidget:
            logwidget.append_text("Calculating player performances.")
            logwidget.append_text_only("")
        names = gefpc[-1]
        for k in names.keys():
            aspn = AppSysPersonName(names[k])
            names[k] = (aspn.name, names[k])
        performance.Performance(
            self,
            "Calculate Player Performances",
            "\n".join(event_report),
            *gefpc
        )
        if logwidget:
            logwidget.append_text("Calculations completed.")
            logwidget.append_text_only("")
        return

    def calculate_population_map_analysis(self, database, logwidget):
        """Display population map analysis for selected events."""
        esel = self.eventgrid.selection
        ebkm = self.eventgrid.bookmarks
        calculate_events = []
        for e in ebkm:
            calculate_events.append(e)
        for e in esel:
            if e not in ebkm:
                calculate_events.append(e)

        if len(calculate_events) == 0:
            if logwidget:
                logwidget.append_text(
                    " ".join(
                        (
                            "Cannot calculate population map analysis",
                            "when no events selected.",
                        )
                    )
                )
                logwidget.append_text_only("")
                return
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot calculate population map analysis",
                        "when no events selected.",
                    )
                ),
                title="Events",
            )
            return

        ro = []
        for e in calculate_events:
            rv = resultsrecord.get_event_from_record_value(
                database.get_primary_record(filespec.EVENT_FILE_DEF, e[-1])
            ).value
            er = [rv.name, rv.startdate, rv.enddate, rv.name]
            er.extend(
                [
                    resultsrecord.get_name_from_record_value(
                        database.get_primary_record(filespec.NAME_FILE_DEF, s)
                    ).value.name
                    for s in rv.sections
                ]
            )
            ro.append(er)
        event_report = []
        for er in sorted(ro):
            event_report.append("\t".join(er[1:]))
        if logwidget:
            logwidget.append_text(
                "Finding players and game results for selected events"
            )
            logwidget.append_text_only("")
        gefpc = resultsrecord.get_events_for_performance_calculation(
            database, calculate_events
        )
        if gefpc is None:
            if logwidget:
                logwidget.append_text(
                    " ".join(
                        (
                            "Cannot resolve all player identities.  This may be ",
                            "because one or more players in the selected events have ",
                            "not been merged on the New Players tab.",
                        )
                    )
                )
                logwidget.append_text_only("")
                return
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot resolve all player identities.  This may be ",
                        "because one or more players in the selected events have ",
                        "not been merged on the New Players tab.",
                    )
                ),
                title="Events",
            )
            return
        names = gefpc[-1]
        for k in names.keys():
            aspn = AppSysPersonName(names[k])
            names[k] = (aspn.name, names[k])
        if logwidget:
            logwidget.append_text(
                "Calculating population map analysis and details."
            )
            logwidget.append_text_only("")
        population.Population(
            self,
            "Calculate Population Map Analysis",
            "\n".join(event_report),
            *gefpc
        )
        if logwidget:
            logwidget.append_text("Calculations completed.")
            logwidget.append_text_only("")
        return

    def display_game_summary(self, database, logwidget):
        """Display game summary for selected events."""
        esel = self.eventgrid.selection
        ebkm = self.eventgrid.bookmarks
        summary_events = []
        for e in ebkm:
            summary_events.append(e)
        for e in esel:
            if e not in ebkm:
                summary_events.append(e)

        if len(summary_events) == 0:
            if logwidget:
                logwidget.append_text(
                    " ".join(
                        (
                            "Cannot display game summary",
                            "when no events selected.",
                        )
                    )
                )
                logwidget.append_text_only("")
                return
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    ("Cannot display game summary", "when no events selected.")
                ),
                title="Events",
            )
            return

        if logwidget:
            logwidget.append_text("Extracting game summaries for each event.")
            logwidget.append_text_only("")
        for e in summary_events:
            gamesummary.GameSummary(self, database, e)
        if logwidget:
            logwidget.append_text("Extract completed.")
            logwidget.append_text_only("")

    def generate_event_summary(self, database, logwidget):
        """Write events selected for summary to serial file."""
        esel = self.eventgrid.selection
        ebkm = self.eventgrid.bookmarks
        summary_events = []
        for e in ebkm:
            summary_events.append(e)
        for e in esel:
            if e not in ebkm:
                summary_events.append(e)

        if len(summary_events) == 0:
            if logwidget:
                logwidget.append_text(
                    " ".join(
                        (
                            "Cannot generate event summary",
                            "when no events selected.",
                        )
                    )
                )
                logwidget.append_text_only("")
                return
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        (
                            "Cannot generate event summary",
                            "when no events selected.",
                        )
                    ),
                    title="Events",
                ),
            )
            return

        for e in summary_events:
            rv = resultsrecord.get_event_from_record_value(
                database.get_primary_record(filespec.EVENT_FILE_DEF, e[-1])
            ).value
            er = [rv.startdate, rv.enddate, rv.name]
            er.extend(
                [
                    resultsrecord.get_name_from_record_value(
                        database.get_primary_record(filespec.NAME_FILE_DEF, s)
                    ).value.name
                    for s in rv.sections
                ]
            )
            if logwidget:
                logwidget.append_text_only("\t".join(er))

        # get all games for events included in summary
        if logwidget:
            logwidget.append_text_only("")
            logwidget.append_text("Finding all games in the events.")
            logwidget.append_text_only("")
        games = []
        for event in summary_events:
            eventgames = resultsrecord.get_games_for_event(
                database, resultsrecord.get_event(database, event[-1])
            )
            games.extend(eventgames)
        if logwidget:
            logwidget.append_text("Finding detail of all games in the events.")
            logwidget.append_text_only("")
        # get encoded data for games in events included in summary
        players = set()
        teams = set()
        sections = set()
        events = set()
        gamecounts = dict()
        for g in games:
            for ak in (g.value.homeplayer, g.value.awayplayer):
                players.add(ak)
                gamecounts[ak] = gamecounts.setdefault(ak, 0) + 1
            for tk in (g.value.hometeam, g.value.awayteam):
                teams.add(tk)
            sections.add(g.value.section)
            events.add(g.value.event)
        # Extract translations for encoded game data
        events = {
            e: resultsrecord.get_event_from_record_value(
                database.get_primary_record(filespec.EVENT_FILE_DEF, e)
            ).value
            for e in events
        }
        teams = {
            t: resultsrecord.get_name_from_record_value(
                database.get_primary_record(filespec.NAME_FILE_DEF, t)
            ).value.name
            if t
            else ""
            for t in teams
        }
        sections = {
            s: resultsrecord.get_name_from_record_value(
                database.get_primary_record(filespec.NAME_FILE_DEF, s)
            ).value.name
            if s
            else ""
            for s in sections
        }

        # gradingcodes below needs the first step in setting players.
        players = {p: resultsrecord.get_alias(database, p) for p in players}

        # Generate unique number for each person.
        personnumbers = {}
        personevents = {}
        for k, v in players.items():
            personevents[k] = v.value.event
            m = v.value.merge
            if m in (None, False):
                m = k
            if m not in personnumbers:
                personnumbers[m] = len(personnumbers)
            if k not in personnumbers:
                personnumbers[k] = personnumbers[m]

        # Generate unique number for each event.
        eventnumbers = {}
        for k in events:
            if k not in eventnumbers:
                eventnumbers[k] = len(eventnumbers)

        # Maybe put this in subclass methods eventually.
        if self.get_appsys().show_master_list_grading_codes:
            gradingcodes = {
                p: ecfmaprecord.get_merge_grading_code_for_person(
                    database, person
                )
                for p, person in resultsrecord.get_persons(
                    database, players
                ).items()
            }
        elif self.get_appsys().show_grading_list_grading_codes:
            gradingcodes = {
                p: ecfgcodemaprecord.get_grading_code_for_person(
                    database, person
                )
                for p, person in resultsrecord.get_persons(
                    database, players
                ).items()
            }
        else:
            gradingcodes = {}

        # gradingcodes above needed the first step in setting players.
        players = {p: players[p].value.name for p in players}

        # Maybe put this in subclass methods eventually.
        # gradingcodes values like (key, None) occur sometimes, origin unknown
        # but seen only when mixing event imports and ecf reference data
        # imports.
        # Ignoring them should be correct, and seems ok too.
        # Find and delete them offline.
        # See basecore.ecfdataimport too.
        if self.get_appsys().show_master_list_grading_codes:
            ecfplayers = {}
            for p in gradingcodes:
                if gradingcodes[p]:
                    r = ecfrecord.get_ecf_player_for_grading_code(
                        database, gradingcodes[p]
                    )
                    if r:
                        ecfplayers[p] = r.value.ECFname
                    else:
                        ecfplayers[p] = ""
                else:
                    ecfplayers[p] = ""
        elif self.get_appsys().show_grading_list_grading_codes:
            ecfplayers = {
                p: ecfogdrecord.get_ecf_ogd_player_for_grading_code(
                    database, gradingcodes[p]
                ).value.ECFOGDname
                if gradingcodes[p]
                else ""
                for p in gradingcodes
            }
        else:
            ecfplayers = {}

        # Prepare sorted list of games using decoded values from game records
        games = sorted(
            [
                (
                    events[g.value.event].name,
                    events[g.value.event].startdate,
                    events[g.value.event].enddate,
                    sections[g.value.section],
                    teams[g.value.hometeam],
                    teams[g.value.awayteam],
                    g.value.round if g.value.round else "",
                    g.value.date if g.value.date else "",
                    g.value.board if g.value.board else "",
                    ecfplayers[g.value.homeplayer]
                    if g.value.homeplayer in ecfplayers
                    else "",
                    ecfplayers[g.value.awayplayer]
                    if g.value.awayplayer in ecfplayers
                    else "",
                    players[g.value.homeplayer],
                    players[g.value.awayplayer],
                    gameresults.displayresult.get(g.value.result, ""),
                    HOME_PLAYER_COLOUR.get(g.value.homeplayerwhite, ""),
                    personnumbers[g.value.homeplayer],
                    personnumbers[g.value.awayplayer],
                    eventnumbers[g.value.event],
                )
                for g in games
            ]
        )

        # Prepare sorted list of games counts for player names in sources
        gamecounts = sorted(
            [
                (
                    gradingcodes[p] if p in gradingcodes else "",
                    ecfplayers[p] if p in ecfplayers else "",
                    players[p],
                    gc,
                    personnumbers[p],
                    eventnumbers[personevents[p]],
                )
                for p, gc in gamecounts.items()
            ]
        )

        self.__eventsummary = (games, gamecounts)
        if logwidget:
            logwidget.append_text("Ready to save event summary.")
            logwidget.append_text_only("")

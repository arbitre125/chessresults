# events.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Event panel class.
"""
import tkinter.messagebox

from ..core import resultsrecord
from ..core import ecfmaprecord
from ..core import filespec
from . import events_lite


class Events(events_lite.Events):

    """The Events panel for a Results database."""

    _btn_ecfplayers = "events_players"

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database events panel."""
        super(Events, self).__init__(parent=parent, cnf=cnf, **kargs)

    def on_ecf_players(self, event=None):
        """Do processing for buttons with command set to on_ecf_players."""
        self.update_players_to_ecf()
        return "break"

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
            self._btn_join_event_new_players,
            text="Join Event New Players",
            tooltip="Join new players with same same as earlier events.",
            underline=0,
            switchpanel=True,
            command=self.on_join_event_new_players,
        )
        self.define_button(
            self._btn_ecfplayers,
            text="To ECF",
            tooltip=(
                "Update list of players with results for submission to ECF."
            ),
            underline=1,
            command=self.on_ecf_players,
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
            underline=7,
            switchpanel=True,
            command=self.on_event_summary,
        )

    def show_event_panel_actions_allowed_buttons(self):
        """Specify buttons to show on events panel."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (
                self._btn_dropevent,
                self._btn_join_event_new_players,
                self._btn_ecfplayers,
                self._btn_exportevents,
                self._btn_game_summary,
                self._btn_event_summary,
            )
        )

    def update_players_to_ecf(self):
        """Add players in event to players whose results to be sent to ECF."""
        esel = self.eventgrid.selection
        ebkm = self.eventgrid.bookmarks
        update_events = []
        for e in ebkm:
            update_events.append(e)
        for e in esel:
            if e not in ebkm:
                update_events.append(e)

        if len(update_events) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot update lists of events and players for",
                        "submission to ECF when no events selected.",
                    )
                ),
                title="Events",
            )
            return
        else:
            if len(update_events) == 1:
                txt = "One event"
            else:
                txt = " ".join((str(len(update_events)), "events"))
            if not tkinter.messagebox.askyesno(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        txt,
                        "selected for updating lists of events and",
                        "players for submission to ECF.\nDo",
                        "you wish to continue?",
                    )
                ),
                title="Events",
            ):
                return

        mapclub = ecfmaprecord.ECFmapDBrecordClub()
        mapplayer = ecfmaprecord.ECFmapDBrecordPlayer()
        db = self.get_appsys().get_results_database()
        ccount = 0
        pcount = 0
        db.start_transaction()
        mapclubcursor = db.database_cursor(
            filespec.MAPECFCLUB_FILE_DEF, filespec.PLAYERALIASID_FIELD_DEF
        )
        try:
            mapplayercursor = db.database_cursor(
                filespec.MAPECFPLAYER_FILE_DEF, filespec.PERSONID_FIELD_DEF
            )
            try:
                for event in update_events:
                    games = resultsrecord.get_games_for_event(
                        db,
                        resultsrecord.get_event_from_record_value(
                            db.get_primary_record(
                                filespec.EVENT_FILE_DEF, event[-1]
                            )
                        ),
                    )
                    players = resultsrecord.get_players(
                        db, resultsrecord.get_aliases_for_games(db, games)
                    )
                    persons = resultsrecord.get_persons(db, players)
                    for p in players:
                        skey = db.encode_record_number(players[p].key.recno)
                        r = mapclubcursor.nearest(skey)
                        if r is not None:
                            if db.encode_record_selector(r[0]) == skey:
                                continue
                        mapclub.empty()
                        mapclub.value.playerkey = repr(players[p].key.recno)
                        mapclub.value.playername = players[
                            p
                        ].value.identity_packed()
                        mapclub.key.recno = None
                        mapclub.put_record(db, filespec.MAPECFCLUB_FILE_DEF)
                        ccount += 1

                        # DPT database engine returns new cursor with fresh
                        # recordset. bsddb and sqlite3 database engines return
                        # mapclubcursor but do nothing else.
                        mapclubcursor = db.repair_cursor(
                            mapclubcursor,
                            filespec.MAPECFCLUB_FILE_DEF,
                            filespec.PLAYERALIASID_FIELD_DEF,
                        )

                    for p in persons:
                        skey = db.encode_record_number(persons[p].key.recno)
                        r = mapplayercursor.nearest(skey)
                        if r is not None:
                            if db.encode_record_selector(r[0]) == skey:
                                continue
                        mapplayer.empty()
                        mapplayer.value.playerkey = repr(persons[p].key.recno)
                        mapplayer.value.playername = persons[
                            p
                        ].value.identity_packed()
                        mapplayer.key.recno = None
                        mapplayer.put_record(
                            db, filespec.MAPECFPLAYER_FILE_DEF
                        )
                        pcount += 1

                        # DPT database engine returns new cursor with fresh
                        # recordset. bsddb and sqlite3 database engines return
                        # mapplayercursor but do nothing else.
                        mapplayercursor = db.repair_cursor(
                            mapplayercursor,
                            filespec.MAPECFPLAYER_FILE_DEF,
                            filespec.PERSONID_FIELD_DEF,
                        )

            finally:
                mapplayercursor.close()
        finally:
            mapclubcursor.close()
        # if ccount or pcount:
        #    db.commit()
        db.commit()

        if pcount:
            pmsg = " ".join(
                (
                    str(pcount),
                    "players added to list of players awaiting",
                    "attachment to grading codes",
                )
            )
            self.refresh_controls(
                (
                    (
                        db,
                        filespec.MAPECFPLAYER_FILE_DEF,
                        filespec.PERSONMAP_FIELD_DEF,
                    ),
                )
            )
        else:
            pmsg = " ".join(
                (
                    "No players needed adding to list of players awaiting",
                    "attachment to grading codes",
                )
            )
        if ccount:
            cmsg = " ".join(
                (
                    str(ccount),
                    "players added to list of players awaiting",
                    "attachment to ECF clubs",
                )
            )
            self.refresh_controls(
                (
                    (
                        db,
                        filespec.MAPECFCLUB_FILE_DEF,
                        filespec.PLAYERALIASMAP_FIELD_DEF,
                    ),
                )
            )
        else:
            cmsg = " ".join(
                (
                    "No players needed adding to list of players awaiting",
                    "attachment to ECF clubs",
                )
            )
        dlg = tkinter.messagebox.showinfo(
            parent=self.get_widget(),
            message="\n".join((pmsg, cmsg)),
            title="Events",
        )

# joineventplayers.py
# Copyright 2017 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Display detail of name's involvement in earlier editions of event.

A player is likely referred to using the same name from year to year in an
event.  An ECF grading code will have been used to report the results for
grading.

The option to merge the name from the current event with the earlier editions
is offered, which will cause the same ECF grading code to be used to report
results for the current event.

"""
import tkinter.messagebox

from solentware_misc.gui import panel

from . import eventplayergrids, playerdetail
from ..basecore import playerfind
from ..core import resultsrecord, filespec, mergeplayers


class JoinEventPlayers(panel.PanedPanelGridSelector):

    """The New Players panel for a Results database."""

    _btn_join = "joineventplayers_join"
    _btn_cancel = "joineventplayers_cancel"
    _btn_person = "joineventplayers_person"

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database events panel."""
        self.joineventplayersgrid = None
        super().__init__(parent=parent, cnf=cnf, **kargs)
        self.show_join_event_players_panel_actions_allowed_buttons()
        self.create_buttons()
        (self.joineventplayersgrid,) = self.make_grids(
            (
                dict(
                    grid=eventplayergrids.EventPlayerGrid,
                    gridfocuskey="<KeyPress-F7>",
                ),
            )
        )

    def show_join_event_players_panel_actions_allowed_buttons(self):
        """Specify buttons to show on join event's players panel."""
        # Do nothing. All buttons shown by default.

    def describe_buttons(self):
        """Define all action buttons that may appear on join event's players
        page.
        """
        super().describe_buttons()
        self.define_button(
            self._btn_join,
            text="Join",
            tooltip="Join selected players to use grading codes shown.",
            underline=0,
            command=self.on_join,
        )
        self.define_button(
            self._btn_person,
            text="Player Details",
            tooltip="Show details, including all aliases, of selected player.",
            underline=5,
            command=self.on_person,
        )
        self.define_button(
            self._btn_cancel,
            text="Cancel",
            tooltip="Return to Event panel without joining selected players",
            underline=5,
            switchpanel=True,
            command=self.on_cancel,
        )

    def on_join(self, event=None):
        """ """
        msgtitle = "Join Event Players"
        psel = self.joineventplayersgrid.selection
        pbkm = self.joineventplayersgrid.bookmarks

        if len(psel) + len(pbkm) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="No players selected for join.",
                title=msgtitle,
            )
            return

        if not tkinter.messagebox.askokcancel(
            parent=self.get_widget(),
            message="".join(
                (
                    "Please confirm the selected players are to be ",
                    "joined with same-named players in other ",
                    "editions of this event.",
                )
            ),
            title=msgtitle,
        ):
            return

        selected = {s[0] for s in psel + pbkm}
        db = self.get_appsys().get_results_database()
        event = resultsrecord.get_event_from_record_value(
            db.get_primary_record(
                filespec.EVENT_FILE_DEF,
                self.get_appsys()
                .get_event_detail_context()
                .eventgrid.selection[0][-1],
            )
        )
        for k, v in playerfind.find_player_names_in_other_editions_of_event(
            db, event
        ).items():
            if k not in selected:
                continue
            person = resultsrecord.get_alias(db, v[1])
            merges = [resultsrecord.get_alias(db, k)]
            message = mergeplayers.merge_new_players(db, person, merges)
            if message:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(), message=message, title=msgtitle
                )
            else:
                selected.discard(k)
            self.joineventplayersgrid.datasource.remove_record_from_recordset(
                k
            )
        self.joineventplayersgrid.bookmarks[:] = []
        self.joineventplayersgrid.selection[:] = []
        self.refresh_controls(
            (
                (db, filespec.PLAYER_FILE_DEF, filespec.PLAYER_FILE_DEF),
                (
                    db,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYERPARTIALNEW_FIELD_DEF,
                ),
                (db, filespec.PLAYER_FILE_DEF, filespec.PLAYERNAME_FIELD_DEF),
                (
                    db,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYERNAMEIDENTITY_FIELD_DEF,
                ),
            )
        )

    def on_cancel(self, event=None):
        """Do nothing."""
        # define_button has switchpanel=True which gets the action done.

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """
        pass

    def on_person(self, event=None):
        """Display details for a player."""
        self.display_player_details()
        return "break"

    def display_player_details(self):
        """Display identity for alias and aliases associated with identity."""
        title = "Player Details"
        psel = self.joineventplayersgrid.selection
        if len(psel) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Please select the player, or players, for whom",
                        "details are to be displayed",
                    )
                ),
                title=title,
            )
            return
        if len(psel) > 1:
            if not tkinter.messagebox.askyesno(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Confirm that details for multiple players are to be",
                        "displayed",
                    )
                ),
                title=title,
            ):
                return

        found = False
        db = self.get_appsys().get_results_database()
        pk = self.joineventplayersgrid.datasource.map_newplayer_to_knownplayer
        for k, v in pk.items():
            if k == psel[0][0]:
                pr = resultsrecord.get_alias(db, v[1])
                playerdetail.display_player_details(
                    self, ([(pr.srvalue, pr.key.recno)],), title
                )
                found = True
        if not found:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Unable to display details for seleted player.\n\n",
                        "Probably you will have to use the New Player tab to ",
                        "deal with this player.",
                    )
                ),
                title=title,
            )
            return

# newplayers.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database NewPlayers panel class.

Identify new players.  Declare the new player to be the same as one already
on database or to be new to this database.

"""
import tkinter
import tkinter.messagebox

from solentware_misc.gui import panel, dialogue

from . import playergrids
from . import playerdetail
from ..core import resultsrecord
from ..core import mergeplayers
from ..core import filespec


class NewPlayers(panel.PanedPanelGridSelectorBar):

    """The New Players panel for a Results database."""

    _btn_merge = "newplayers_merge"
    _btn_join = "newplayers_join"
    _btn_person_details = "newplayers_details"

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database new player panel."""
        self.newplayergrid = None
        self.playergrid = None

        super(NewPlayers, self).__init__(parent=parent, cnf=cnf, **kargs)

        self.show_panel_buttons((self._btn_merge,))
        self.create_buttons()

        self.newplayergrid, self.playergrid = self.make_grids(
            (
                dict(
                    grid=playergrids.NewGrid,
                    selectlabel="Select New Player:  ",
                    gridfocuskey="<KeyPress-F7>",
                    selectfocuskey="<KeyPress-F5>",
                    slavegrids=("<KeyPress-F8>",),
                ),
                dict(
                    grid=playergrids.AliasLinkGrid,
                    selectlabel="Select Player Reference:  ",
                    gridfocuskey="<KeyPress-F8>",
                    selectfocuskey="<KeyPress-F6>",
                ),
            )
        )

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """
        pass

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

    def join_merged_players(self):
        """Merge identified players after confirmation dialogue.

        Two or more sets of identified players may later turn out to be same
        player.  This method merges the sets into one.

        """
        msgtitle = "Join Merged Players"
        psel = self.playergrid.selection
        pbkm = self.playergrid.bookmarks

        if len(psel) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="No player selected as main entry after join.",
                title=msgtitle,
            )
            return

        if len(pbkm) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="No players selected for join.",
                title=msgtitle,
            )
            return

        if len(psel) > 1:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="Select one player as main entry after join.",
                title=msgtitle,
            )
            return

        if pbkm == psel:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="No players selected for join to main entry.",
                title=msgtitle,
            )
            return

        db = self.get_appsys().get_results_database()
        mainentry = mergeplayers.get_person_for_alias_key(db, psel[0])
        if mainentry is None:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="Cannot find identified player for selection.",
                title=msgtitle,
            )
            return
        gpfak = mergeplayers.get_persons_for_alias_keys(db, pbkm)
        if None in gpfak:
            msg = []
            for k in gpfak[None]:
                msg.append(resultsrecord.get_player_name_text_tabs(db, k[0]))
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "The selected players listed cannot be joined:\n\n",
                        "\n".join(msg),
                    )
                ),
                title=msgtitle,
            )
            return
        mkp = mainentry.key.pack()
        entries = [v for k, v in gpfak.items() if k != mkp]
        if not entries:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="The selected players are already joined.",
                title=msgtitle,
            )
            return
        h = []
        r = []
        h.append(
            "\n".join(
                (
                    "".join(
                        (
                            resultsrecord.get_player_name_text_tabs(
                                db, mainentry.value.identity()
                            ),
                        )
                    ),
                    " ".join(
                        (
                            "\nwill become the main entry on the existing player list",
                            "for the following aliases. These aliases will be",
                            "removed from the list if main entries only are listed",
                            "and will lose any main entry highlighting otherwise.\n",
                        )
                    ),
                )
            )
        )
        for e in entries:
            h.append(
                "".join(
                    (
                        resultsrecord.get_player_name_text_tabs(
                            db, e.value.identity()
                        ),
                    )
                )
            )

        def generate_report(mainrecord):
            ra = []
            for alias in mainrecord.value.get_alias_list():
                aliasrecord = resultsrecord.get_alias(db, alias)
                if aliasrecord is None:
                    dlg = tkinter.messagebox.showinfo(
                        parent=self.get_widget(),
                        message="".join(
                            (
                                "Record for player\n",
                                resultsrecord.get_player_name_text(
                                    db, aliasrecord.value.identity()
                                ),
                                "\ndoes not exist.",
                            )
                        ),
                        title=msgtitle,
                    )
                    return
                ra.append(
                    "".join(
                        (
                            resultsrecord.get_player_name_text_tabs(
                                db, aliasrecord.value.identity()
                            ),
                        )
                    ),
                )
            return ra

        ra = generate_report(mainentry)
        if ra is None:
            return
        if ra:
            r.append(
                "\n".join(
                    (
                        " ".join(("The current aliases of\n",)),
                        "".join(
                            (
                                resultsrecord.get_player_name_text_tabs(
                                    db, mainentry.value.identity()
                                ),
                            )
                        ),
                        " ".join(("\nwill be kept. These are\n",)),
                    )
                )
            )
            r.extend(ra)
        else:
            r.append(
                "\n".join(
                    (
                        "".join(
                            (
                                resultsrecord.get_player_name_text_tabs(
                                    db, mainentry.value.identity()
                                ),
                            )
                        ),
                        " ".join(("\nhas no aliases.",)),
                    )
                )
            )
        for e in entries:
            ra = generate_report(e)
            if ra is None:
                return
            if ra:
                r.append(
                    "\n".join(
                        (
                            " ".join(
                                ("\nThe entry on the existing player list\n",)
                            ),
                            "".join(
                                (
                                    resultsrecord.get_player_name_text_tabs(
                                        db, e.value.identity()
                                    ),
                                )
                            ),
                            " ".join(
                                (
                                    "\nand it's aliases",
                                    "will become aliases of the new main entry.",
                                    "The aliases are\n",
                                )
                            ),
                        )
                    )
                )
                r.extend(ra)
            else:
                r.append(
                    "\n".join(
                        (
                            " ".join(
                                ("\nThe entry on the existing player list\n",)
                            ),
                            "".join(
                                (
                                    resultsrecord.get_player_name_text_tabs(
                                        db, e.value.identity()
                                    ),
                                )
                            ),
                            " ".join(
                                (
                                    "\nhas no aliases and will become an alias of the",
                                    "new main entry.",
                                )
                            ),
                        )
                    )
                )

        cdlg = dialogue.ModalConfirm(
            parent=self,
            title=" ".join(("Confirm", msgtitle)),
            text="\n\n".join(("\n".join(h), "\n".join(r))),
            action_titles={
                "Cancel": "Cancel Merge Player Details",
                "Ok": "Merge Player Details",
            },
            # close=('Cancel', 'Cancel Merge Player Details', 'Tooltip',),
            # ok=('Ok', 'Merge Player Details', 'Tooltip',),
            wrap=tkinter.WORD,
            tabstyle="tabular",
        )

        if cdlg.ok_pressed():
            # After merging the main record for the player will have a list
            # of keys of merged records in value.alias and each subsidiary
            # record will have the key of the main record in value.merge.
            # Any keys in value.alias of the main record before this merge
            # are kept.
            # If value.alias for the main record is empty its value.merge
            # is set to False meaning main record with no merged records.
            message = mergeplayers.join_merged_players(db, mainentry, entries)
            if message:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(), message=message, title=msgtitle
                )
                return
            self.playergrid.bookmarks[:] = []
            self.playergrid.selection[:] = []
            self.clear_selector(self.playergrid)
            self.refresh_controls(
                (
                    self.newplayergrid,
                    self.playergrid,
                    (
                        db,
                        filespec.PLAYER_FILE_DEF,
                        filespec.PLAYERNAMEIDENTITY_FIELD_DEF,
                    ),
                )
            )
        return

    def merge_new_players(self):
        """Merge new players after confirmation dialogue.

        Two or more new players may be known to be the same player.  This could
        be because several versions of a player's name are used in reports of
        results for an event; or because the same player has played in several
        events recorded on the database.  This method merges the players.

        """
        msgtitle = "Merge New Player"
        nsel = self.newplayergrid.selection
        nbkm = self.newplayergrid.bookmarks
        psel = self.playergrid.selection
        pbkm = self.playergrid.bookmarks

        if len(nsel) + len(nbkm) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="No new players selected for merge.",
                title=msgtitle,
            )
            return

        db = self.get_appsys().get_results_database()
        gnpfak = mergeplayers.get_new_players_for_alias_keys(db, nbkm)
        if None in gnpfak:
            msg = []
            for k in gnpfak[None]:
                msg.append(resultsrecord.get_player_name_text_tabs(db, k[0]))
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "The selected players listed cannot be merged:\n\n",
                        "\n".join(msg),
                    )
                ),
                title=msgtitle,
            )
            return

        if len(psel) + len(pbkm) == 0:
            if len(nsel):
                playerkey = nsel[0]
            else:
                playerkey = nbkm[0]
            mainentry = mergeplayers.get_new_player_for_alias_key(
                db, playerkey
            )
            if mainentry is None:
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="Cannot find new player for selection.",
                    title=msgtitle,
                )
                return
            mkp = mainentry.key.pack()
            if mkp in gnpfak:
                del gnpfak[mkp]

        elif len(pbkm) == 1 or len(psel):
            if len(psel):
                playerkey = psel[0]
            else:
                playerkey = pbkm[0]
            mainentry = mergeplayers.get_person_for_alias_key(db, playerkey)
            if mainentry is None:
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="Cannot find identified player for selection.",
                    title=msgtitle,
                )
                return
            if len(nsel):
                r = mergeplayers.get_new_player_for_alias_key(db, nsel[0])
                if r is None:
                    dlg = tkinter.messagebox.showinfo(
                        parent=self.get_widget(),
                        message="Cannot find new player for selection.",
                        title=msgtitle,
                    )
                    return
                rkp = r.key.pack()
                if rkp not in gnpfak:
                    gnpfak[rkp] = r

        else:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Unable to choose between the selected existing",
                        "players for merging the selected new players.",
                    )
                ),
                title=msgtitle,
            )
            return

        entries = [v for k, v in gnpfak.items()]
        h = "\n".join(
            (
                " ".join(
                    (
                        "The new player entries listed below will be added",
                        "as aliases of\n",
                    )
                ),
                "".join(
                    (
                        resultsrecord.get_player_name_text_tabs(
                            db, mainentry.value.identity()
                        ),
                    )
                ),  # should the next bit be here rather than in caption
                " ".join(
                    (
                        "\nAll the entries listed below",
                        "will be removed from the new player list.",
                    )
                ),
            )
        )
        a = [
            "".join(
                (
                    resultsrecord.get_player_name_text_tabs(
                        db, e.value.identity()
                    ),
                )
            )
            for e in entries
        ]
        if len(a):
            a.insert(
                0,
                " ".join(
                    (
                        "The following new player entries will be added",
                        "as aliases:\n",
                    )
                ),
            )
        else:
            a.append("No aliases selected.")
        r = "\n".join(a)

        cdlg = dialogue.ModalConfirm(
            parent=self,
            title=" ".join(("Confirm", msgtitle)),
            text="\n\n".join((h, r)),
            action_titles={
                "Cancel": "Cancel Merge Player Details",
                "Ok": "Merge Player Details",
            },
            # close=('Cancel', 'Cancel Merge Player Details', 'Tooltip',),
            # ok=('Ok', 'Merge Player Details', 'Tooltip',),
            wrap=tkinter.WORD,
            tabstyle="tabular",
        )

        if cdlg.ok_pressed():
            # After merging the main record for the player will have a list
            # of keys of merged records in value.alias and each subsidiary
            # record will have the key of the main record in value.merge.
            # Any keys in value.alias of the main record before this merge
            # are kept.
            # If value.alias for the main record is empty its value.merge
            # is set to False meaning main record with no merged records.
            message = mergeplayers.merge_new_players(db, mainentry, entries)
            if message:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(), message=message, title=msgtitle
                )
                return
            self.newplayergrid.bookmarks[:] = []
            self.newplayergrid.selection[:] = []
            self.playergrid.selection[:] = []
            self.clear_selector(True)
            self.refresh_controls(
                (
                    self.newplayergrid,
                    self.playergrid,
                    (
                        db,
                        filespec.PLAYER_FILE_DEF,
                        filespec.PLAYERIDENTITY_FIELD_DEF,
                    ),
                    (
                        db,
                        filespec.PLAYER_FILE_DEF,
                        filespec.PLAYERNAMEIDENTITY_FIELD_DEF,
                    ),
                )
            )
        return

    def on_join(self, event=None):
        """Join two or more players into one."""
        self.join_merged_players()
        self.newplayergrid.set_select_hint_label()
        return "break"

    def on_merge(self, event=None):
        """Merge one or more new player names into a new or existing player."""
        self.merge_new_players()
        self.newplayergrid.set_select_hint_label()
        return "break"

    def on_person_details(self, event=None):
        """Display player details."""
        self.display_player_details()
        return "break"

    def display_player_details(self):
        """Display identity for alias and aliases associated with identity.

        Displays details for a player selected from any grid showing players.
        Each grid may restrict the kind of player displayed so some options
        may not apply in particular cases.

        """
        title = "Player Details"
        psel = self.playergrid.selection
        pbkm = self.playergrid.bookmarks
        if len(psel) + len(pbkm) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Please select or bookmark the player for whom",
                        "details are to be displayed",
                    )
                ),
                title=title,
            )
            return

        playerdetail.display_player_details(self, (psel, pbkm), title)
        pgo = self.playergrid.objects
        for gr in self.playergrid.bookmarks, self.playergrid.selection:
            for k in gr:
                if k in pgo:
                    pgo[k].set_background_normal(
                        self.playergrid.get_row_widgets(k)
                    )
                    self.playergrid.set_row_under_pointer_background(k)
        self.playergrid.bookmarks[:] = []
        self.playergrid.selection[:] = []

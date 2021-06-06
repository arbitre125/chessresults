# players.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Players panel class.

Show player identification details and cancel identification.  Cancelled
identifications are returned to the new player page so that identification
can be corrected.

"""
import tkinter
import tkinter.messagebox

from solentware_misc.gui import panel, reports, dialogue

from . import playergrids
from . import playerdetail
from ..core import resultsrecord
from ..core import ecfmaprecord
from ..core import mergeplayers
from ..core import filespec
from ..core import ecfgcodemaprecord


class Players(panel.PanedPanelGridSelectorBar):

    """The Players panel for a Results database."""

    _btn_aliases = "players_aliases"
    _btn_demerge_player = "players_demerge_player"
    _btn_break_merge = "players_break_merge"

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database player panel."""
        self.aliasgrid = None
        self.playergrid = None

        super(Players, self).__init__(parent=parent, cnf=cnf, **kargs)

        self.show_panel_buttons(
            (
                self._btn_aliases,
                self._btn_demerge_player,
                self._btn_break_merge,
            )
        )
        self.create_buttons()

        self.aliasgrid, self.playergrid = self.make_grids(
            (
                dict(
                    grid=playergrids.AliasGrid,
                    selectlabel="Select Player:  ",
                    gridfocuskey="<KeyPress-F7>",
                    selectfocuskey="<KeyPress-F5>",
                ),
                dict(
                    grid=playergrids.IdentityGrid,
                    selectlabel="Select Player Reference:  ",
                    gridfocuskey="<KeyPress-F8>",
                    selectfocuskey="<KeyPress-F6>",
                ),
            )
        )

    def break_one_player_merge(self):
        """Demerge selected alias from identity after confirmation dialogue.

        Main entry is selected from lower grid and entry to be demerged is
        selected from upper grid.  The lower grid will typically display main
        entries and upper grid will typically display all entries (main and
        alias).

        """
        title = "Undo selected Merge for Player"
        psel = self.playergrid.selection
        asel = self.aliasgrid.selection
        db = self.get_appsys().get_results_database()
        if len(psel) == 0:
            if len(asel) == 0:
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message=" ".join(
                        (
                            "Please select the main alias for the player in",
                            "the lower list and the alias to be demerged in the",
                            "upper list",
                        )
                    ),
                    title=title,
                )
                return
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Please select the main alias for the player in the upper",
                        "list.\n\n",
                        "The alias to be demerged is already selected in the",
                        "lower list.",
                    )
                ),
                title=title,
            )
            return

        if len(asel) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Please select the alias to be demerged in the upper",
                        "list.\n\n",
                        "The main alias for the player is already selected in the",
                        "lower list.",
                    )
                ),
                title=title,
            )
            return

        mainentry = mergeplayers.get_person_for_alias_key(db, psel[0])
        if mainentry is None:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot find main alias for selected player in lower",
                        "list.",
                    )
                ),
                title=title,
            )
            return
        demergeentry = resultsrecord.get_alias(db, asel[0][-1])
        if demergeentry is None:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Cannot find alias selected in upper list to be",
                        "demerged",
                    )
                ),
                title=title,
            )
            return

        demergekey = demergeentry.key.recno
        if len(mainentry.value.get_alias_list()):
            if demergekey == mainentry.key.recno:  # use report when ready
                pvi = mainentry.value.identity()
                playermap = ecfmaprecord.get_person_for_player(
                    db, mainentry.key.recno
                )
                playergcode = ecfgcodemaprecord.get_grading_code_for_person(
                    db, mainentry
                )
                rep = []
                head = [
                    "\n\n".join(
                        (
                            "Cannot break merge for",
                            resultsrecord.get_player_name_text_tabs(db, pvi),
                            "because other aliases exist. These are listed below.",
                        )
                    )
                ]
                if playermap:
                    head.append(
                        " ".join(
                            (
                                "\n\nThis alias is linked to an ECF Grading Code",
                                "from the ECF master list",
                                "which also prevents breaking single merge.",
                            )
                        )
                    )
                if playergcode:
                    head.append(
                        " ".join(
                            (
                                "\n\nThis alias is linked to a ECF Grading Code",
                                "from the online grading database",
                                "which also prevents breaking single merge.",
                            )
                        )
                    )
                for sk in mainentry.value.alias:
                    r = resultsrecord.get_alias(db, sk)
                    if r is not None:
                        rvi = r.value.identity()
                        if playermap is None:
                            rep.append(
                                resultsrecord.get_player_name_text_tabs(
                                    db, rvi
                                )
                            )
                        elif pvi != rvi:
                            rep.append(
                                resultsrecord.get_player_name_text_tabs(
                                    db, rvi
                                )
                            )
                if len(rep):
                    rep.insert(
                        0, "The following aliases can be demerged singly:\n"
                    )
                inf = "\n".join(rep)
                cdlg = dialogue.ModalInformation(
                    parent=self,
                    title=title,
                    text="\n\n".join(("".join(head), inf)),
                    action_titles={"Ok": "Close Player Details"},
                    # close=('Close', 'Close Player Details', 'Tooltip',),
                    wrap=tkinter.WORD,
                    tabstyle="tabular",
                )
                return
            elif demergekey not in mainentry.value.alias:
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            "Cannot break merge because\n\n",
                            resultsrecord.get_player_name_text(
                                db, demergeentry.value.identity()
                            ),
                            "\n\nis not an alias of\n\n",
                            resultsrecord.get_player_name_text(
                                db, mainentry.value.identity()
                            ),
                            ".",
                        )
                    ),
                    title=title,
                )
                return
            else:
                if not tkinter.messagebox.askyesno(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            "Confirm break merge of\n\n",
                            resultsrecord.get_player_name_text(
                                db, demergeentry.value.identity()
                            ),
                            "\n\ninto\n\n",
                            resultsrecord.get_player_name_text(
                                db, mainentry.value.identity()
                            ),
                            ".",
                        )
                    ),
                    title=title,
                ):
                    return

                aliasrecord = resultsrecord.ResultsDBrecordPlayer()
                r = db.get_primary_record(filespec.PLAYER_FILE_DEF, demergekey)
                if r is None:
                    dlg = tkinter.messagebox.showinfo(
                        parent=self.get_widget(),
                        message="".join(
                            (
                                "Record for player\n\n",
                                resultsrecord.get_player_name_text(
                                    db, demergeentry.value.identity()
                                ),
                                "\n\ndoes not exist.",
                            )
                        ),
                        title=title,
                    )
                    return

                db.start_transaction()
                aliasrecord.load_record(r)
                newaliasrecord = aliasrecord.clone()
                newaliasrecord.value.merge = None
                newaliasrecord.value.alias = []
                aliasrecord.edit_record(
                    db,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYER_FIELD_DEF,
                    newaliasrecord,
                )
        elif demergekey != mainentry.key.recno:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Cannot break merge because\n\n",
                        resultsrecord.get_player_name_text(
                            db, demergeentry.value.identity()
                        ),
                        "\n\nis not\n\n",
                        resultsrecord.get_player_name_text(
                            db, mainentry.value.identity()
                        ),
                        ".",
                    )
                ),
                title=title,
            )
            return
        else:
            msg = []
            playermap = ecfmaprecord.get_person_for_player(
                db, mainentry.key.recno
            )
            if playermap is not None:
                msg.extend(
                    (
                        mainentry.value.name,
                        "\n\nis linked to an ECF Grading Code.",
                        " from the ECF master list.",
                        "\nYou will have to break this link ",
                        "before break merge can proceed.",
                    )
                )
            playergcode = ecfgcodemaprecord.get_grading_code_for_person(
                db, mainentry
            )
            if playergcode:
                msg.extend(
                    (
                        mainentry.value.name,
                        "\n\nis linked to an ECF Grading Code."
                        " from the online grading database.",
                        "\nYou will have to break this link ",
                        "before break merge can proceed.",
                    )
                )
            if msg:
                msg.append("\n\nThere are no aliases.")
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(), message="".join(msg), title=title
                )
                return
            if not tkinter.messagebox.askyesno(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Confirm break merge of\n\n",
                        resultsrecord.get_player_name_text(
                            db, demergeentry.value.identity()
                        ),
                        "\n\ninto\n\n",
                        resultsrecord.get_player_name_text(
                            db, mainentry.value.identity()
                        ),
                        ".",
                    )
                ),
                title=title,
            ):
                return
            db.start_transaction()

        newaliasrecord = mainentry.clone()
        if demergekey in newaliasrecord.value.alias:
            newaliasrecord.value.alias.remove(demergekey)
        else:
            newaliasrecord.value.merge = None
        mainentry.edit_record(
            db,
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYER_FIELD_DEF,
            newaliasrecord,
        )
        db.commit()

        if not len(mainentry.value.get_alias_list()):
            if psel[0] in self.playergrid.bookmarks:
                self.playergrid.bookmarks.remove(psel[0])
            self.playergrid.selection[:] = []
        if asel[0] in self.aliasgrid.bookmarks:
            self.aliasgrid.bookmarks.remove(asel[0])
        self.aliasgrid.selection[:] = []
        self.playergrid.selection[:] = []
        self.clear_selector(self.aliasgrid)
        self.refresh_controls(
            (
                self.playergrid,
                self.aliasgrid,
                (
                    db,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYERPARTIALNEW_FIELD_DEF,
                ),
            )
        )

    def break_player_merges(self):
        """Demerge all aliases and identity after confirmation dialogue.

        Split all aliases in an identity to their initial pre-merged state.
        While it is unlikely that identification of players is so bad that
        this action has to be done it may be the clearest way to tidy up.

        """
        msgtitle = "Undo all Merges for Player"
        psel = self.playergrid.selection
        if len(psel) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join(
                    (
                        "Please select the player for whom all",
                        "merges are to be broken.",
                    )
                ),
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

        pvi = mainentry.value.identity()
        playermap = ecfmaprecord.get_person_for_player(db, mainentry.key.recno)
        if len(mainentry.value.get_alias_list()):
            if playermap is None:
                rep = [resultsrecord.get_player_name_text_tabs(db, pvi)]
            else:
                rep = []
            for sk in mainentry.value.alias:
                r = resultsrecord.get_alias(db, sk)
                if r is not None:
                    rvi = r.value.identity()
                    if playermap is None:
                        rep.append(
                            resultsrecord.get_player_name_text_tabs(db, rvi)
                        )
                    elif pvi != rvi:
                        rep.append(
                            resultsrecord.get_player_name_text_tabs(db, rvi)
                        )
            if len(rep):
                rep.insert(0, "The following aliases will be demerged:\n")
            inf = "\n".join(rep)
            if playermap is None:
                cdlg = dialogue.ModalConfirm(
                    parent=self,
                    title=" ".join(("Confirm", msgtitle)),
                    text="\n\n".join(
                        (
                            "\n\n".join(
                                (
                                    "Confirm Demerge for",
                                    mainentry.value.name,
                                )
                            ),
                            "".join(
                                (
                                    resultsrecord.get_player_name_text_tabs(
                                        db, pvi
                                    ),
                                    "\n\n",
                                    "is not linked to an ECF Grading Code so all",
                                    " aliases will be demerged",
                                )
                            ),
                        )
                    ),
                    action_titles={
                        "Cancel": "Cancel Demerge Player",
                        "Ok": "Demerge Player",
                    },
                    # close=('Cancel', 'Cancel Demerge Player', 'Tooltip',),
                    # ok=('Ok', 'Demerge Player', 'Tooltip',),
                    wrap=tkinter.WORD,
                    tabstyle="tabular",
                )
            else:
                cdlg = dialogue.ModalConfirm(
                    parent=self,
                    title=" ".join(("Confirm", msgtitle)),
                    text="\n\n".join(
                        (
                            "".join(
                                (
                                    resultsrecord.get_player_name_text_tabs(
                                        db, pvi
                                    ),
                                    "\n\n",
                                    "is linked to an ECF Grading Code so all",
                                    " aliases except this one will be demerged.",
                                    "\n\n",
                                    "You will have to break the link to the grading ",
                                    "code if this must be broken as well",
                                )
                            ),
                        )
                    ),
                    action_titles={
                        "Cancel": "Cancel Demerge Player",
                        "Ok": "Demerge Player",
                    },
                    # close=('Cancel', 'Cancel Demerge Player', 'Tooltip',),
                    # ok=('Ok', 'Demerge Player', 'Tooltip',),
                    wrap=tkinter.WORD,
                    tabstyle="tabular",
                )
            if not cdlg.ok_pressed():
                return
        else:
            if playermap is None:
                if not tkinter.messagebox.askyesno(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            "Confirm Demerge for\n\n",
                            mainentry.value.name,
                            "\n\nThere are no aliases.",
                            "\nThe player is not linked to an ECF Grading Code.",
                        )
                    ),
                    title=msgtitle,
                ):
                    return
            else:
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            mainentry.value.name,
                            "\n\nis linked to an ECF Grading Code.",
                            ".\nThere are no aliases.",
                            "\nYou will have to break the link to the ECF ",
                            "Grading Code before Demerge can proceed.",
                        )
                    ),
                    title=msgtitle,
                )
                return

        db.start_transaction()
        aliasrecord = resultsrecord.ResultsDBrecordPlayer()
        for sk in mainentry.value.alias:
            r = db.get_primary_record(filespec.PLAYER_FILE_DEF, sk)
            if r is not None:
                aliasrecord.load_record(r)
                newaliasrecord = aliasrecord.clone()
                newaliasrecord.value.merge = None
                newaliasrecord.value.alias = []
                aliasrecord.edit_record(
                    db,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYER_FIELD_DEF,
                    newaliasrecord,
                )

        newaliasrecord = mainentry.clone()
        if playermap is None:
            newaliasrecord.value.merge = None
            newaliasrecord.value.alias = []
        mainentry.edit_record(
            db,
            filespec.PLAYER_FILE_DEF,
            filespec.PLAYER_FIELD_DEF,
            newaliasrecord,
        )
        db.commit()

        self.aliasgrid.bookmarks[:] = []
        self.aliasgrid.selection[:] = []
        self.playergrid.selection[:] = []
        self.playergrid.bookmarks[:] = []
        self.clear_selector(self.playergrid)
        self.refresh_controls(
            (
                self.playergrid,
                self.aliasgrid,
                (
                    db,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYERPARTIALNEW_FIELD_DEF,
                ),
            )
        )

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """
        pass

    def describe_buttons(self):
        """Define all action buttons that may appear on players page."""
        self.define_button(
            self._btn_aliases,
            text="Player Details",
            tooltip="Show details, including all aliases, of selected players.",
            underline=1,
            command=self.on_aliases,
        )
        self.define_button(
            self._btn_demerge_player,
            text="Split Player",
            tooltip=" ".join(
                (
                    "Break merges and return player and aliases to",
                    "New Player tab.",
                )
            ),
            underline=3,
            command=self.on_demerge_player,
        )
        self.define_button(
            self._btn_break_merge,
            text="Break Merge",
            tooltip="Return selected alias to New Player tab.",
            underline=0,
            command=self.on_break_merge,
        )

    def display_player_details(self):
        """Display identity for alias and aliases associated with identity.

        Displays details for a player selected from any grid showing players.
        Each grid may restrict the kind of player displayed so some options
        may not apply in particular cases.

        """
        title = "Player Details"
        psel = self.playergrid.selection
        asel = self.aliasgrid.selection
        if len(psel) == 0:
            if len(asel) == 0:
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
        if len(psel) > 1 or len(asel) > 1:
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

        playerdetail.display_player_details(self, (psel, asel), title)

    def on_aliases(self, event=None):
        """Display details for a player."""
        self.display_player_details()
        self.playergrid.set_select_hint_label()
        return "break"

    def on_break_merge(self, event=None):
        """Break merge for one of a player's names."""
        self.break_one_player_merge()
        self.aliasgrid.set_select_hint_label()
        return "break"

    def on_demerge_player(self, event=None):
        """Break all merges for a player."""
        self.break_player_merges()
        self.aliasgrid.set_select_hint_label()
        return "break"

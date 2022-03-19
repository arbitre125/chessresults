# ecfplayers.py
# Copyright 2010 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database panel for grading and club codes allocated to players.

Display of player grading codes and club codes and actions for breaking these
allocations are available on this panel.

"""

import tkinter
import tkinter.messagebox

from solentware_misc.gui import panel, dialogue

from ..core import ecfrecord
from ..core import ecfmaprecord
from ..core import resultsrecord
from ..core import filespec
from . import ecfplayergrids


class ECFPlayers(panel.PanedPanelGridSelectorBar):

    """The ECFPlayers panel for a Results database."""

    _btn_break_affiliation = "ecfplayers_break_affiliation"
    _btn_remove_code = "ecfplayers_remove_code"
    _btn_edit_ecf_name = "ecfplayers_edit_name"

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database ECF club code panel."""
        self.playerclubgrid = None

        super(ECFPlayers, self).__init__(parent=parent, cnf=cnf, **kargs)

        self.show_panel_buttons(
            (
                self._btn_break_affiliation,
                self._btn_remove_code,
                self._btn_edit_ecf_name,
            )
        )
        self.create_buttons()

        (self.playerclubgrid,) = self.make_grids(
            (
                dict(
                    grid=ecfplayergrids.PlayerECFDetailGrid,
                    selectlabel="Select Player:  ",
                    gridfocuskey="<KeyPress-F7>",
                    selectfocuskey="<KeyPress-F6>",
                ),
            )
        )

    def break_players_affiliations(self):
        """Mark selected players as not affiliated to an ECF club."""
        msgtitle = "Club Codes"
        psel = self.playerclubgrid.selection
        pbkm = self.playerclubgrid.bookmarks
        db = self.get_appsys().get_results_database()

        if len(psel) + len(pbkm) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="No player(s) selected for breaking affiliations.",
                title=msgtitle,
            )
            return

        affiliated = []
        nonaffiliated = []
        lookup = dict()

        def build_affiliation_lookup(key):
            mr = ecfmaprecord.get_player_for_alias(db, key)
            if mr:
                affiliated.append(key)
            else:
                nonaffiliated.append(key)
            lookup[key] = (
                key,
                resultsrecord.get_player_name_text_tabs(
                    db, resultsrecord.get_alias(db, key).value.identity()
                ),
            )

        for p in pbkm:
            build_affiliation_lookup(p[-1])
        if len(psel):
            if psel[0] not in pbkm:
                build_affiliation_lookup(psel[0][-1])

        if len(affiliated) == 0:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="None of selected players have a club affiliation.",
                title=msgtitle,
            )
            return

        affheader = (
            "The affiliations of the players listed below will be removed"
        )
        nonaffheader = (
            "The players listed below have no affiliation and are ignored"
        )
        affreport = "\n".join([lookup[k][-1] for k in affiliated])
        if len(nonaffiliated):
            nonaffreport = "\n".join([lookup[k][-1] for k in nonaffiliated])
            header = (affheader, nonaffheader)
            detail = (affreport, nonaffreport)
        else:
            header = (affheader,)
            detail = (affreport,)
        dlg = dialogue.ModalConfirm(
            parent=self,
            title="Break Players Club Affiliation",
            text="\n\n".join(("\n".join(header), "\n".join(detail))),
            action_titles={
                "Cancel": "Cancel Remove Affiliation Details",
                "Ok": "Remove Affiliation Details",
            },
            # close=('Cancel', 'Cancel Remove Affiliation Details', 'Tooltip',),
            # ok=('Ok', 'Remove Affiliation Details', 'Tooltip',),
            wrap=tkinter.WORD,
            tabstyle="tabular",
        )
        if not dlg.ok_pressed():
            return

        db.start_transaction()
        for p in affiliated:
            mr = ecfmaprecord.get_player_for_alias(db, p)
            if mr is None:
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            " ".join(lookup[p][-1].split("\t")),
                            "\nrecord has been deleted.\n",
                            "Cannot proceed with removing club code ",
                            "allocation for this player.",
                        )
                    ),
                    title=msgtitle,
                )
                continue
            newmr = mr.clone()
            newmr.value.clubcode = None
            mr.edit_record(
                db,
                filespec.MAPECFCLUB_FILE_DEF,
                filespec.MAPECFCLUB_FIELD_DEF,
                newmr,
            )
        db.commit()

        self.playerclubgrid.selection[:] = []
        self.playerclubgrid.bookmarks[:] = []
        self.refresh_controls(
            (
                self.playerclubgrid,
                (
                    db,
                    filespec.MAPECFCLUB_FILE_DEF,
                    filespec.PLAYERALIASMAP_FIELD_DEF,
                ),
            )
        )
        return

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """
        pass

    def describe_buttons(self):
        """Define all action buttons that may appear on ECF club codes page."""
        self.define_button(
            self._btn_break_affiliation,
            text="Break Club Affiliation",
            tooltip="Remove affiliation from selected players.",
            underline=4,
            command=self.on_break_affiliation,
        )
        self.define_button(
            self._btn_remove_code,
            text="Break Grading Code Link",
            tooltip="Break link between player and ECF grading code.",
            underline=0,
            command=self.on_remove_code,
        )
        self.define_button(
            self._btn_edit_ecf_name,
            text="Edit ECF Name",
            tooltip="Edit name from master file for ECF submission file.",
            underline=2,
            command=self.on_edit_ecf_name,
        )

    def edit_player_ecf_name(self):
        """Add player to new player grid for editing of ECF version of name."""
        msgtitle = "Player Name"
        psel = self.playerclubgrid.selection
        if len(psel) == 0:
            msg = " ".join(
                (
                    "Select the player whose ECF form of name",
                    "is to be modified .",
                )
            )
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(), message=msg, title=msgtitle
            )
            return

        db = self.get_appsys().get_results_database()
        mr = ecfmaprecord.get_person_for_alias(
            db,
            resultsrecord.get_person_from_player(
                db, resultsrecord.get_alias(db, psel[0][-1])
            ).key.recno,
        )
        if mr is None:
            pr = resultsrecord.get_alias(db, psel[0][-1])
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        resultsrecord.get_player_name_text(
                            db, pr.value.identity()
                        ),
                        "\nrecord has been deleted.\nCannot ",
                        "proceed with amendment of ECF version of name.",
                    )
                ),
                title=msgtitle,
            )
            return

        if mr.value.playercode is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "ECF grading code not held for\n\n",
                        resultsrecord.get_player_name_text(
                            db, mr.value.get_unpacked_playername()
                        ),
                        "\n\nCannot amend ECF version of name.",
                    )
                ),
                title=msgtitle,
            )
            return
        ecfrec = ecfrecord.get_ecf_player_for_grading_code(
            db, mr.value.playercode
        )
        if ecfrec is None:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        resultsrecord.get_player_name_text(
                            db, mr.value.get_unpacked_playername()
                        ),
                        "\nhas no ECF master file record.\nCannot ",
                        "proceed with amendment of ECF version of name.",
                    )
                ),
                title=msgtitle,
            )
            return

        if not tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="".join(
                (
                    "Confirm record for\n",
                    resultsrecord.get_player_name_text(
                        db, mr.value.get_unpacked_playername()
                    ),
                    "\nto be made available for editing ECF version of name.",
                )
            ),
            title=msgtitle,
        ):
            return

        newmr = mr.clone()
        if ecfrec.value.ECFactive:
            newmr.value.playerecfcode = ecfrec.value.ECFcode
            newmr.value.playerecfname = ecfrec.value.ECFname
        else:
            newmr.value.playerecfcode = ""
            newmr.value.playerecfname = ""
        db.start_transaction()
        mr.edit_record(
            db,
            filespec.MAPECFPLAYER_FILE_DEF,
            filespec.MAPECFPLAYER_FIELD_DEF,
            newmr,
        )
        db.commit()
        if psel[0] in self.playerclubgrid.bookmarks:
            self.playerclubgrid.bookmarks.remove(psel[0])
        self.playerclubgrid.selection[:] = []
        self.refresh_controls(
            (
                self.playerclubgrid,
                (
                    db,
                    filespec.MAPECFPLAYER_FILE_DEF,
                    filespec.PERSONMAP_FIELD_DEF,
                ),
            )
        )
        return

    def on_break_affiliation(self, event=None):
        """Break player's link to a club."""
        self.break_players_affiliations()
        return "break"

    def on_edit_ecf_name(self, event=None):
        """Edit the locally entered version of player's name in ECF format."""
        self.edit_player_ecf_name()
        return "break"

    def on_remove_code(self, event=None):
        """Break player's link to grading code."""
        self.remove_grading_code()
        return "break"

    def remove_grading_code(self):
        """Remove ECF grading code from player after confirmation dialogue."""
        msgtitle = "Grading Codes"
        psel = self.playerclubgrid.selection
        if len(psel) == 0:
            msg = " ".join(
                (
                    "Select the player whose ECF grading code",
                    "will be removed.",
                )
            )
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(), message=msg, title=msgtitle
            )
            return

        db = self.get_appsys().get_results_database()
        mr = ecfmaprecord.get_person_for_alias(
            db,
            resultsrecord.get_person_from_player(
                db, resultsrecord.get_alias(db, psel[0][-1])
            ).key.recno,
        )
        if mr is None:
            pr = resultsrecord.get_alias(db, psel[0][-1])
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        resultsrecord.get_player_name_text(
                            db, pr.value.identity()
                        ),
                        "\nrecord has been deleted.\n",
                        "Cannot proceed with grading code removal.",
                    )
                ),
                title=msgtitle,
            )
            return
        if mr.value.playercode is None:
            pr = resultsrecord.get_alias(db, psel[0][-1])
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        resultsrecord.get_player_name_text(
                            db, pr.value.identity()
                        ),
                        "\nis not associated with a grading code.",
                    )
                ),
                title=msgtitle,
            )
            return

        if not tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="".join(
                (
                    "Confirm Grading Code ",
                    mr.value.playercode,
                    " to be removed from\n",
                    resultsrecord.get_player_name_text(
                        db, mr.value.get_unpacked_playername()
                    ),
                    ".",
                )
            ),
            title=msgtitle,
        ):
            return

        newmr = mr.clone()
        newmr.value.playercode = None
        db.start_transaction()
        mr.edit_record(
            db,
            filespec.MAPECFPLAYER_FILE_DEF,
            filespec.MAPECFPLAYER_FIELD_DEF,
            newmr,
        )
        db.commit()
        if psel[0] in self.playerclubgrid.bookmarks:
            self.playerclubgrid.bookmarks.remove(psel[0])
        self.playerclubgrid.selection[:] = []
        self.refresh_controls(
            (
                self.playerclubgrid,
                (
                    db,
                    filespec.MAPECFPLAYER_FILE_DEF,
                    filespec.PERSONMAP_FIELD_DEF,
                ),
            )
        )
        return

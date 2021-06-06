# ecfclubcodes.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database ECF club codes panel.

Assign ECF club code to player and adjust existing assignment actions are
available on this panel.

"""

import tkinter
import tkinter.messagebox

from solentware_misc.gui import panel, dialogue

from ..core import ecfrecord
from ..core import ecfmaprecord
from ..core import resultsrecord
from ..core import filespec
from . import ecfplayergrids, ecfdetail


class ECFClubCodes(panel.PanedPanelGridSelectorBar):

    """The ECFClubCodes panel for a Results database."""

    _btn_affiliate = "ecfclubcodes_affiliate"
    _btn_ecf_club = "ecfclubcodes_ecf_club"
    _btn_ecf_club_download = "ecfclubcodes_ecf_club_download"
    _btn_no_club = "ecfclubcodes_no_club"

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database ECF club code panel."""
        self.newplayerclubgrid = None
        self.ecfclubcodegrid = None

        super(ECFClubCodes, self).__init__(parent=parent, cnf=cnf, **kargs)

        self.show_panel_buttons(
            (
                self._btn_affiliate,
                self._btn_ecf_club,
                self._btn_ecf_club_download,
                self._btn_no_club,
            )
        )
        self.create_buttons()

        self.newplayerclubgrid, self.ecfclubcodegrid = self.make_grids(
            (
                dict(
                    grid=ecfplayergrids.NewPlayerClubGrid,
                    selectlabel="Select Player:  ",
                    gridfocuskey="<KeyPress-F7>",
                    selectfocuskey="<KeyPress-F5>",
                ),
                dict(
                    grid=ecfplayergrids.ECFClubCodeGrid,
                    selectlabel="Select Club Reference:  ",
                    gridfocuskey="<KeyPress-F8>",
                    selectfocuskey="<KeyPress-F6>",
                ),
            )
        )

    def affiliate_players_to_club(self):
        """Mark selected players as affiliated to selected ECF club."""
        msgtitle = "Club Codes"
        npsel = self.newplayerclubgrid.selection
        npbkm = self.newplayerclubgrid.bookmarks
        ecsel = self.ecfclubcodegrid.selection
        db = self.get_appsys().get_results_database()

        if len(npsel) + len(npbkm) == 0 or len(ecsel) == 0:
            if len(npsel) + len(ecsel) + len(npbkm) == 0:
                msg = " ".join(
                    (
                        "No players selected for affiliation and",
                        "no club selected either.",
                    )
                )
            elif len(ecsel) == 0:
                msg = "No club selected for affiliation of player(s)."
                msg = " ".join(
                    (
                        "No club selected for affiliation",
                        "of selected player(s).",
                    )
                )
            else:
                msg = " ".join(
                    (
                        "No player(s) selected for affiliation",
                        "to selected club.",
                    )
                )

            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(), message=msg, title=msgtitle
            )
            return

        players = npbkm[:]
        if len(npsel):
            if npsel[0] not in npbkm:
                players.append(npsel[0])
        dlg = dialogue.ModalConfirm(
            parent=self,
            title="Affiliate Players to Club",
            text="\n\n".join(
                (
                    " ".join(
                        (
                            "The players listed below will be affiliated to",
                            self.ecfclubcodegrid.objects[
                                ecsel[0]
                            ].value.ECFname,
                        )
                    ),
                    "\n".join(
                        [
                            resultsrecord.get_player_name_text_tabs(
                                db,
                                resultsrecord.get_unpacked_player_identity(
                                    ecfmaprecord.get_player(
                                        db, p[-1]
                                    ).value.playername
                                ),
                            )
                            for p in players
                        ]
                    ),
                )
            ),
            action_titles={
                "Cancel": "Cancel Affiliate Players to Club",
                "Ok": "Affiliate Players to Club",
            },
            # close=('Cancel', 'Cancel Affiliate Players to Club', 'Tooltip',),
            # ok=('Ok', 'Affiliate Players to Club', 'Tooltip',),
            wrap=tkinter.WORD,
            tabstyle="tabular",
        )
        if not dlg.ok_pressed():
            return

        ecfrec = ecfrecord.get_ecf_club(db, ecsel[0][-1])

        db.start_transaction()
        for p in players:
            mr = ecfmaprecord.get_player(db, p[-1])
            if mr is None:
                pr = ecfmaprecord.ECFmapDBrecordClub()
                pr.load_record(self.newpersongrid.objects[p])
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            resultsrecord.get_player_name_text(
                                db, pr.value.get_unpacked_playername()
                            ),
                            "\nrecord has been deleted.\n",
                            "Cannot proceed with club code allocation ",
                            "for this player.",
                        )
                    ),
                    title=msgtitle,
                )
                continue
            newmr = mr.clone()
            newmr.value.clubcode = ecfrec.value.ECFcode
            mr.edit_record(
                db,
                filespec.MAPECFCLUB_FILE_DEF,
                filespec.MAPECFCLUB_FIELD_DEF,
                newmr,
            )
        db.commit()

        self.newplayerclubgrid.bookmarks[:] = []
        if ecsel[0] in self.ecfclubcodegrid.bookmarks:
            self.ecfclubcodegrid.bookmarks.remove(ecsel[0])
        self.ecfclubcodegrid.selection[:] = []
        self.newplayerclubgrid.selection[:] = []
        self.clear_selector(True)
        self.ecfclubcodegrid.set_grid_properties()
        self.refresh_controls(
            (
                self.newplayerclubgrid,
                (db, filespec.PLAYER_FILE_DEF, filespec.PLAYERNAME_FIELD_DEF),
            )
        )
        return

    def affiliate_players_to_no_club(self):
        """Mark selected players as affiliated to no ECF club."""
        msgtitle = "Club Codes"
        npsel = self.newplayerclubgrid.selection
        npbkm = self.newplayerclubgrid.bookmarks
        db = self.get_appsys().get_results_database()

        if len(npsel) + len(npbkm) == 0:
            msg = " ".join(
                ("No player(s) selected for affiliation", "to no club.")
            )

            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(), message=msg, title=msgtitle
            )
            return

        players = npbkm[:]
        if len(npsel):
            if npsel[0] not in npbkm:
                players.append(npsel[0])
        dlg = dialogue.ModalConfirm(
            parent=self,
            title="Affiliate Players to Club",
            text="\n\n".join(
                (
                    " ".join(
                        (
                            "The players listed below will be affiliated to",
                            "no club",
                        )
                    ),
                    "\n".join(
                        [
                            resultsrecord.get_player_name_text_tabs(
                                db,
                                resultsrecord.get_unpacked_player_identity(
                                    ecfmaprecord.get_player(
                                        db, p[-1]
                                    ).value.playername
                                ),
                            )
                            for p in players
                        ]
                    ),
                )
            ),
            action_titles={
                "Cancel": "Cancel Affiliate Players to Club",
                "Ok": "Affiliate Players to Club",
            },
            # close=('Cancel', 'Cancel Affiliate Players to Club', 'Tooltip',),
            # ok=('Ok', 'Affiliate Players to Club', 'Tooltip',),
            wrap=tkinter.WORD,
            tabstyle="tabular",
        )
        if not dlg.ok_pressed():
            return

        db.start_transaction()
        for p in players:
            mr = ecfmaprecord.get_player(db, p[-1])
            if mr is None:
                pr = ecfmaprecord.ECFmapDBrecordClub()
                pr.load_record(self.newpersongrid.objects[p])
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            resultsrecord.get_player_name_text(
                                db, pr.value.get_unpacked_playername()
                            ),
                            "\nrecord has been deleted.\n",
                            "Cannot proceed with club code allocation ",
                            "for this player.",
                        )
                    ),
                    title=msgtitle,
                )
                continue
            newmr = mr.clone()
            newmr.value.clubcode = False
            mr.edit_record(
                db,
                filespec.MAPECFCLUB_FILE_DEF,
                filespec.MAPECFCLUB_FIELD_DEF,
                newmr,
            )
        db.commit()

        self.newplayerclubgrid.bookmarks[:] = []
        self.newplayerclubgrid.selection[:] = []
        self.clear_selector(self.newplayerclubgrid)
        self.refresh_controls(
            (
                self.newplayerclubgrid,
                (db, filespec.PLAYER_FILE_DEF, filespec.PLAYERNAME_FIELD_DEF),
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
            self._btn_affiliate,
            text="Affiliate",
            tooltip="Mark selected players affiliated to selected club.",
            underline=1,
            command=self.on_affiliate,
        )
        self.define_button(
            self._btn_ecf_club,
            text="New ECF Club",
            tooltip="Edit new club name and code for ECF submission file.",
            underline=10,
            command=self.on_ecf_club,
        )
        self.define_button(
            self._btn_ecf_club_download,
            text="Download Club Code",
            tooltip="Download club's details from ECF.",
            underline=2,
            command=self.on_ecf_club_download,
        )
        self.define_button(
            self._btn_no_club,
            text="No Club",
            tooltip="Mark selected players not affiliated to any club.",
            underline=1,
            command=self.on_no_club,
        )

    def edit_new_club_ecf_detail(self):
        """Show dialogue to edit ECF form of new club details and do update."""
        msgtitle = "New Club Name"
        npsel = self.newplayerclubgrid.selection
        if len(npsel) == 0:
            msg = " ".join(
                (
                    "Select the player whose ECF club detail",
                    "is to be modified (probably before first",
                    "submission of results for the new player).",
                )
            )
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(), message=msg, title=msgtitle
            )
            return

        db = self.get_appsys().get_results_database()
        mr = ecfmaprecord.get_player(db, npsel[0][-1])
        if mr is None:
            pr = ecfmaprecord.ECFmapDBrecordClub()
            pr.load_record(self.newplayerclubgrid.objects[npsel[0]])
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        resultsrecord.get_player_name_text(
                            db, pr.value.get_unpacked_playername()
                        ),
                        "\nrecord has been deleted.\nCannot ",
                        "proceed with amendment of ECF version of name.",
                    )
                ),
                title=msgtitle,
            )
            return
        if mr.value.clubecfcode:
            if mr.value.clubcode is not None:
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            resultsrecord.get_player_name_text(
                                db, mr.value.get_unpacked_playername()
                            ),
                            "\nrecord has ECF Club Code.\nCannot ",
                            "proceed with amendment of ECF club details.",
                        )
                    ),
                    title=msgtitle,
                )
                return

        mr.database = db
        # Is it a design flaw having to set mr.dbname this way? And what to do?
        mr.dbname = self.newplayerclubgrid.datasource.dbset
        dlg = ecfdetail.ECFClubDialog(None, mr)
        if dlg.is_yes():
            self.refresh_controls((self.newplayerclubgrid,))

    def download_new_club_ecf_detail(self):
        """Show dialogue to download club's ECF club code and do update."""
        msgtitle = "Download Club Code"

        db = self.get_appsys().get_results_database()
        dlg = ecfdetail.ECFDownloadClubCodeDialog(None, db)
        if dlg.is_yes():
            self.refresh_controls((self.ecfclubcodegrid,))

    def on_affiliate(self, event=None):
        """Affiliate player with club."""
        self.affiliate_players_to_club()
        self.ecfclubcodegrid.set_select_hint_label()
        return "break"

    def on_ecf_club(self, event=None):
        """Edit ECF club name."""
        self.edit_new_club_ecf_detail()
        return "break"

    def on_ecf_club_download(self, event=None):
        """Download ECF club code."""
        self.download_new_club_ecf_detail()
        return "break"

    def on_no_club(self, event=None):
        """Affiliate player with no club."""
        self.affiliate_players_to_no_club()
        self.ecfclubcodegrid.set_select_hint_label()
        return "break"

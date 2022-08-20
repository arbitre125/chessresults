# sourceedit.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Schedule and results raw data edit class plus database update."""

import tkinter
import tkinter.messagebox
import os
import csv

from chessvalidate.gui import sourceedit
from chessvalidate.core.gameobjects import (
    get_game_rows_for_csv_format,
    split_codes_from_name,
)

from chessvalidate.core.gameresults import resultmapecf

from ..core.resultsrecord import (
    get_events_matching_event_name,
    get_aliases_for_event,
    get_name,
    get_alias,
)
from ..core.ecf.ecfmaprecord import get_grading_code_for_person
from ..core.ecf.ecfrecord import get_ecf_player_for_grading_code
from ..core import collationdb
from ..core import filespec


class SourceEdit(sourceedit.SourceEdit):
    """The Edit panel for raw results data."""

    _btn_update = "sourceedit_update"

    def describe_buttons(self):
        """Define all action buttons that may appear on data input page."""
        super().describe_buttons()
        self.define_button(
            self._btn_generate,
            text="Generate",
            tooltip="Generate data for input to League database.",
            underline=0,
            command=self.on_generate,
        )
        self.define_button(
            self._btn_toggle_compare,
            text="Show Original",
            tooltip=" ".join(
                (
                    "Display original and edited results data but not generated",
                    "data.",
                )
            ),
            underline=5,
            command=self.on_toggle_compare,
        )
        self.define_button(
            self._btn_toggle_generate,
            text="Hide Original",
            tooltip=" ".join(
                (
                    "Display edited source and generated data but not original",
                    "source.",
                )
            ),
            underline=5,
            command=self.on_toggle_generate,
        )
        self.define_button(
            self._btn_save,
            text="Save",
            tooltip=(
                "Save edited results data with changes from original noted."
            ),
            underline=2,
            command=self.on_save,
        )
        self.define_button(
            self._btn_report,
            text="Report",
            tooltip="Save reports generated from source data.",
            underline=2,
            command=self.on_report,
        )
        self.define_button(
            self._btn_update,
            text="Update",
            tooltip="Update results database from generated data.",
            underline=0,
            command=self.on_update,
        )
        self.define_button(
            self._btn_closedata,
            text="Close",
            tooltip="Close the folder containing data.",
            underline=0,
            switchpanel=True,
            command=self.on_close_data,
        )

    def on_update(self, event=None):
        """Update database from validated source document."""
        if self.update_event_results():
            db = self.get_appsys().get_results_database()
            self.refresh_controls(
                (
                    (
                        db,
                        filespec.PLAYER_FILE_DEF,
                        filespec.PLAYERPARTIALNEW_FIELD_DEF,
                    ),
                    (
                        db,
                        filespec.EVENT_FILE_DEF,
                        filespec.EVENTNAME_FIELD_DEF,
                    ),
                )
            )
            self.show_buttons_for_generate()
            self.create_buttons()

    def show_buttons_for_update(self):
        """Show buttons for actions allowed after generating reports."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (
                self._btn_generate,
                self._btn_toggle_compare,
                self._btn_closedata,
                self._btn_save,
                self._btn_report,
                self._btn_update,
            )
        )

    def report_players_by_club(self, data):
        """Append list of players sorted by club to results report."""
        if len(data.collation.reports.error):
            return
        gca = self.get_appsys().show_master_list_grading_codes
        db = self.get_appsys().get_results_database()
        clubs = data.collation.get_players_by_club()
        eventname = set()
        for cp in clubs.values():
            for pn in cp:
                eventname.add(pn[1:-1])
        event, events = get_events_matching_event_name(
            db, eventname, data.collation.matches
        )
        genres = self.generated_results

        # No database open or not using ecf module.
        if not event or not gca:
            genres.append(("Players by club\n", None))
            genres.append(
                (
                    "".join(
                        (
                            "This report was generated without a database open ",
                            "to look up grading codes.",
                        )
                    ),
                    None,
                )
            )
            genres.append(
                (
                    "".join(
                        (
                            "Any reported codes, usually grading codes, follow ",
                            "the player name.\n",
                        )
                    ),
                    None,
                )
            )
            for cp in sorted(clubs.keys()):
                clubplayers = data.collation.clubplayers[cp]
                genres.append((cp + "\n", None))
                for pn in clubs[cp]:
                    genres.append(
                        (
                            "\t\t\t\t".join(
                                (pn[0], " ".join(clubplayers[pn]))
                            ),
                            None,
                        )
                    )
                genres.append(("", None))
            return

        # Database open.
        aliases = {}  # (name, section):(start, end, eventkey, aliaskey, merge)
        known = {}
        nogcode = {}

        def populate_aliases(e, a):
            evkey = e[1].key.recno
            sd = e[1].value.startdate
            ed = e[1].value.enddate
            for k, v in get_aliases_for_event(db, e[1]).items():
                ns = v.value.name, get_name(db, v.value.section).value.name
                nsd = sd, ed, evkey, v.key.recno, v.value.merge
                a.setdefault(ns, []).append(nsd)
                if v.value.merge is not None:
                    known.setdefault(ns[1], set()).add(ns[0])

        populate_aliases(event, aliases)
        for e in events:
            populate_aliases(e, aliases)
        startdate = event[1].value.startdate
        enddate = event[1].value.enddate
        genres.append(("Players by club\n", None))
        genres.append(
            (
                "".join(
                    (
                        "Names prefixed with same number or grading code ",
                        "are assumed to be same person.",
                    )
                ),
                None,
            )
        )
        genres.append(
            (
                "".join(
                    (
                        "If it is a number please give the player's grading ",
                        "code or confirm the player\ndoes not have one.",
                    )
                ),
                None,
            )
        )
        genres.append(
            (
                "".join(
                    (
                        "If neither is given please give the player's grading ",
                        "code or confirm the player\ndoes not have one.",
                    )
                ),
                None,
            )
        )
        genres.append(
            (
                "".join(
                    (
                        "The '!', '!!', '?', and '*', prefixes are asking for ",
                        "confirmation or correction\nof the grading code. ",
                        "Their absence means only corrections are needed.",
                    )
                ),
                None,
            )
        )
        genres.append(
            (
                "".join(
                    (
                        "'!' means name used in previous season and '!!' ",
                        "means at least a season gap\nsince previous use.",
                    )
                ),
                None,
            )
        )
        genres.append(
            (
                "".join(
                    (
                        "'?' means name referred to different person in at ",
                        "least one earlier season.",
                    )
                ),
                None,
            )
        )
        genres.append(
            (
                "".join(
                    (
                        "'*' means it was not possible to decide which of '!', ",
                        "'!!' is appropriate\n(because of a date error).\n",
                    )
                ),
                None,
            )
        )
        genres.append(
            (
                "".join(
                    (
                        "A grading code in brackets immediately following the ",
                        "name is the code shown\non the ECF Grading Database ",
                        "rather than the one before the name.\n",
                    )
                ),
                None,
            )
        )
        genres.append(
            (
                "".join(
                    (
                        "Any reported codes, usually grading codes, follow ",
                        "the player name after a\nnoticable gap.\n",
                    )
                ),
                None,
            )
        )
        for cp in sorted(clubs.keys()):
            clubplayers = data.collation.clubplayers[cp]
            genres.append((cp + "\n", None))
            for pn in clubs[cp]:
                grading_code = ""
                merged_grading_code = ""
                ns = pn[0], pn[4]
                nsdate = pn[2], pn[3]
                tag = ""
                peopletag = ""
                recenttag = ""
                if ns in aliases:
                    refs = aliases[ns]
                    if nsdate == refs[0][:2]:
                        merge = refs[0][4]
                        if merge is False:
                            person = refs[0][3]
                        elif merge is None:
                            person = refs[0][3]
                        else:
                            person = refs[0][4]
                    else:
                        merge = None
                        person = None
                    if len(refs) != 1:
                        try:
                            y1 = int(pn[2].split("-")[0])
                            y2 = int(refs[1][0].split("-")[0])
                            if abs(y1 - y2) == 1:
                                recenttag = "!" if merge is None else ""
                            else:
                                recenttag = "!!" if merge is None else ""
                        except:
                            recenttag = "*"
                    players = []
                    for r in refs:
                        if r[4] is False:
                            players.append(r[3])
                        elif r[4] is not None:
                            players.append(r[4])
                    if len(set(players)) > 1:
                        peopletag = "?"
                    if len(players):
                        grading_code = get_grading_code_for_person(
                            db, get_alias(db, players[0])
                        )
                        playerecf = get_ecf_player_for_grading_code(
                            db, grading_code
                        )
                        if playerecf:
                            if playerecf.value.ECFmerge:
                                merged_grading_code = grading_code
                                grading_code = playerecf.value.ECFmerge
                    else:
                        grading_code = ""
                    if grading_code == "":
                        if person not in nogcode:
                            nogcode[person] = len(nogcode) + 1
                        if merge is not None:
                            grading_code = nogcode[person]
                tag = "{:>3}".format(peopletag + recenttag)
                grading_code = "{:>7}".format(grading_code)
                if merged_grading_code:
                    pnrc = "\t\t\t\t\t".join(
                        (
                            " ".join(
                                (
                                    pn[0],
                                    merged_grading_code.join(("(", ")")),
                                )
                            ),
                            " ".join(clubplayers[pn]),
                        )
                    )
                    genres.append(
                        (
                            " ".join(
                                (
                                    tag,
                                    grading_code,
                                    " ",
                                    pnrc,
                                )
                            ),
                            None,
                        )
                    )
                else:
                    pnrc = "\t\t\t\t\t".join(
                        (pn[0], " ".join(clubplayers[pn]))
                    )
                    genres.append(
                        (" ".join((tag, grading_code, " ", pnrc)), None)
                    )
            genres.append(("", None))

    def update_event_results(self):
        """Show dialogue to update database and return true if updated."""
        if self.is_report_modified():
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Event data has been modified.\n\n",
                        "Save the data first.",
                    )
                ),
                title="Update",
            )
            return False
        db = self.get_appsys().get_results_database()
        if not db:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Cannot update. No results database open.\n\n",
                        "To proceed open a results database",
                    )
                ),
                title="Update",
            )
            return False
        if not tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="".join(("Do you want to update results?")),
            title="Update",
        ):
            return False

        self._collate_unfinished_games()
        collatedb = collationdb.CollationDB(
            self.get_context().results_data.get_collated_games(), db
        )
        db.start_transaction()
        u = collatedb.update_results()
        if isinstance(u, tuple):
            db.backout()
            dialogue.Report(
                parent=self,
                title="Player records blocking update",
                action_titles={"Save": "Save Blocking Update Details"},
                wrap=tkinter.WORD,
                tabstyle="tabular",
            ).append("\n\n".join(u))
        else:
            db.commit()
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(("Results database updated")),
                title="Update",
            )
        return True

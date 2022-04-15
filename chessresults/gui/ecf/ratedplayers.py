# ratedplayers.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ECF 'players_ratings' download database update class.

Display the 'players_ratings' download and offer the option to update the open
database.

Player's names, ecf_codes, and club_codes, are taken from the download. 

Assume that all clubs referenced in the download are in the 'active_clubs'
download, and any club not referenced in the download is absent from the
'active_clubs' download.

"""

import tkinter
import tkinter.messagebox
import datetime

from solentware_misc.gui import logpanel
from solentware_misc.gui import textreadonly
from solentware_misc.gui import tasklog

from ...core.ecf import ecfmaprecord
from ...core.ecf import ecfrecord
from ...core.ecf import ecfdataimport
from ...core import resultsrecord
from ...core import filespec
from ...core import constants

_REFRESH_FILE_FIELD = {
    filespec.ECFPLAYER_FILE_DEF: filespec.ECFPLAYERNAME_FIELD_DEF,
    filespec.ECFCLUB_FILE_DEF: filespec.ECFCLUBNAME_FIELD_DEF,
}


class RatedPlayers(logpanel.WidgetAndLogPanel):

    """The 'players_ratings' panel for a Results database."""

    _btn_closeratedplayers = "ratedplayers_close"
    _btn_applyratedplayers = "ratedplayers_apply"

    def __init__(
        self,
        parent=None,
        datafile=None,
        closecontexts=(),
        starttaskmsg=None,
        cnf=dict(),
        **kargs
    ):
        """Extend and define the 'players_ratings' database update panel."""

        self.datafilename, self.downloaddate, self.all_players = datafile

        super().__init__(
            parent=parent,
            taskheader="   ".join(
                (
                    "Player download from",
                    self.datafilename,
                    self.downloaddate.join(("(", ")")),
                )
            ),
            maketaskwidget=self._create_rated_players_download_widget,
            taskbuttons={
                self._btn_closeratedplayers: dict(
                    text="Cancel Apply Rated Players",
                    tooltip="Cancel the rated players update.",
                    underline=0,
                    switchpanel=True,
                    command=self.on_cancel_apply_downloaded_rated_players,
                ),
                self._btn_applyratedplayers: dict(
                    text="Apply Rated Players",
                    tooltip="Apply rated players updates to database.",
                    underline=0,
                    command=self.on_apply_downloaded_rated_players,
                ),
            },
            starttaskbuttons=(
                self._btn_closeratedplayers,
                self._btn_applyratedplayers,
            ),
            runmethod=False,
            runmethodargs=dict(),
            cnf=cnf,
            **kargs
        )
        self._closecontexts = closecontexts

        # Import may need to increase file size (DPT) so close DPT contexts in
        # this thread.
        # Doing this leads to other thread freeing file after which this thread
        # is unable to open the file unless it allocates the file first.
        # There should be better synchronization of what happens!  Like in the
        # process versions used elsewhere.  This code was split to keep the UI
        # responsive while doing long imports.
        self.get_appsys().get_results_database().close_database_contexts(
            closecontexts
        )

        if starttaskmsg is not None:
            self.tasklog.append_text(starttaskmsg)

    def _create_rated_players_download_widget(self, master):
        """Create customised Text widget under master containing download data.

        This method is designed to be passed as the maketaskwidget argument
        to a WidgetAndLogPanel(...) call.

        """
        self.resultsdbfolder = tkinter.Label(master=self.get_widget(), text="")
        self.resultsdbfolder.pack(side=tkinter.TOP, fill=tkinter.X)
        tf = tkinter.Frame(master=self.get_widget())
        header = tkinter.Text(
            master=tf,
            wrap=tkinter.WORD,
            undo=tkinter.FALSE,
            tabs="2c 4c 6c 12c 14c 20c",
            height=1,
        )

        # The important columns for results submission are 0, 1, 2, 3, -2, -1.
        # Put these first and the rest under the generic name
        # 'Other Items in Order'.
        # Tab stops chosen by experiment.
        cn = self.all_players[constants.P_R_COLUMN_NAMES]
        for i in (0, 1, 2, 3, -2, -1):
            header.insert(tkinter.END, cn[i] + "\t")
        header.insert(tkinter.END, "Other Items in Order")
        header.configure(state=tkinter.DISABLED)
        fbf, feedbackctrl = textreadonly.make_scrolling_text_readonly(
            master=tf,
            wrap=tkinter.WORD,
            undo=tkinter.FALSE,
            tabs="".join(
                (
                    "2c 4c 6c 12c 14c 20c 21c 22c 24c 26c 27c ",
                    "28c 29c 30c 31c 32c",
                    " 33c 34c 35c 36c 37c 38c 39c 40c 41c 42c",
                )
            ),
        )
        tf.columnconfigure(0, weight=1)
        tf.rowconfigure(1, weight=1)
        header.grid(row=0, sticky=tkinter.NSEW)
        fbf.grid(row=1, sticky=tkinter.NSEW)

        ignore = set(
            (
                0,
                1,
                2,
                3,
                len(self.all_players[constants.P_R_COLUMN_NAMES]) - 2,
                len(self.all_players[constants.P_R_COLUMN_NAMES]) - 1,
            )
        )
        errors = 0
        expected_p_length = len(constants.PLAYERS_RATINGS_COLUMN_NAMES)
        for p in self.all_players[constants.P_R_PLAYERS]:
            if not isinstance(p, list):
                errors += 1
                continue
            if len(p) != expected_p_length:
                errors += 1
                continue
            row = []

            # Club code is treated as a number if it is all digits, and some
            # start with '0'.  May change shortly.
            for i in (0, 1, 2, 3):  # , -2, -1):
                v = p[i]
                if v is None:
                    v = ""
                else:
                    v = str(v)
                row.append(v + "\t")
            v = p[-2]
            if v is None:
                v = ""
            elif isinstance(v, int):
                v = str(v).zfill(4)
            else:
                v = str(v)
            row.append(v + "\t")
            v = p[-1]
            if v is None:
                v = ""
            else:
                v = str(v)
            row.append(v + "\t")
            other_items = []
            for e, v in enumerate(p):
                if e in ignore:
                    continue
                if v is None:
                    other_items.append("")
                else:
                    other_items.append(str(v))
            row.append("\t".join(other_items))
            feedbackctrl.insert(tkinter.END, "".join(row) + "\n")

        if errors:
            feedbackctrl.delete("1.0", tkinter.END)
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title="Apply Rated Players",
                message="".join(
                    (
                        "Unexpected data found in ",
                        str(errors),
                        " records in total of ",
                        str(len(self.all_players[constants.P_R_PLAYERS])),
                        " records",
                    )
                ),
            )
        return tf

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """
        pass

    def apply_downloaded_rated_players(self, *args, **kargs):
        """Apply new, and update existing, ecf_codes from download.

        args and kargs soak up arguments set by threading or multiprocessing
        when running this method.

        """
        ecfdataimport.copy_ecf_players_post_2020_rules(
            self,
            logwidget=self.tasklog,
            ecfdata=self.all_players,
            downloaddate=self.downloaddate,
        )

    def on_cancel_apply_downloaded_rated_players(self, event=None):
        """Do any tidy up before switching to next panel.

        Re-open the files that were closed on creating this widget.
        """
        self.get_appsys().get_results_database().allocate_and_open_contexts(
            files=self._closecontexts
        )

        for filedef in self._closecontexts:
            fielddef = _REFRESH_FILE_FIELD.get(filedef)
            if fielddef:
                self.refresh_controls(
                    (
                        (
                            self.get_appsys().get_results_database(),
                            filedef,
                            fielddef,
                        ),
                    )
                )

    def on_apply_downloaded_rated_players(self, event=None):
        """Run apply_downloaded_rated_players in separate thread."""
        dlg = tkinter.messagebox.askquestion(
            parent=self.get_widget(),
            title="Apply Rated Players",
            message="".join(
                (
                    "Do you want to update players with data published on ",
                    self.all_players["rating_effective_date"],
                )
            ),
        )
        if dlg != tkinter.messagebox.YES:
            return
        self.tasklog.run_method(method=self.apply_downloaded_rated_players)

    def show_buttons_for_cancel_import(self):
        """Show buttons for actions allowed at start of import process."""
        self.hide_panel_buttons()
        self.show_panel_buttons((self._btn_closeratedplayers,))

    def show_buttons_for_start_import(self):
        """Show buttons for actions allowed at start of import process."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (self._btn_closeratedplayers, self._btn_applyratedplayers)
        )

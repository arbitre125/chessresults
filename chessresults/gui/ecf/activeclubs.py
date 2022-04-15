# activeclubs.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""ECF 'active_clubs' download database update class.

Display the 'active_clubs' download and offer the option to update the open
database.

Club's club_names, club_codes, and assoc_codes, are taken from the download.

Assume that all clubs in the download are referenced in the 'players_ratings'
download, and any club absent from the download is not referenced in the
'players_ratings' download.

"""

import tkinter
import tkinter.messagebox

from solentware_misc.gui import logpanel
from solentware_misc.gui import textreadonly
from solentware_misc.gui import tasklog

from ...core import resultsrecord
from ...core import filespec
from ...core import constants
from ...core.ecf import ecfmaprecord
from ...core.ecf import ecfrecord
from ...core.ecf import ecfdataimport

_REFRESH_FILE_FIELD = {
    filespec.ECFPLAYER_FILE_DEF: filespec.ECFPLAYERNAME_FIELD_DEF,
    filespec.ECFCLUB_FILE_DEF: filespec.ECFCLUBNAME_FIELD_DEF,
}


class ActiveClubs(logpanel.WidgetAndLogPanel):

    """The 'active_clubs' panel for a Results database."""

    _btn_closeactiveclubs = "activeclubs_close"
    _btn_applyactiveclubs = "activeclubs_apply"

    def __init__(
        self,
        parent=None,
        datafile=None,
        closecontexts=(),
        starttaskmsg=None,
        cnf=dict(),
        **kargs
    ):
        """Extend and define the 'active_clubs' database update panel."""

        self.datafilename, self.downloaddate, self.active_clubs = datafile

        super().__init__(
            parent=parent,
            taskheader="   ".join(
                (
                    "Club download from",
                    self.datafilename,
                    self.downloaddate.join(("(", ")")),
                )
            ),
            maketaskwidget=self._create_club_download_widget,
            taskbuttons={
                self._btn_closeactiveclubs: dict(
                    text="Cancel Apply Active Clubs",
                    tooltip="Cancel the active clubs update.",
                    underline=0,
                    switchpanel=True,
                    command=self.on_cancel_apply_downloaded_active_clubs,
                ),
                self._btn_applyactiveclubs: dict(
                    text="Apply Active Clubs",
                    tooltip="Apply active clubs updates to database.",
                    underline=0,
                    command=self.on_apply_downloaded_active_clubs,
                ),
            },
            starttaskbuttons=(
                self._btn_closeactiveclubs,
                self._btn_applyactiveclubs,
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

    def _create_club_download_widget(self, master):
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
            tabs="2c 9c center 10c left 12c",
            height=1,
        )
        header.insert(
            tkinter.END, "\t".join(constants.ACTIVE_CLUBS_ROW_KEY_NAMES)
        )
        header.configure(state=tkinter.DISABLED)
        fbf, feedbackctrl = textreadonly.make_scrolling_text_readonly(
            master=tf,
            wrap=tkinter.WORD,
            undo=tkinter.FALSE,
            tabs="2c 9c 10c 12c",
        )
        tf.columnconfigure(0, weight=1)
        tf.rowconfigure(1, weight=1)
        header.grid(row=0, sticky=tkinter.NSEW)
        fbf.grid(row=1, sticky=tkinter.NSEW)
        errors = 0
        expected_c_set = set(constants.ACTIVE_CLUBS_ROW_KEY_NAMES)
        for c in self.active_clubs[constants.A_C_CLUBS]:
            if not isinstance(c, dict):
                errors += 1
                continue
            if set(c) - expected_c_set:
                errors += 1
                continue
            row = []
            for k in constants.ACTIVE_CLUBS_ROW_KEY_NAMES:
                v = c.get(k)
                if v is None:
                    v = ""
                row.append(v)
            feedbackctrl.insert(tkinter.END, "\t".join(row) + "\n")
        if errors:
            feedbackctrl.delete("1.0", tkinter.END)
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title="Apply Active Clubs",
                message="".join(
                    (
                        "Unexpected data found in ",
                        str(errors),
                        " records in total of ",
                        str(len(self.active_clubs[constants.A_C_CLUBS])),
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

    def apply_downloaded_active_clubs(self, *args, **kargs):
        """Apply new, and update existing, club_codes from download.

        args and kargs soak up arguments set by threading or multiprocessing
        when running this method.

        """
        ecfdataimport.copy_ecf_clubs_post_2020_rules(
            self,
            logwidget=self.tasklog,
            ecfdata=self.active_clubs,
            downloaddate=self.downloaddate,
        )

    def on_cancel_apply_downloaded_active_clubs(self, event=None):
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

    def on_apply_downloaded_active_clubs(self, event=None):
        """Run apply_downloaded_active_clubs in separate thread."""
        dlg = tkinter.messagebox.askquestion(
            parent=self.get_widget(),
            title="Apply Active Clubs",
            message="".join(
                (
                    "Do you want to update clubs with data downloaded on ",
                    self.downloaddate,
                )
            ),
        )
        if dlg != tkinter.messagebox.YES:
            return
        self.tasklog.run_method(method=self.apply_downloaded_active_clubs)

    def show_buttons_for_cancel_import(self):
        """Show buttons for actions allowed at start of import process."""
        self.hide_panel_buttons()
        self.show_panel_buttons((self._btn_closeactiveclubs,))

    def show_buttons_for_start_import(self):
        """Show buttons for actions allowed at start of import process."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (self._btn_closeactiveclubs, self._btn_applyactiveclubs)
        )

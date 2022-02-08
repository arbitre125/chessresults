# takeonedit.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Schedule and results raw data edit class for data takeon.

Event data files in a format similar to the ECF submission format (2006) are
processed by this class.  The ECF submission format itself cannot be processed
by this class.  The module preparesource.py makes suitable files, from valid
ECF submission files,  which themselves are not valid ECF submission files.

Database dump files produced by version 9.1 of the League program (the last one
released) are also supported.

Only the MATCH RESULTS field on the event data files can be amended.  Player
affiliations are derived from this data to assist in identifying the player
with a player already on the database.  Sometimes the guess is not very good
because MATCH RESULTS contains data additional to the teams involved.  Typing
errors as well of course.  But if the guess is good enough it is probably
best not to edit.

The rest of the data cannot be edited because such cannot be justified away
from the source database.  Mistyped player names must be dealt with on the New
Players tab.

"""

import tkinter
import tkinter.messagebox
import difflib
import os
import datetime

from solentware_misc.gui import panel, dialogue, textreadonly, texttab

from ..core import takeoncollationdb
from ..core import filespec


class TakeonEdit(panel.PlainPanel):

    """The Edit panel for raw results data.

    This class is no longer derived from SourceEditBase, which held elements
    common to TakeonEdit and SourceEdit, because the two classes now support
    different interfaces.  Those bits of SourceEditBase not overridden are
    copied to this class.

    """

    _btn_generate = "takeonedit_generate"
    _btn_closedata = "takeonedit_close"
    _btn_save = "takeonedit_save"
    _btn_toggle_compare = "takeonedit_toggle_compare"
    _btn_toggle_generate = "takeonedit_toggle_generate"
    _btn_update = "takeonedit_update"
    _btn_report = "takeonedit_report"

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define results data input panel for a results database"""
        super().__init__(parent=parent, cnf=cnf, **kargs)
        self.generated_schedule = []
        self.generated_results = []
        self.origschedctrl = None
        self.origresctrl = None
        self.editschedctrl = None
        self.editresctrl = None
        self.schedulectrl = None
        self.resultsctrl = None
        self.originalpane = None
        self.editpane = None
        self.generatedpane = None
        self.show_buttons_for_generate()
        self.create_buttons()
        self.folder = tkinter.Label(
            master=self.get_widget(),
            text=self.get_context().get_season_folder(),
        )
        self.folder.pack(side=tkinter.TOP, fill=tkinter.X)
        self.toppane = tkinter.PanedWindow(
            master=self.get_widget(),
            opaqueresize=tkinter.FALSE,
            orient=tkinter.HORIZONTAL,
        )
        self.toppane.pack(side=tkinter.TOP, expand=True, fill=tkinter.BOTH)
        self.show_edits_and_generated()
        self.editschedctrl.edit_modified(tkinter.FALSE)
        self.editresctrl.edit_modified(tkinter.FALSE)

    def generate_event_report(self):
        """Generate report on data input and return True if data is ok.

        Data can be ok and still be wrong.  ok means merely that the data
        input is consistent.  A number of formats are acceptable and named
        in sectiontypes below.

        """
        data = self.get_context().results_data
        self.get_schedule(data)
        self.report_fixtures(data)
        self.get_results(data)
        if not len(data.collation.error) and not len(data._fixtures.error):
            report = data.collation.reports.report_games()
            for w, r in zip(
                (self.generated_schedule, self.generated_results), report
            ):
                for t, v in r:
                    w.append(t)
                    w.append(v)
                    w.append("\n\n")
        self.schedulectrl.delete("1.0", tkinter.END)
        self.schedulectrl.insert(
            tkinter.END, "\n".join(self.generated_schedule)
        )
        self.resultsctrl.delete("1.0", tkinter.END)
        self.resultsctrl.insert(tkinter.END, "\n".join(self.generated_results))
        return not len(data.collation.error)

    def report_fixtures(self, data):
        """Append fixtures to event schedule report."""
        fixdata = data._fixtures
        if len(fixdata.error):
            return
        #
        # Fixtures report is part of results report in TakeonEdit class.
        # Commented code below is minimum that a normal report_fixtures
        # method would do.
        #
        # genfix = self.generated_schedule
        # self.schedulectrl.delete('1.0', Tkinter.END)
        # self.schedulectrl.insert(Tkinter.END, '\n'.join(genfix))

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
        collatedb = takeoncollationdb.TakeonCollationDB(
            self.get_context().results_data.collation, db
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
            collatedb.merge_players()
            db.commit()
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(("Results database updated")),
                title="Update",
            )
        return True

    # Copied methods from here on

    def show_edits_and_generated(self):
        """Display widgets showing current data and generated reports."""
        self._hide_panes()
        if self.editpane is None:
            self.editpane = tkinter.PanedWindow(
                master=self.toppane,
                opaqueresize=tkinter.FALSE,
                orient=tkinter.VERTICAL,
            )
        if self.generatedpane is None:
            self.generatedpane = tkinter.PanedWindow(
                master=self.toppane,
                opaqueresize=tkinter.FALSE,
                orient=tkinter.VERTICAL,
            )
        if self.editschedctrl == None:
            self.editschedctrl = texttab.make_text_tab(master=self.editpane)
        if self.editresctrl == None:
            self.editresctrl = texttab.make_text_tab(master=self.editpane)
        if self.schedulectrl == None:
            self.schedulectrl = textreadonly.make_text_readonly(
                master=self.generatedpane
            )
        if self.resultsctrl == None:
            self.resultsctrl = textreadonly.make_text_readonly(
                master=self.generatedpane
            )
        self.editpane.add(self.editschedctrl)
        self.editpane.add(self.editresctrl)
        self.generatedpane.add(self.schedulectrl)
        self.generatedpane.add(self.resultsctrl)
        self.toppane.add(self.editpane)
        self.toppane.add(self.generatedpane)
        self.editschedctrl.delete("1.0", tkinter.END)
        self.editresctrl.delete("1.0", tkinter.END)
        self.schedulectrl.delete("1.0", tkinter.END)
        self.resultsctrl.delete("1.0", tkinter.END)
        self.editschedctrl.insert(
            tkinter.END,
            "\n".join(
                list(
                    difflib.restore(
                        self.get_context().results_data.fixtures, 2
                    )
                )
            ),
        )
        self.editresctrl.insert(
            tkinter.END,
            "\n".join(
                list(
                    difflib.restore(self.get_context().results_data.results, 2)
                )
            ),
        )
        self.schedulectrl.insert(
            tkinter.END, "\n".join(self.generated_schedule)
        )
        self.resultsctrl.insert(tkinter.END, "\n".join(self.generated_results))

    def show_originals_and_edits(self):
        """Display widgets comparing database and edited versions of data."""
        self._hide_panes()
        if self.editpane is None:
            self.editpane = tkinter.PanedWindow(
                master=self.toppane,
                opaqueresize=tkinter.FALSE,
                orient=tkinter.VERTICAL,
            )
        if self.originalpane is None:
            self.originalpane = tkinter.PanedWindow(
                master=self.toppane,
                opaqueresize=tkinter.FALSE,
                orient=tkinter.VERTICAL,
            )
        if self.editschedctrl == None:
            self.editschedctrl = texttab.make_text_tab(master=self.editpane)
        if self.editresctrl == None:
            self.editresctrl = texttab.make_text_tab(master=self.editpane)
        if self.origschedctrl == None:
            self.origschedctrl = textreadonly.make_text_readonly(
                master=self.originalpane
            )
        if self.origresctrl == None:
            self.origresctrl = textreadonly.make_text_readonly(
                master=self.originalpane
            )
        self.originalpane.add(self.origschedctrl)
        self.originalpane.add(self.origresctrl)
        self.editpane.add(self.editschedctrl)
        self.editpane.add(self.editresctrl)
        self.toppane.add(self.originalpane)
        self.toppane.add(self.editpane)
        self.origschedctrl.delete("1.0", tkinter.END)
        self.editschedctrl.delete("1.0", tkinter.END)
        self.origresctrl.delete("1.0", tkinter.END)
        self.editresctrl.delete("1.0", tkinter.END)
        self.origschedctrl.insert(
            tkinter.END,
            "\n".join(
                list(
                    difflib.restore(
                        self.get_context().results_data.fixtures, 1
                    )
                )
            ),
        )
        self.editschedctrl.insert(
            tkinter.END,
            "\n".join(
                list(
                    difflib.restore(
                        self.get_context().results_data.fixtures, 2
                    )
                )
            ),
        )
        self.origresctrl.insert(
            tkinter.END,
            "\n".join(
                list(
                    difflib.restore(self.get_context().results_data.results, 1)
                )
            ),
        )
        self.editresctrl.insert(
            tkinter.END,
            "\n".join(
                list(
                    difflib.restore(self.get_context().results_data.results, 2)
                )
            ),
        )

    def get_schedule(self, data):
        """Extract event schedule and prepare report of errors."""
        data.extract_schedule(
            self.editschedctrl.get("1.0", tkinter.END).splitlines()
        )
        fixdata = data._fixtures
        genfix = self.generated_schedule
        del genfix[:]
        if len(fixdata.error):
            genfix.append("Errors\n")
            genfix.append("\n".join(fixdata.error))

    def get_results(self, data):
        """Extract event results and prepare report of errors."""
        data.extract_results(
            self.editresctrl.get("1.0", tkinter.END).splitlines()
        )
        resdata = data.collation
        genres = self.generated_results
        del genres[:]
        if len(resdata.error):
            genres.append("Errors\n")
            genres.append("\n".join(resdata.error))

    def save_data_folder(self, msg=None):
        """Show save data input file dialogue and return True if saved."""
        if not self.is_report_modified():
            if not tkinter.messagebox.askyesno(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Event data has not been edited.\n\n",
                        "Do you want to save event data anyway?",
                    )
                ),
                title="Save",
            ):
                return
        if msg == None:
            msg = " ".join(
                (
                    "Save",
                    self.get_context().get_season_folder(),
                    "folder containing results data",
                )
            )

        if tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message=" ".join(
                (
                    "Save\n\n",
                    self.get_context().get_season_folder(),
                    "\n\nfolder containing results data",
                )
            ),
            title="Save",
        ):
            self.get_context().results_data.save_difference_files(
                self.editschedctrl.get("1.0", tkinter.END).splitlines(),
                self.editresctrl.get("1.0", tkinter.END).splitlines(),
            )
            self.editschedctrl.edit_modified(tkinter.FALSE)
            self.editresctrl.edit_modified(tkinter.FALSE)
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="Event data saved.",
                title="Save",
            )
            self.editschedctrl.edit_modified(False)
            self.editresctrl.edit_modified(False)
            return True

    def is_report_modified(self):
        """Return Text.edit_modified(). Work around see Python issue 961805."""
        # return self.editresctrl.edit_modified()
        if self.editschedctrl.winfo_toplevel().tk.call(
            "eval", "%s edit modified" % self.editschedctrl
        ):
            return True
        return self.editresctrl.winfo_toplevel().tk.call(
            "eval", "%s edit modified" % self.editresctrl
        )

    def _hide_panes(self):
        """Forget the configuration of PanedWindows on data input page."""
        for p in (
            self.originalpane,
            self.editpane,
            self.generatedpane,
            self.toppane,
        ):
            if p is not None:
                for w in p.panes():
                    p.forget(w)

    def describe_buttons(self):
        """Define all action buttons that may appear on data input page."""
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

    def on_close_data(self, event=None):
        """Close source document."""
        self.close_data_folder()
        self.inhibit_context_switch(self._btn_closedata)

    def on_generate(self, event=None):
        """Validate source document."""
        if self.generate_event_report():
            self.show_buttons_for_update()
            self.create_buttons()

    def on_report(self, event=None):
        """Save validation report."""
        self.save_reports()

    def on_save(self, event=None):
        """Save source document."""
        self.save_data_folder()

    def on_toggle_compare(self, event=None):
        """Display original source document alongside edited source document."""
        self.show_buttons_for_compare()
        self.create_buttons()
        self.show_originals_and_edits()

    def on_toggle_generate(self, event=None):
        """Display edited source document alongside validation report widgets."""
        self.show_buttons_for_generate()
        self.create_buttons()
        self.show_edits_and_generated()

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

    def show_buttons_for_compare(self):
        """Show buttons for actions allowed comparing input data versions."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (self._btn_toggle_generate, self._btn_closedata, self._btn_save)
        )

    def show_buttons_for_generate(self):
        """Show buttons for actions allowed displaying current input data."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (
                self._btn_generate,
                self._btn_toggle_compare,
                self._btn_closedata,
                self._btn_save,
            )
        )

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

    def save_reports(self):
        """Show save data report file dialogue and return True if saved."""
        reports = os.path.join(
            self.get_context().get_season_folder(), "Reports"
        )
        if not tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="".join(
                ("Do you want to save reports in\n\n", reports, "\n\nfolder.")
            ),
            title="Save Reports",
        ):
            return False
        if not os.path.isdir(reports):
            try:
                os.mkdir(reports)
            except:
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            "Unable to create folder\n\n",
                            reports,
                            "\n\nfor reports.",
                        )
                    ),
                    title="Save Reports",
                )
                return
        dt = datetime.datetime.today().isoformat()
        for control, filename in (
            (self.schedulectrl, "rep_schedule"),
            (self.resultsctrl, "rep_results"),
            (self.editschedctrl, "src_schedule"),
            (self.editresctrl, "src_results"),
        ):
            report_file = os.path.join(reports, "_".join((dt, filename)))
            f = open(report_file, "w", encoding="utf8")
            try:
                f.write(control.get("1.0", tkinter.END))
            finally:
                f.close()
        dlg = tkinter.messagebox.showinfo(
            parent=self.get_widget(),
            message="".join(("Reports saved in folder\n\n", reports)),
            title="Save Reports",
        )

    def get_context(self):
        """Return the data input page."""
        return self.get_appsys().get_results_context()

    def close_data_folder(self):
        """Show close data input file dialogue and return True if closed."""
        if self.is_report_modified():
            if not tkinter.messagebox.askyesno(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Event data has been modified.\n\n",
                        "Do you want to close without saving?",
                    )
                ),
                title="Close",
            ):
                return
        self.get_context().results_close()

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """
        pass

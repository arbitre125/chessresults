# importevents.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Import Events panel class.
"""

import tkinter
import tkinter.messagebox
import tkinter.filedialog
import os
import bz2
from time import ctime

from solentware_misc.gui import logpanel

from ..core import importreports
from ..core import importcollationdb
from ..core import importcollation


class ImportEvents(logpanel.TextAndLogPanel):

    """The panel for importing events from another Results database."""

    _btn_closeimport = "importevents_close"
    _btn_startimport = "importevents_start"
    _btn_previewimport = "importevents_preview"
    _btn_renameimporteventsreport = "importevents_rename"
    _btn_pickreportforvalidation = "importevents_pick"

    def __init__(
        self,
        parent=None,
        datafile=None,
        closecontexts=(),
        starttaskmsg=None,
        tabtitle=None,
        copymethod=None,
        cnf=dict(),
        **kargs
    ):
        """Extend and define the results database import event tab."""

        # See comment in function _do_ecf_reference_data_import of relative
        # module ..core.ecfdataimport for explanation of this change.
        # Binding the instance attribute is not delegated to the superclass,
        # which populates the widget that may not be accessible later depending
        # on compile-time decisions for tkinter.
        # self.datafilename, importtext = datafile
        self.datafilename, self.importtext = datafile

        super(ImportEvents, self).__init__(
            parent=parent,
            taskheader=self.datafilename,
            # taskdata=importtext,
            taskdata=self.importtext,  # See preceding comment.
            taskbuttons={
                self._btn_closeimport: dict(
                    text="Cancel Import",
                    tooltip="Cancel the Events import.",
                    underline=0,
                    switchpanel=True,
                    command=self.on_cancel_import_events,
                ),
                self._btn_startimport: dict(
                    text="Start Import",
                    tooltip="Start the Events import.",
                    underline=6,
                    command=self.on_start_import_events,
                ),
                self._btn_previewimport: dict(
                    text="Preview Import",
                    tooltip="Show what the import will do and needs.",
                    underline=0,
                    command=self.on_preview_import_events,
                ),
                self._btn_renameimporteventsreport: dict(
                    text="Rename Import Report",
                    tooltip="".join(
                        (
                            "The report is used in the Identify application to ",
                            "resolve player identities",
                        )
                    ),
                    underline=2,
                    command=self.on_rename_import_event_report,
                ),
                self._btn_pickreportforvalidation: dict(
                    text="Pick Validation Report",
                    tooltip="Validate against original Import.",
                    underline=5,
                    command=self.on_pick_report_for_validation,
                ),
            },
            starttaskbuttons=(
                self._btn_closeimport,
                self._btn_previewimport,
                self._btn_pickreportforvalidation,
                self._btn_renameimporteventsreport,
                self._btn_startimport,
            ),
            runmethod=False,
            runmethodargs=dict(),
            cnf=cnf,
            **kargs
        )
        self._copymethod = copymethod
        self._closecontexts = closecontexts
        self._validation_report = None
        self._importevent_report = None
        self._importdata = None

        # Import may need to modify records: so close contexts in this thread
        # to avoid record locking conflicts (DPT).
        # Doing this leads to other thread freeing file after which this thread
        # is unable to open the file unless it allocates the file first.
        # Creating the recordsets which support cursors, see dptbase module,
        # with 'find without locks' rather than 'find' is an alternative.  This
        # option is ignored because it will not do if support for increase file
        # size (DPT) is added to this path.
        # There should be better synchronization of what happens!  Like in the
        # process versions used elsewhere.  This code was split to keep the UI
        # responsive while doing long imports.
        self.get_appsys().get_results_database().close_database_contexts(
            closecontexts
        )

    def on_cancel_import_events(self, event=None):
        """Do any tidy up before switching to next panel.

        Re-open the files that were closed on creating this widget.
        """
        self.get_appsys().get_results_database().allocate_and_open_contexts(
            files=self._closecontexts
        )

    def on_start_import_events(self, event=None):
        """Run import_event in separate thread."""
        self.tasklog.run_method(method=self.import_events)

    def on_preview_import_events(self, event=None):
        """Run list_events_in_import_file in separate thread."""
        self.tasklog.run_method(method=self.list_events_in_import_file)

    def on_rename_import_event_report(self, event=None):
        """Run save_import_event_report in separate thread."""
        dlg = tkinter.filedialog.asksaveasfilename(
            parent=self.get_widget(),
            title="Import Report Name",
            defaultextension=".bz2",
            filetypes=(("bz2 compressed", "*.bz2"),),
        )
        if dlg:
            old, self._importevent_report = self._importevent_report, dlg
            if old:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            "The next import report will be saved in file\n\n",
                            self._importevent_report,
                            "\n\nrather than:\n\n.",
                            old,
                        )
                    ),
                    title="Import Report Name",
                )
            else:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            "The next import report will be saved in file\n\n",
                            self._importevent_report,
                            "\n\nrather than one named from the (system) time.",
                        )
                    ),
                    title="Import Report Name",
                )
        elif self._importevent_report:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "The file name already set:\n\n",
                        self._importevent_report,
                        "\n\nwill be used for the next import report.",
                    )
                ),
                title="Import Report Name",
            )
        else:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "The next import report will be saved in a file ",
                        "named from the (system) time.",
                    )
                ),
                title="Import Report Name",
            )

    def on_pick_report_for_validation(self, event=None):
        """Specify the import report to be used for validation."""
        title = "Validate against Report for previous Import"
        dlg = tkinter.filedialog.askopenfilename(
            parent=self.get_widget(),
            title=title,
            defaultextension=".bz2",
            filetypes=(("bz2 compressed", "*.bz2"),),
            initialdir="~",
        )
        if dlg:
            self._validation_report = dlg
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Import will be validated against\n\n",
                        os.path.basename(dlg),
                        "\n\nreport file.",
                    )
                ),
                title=title,
            )
        elif self._validation_report:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Import will be validated against\n\n",
                        os.path.basename(dlg),
                        "\n\nreport file.  This was already set.",
                    )
                ),
                title=title,
            )
        else:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Validation report file not set and import will not ",
                        "be done if validation is needed.",
                    )
                ),
                title=title,
            )

    def get_event_data_to_be_imported(self, logwidget=None):
        """Import data from file in results export format."""
        tasklog = self.tasklog

        # See comment in function _do_ecf_reference_data_import of relative
        # module ..core.ecfdataimport for explanation of this change.
        # But this bit should have been done this way anyway.
        # importdata = importreports.get_import_event_reports(
        #    self.datawidget.get(
        #        '1.0', tkinter.END).rstrip().split('\n'))
        importdata = importreports.get_import_event_reports(
            self.importtext.decode().rstrip().split("\n")
        )

        if importdata is None:
            tasklog.append_text("Unable to extract events from import file.")
            tasklog.append_text_only("")
            return False
        else:
            ien = importdata.get_event_names()
            if len(ien) == 0:
                if tasklog:
                    tasklog.append_text("No events in input file.")
                    tasklog.append_text_only("")
                    return False
            elif len(ien) == 1:
                tasklog.append_text("Event to be imported:")
            else:
                tasklog.append_text("Events to be imported:")
            for en in ien:
                tasklog.append_text_only("  ".join((en[1], en[2], en[0])))
            tasklog.append_text_only("")
            self._importdata = importdata
            return True

    def import_events(self, logwidget=None):
        """Import data from file in results export format."""
        tasklog = self.tasklog
        tasklog.append_text("Import Events started.")
        tasklog.append_text_only("")

        if not self.get_event_data_to_be_imported(logwidget=logwidget):
            return False

        if not self._importdata:
            tasklog.append_text(
                "".join(
                    (
                        "Import Events abandoned.  No data extracted from ",
                        "import file.",
                    )
                )
            )
            tasklog.append_text_only("")
            return False

        importdata = self._importdata
        if importdata.remoteplayer:
            if len(importdata.get_new_players()):
                # input contains new players that have not been matched
                # with known players or not declared new.
                # remoteplayer is empty for the initial submission
                message = " ".join(
                    (
                        "Some exported players are not identified on the ",
                        "importing database.  Use the Identify application to ",
                        "decide the missing identifications.\n\nThe owner of ",
                        "the exporting database is probably able to do this ",
                        "best.",
                    )
                )
                tasklog.append_text(
                    "".join(
                        (
                            "Import Events abandoned.  Identification decisions ",
                            "are missing for some unmatched players.",
                        )
                    )
                )
                tasklog.append_text_only("")
                tasklog.append_text_only(message)
                return
            if not self._validation_report:
                tasklog.append_text("Validation Report file not set.")
                tasklog.append_text_only("")
                tasklog.append_text_only(
                    "".join(
                        (
                            "The import file contains identification decisions for ",
                            "all players in the events being imported.  Before ",
                            "importing the events, this import file must be ",
                            "validated against the report file produced for the ",
                            "original import file.",
                        )
                    )
                )
                tasklog.append_text_only("")
                return

            # if import file is response to request for player identifications
            # there should be request file consistent with import file being
            # processed
            importdata = self._importdata
            tasklog.append_text(
                "Validating import againt report to which it is the response."
            )
            tasklog.append_text_only("")
            tasklog.append_text_only("Import file:")
            tasklog.append_text_only(self.datafilename)
            tasklog.append_text_only("Report file:")
            tasklog.append_text_only(self._validation_report)
            tasklog.append_text_only("")
            if self._validation_report == self.datafilename:
                tasklog.append_text_only(
                    "Must not validate import file against itself."
                )
                tasklog.append_text_only("")
                return False
            bz2file = bz2.open(self._validation_report, "rt", encoding="utf8")
            originaldata = bz2file.read()
            bz2file.close()

            # See comment in function _do_ecf_reference_data_import of relative
            # module ..core.ecfdataimport for explanation of this change.
            # But this bit should have been done this way anyway.
            # if originaldata == self.datawidget.get(
            #    '1.0', tkinter.END).rstrip():
            if originaldata == self.importtext.decode().rstrip():
                tasklog.append_text_only(
                    "".join(
                        (
                            "Must not validate import file against a file which ",
                            "contains the data.",
                        )
                    )
                )
                tasklog.append_text_only("")
                return False

            req = importreports.get_import_event_reports(
                originaldata.split("\n")
            )
            if not req:
                tasklog.append_text_only(
                    "The selected report file is not a valid report file."
                )
                tasklog.append_text_only("")
                return False
            if not importdata.is_reply_consistent_with_request(req):
                tasklog.append_text_only(
                    "".join(
                        (
                            "Cannot proceed with import becuse the import file is ",
                            "not consistent with the selected report file.  Perhaps ",
                            "the wrong report file was selected.",
                        )
                    )
                )
                tasklog.append_text_only("")
                return False
            del req

            self.get_appsys().get_results_database().do_database_task(
                self.validate_and_do_updates,
                tasklog,
                dict(importdata=importdata),
            )
        else:
            self.get_appsys().get_results_database().do_database_task(
                self.do_updates, tasklog
            )

    def list_events_in_import_file(self, logwidget=None):
        """List events found in file in results export format."""
        tasklog = self.tasklog
        tasklog.append_text("Preview Events to be imported started.")
        tasklog.append_text_only("")

        if not self.get_event_data_to_be_imported(logwidget=logwidget):
            return False

        if not self._importdata:
            tasklog.append_text(
                "".join(
                    (
                        "List Events abandoned.  No data extracted from ",
                        "import file.",
                    )
                )
            )
            tasklog.append_text_only("")
            return False

        importdata = self._importdata
        if importdata.remoteplayer:
            if len(importdata.get_new_players()):
                # input contains new players that have not been matched
                # with known players or not declared new.
                # remoteplayer is empty for the initial submission
                message = " ".join(
                    (
                        "Some exported players are not identified on the ",
                        "importing database.  Use the Identify application to ",
                        "decide the missing identifications.\n\nThe owner of ",
                        "the exporting database is probably able to do this ",
                        "best.",
                    )
                )
                tasklog.append_text(
                    "".join(
                        (
                            "List Events abandoned.  Identification decisions ",
                            "are missing for some unmatched players.",
                        )
                    )
                )
                tasklog.append_text_only("")
                tasklog.append_text_only(message)
                return
            tasklog.append_text(
                "".join(
                    (
                        "The import file contains identification decisions for ",
                        "all players in the events being imported.  Before ",
                        "importing the events, this import file must be ",
                        "validated against the report file produced for the ",
                        "original import file.",
                    )
                )
            )
            tasklog.append_text_only("")
            return

        self.get_appsys().get_results_database().do_database_task(
            self.list_events, tasklog
        )

    def list_events(self, database, tasklog):
        """The import file is ok.  List the events in the file."""
        importdata = self._importdata
        tasklog.append_text(
            "Preparing to check the import file against the database."
        )
        tasklog.append_text_only("")
        collation = importcollation.ImportCollation(importdata)
        collatedb = importcollationdb.ImportCollationDB(collation, database)
        if not collatedb.is_database_empty_of_players():
            tasklog.append_text(
                "".join(
                    (
                        "Check that player identifications are consistent between ",
                        "import file and database.",
                    )
                )
            )
            inconsistent = collatedb.is_player_identification_inconsistent()
            if len(inconsistent):
                tasklog.append_text(
                    "".join(
                        (
                            "The import would not be attempted because player ",
                            "identifications on import are not consistent with ",
                            "player records on database.",
                        )
                    )
                )
                tasklog.append_text_only("")
                return
            tasklog.append_text("The import would be attempted.")
            tasklog.append_text_only("")
        else:
            # warning if import file expects an occupied database?
            tasklog.append_text("The import would be attempted.")
            tasklog.append_text(
                "The exporting database's identifications would be accepted."
            )
            tasklog.append_text_only(
                "(The database was empty at time of assessment.)"
            )
            tasklog.append_text_only("")

    def do_updates(self, database, tasklog):
        """The import file is ok.  Do the updates."""
        importdata = self._importdata
        tasklog.append_text(
            "Preparing to check the import file against the database."
        )
        tasklog.append_text_only("")
        collation = importcollation.ImportCollation(importdata)
        collatedb = importcollationdb.ImportCollationDB(collation, database)
        if not collatedb.is_database_empty_of_players():
            tasklog.append_text(
                "".join(
                    (
                        "Check that player identifications are consistent between ",
                        "import file and database.",
                    )
                )
            )
            inconsistent = collatedb.is_player_identification_inconsistent()
            if len(inconsistent):
                tasklog.append_text(
                    "".join(
                        (
                            "Cannot proceed with import because player ",
                            "identifications on import are not consistent with ",
                            "player records on database.",
                        )
                    )
                )
                tasklog.append_text_only("")
                return
            database.start_transaction()
            tasklog.append_text("Update database with imported results.")
            collatedb.update_results()
            tasklog.append_text("Merge exported database players.")
            collatedb.merge_players()
        else:
            # warning if import file expects an occupied database?
            database.start_transaction()
            tasklog.append_text("Update database with imported results.")
            collatedb.update_results()
            tasklog.append_text("Accept exporting database identifications.")
            tasklog.append_text_only(
                "(The database was empty before importing these events)"
            )
            collatedb.identify_players()
        tasklog.append_text("Commit updates.")
        database.commit()
        tasklog.append_text("Database update completed.")
        tasklog.append_text_only("")

        # See comment in function _do_ecf_reference_data_import of relative
        # module ..core.ecfdataimport for explanation of this change.
        # But this bit should have been done this way anyway.
        # reportdata = self.datawidget.get(
        #    '1.0', tkinter.END).rstrip().split('\n')
        reportdata = self.importtext.decode().rstrip().split("\n")
        reportdata.extend(collatedb.export_players_on_database())

        importevent_report = self._importevent_report
        if not importevent_report:
            importevent_report = os.path.join(
                os.path.dirname(self.datafilename),
                "".join("".join(ctime().split()).split(":")),
            )
            tasklog.append_text("Validation report file name not available.")
            tasklog.append_text_only(
                "A name generated from the current (system) time will be used."
            )
            tasklog.append_text_only("")
        self._importevent_report = None
        tasklog.append_text("Saving Import Events report.")
        tasklog.append_text_only("")
        ouputfile = bz2.open(importevent_report, mode="wt", encoding="utf8")
        try:
            ouputfile.write("\n".join(reportdata))
            tasklog.append_text("Import Events report saved in")
            tasklog.append_text_only(importevent_report)
            tasklog.append_text_only("")
        finally:
            ouputfile.close()
        tasklog.append_text_only(
            "".join(
                (
                    "The Import Events Report enables use of the Identify ",
                    "application to record decisions identifying players on the ",
                    "exporting database as players on the importing database.",
                )
            )
        )
        tasklog.append_text_only("")

    def validate_and_do_updates(self, database, tasklog, importdata=None):
        """Validate merge import against original import."""
        collreq = importcollation.ImportCollation(importdata)
        collreqdb = importcollationdb.ImportCollationDB(collreq, database)
        if not collreqdb.is_database_empty_of_players():
            if collreqdb.is_new_player_inconsistent():
                tasklog.append_text(
                    "".join(
                        (
                            "Cannot proceed with import because new players are ",
                            "not consistent with database.  Perhaps validation ",
                            "done against wrong request.",
                        )
                    )
                )
                tasklog.append_text_only("")
                return
        del collreq, collreqdb

        self.do_updates(database, tasklog)

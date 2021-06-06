# importecfogd.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Import ECF Online Grading Database panel class.

Import ECF Online Grading Database actions are on this panel.

"""

import tkinter
import tkinter.messagebox
import os
import csv

from solentware_grid.datagrid import DataGridReadOnly
from solentware_grid.core.dataclient import DataSource

from solentware_misc.gui import logpanel, tasklog, exceptionhandler

from ..minorbases.textapi import TextapiError
from ..core import ecfogddb
from ..core import ecfogdrecord
from ..core import filespec
from .minorbases.textdatarow import TextDataRow, TextDataHeader


class ImportECFOGD(logpanel.WidgetAndLogPanel):

    """The panel for importing an ECF Online Grading Database CSV file."""

    _btn_closeecfogdimport = "importecfogd_close"
    _btn_startecfogdimport = "importecfogd_start"

    def __init__(
        self,
        parent=None,
        datafilespec=None,
        datafilename=None,
        closecontexts=(),
        starttaskmsg=None,
        tabtitle=None,
        copymethod=None,
        cnf=dict(),
        **kargs
    ):
        """Extend and define the ECF Online Grading Database import tab."""

        def _create_ogd_datagrid_widget(master):
            """Create a DataGrid under master.

            This method is designed to be passed as the maketaskwidget argument
            to a WidgetAndLogPanel(...) call.

            """

            # Added when DataGridBase changed to assume a popup menu is
            # available when right-click done on empty part of data drid frame.
            # The popup is used to show all navigation available from grid: but
            # this is not done in results, at least yet, so avoid the temporary
            # loss of focus to an empty popup menu.
            class OGDimportgrid(
                exceptionhandler.ExceptionHandler, DataGridReadOnly
            ):
                def show_popup_menu_no_row(self, event=None):
                    pass

            self.datagrid = OGDimportgrid(master)
            try:
                self.datagrid.set_data_source(
                    DataSource(newrow=TextDataRow, *datafilespec)
                )
                db = self.datagrid.get_data_source().dbhome.main[
                    ecfogddb.PLAYERS
                ]
                self.datagrid.set_data_header(header=TextDataHeader)
                self.datagrid.make_header(
                    TextDataHeader.make_header_specification(
                        fieldnames=[db.headerline]
                    )
                )
                return self.datagrid.frame
            except TextapiError as msg:
                try:
                    datafile.close_context()
                except:
                    pass
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message=str(msg),
                    title=" ".join(["Open ECF reference file"]),
                )
            except Exception as msg:
                try:
                    datafilespec[0].close_context()
                except:
                    pass
                dlg = tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message=" ".join([str(Exception), str(msg)]),
                    title=" ".join(["Open ECF reference file"]),
                )

        super(ImportECFOGD, self).__init__(
            parent=parent,
            taskheader="   ".join(
                (datafilename[0], datafilename[1].join(("(", ")")))
            ),
            maketaskwidget=_create_ogd_datagrid_widget,
            taskbuttons={
                self._btn_closeecfogdimport: dict(
                    text="Cancel Import",
                    tooltip="Cancel the Events import.",
                    underline=0,
                    switchpanel=True,
                    command=self.on_cancel_ecf_import,
                ),
                self._btn_startecfogdimport: dict(
                    text="Start Import",
                    tooltip="Start the Events import.",
                    underline=6,
                    command=self.on_start_ecf_import,
                ),
            },
            starttaskbuttons=(
                self._btn_closeecfogdimport,
                self._btn_startecfogdimport,
            ),
            runmethod=False,
            runmethodargs=dict(),
            cnf=cnf,
            **kargs
        )
        self._copymethod = copymethod
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

    def on_cancel_ecf_import(self, event=None):
        """Do any tidy up before switching to next panel.

        Re-open the files that were closed on creating this widget.
        """
        self.get_appsys().get_results_database().allocate_and_open_contexts(
            files=self._closecontexts
        )

        try:
            self.datagrid.get_data_source().get_database().close()
        except:
            pass

    def on_start_ecf_import(self, event=None):
        """Run get_event_data_to_be_imported in separate thread."""
        self.tasklog.run_method(method=self._copymethod, args=(self,))

    def show_buttons_for_cancel_import(self):
        """Show buttons for actions allowed at start of import process."""
        self.hide_panel_buttons()
        self.show_panel_buttons((self._btn_closeecfogdimport,))

    def _copy_ogd_players(self, logwidget=None):
        """Import a new ECF Online Grading Database (player file)."""
        self.tasklog.append_text(
            "Extract players from Online Grading Database file."
        )
        self.tasklog.append_text_only("")
        results = self.get_appsys().get_results_database()
        ogdfile = self.datagrid.get_data_source().dbhome.main[ecfogddb.PLAYERS]
        gcodes = dict()
        duplicates = []
        checkfails = []
        ref = ecfogdrecord._ECFOGDplayercodefield
        name = ecfogdrecord._ECFOGDplayernamefield
        clubs = ecfogdrecord._ECFOGDplayerclubsfields
        r = csv.DictReader(
            [o.decode("iso-8859-1") for o in ogdfile.textlines],
            ogdfile.fieldnames,
        )
        for row in r:
            gcodes.setdefault(row[ref], []).append(
                (row[name], [row[c] for c in clubs])
            )
        for k, v in gcodes.items():
            if len(v) > 1:
                duplicates.append(k)
            if len(k) != 7:
                checkfails.append(k)
            else:
                tokens = list(k)
                checkdigit = 0
                for i in range(6):
                    if not tokens[i].isdigit():
                        checkfails.append(k)
                        break
                    checkdigit += int(tokens[5 - i]) * (i + 2)
                else:
                    if tokens[-1] != "ABCDEFGHJKL"[checkdigit % 11]:
                        checkfails.append(k)
        if len(duplicates) or len(checkfails):
            self.tasklog.append_text(
                "Import from Online Grading Database abandonned."
            )
            if len(duplicates):
                self.tasklog.append_text_only("Duplicate grading codes exist.")
            if len(checkfails):
                self.tasklog.append_text_only(
                    "Grading codes exist that fail the checkdigit test."
                )
            self.tasklog.append_text_only("")
            return

        results.start_transaction()
        self.tasklog.append_text(
            "Update existing records from Online Grading Database file."
        )
        startlengcodes = len(gcodes)
        ogdplayerrec = ecfogdrecord.ECFrefOGDrecordPlayer()
        ogdplayers = results.database_cursor(
            filespec.ECFOGDPLAYER_FILE_DEF, filespec.ECFOGDPLAYER_FIELD_DEF
        )
        try:
            data = ogdplayers.first()
            while data:
                ogdplayerrec.load_record(data)
                code = ogdplayerrec.value.ECFOGDcode
                newrec = ogdplayerrec.clone()
                if code in gcodes:
                    newrec.value.ECFOGDname = gcodes[code][0][0]
                    newrec.value.ECFOGDclubs = [c for c in gcodes[code][0][1]]
                    del gcodes[code]
                else:
                    newrec.value.ECFOGDname = None
                    newrec.value.ECFOGDclubs = []
                ogdplayerrec.edit_record(
                    results,
                    filespec.ECFOGDPLAYER_FILE_DEF,
                    filespec.ECFOGDPLAYER_FIELD_DEF,
                    newrec,
                )
                data = ogdplayers.next()
        finally:
            ogdplayers.close()
        self.tasklog.append_text_only(
            "".join(
                (
                    str(startlengcodes - len(gcodes)),
                    " records were updated.",
                )
            )
        )

        self.tasklog.append_text(
            "Create new records from Online Grading Database file."
        )
        self.tasklog.append_text_only(
            "".join(
                (
                    str(len(gcodes)),
                    " records will be created.",
                )
            )
        )
        for k, v in gcodes.items():
            ogdplayerrec = ecfogdrecord.ECFrefOGDrecordPlayer()
            ogdplayerrec.key.recno = None
            ogdplayerrec.value.ECFOGDcode = k
            ogdplayerrec.value.ECFOGDname = v[0][0]
            ogdplayerrec.value.ECFOGDclubs = [c for c in v[0][1]]
            ogdplayerrec.put_record(results, filespec.ECFOGDPLAYER_FILE_DEF)
        self.tasklog.append_text("Commit database update.")
        self.tasklog.append_text_only("")
        results.commit()
        self.tasklog.append_text(
            "".join(
                (
                    "Grading Codes and names imported from ",
                    "Online Grading database.",
                )
            )
        )
        self.tasklog.append_text_only("")
        return True

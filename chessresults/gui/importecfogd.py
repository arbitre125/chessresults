# importecfogd.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Import ECF Online Grading Database panel class.

Import ECF Online Grading Database actions are on this panel.

"""

import tkinter
import tkinter.messagebox

from solentware_grid.datagrid import DataGridReadOnly
from solentware_grid.core.dataclient import DataSource

from solentware_misc.gui import logpanel, tasklog, exceptionhandler

from ..minorbases.textapi import TextapiError
from ..core import ecfogddb
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

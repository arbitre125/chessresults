# importecfdata.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Import ECF Data panel class.

Import ECF data actions are on this panel.
"""

import tkinter
import tkinter.messagebox
import os

from solentware_grid.datagrid import DataGridReadOnly
from solentware_grid.core.dataclient import DataSource

from solentware_misc.api import utilities
from solentware_misc.gui import logpanel, tasklog, exceptionhandler

from ..core import filespec
from ..minorbases.dbaseapi import dBaseapiError
from .minorbases.dbasedatarow import dBaseDataRow, dBaseDataHeader

_REFRESH_FILE_FIELD = {
    filespec.ECFPLAYER_FILE_DEF: filespec.ECFPLAYERNAME_FIELD_DEF,
    filespec.ECFCLUB_FILE_DEF: filespec.ECFCLUBNAME_FIELD_DEF,
}


class ImportECFData(logpanel.WidgetAndLogPanel):

    """The panel for importing an ECF dBaseIII reference file."""

    _btn_closeecfimport = "importecfdata_close"
    _btn_startecfimport = "importecfdata_start"

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
        """Extend and define the results ECF reference data import tab."""

        def _create_ecf_datagrid_widget(master):
            """Create a DataGrid under master.

            This method is designed to be passed as the maketaskwidget argument
            to a WidgetAndLogPanel(...) call.

            """
            self.ecfdatecontrol = tkinter.Entry(master=self.get_widget())
            self.ecfdatecontrol.pack(side=tkinter.TOP, fill=tkinter.X)
            self.ecfdatecontrol.insert(
                tkinter.END, self._get_date_from_filename(datafilename[1])
            )

            # Added when DataGridBase changed to assume a popup menu is
            # available when right-click done on empty part of data drid frame.
            # The popup is used to show all navigation available from grid: but
            # this is not done in results, at least yet, so avoid the temporary
            # loss of focus to an empty popup menu.
            class ECFimportgrid(
                exceptionhandler.ExceptionHandler, DataGridReadOnly
            ):
                def show_popup_menu_no_row(self, event=None):
                    pass

            self.datagrid = ECFimportgrid(master)
            try:
                self.datagrid.set_data_source(
                    DataSource(newrow=dBaseDataRow, *datafilespec)
                )
                self.datagrid.set_data_header(header=dBaseDataHeader)
                self.datagrid.make_header(
                    dBaseDataHeader.make_header_specification(
                        fieldnames=self.datagrid.get_database().fieldnames
                    )
                )
                return self.datagrid.frame
            except dBaseapiError as msg:
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

        super(ImportECFData, self).__init__(
            parent=parent,
            taskheader="   ".join(
                (datafilename[0], datafilename[1].join(("(", ")")))
            ),
            maketaskwidget=_create_ecf_datagrid_widget,
            taskbuttons={
                self._btn_closeecfimport: dict(
                    text="Cancel Import",
                    tooltip="Cancel the Events import.",
                    underline=0,
                    switchpanel=True,
                    command=self.on_cancel_ecf_import,
                ),
                self._btn_startecfimport: dict(
                    text="Start Import",
                    tooltip="Start the Events import.",
                    underline=6,
                    command=self.on_start_ecf_import,
                ),
            },
            starttaskbuttons=(
                self._btn_closeecfimport,
                self._btn_startecfimport,
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

    def get_ecf_date(self):
        """Return ECF file date in 'yyyymmdd' format."""
        if self.ecfdatecontrol != None:
            ecfdate = utilities.AppSysDate()
            dv = self.ecfdatecontrol.get()
            d = ecfdate.parse_date(dv)
            if d == len(dv):
                return "".join(ecfdate.iso_format_date().split("-"))
        return False

    def is_ecf_date_valid(self):
        """Show dialogue to confirm date of ECF master file."""
        if self.ecfdatecontrol != None:
            ecfdate = utilities.AppSysDate()
            dv = self.ecfdatecontrol.get()
            d = ecfdate.parse_date(dv)
            if d == len(dv):
                if tkinter.messagebox.askyesno(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            "Confirm ",
                            dv,
                            ecfdate.iso_format_date().join(("\n(", ")\n")),
                            "is correct date for the ECF data file",
                        )
                    ),
                    title="Import ECF data",
                ):
                    return "".join(ecfdate.iso_format_date().split("-"))
                else:
                    return False
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join((dv, "is not a date")),
                title="Import ECF data",
            )
        else:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="A date for the ECF data is not available",
                title="Import ECF data",
            )
        return False

    def on_cancel_ecf_import(self, event=None):
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
        try:
            self.datagrid.get_data_source().get_database().close()
        except:
            pass

    def on_start_ecf_import(self, event=None):
        """Run get_event_data_to_be_imported in separate thread."""
        if not self.is_ecf_date_valid():
            return

        # tkinter may have been compiled without --enable-threads so pass
        # self.get_ecf_date(), self.ecfdatecontrol.get(), and self separately.
        # See comment in relative module ..core.ecfdataimport in function
        # _do_ecf_reference_data_import().
        self.tasklog.run_method(
            method=self._copymethod,
            args=(self,),
            kwargs=dict(
                ecfdate=self.get_ecf_date(),
                datecontrol=self.ecfdatecontrol.get(),
            ),
        )

    def show_buttons_for_cancel_import(self):
        """Show buttons for actions allowed at start of import process."""
        self.hide_panel_buttons()
        self.show_panel_buttons((self._btn_closeecfimport,))

    def show_buttons_for_start_ecf_import(self):
        """Show buttons for actions allowed at start of import process."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (self._btn_closeecfimport, self._btn_startecfimport)
        )

    def _get_date_from_filename(self, filename):
        """Return date derived from filename."""
        dt = utilities.AppSysDate()
        bdate = [
            d
            for d in os.path.split(os.path.splitext(filename)[0])[-1]
            if d.isdigit()
        ]
        baseyear = "".join(bdate[:-4])
        year = str(dt.get_current_year())
        byear = "".join((year[: -len(baseyear)], baseyear))
        if byear > year:
            byear = str(int(byear) - (10 * len(baseyear)))
        ds = ".".join(("".join(bdate[-2:]), "".join(bdate[-4:-2]), byear))
        if dt.parse_date(ds) == len(ds):
            return " ".join(
                (
                    str(int("".join(bdate[-2:]))),
                    dt.get_month_name(int("".join(bdate[-4:-2])) - 1),
                    byear,
                )
            )
        else:
            return ""

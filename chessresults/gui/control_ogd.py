# control_ogd.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Control panel class.

Open and close databases and import and export data functions are available
on this panel.

"""

import tkinter
import tkinter.messagebox
import tkinter.filedialog
import os
import zipfile
import io

from ..minorbases.textapi import TextapiError
from ..core.filespec import ECFOGDPLAYER_FILE_DEF, MAPECFOGDPLAYER_FILE_DEF
from ..core import ecfogddataimport
from ..core import ecfogddb
from . import control_lite


class Control(control_lite.Control):

    """The Control panel for a Results database."""

    _btn_copyecfogdgradingfile = "control_ogd_copy_grading"
    _btn_ecfogdgradingfile = "control_ogd_grading_file"
    _btn_quitecfogdzippedfiles = "control_ogd_quit"

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database control panel."""
        super(Control, self).__init__(parent=parent, cnf=cnf, **kargs)

        self.ecfogdfile = None

    def close_update_resources(self):
        """Close any open files containing master data from ECF."""
        if self.ecfogdfile != None:
            self.ecfogdfile.close_context()
            self._delete_text_files(self.ecfogdfile)
            self.ecfogdfile = None

    def describe_buttons(self):
        """Define all action buttons that may appear on Control page."""
        self.define_button(
            self._btn_closedatabase,
            text="Shut Database",
            tooltip="Close the open database.",
            underline=9,
            switchpanel=True,
            command=self.on_close_database,
        )
        self.define_button(
            self._btn_importevents,
            text="Import Events",
            tooltip="Import event data exported by Export Events.",
            underline=0,
            switchpanel=True,
            command=self.on_import_events,
        )
        self.define_button(
            self._btn_ecfogdgradingfile,
            text="ECF OGD File",
            tooltip="Open a zipped ECF Online Grading Database file.",
            underline=4,
            command=self.on_ecf_ogd_grading_file,
        )
        self.define_button(
            self._btn_copyecfogdgradingfile,
            text="Show ECF OGD File",
            tooltip="Build new Master file for players.",
            underline=13,
            switchpanel=True,
            command=self.on_copy_ecf_ogd_grading_file,
        )
        self.define_button(
            self._btn_quitecfogdzippedfiles,
            text="Close File List",
            tooltip="Close the list of files in the zipped archive.",
            underline=1,
            command=self.on_quit_ecf_ogd_zipped_files,
        )

    def display_ecf_ogd_zipped_file_contents(self, initialdir=""):
        """Display ECF master data with date for confirmation of update."""
        if not initialdir:
            initialdir = "~"
        dlg = tkinter.filedialog.askopenfilename(
            parent=self.get_widget(),
            title="Open ECF data file",
            defaultextension=".zip",
            filetypes=(("ECF master lists", "*.zip"),),
            initialdir=initialdir,
        )
        if not dlg:
            return

        ziparchive = zipfile.ZipFile(dlg, "r")
        try:
            namelist = ziparchive.namelist()
            if len(namelist):
                frame = tkinter.Frame(master=self.get_widget())
                listbox = tkinter.Listbox(master=frame)
                yscrollbar = tkinter.Scrollbar(
                    master=frame,
                    orient=tkinter.VERTICAL,
                    command=listbox.yview,
                )
                xscrollbar = tkinter.Scrollbar(
                    master=frame,
                    orient=tkinter.HORIZONTAL,
                    command=listbox.xview,
                )
                listbox.configure(
                    yscrollcommand=yscrollbar.set,
                    xscrollcommand=xscrollbar.set,
                )
                yscrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
                xscrollbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
                listbox.pack(fill=tkinter.BOTH, expand=tkinter.TRUE)
                frame.pack(fill=tkinter.BOTH, expand=tkinter.TRUE)
                listbox.insert(tkinter.END, *sorted(namelist))
                self.datafilepath.configure(text=dlg)
                self.ecf_reference_file = listbox
                self._ecf_reference_widget = frame
                return True
        finally:
            ziparchive.close()

    def on_quit_ecf_ogd_data(self, event=None):
        """Do quit import ECF Grading List actions."""
        if self.close_import_file("ECF Online Grading Database"):
            self.show_buttons_for_open_database()
            self.create_buttons()

    def show_buttons_for_import_ecf_ogd_data(self):
        """Show buttons for actions allowed selecting ECF data to import."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (
                self._btn_closedatabase,
                self._btn_quitecfogdzippedfiles,
                self._btn_copyecfogdgradingfile,
            )
        )

    def show_buttons_for_open_database(self):
        """Show buttons for actions allowed when database is open."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (
                self._btn_closedatabase,
                self._btn_ecfogdgradingfile,
                self._btn_importevents,
            )
        )

    def _delete_text_files(self, textobject):
        """Delete files extracted from ECF Grading List ZIP file."""
        if not textobject:
            return False

        for obj in textobject.textdbfiles.values():
            if os.path.isfile(obj["file"]):
                try:
                    os.remove(obj["file"])
                except:
                    pass

    def on_quit_ecf_ogd_zipped_files(self, event=None):
        """Do quit import ECF Grading List actions."""
        self._ecf_reference_widget.destroy()
        self._ecf_reference_widget = None
        self.datafilepath.configure(
            text=os.path.dirname(self.datafilepath.cget("text"))
        )
        self.ecf_reference_file = None
        self.show_buttons_for_open_database()
        self.create_buttons()

    def on_ecf_ogd_grading_file(self, event=None):
        """Do display ECF Grading List actions."""
        if self.display_ecf_ogd_zipped_file_contents(
            self.datafilepath.cget("text"),
        ):
            self.show_buttons_for_import_ecf_ogd_data()
            self.create_buttons()

    def on_copy_ecf_ogd_grading_file(self, event=None):
        """Do copy ECF Grading List actions."""
        dbspec = self._get_memory_csv_from_zipfile(ecfogddb.ECFOGD)
        if dbspec is None:
            self.inhibit_context_switch(self._btn_copyecfogdgradingfile)
            return
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            dict(
                datafilespec=(dbspec[0], ecfogddb.PLAYERS, ecfogddb.PLAYERS),
                datafilename=dbspec[1],
                closecontexts=(
                    ECFOGDPLAYER_FILE_DEF,
                    MAPECFOGDPLAYER_FILE_DEF,
                ),
                tabtitle="Grading List",
                copymethod=ecfogddataimport.copy_ecf_ogd_players_post_2006_rules,
            )
        )

    def _get_memory_csv_from_zipfile(self, dbdefinition):
        """Create 'in-memory' CSV file from zipped file."""
        selection = self.ecf_reference_file.curselection()
        if not selection:
            return
        selected_file = self.datafilepath.cget("text")
        selected_element = self.ecf_reference_file.get(selection)
        return self.open_file_from_ecf_zipped_master_file(
            dbdefinition,
            None,
            None,
            selected_file,
            selected_element,
        )

    def open_file_from_ecf_zipped_master_file(
        self, dbdefinition, dbset, dbname, archive, element
    ):
        """Display ECF grsding list data with date for confirmation of update."""
        memory_file = None
        ziparchive = zipfile.ZipFile(archive, "r")
        try:
            for za in ziparchive.namelist():
                if za == element:
                    memory_file = io.BytesIO(ziparchive.read(za))
                    break
        finally:
            ziparchive.close()

        ecffile = dbdefinition(memory_file)
        try:
            ecffile.open_context()
            return (ecffile, (archive, element))
        except TextapiError as msg:
            try:
                ecffile.close_context()
            except:
                pass
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=str(msg),
                title=" ".join(["Open ECF OGD file"]),
            )
        except Exception as msg:
            try:
                ecffile.close_context()
            except:
                pass
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join([str(Exception), str(msg)]),
                title=" ".join(["Open ECF OGD file"]),
            )

# control.py
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
import email
import base64
import json
import urllib.request
import datetime

try:
    import tnefparse
except ImportError:  # Not ModuleNotFoundError for Pythons earlier than 3.6
    tnefparse = None

from solentware_misc.gui import dialogue
from solentware_misc.core.getconfigurationitem import get_configuration_item

from .feedback_monthly import show_ecf_results_feedback_monthly_tab
from ..minorbases.dbaseapi import dBaseapiError
from ..core.filespec import (
    ECFPLAYER_FILE_DEF,
    ECFCLUB_FILE_DEF,
    ECFTXN_FILE_DEF,
    MAPECFPLAYER_FILE_DEF,
)
from ..core import ecfdataimport
from ..core import ecfclubdb
from ..core import ecfplayerdb
from . import control_lite
from ..core import constants
from . import ecfdownload
from ..core import configuration


class Control(control_lite.Control):

    """The Control panel for a Results database."""

    _btn_ecfresultsfeedback = "control_feedback"
    _btn_ecfresultsfeedbackmonthly = "control_feedback_monthly"
    _btn_ecfmasterfile = "control_master_file"
    _btn_quitecfzippedfiles = "control_quit"
    _btn_copyecfmasterplayer = "control_copy_master_player"
    _btn_copyecfmasterclub = "control_copy_master_club"
    _btn_playersdownload = "control_players_download"
    _btn_clubsdownload = "control_clubs_download"

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database control panel."""
        super(Control, self).__init__(parent=parent, cnf=cnf, **kargs)

        self.ecf_reference_file = None
        self._ecf_reference_widget = None
        self.ecfclubfile = None
        self.ecfplayerfile = None
        self.ecfdatecontrol = None

    def close_update_resources(self):
        """Close any open files containing master data from ECF."""
        if self.ecfplayerfile != None:
            self.ecfplayerfile.close_context()
            self._delete_dbase_files(self.ecfplayerfile)
            self.ecfplayerfile = None
        if self.ecfclubfile != None:
            self.ecfclubfile.close_context()
            self._delete_dbase_files(self.ecfclubfile)
            self.ecfclubfile = None
        if self.ecfdatecontrol != None:
            self.ecfdatecontrol.destroy()
            self.ecfdatecontrol = None

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
            self._btn_ecfresultsfeedback,
            text="ECF Results Feedback",
            tooltip="Display a feedback email for a results submission to ECF.",
            underline=12,
            switchpanel=True,
            command=self.on_ecf_results_feedback,
        )
        self.define_button(
            self._btn_ecfresultsfeedbackmonthly,
            text="ECF Monthly Feedback",
            tooltip="Display a feedback email for a results upload to ECF.",
            underline=19,
            switchpanel=True,
            command=self.on_ecf_results_feedback_monthly,
        )
        self.define_button(
            self._btn_playersdownload,
            text="Rated Players Download",
            tooltip="Download list of rated players from ECF website",
            underline=7,
            switchpanel=True,
            command=self.on_ecf_players_download,
        )
        self.define_button(
            self._btn_clubsdownload,
            text="Active Clubs Download",
            tooltip="Download list of active clubs from ECF website",
            underline=4,
            switchpanel=True,
            command=self.on_ecf_clubs_download,
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
            self._btn_ecfmasterfile,
            text="ECF Master File",
            tooltip="Open a zipped ECF Master file.",
            underline=4,
            command=self.on_ecf_master_file,
        )
        self.define_button(
            self._btn_quitecfzippedfiles,
            text="Close File List",
            tooltip="Close the list of files in the zipped archive.",
            underline=1,
            command=self.on_quit_ecf_zipped_files,
        )
        self.define_button(
            self._btn_copyecfmasterplayer,
            text="Show Master File",
            tooltip="Build new Master file for players.",
            underline=3,
            switchpanel=True,
            command=self.on_copy_ecf_master_player,
        )
        self.define_button(
            self._btn_copyecfmasterclub,
            text="Show Master Club File",
            tooltip="Build new Master file for clubs.",
            underline=1,
            switchpanel=True,
            command=self.on_copy_ecf_master_club,
        )

    def on_ecf_results_feedback(self, event=None):
        """Do ECF feedback actions."""
        filepath = tkinter.filedialog.askopenfilename(
            parent=self.get_widget(),
            title="Open ECF feedback email or attachment",
            # defaultextension='.txt',
            # filetypes=(('ECF feedback', '*.txt'),),
            initialdir=configuration.get_configuration_value(
                constants.RECENT_FEEDBACK_EMAIL
            ),
        )
        if not filepath:
            self.inhibit_context_switch(self._btn_ecfresultsfeedback)
            return
        configuration.set_configuration_value(
            constants.RECENT_FEEDBACK_EMAIL,
            configuration.convert_home_directory_to_tilde(
                os.path.dirname(filepath)
            ),
        )
        try:
            feedbackfile = open(filepath, "rb")
            try:
                self.get_appsys().set_kwargs_for_next_tabclass_call(
                    dict(datafile=(filepath, _get_feedback_text(feedbackfile)))
                )
            finally:
                feedbackfile.close()
        except:
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    ("File\n", os.path.split(dlg)[-1], "\ndoes not exist")
                ),
                title=" ".join(["Open ECF feedback email or attachment"]),
            )
            return

    def on_ecf_results_feedback_monthly(self, event=None):
        """Do ECF feedback actions."""
        show_ecf_results_feedback_monthly_tab(
            self, self._btn_ecfresultsfeedbackmonthly)

    def _ecf_download(self, name, button, default_url, contexts, structure):
        """Do download actions for rated players or active clubs.

        The process is identical so provide arguments to fit each case.

        """
        name_title = name.title()
        title = " ".join(("Get", name_title))
        dlg = ecfdownload.ECFDownloadDialogue(
            self.appsys,
            title,
            text=name,
            scroll=False,
            height=7,
            width=60,
            wrap=tkinter.WORD,
        )
        dlg.go()
        if dlg.cancel_pressed():
            self.inhibit_context_switch(button)
            return
        if dlg.download_pressed():
            dialogue_result = dialogue.ModalEntryApply(
                self.appsys,
                title,
                body=(
                    (
                        "URL",
                        get_configuration_item(
                            os.path.expanduser(
                                os.path.join("~", constants.RESULTS_CONF)
                            ),
                            default_url,
                            constants.DEFAULT_URLS,
                        ),
                        None,
                        False,
                    ),
                ),
            ).result
            if dialogue_result is None:
                self.inhibit_context_switch(button)
                return
            urlname = dialogue_result["URL"]
            try:
                url = urllib.request.urlopen(urlname)
            except Exception as exc:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    title=title,
                    message="".join(
                        ("Exception raised trying to open URL\n\n", str(exc))
                    ),
                )
                self.inhibit_context_switch(button)
                return
            try:
                urldata = url.read()
            except Exception as exc:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    title=title,
                    message="".join(
                        ("Exception raised trying to read URL\n\n", str(exc))
                    ),
                )
                self.inhibit_context_switch(button)
                return
            try:
                data = structure(json.loads(urldata))
                self.get_appsys().set_kwargs_for_next_tabclass_call(
                    dict(
                        datafile=(urlname, str(datetime.date.today()), data),
                        closecontexts=contexts,
                    )
                )
            except Exception as exc:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    title=title,
                    message="".join(
                        (
                            name.join(
                                (
                                    "Exception raised trying to extract ",
                                    " from URL\n\n",
                                )
                            ),
                            str(exc),
                        )
                    ),
                )
                self.inhibit_context_switch(button)
                return
            return
        if dlg.extract_pressed():
            open_title = " ".join(("Open downloaded", name_title))
            dlg = tkinter.filedialog.askopenfilename(
                parent=self.get_widget(), title=open_title, initialdir="~"
            )
            if not dlg:
                self.inhibit_context_switch(button)
                return
            try:
                urldata = open(dlg).read()
            except Exception as exc:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    title=open_title,
                    message="".join(
                        ("Exception raised trying to read File\n\n", str(exc))
                    ),
                )
                self.inhibit_context_switch(button)
                return
            try:
                data = structure(json.loads(urldata))
                self.get_appsys().set_kwargs_for_next_tabclass_call(
                    dict(
                        datafile=(dlg, str(datetime.date.today()), data),
                        closecontexts=contexts,
                    )
                )
            except Exception as exc:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    title=open_title,
                    message="".join(
                        (
                            name.join(
                                (
                                    "Exception raised trying to extract ",
                                    " from URL\n\n",
                                )
                            ),
                            str(exc),
                        )
                    ),
                )
                self.inhibit_context_switch(button)
                return

    def _ecf_players_structure(self, data):
        """Callback for _ecf_download to validate json data structure."""
        if set(data.keys()) == constants.PLAYERS_RATINGS_KEYS:
            if (
                tuple(data[constants.P_R_COLUMN_NAMES])
                == constants.PLAYERS_RATINGS_COLUMN_NAMES
            ):
                return data
        raise RuntimeError(
            "Downloaded data not in expected format for rated players"
        )

    def _ecf_clubs_structure(self, data):
        """Callback for _ecf_download to validate json data structure."""
        if set(data.keys()) == constants.ACTIVE_CLUBS_KEYS:
            return data
        raise RuntimeError(
            "Downloaded data not in expected format for active clubs"
        )

    def on_ecf_players_download(self, event=None):
        """Do list of rated players download actions."""
        self._ecf_download(
            "rated players",
            self._btn_playersdownload,
            constants.PLAYERS_RATINGS_URL,
            (ECFPLAYER_FILE_DEF, ECFTXN_FILE_DEF, MAPECFPLAYER_FILE_DEF),
            self._ecf_players_structure,
        )

    def on_ecf_clubs_download(self, event=None):
        """Do ECF clubs download actions."""
        self._ecf_download(
            "active clubs",
            self._btn_clubsdownload,
            constants.ACTIVE_CLUBS_URL,
            (ECFCLUB_FILE_DEF, ECFTXN_FILE_DEF),
            self._ecf_clubs_structure,
        )

    def on_quit_ecf_zipped_files(self, event=None):
        """Do quit import ECF Master File actions."""
        self._ecf_reference_widget.destroy()
        self._ecf_reference_widget = None
        self.datafilepath.configure(
            text=os.path.dirname(self.datafilepath.cget("text"))
        )
        self.ecf_reference_file = None
        self.show_buttons_for_open_database()
        self.create_buttons()

    def on_copy_ecf_master_player(self, event=None):
        """Do copy ECF Master File (players) actions."""
        dbspec = self._get_memory_dBaseIII_from_zipfile(
            ecfplayerdb.ECFplayersDB
        )
        if dbspec is None:
            self.inhibit_context_switch(self._btn_copyecfmasterplayer)
            return
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            dict(
                datafilespec=(
                    dbspec[0],
                    ecfplayerdb.PLAYERS,
                    ecfplayerdb.PLAYERS,
                ),
                datafilename=dbspec[1],
                closecontexts=(
                    ECFPLAYER_FILE_DEF,
                    ECFTXN_FILE_DEF,
                    MAPECFPLAYER_FILE_DEF,
                ),
                tabtitle="Master List",
                copymethod=ecfdataimport.copy_ecf_players_post_2011_rules,
            )
        )

    def on_copy_ecf_master_club(self, event=None):
        """Do copy ECF club file actions."""
        dbspec = self._get_memory_dBaseIII_from_zipfile(ecfclubdb.ECFclubsDB)
        if dbspec is None:
            self.inhibit_context_switch(self._btn_copyecfmasterclub)
            return
        self.get_appsys().set_kwargs_for_next_tabclass_call(
            dict(
                datafilespec=(dbspec[0], ecfclubdb.CLUBS, ecfclubdb.CLUBS),
                datafilename=dbspec[1],
                closecontexts=(ECFCLUB_FILE_DEF, ECFTXN_FILE_DEF),
                tabtitle="Club List",
                copymethod=ecfdataimport.copy_ecf_clubs_post_2011_rules,
            )
        )

    def on_ecf_master_file(self, event=None):
        """Do unzip ECF master file actions"""
        if self.display_ecf_zipped_file_contents():
            self.show_buttons_for_ecf_master_file()
            self.create_buttons()

    def display_ecf_zipped_file_contents(self):
        """Display ECF master data with date for confirmation of update."""
        filepath = tkinter.filedialog.askopenfilename(
            parent=self.get_widget(),
            title="Open ECF data file",
            defaultextension=".zip",
            filetypes=(("ECF master lists", "*.zip"),),
            initialdir=configuration.get_configuration_value(
                constants.RECENT_MASTERFILE
            ),
        )
        if not filepath:
            return
        configuration.set_configuration_value(
            constants.RECENT_MASTERFILE,
            configuration.convert_home_directory_to_tilde(
                os.path.dirname(filepath)
            ),
        )

        ziparchive = zipfile.ZipFile(filepath, "r")
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
                self.datafilepath.configure(text=filepath)
                self.ecf_reference_file = listbox
                self._ecf_reference_widget = frame
                return True
        finally:
            ziparchive.close()

    def open_file_from_ecf_zipped_master_file(
        self, dbdefinition, dbset, dbname, archive, element
    ):
        """Display ECF master data with date for confirmation of update."""
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
        except dBaseapiError as msg:
            try:
                ecffile.close_context()
            except:
                pass
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=str(msg),
                title=" ".join(["Open ECF player file"]),
            )
        except Exception as msg:
            try:
                ecffile.close_context()
            except:
                pass
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message=" ".join([str(Exception), str(msg)]),
                title=" ".join(["Open ECF player file"]),
            )

    def show_buttons_for_ecf_master_file(self):
        """Show buttons for actions allowed importing new ECF player data."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (
                self._btn_closedatabase,
                self._btn_quitecfzippedfiles,
                self._btn_copyecfmasterclub,
                self._btn_copyecfmasterplayer,
            )
        )

    def show_buttons_for_open_database(self):
        """Show buttons for actions allowed when database is open."""
        self.hide_panel_buttons()
        self.show_panel_buttons(
            (
                self._btn_closedatabase,
                self._btn_ecfresultsfeedbackmonthly,
                self._btn_ecfresultsfeedback,
                self._btn_playersdownload,
                self._btn_clubsdownload,
                self._btn_ecfmasterfile,
                self._btn_importevents,
            )
        )

    def _delete_dbase_files(self, dbaseobject):
        """Delete DBF files extracted from ECF master file ZIP file."""
        if not dbaseobject:
            return False

        for obj in dbaseobject.dBasefiles.values():
            if os.path.isfile(obj._file):
                try:
                    os.remove(obj._file)
                except:
                    pass

    def _get_memory_dBaseIII_from_zipfile(self, dbdefinition):
        """Create 'in-memory' dBaseIII file from zipped file."""
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


def _get_feedback_text(file):
    """Return feedback text from open file.

    Required text is assumed to be in 'text/plain' parts of message, where the
    'text/plain' may be inside an 'application/ms-tnef' attachment.

    """
    m = email.message_from_binary_file(file)

    # Assume file is a saved attachment file when there are no headers.
    if not m.keys():
        file.seek(0)
        return [line.rstrip() for line in file.readlines()]

    text = []
    for part in m.walk():
        ct = part.get_content_type()
        if ct == "text/plain":
            text.extend(
                [
                    line.rstrip()
                    for line in part.get_payload().encode("utf8").split(b"\n")
                ]
            )
        elif ct == "application/ms-tnef":
            if not tnefparse:
                text.append(
                    b"Cannot process feedback: tnefparse is not installed."
                )
                continue

            # Assume the attachments are txt.
            # Feedback attachments have always been txt files: until December
            # 2016 these were not wrapped inside an application/ms-tnef
            # attachment.
            tnef = tnefparse.TNEF(base64.b64decode(part.get_payload()))
            for attachment in tnef.attachments:
                text.extend(
                    [line.rstrip() for line in attachment.data.split(b"\n")]
                )

    return text

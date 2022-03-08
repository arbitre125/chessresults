# leagues.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Leagues frame class.
"""

import os
import importlib
import tkinter.messagebox

from solentware_misc.gui.configuredialog import ConfigureDialog

from . import control
from . import events
from . import newplayers
from . import players
from . import ecfgradingcodes
from . import ecfclubcodes
from . import ecfevents
from . import ecfplayers
from . import newevent
from . import leagues_lite
from . import importecfdata
from . import feedback
from . import feedback_monthly
from . import joineventplayers
from . import activeclubs
from . import ratedplayers
from .. import ECF_DATA_IMPORT_MODULE
from .. import KNOWN_NAME_DATASOURCE_MODULE
from ..core import constants


class Leagues(leagues_lite.Leagues):

    """The Results frame for a Results database."""

    _tab_ecfeventdetail = "leagues_tab_ecfeventdetail"
    _tab_ecfgradingcodes = "leagues_tab_ecfgradingcodes"
    _tab_ecfclubcodes = "leagues_tab_ecfclubcodes"
    _tab_ecfevents = "leagues_tab_ecfevents"
    _tab_ecfplayers = "leagues_tab_ecfplayers"
    _tab_importecfdata = "leagues_tab_importecfdata"
    _tab_importfeedback = "leagues_tab_importfeedback"
    _tab_importfeedbackmonthly = "leagues_tab_importfeedback_monthly"
    _tab_joineventplayers = "leagues_tab_joineventplayers"
    _tab_clubsdownload = "leagues_tab_clubsdownload"
    _tab_playersdownload = "leagues_tab_playersdownload"

    _state_ecfeventdetail = "leagues_state_ecfeventdetail"
    _state_importecfdata = "leagues_state_importecfdata"
    _state_importfeedback = "leagues_state_importfeedback"
    _state_importfeedbackmonthly = "leagues_state_importfeedback_monthly"
    _state_joineventplayers = "leagues_state_joineventplayers"
    _state_clubsdownload = "leagues_state_clubsdownload"
    _state_playersdownload = "leagues_state_playersdownload"

    def __init__(self, master=None, cnf=dict(), **kargs):
        """Extend and define the results database results frame."""
        super(Leagues, self).__init__(master=master, cnf=cnf, **kargs)

        self._show_master_list_grading_codes = True

        self.define_tab(
            self._tab_control,
            text="Administration",
            tooltip="Open and close databases and import data.",
            underline=0,
            tabclass=lambda **k: control.Control(**k),
            create_actions=(control.Control._btn_opendatabase,),
            destroy_actions=(control.Control._btn_closedatabase,),
        )
        self.define_tab(
            self._tab_events,
            text="Events",
            tooltip=" ".join(
                (
                    "Export event data and initiate preparation of results",
                    "for submission to ECF",
                )
            ),
            underline=0,
            tabclass=lambda **k: events.Events(gridhorizontal=False, **k),
            destroy_actions=(control.Control._btn_closedatabase,),
        )
        self.define_tab(
            self._tab_newplayers,
            text="NewPlayers",
            tooltip="Identify new players and merge with existing players.",
            underline=0,
            tabclass=lambda **k: newplayers.NewPlayers(
                gridhorizontal=False, **k
            ),
            destroy_actions=(control.Control._btn_closedatabase,),
        )
        self.define_tab(
            self._tab_players,
            text="Players",
            tooltip="Merge or separate existing players.",
            underline=0,
            tabclass=lambda **k: players.Players(gridhorizontal=False, **k),
            destroy_actions=(control.Control._btn_closedatabase,),
        )
        self.define_tab(
            self._tab_ecfgradingcodes,
            text="Grading Codes",
            tooltip="Associate player with ECF grading code.",
            underline=0,
            tabclass=lambda **k: ecfgradingcodes.ECFGradingCodes(
                gridhorizontal=False, **k
            ),
            destroy_actions=(control.Control._btn_closedatabase,),
        )
        self.define_tab(
            self._tab_ecfclubcodes,
            text="Club Codes",
            tooltip="Associate player with ECF club code.",
            underline=0,
            tabclass=lambda **k: ecfclubcodes.ECFClubCodes(
                gridhorizontal=False, **k
            ),
            destroy_actions=(control.Control._btn_closedatabase,),
        )
        self.define_tab(
            self._tab_ecfevents,
            text="ECF Events",
            tooltip="Select an event to submit to ECF.",
            underline=5,
            tabclass=lambda **k: ecfevents.ECFEvents(
                gridhorizontal=False, **k
            ),
            destroy_actions=(control.Control._btn_closedatabase,),
        )
        self.define_tab(
            self._tab_ecfeventdetail,
            text="ECF Event Detail",
            tooltip="Update details of event for submission to ECF.",
            tabclass=lambda **k: newevent.NewEvent(**k),
            destroy_actions=(
                newevent.NewEvent._btn_cancel,
                control.Control._btn_closedatabase,
            ),
        )
        self.define_tab(
            self._tab_ecfplayers,
            text="Player ECF Detail",
            tooltip="Grading codes and club codes allocated to players.",
            underline=3,
            tabclass=lambda **k: ecfplayers.ECFPlayers(
                gridhorizontal=False, **k
            ),
            destroy_actions=(control.Control._btn_closedatabase,),
        )
        self.define_tab(
            self._tab_importecfdata,
            text="Import ECF Reference Data",
            tooltip="Import data from ECF Master and Update zipped files.",
            underline=-1,
            tabclass=lambda **k: importecfdata.ImportECFData(**k),
            destroy_actions=(
                importecfdata.ImportECFData._btn_closeecfimport,
                control.Control._btn_closedatabase,
            ),
        )
        self.define_tab(
            self._tab_importfeedback,
            text="Feedback",
            tooltip="Import data from ECF feedback text files.",
            underline=-1,
            tabclass=lambda **k: feedback.Feedback(**k),
            destroy_actions=(
                feedback.Feedback._btn_closefeedback,
                control.Control._btn_closedatabase,
            ),
        )
        self.define_tab(
            self._tab_importfeedbackmonthly,
            text="Feedback Monthly",
            tooltip="Import data from ECF feedback text files.",
            underline=-1,
            tabclass=lambda **k: feedback_monthly.FeedbackMonthly(**k),
            destroy_actions=(
                feedback_monthly.FeedbackMonthly._btn_closefeedbackmonthly,
                control.Control._btn_closedatabase,
            ),
        )
        self.define_tab(
            self._tab_joineventplayers,
            text="Join Event Players",
            tooltip="Join an event's players with same-named players.",
            underline=-1,
            tabclass=lambda **k: joineventplayers.JoinEventPlayers(**k),
            destroy_actions=(
                joineventplayers.JoinEventPlayers._btn_cancel,
                control.Control._btn_closedatabase,
            ),
        )
        self.define_tab(
            self._tab_clubsdownload,
            text="Active Clubs Download",
            tooltip="Import data from ECF feedback text files.",
            underline=-1,
            tabclass=lambda **k: activeclubs.ActiveClubs(**k),
            destroy_actions=(activeclubs.ActiveClubs._btn_closeactiveclubs,),
        )
        self.define_tab(
            self._tab_playersdownload,
            text="Players Download",
            tooltip="Import data from ECF feedback text files.",
            underline=-1,
            tabclass=lambda **k: ratedplayers.RatedPlayers(**k),
            destroy_actions=(
                ratedplayers.RatedPlayers._btn_closeratedplayers,
            ),
        )

        self.define_state_transitions(
            tab_state={
                self._state_dbopen: (
                    self._tab_control,
                    self._tab_events,
                    self._tab_newplayers,
                    self._tab_players,
                    self._tab_ecfgradingcodes,
                    self._tab_ecfclubcodes,
                    self._tab_ecfplayers,
                    self._tab_ecfevents,
                ),
                self._state_ecfeventdetail: (self._tab_ecfeventdetail,),
                self._state_importecfdata: (self._tab_importecfdata,),
                self._state_importfeedback: (self._tab_importfeedback,),
                self._state_importfeedbackmonthly: (
                    self._tab_importfeedbackmonthly,
                ),
                self._state_joineventplayers: (self._tab_joineventplayers,),
                self._state_clubsdownload: (self._tab_clubsdownload,),
                self._state_playersdownload: (self._tab_playersdownload,),
            },
            switch_state={
                (
                    self._state_dbopen,
                    ecfevents.ECFEvents._btn_ecfeventdetail,
                ): [self._state_ecfeventdetail, self._tab_ecfeventdetail],
                (self._state_ecfeventdetail, newevent.NewEvent._btn_ok): [
                    self._state_dbopen,
                    self._tab_ecfevents,
                ],
                (self._state_ecfeventdetail, newevent.NewEvent._btn_cancel): [
                    self._state_dbopen,
                    self._tab_ecfevents,
                ],
                (
                    self._state_dbopen,
                    control.Control._btn_copyecfmasterplayer,
                ): [self._state_importecfdata, self._tab_importecfdata],
                (self._state_dbopen, control.Control._btn_copyecfmasterclub): [
                    self._state_importecfdata,
                    self._tab_importecfdata,
                ],
                (
                    self._state_importecfdata,
                    importecfdata.ImportECFData._btn_closeecfimport,
                ): [self._state_dbopen, self._tab_control],
                (
                    self._state_dbopen,
                    control.Control._btn_ecfresultsfeedback,
                ): [self._state_importfeedback, self._tab_importfeedback],
                (
                    self._state_importfeedback,
                    feedback.Feedback._btn_closefeedback,
                ): [self._state_dbopen, self._tab_control],
                (
                    self._state_dbopen,
                    control.Control._btn_ecfresultsfeedbackmonthly,
                ): [
                    self._state_importfeedbackmonthly,
                    self._tab_importfeedbackmonthly,
                ],
                (
                    self._state_importfeedbackmonthly,
                    feedback_monthly.FeedbackMonthly._btn_closefeedbackmonthly,
                ): [self._state_dbopen, self._tab_control],
                (
                    self._state_dbopen,
                    events.Events._btn_join_event_new_players,
                ): [self._state_joineventplayers, self._tab_joineventplayers],
                (
                    self._state_joineventplayers,
                    joineventplayers.JoinEventPlayers._btn_cancel,
                ): [self._state_dbopen, self._tab_events],
                (self._state_dbopen, control.Control._btn_clubsdownload): [
                    self._state_clubsdownload,
                    self._tab_clubsdownload,
                ],
                (
                    self._state_clubsdownload,
                    activeclubs.ActiveClubs._btn_closeactiveclubs,
                ): [self._state_dbopen, self._tab_control],
                (self._state_dbopen, control.Control._btn_playersdownload): [
                    self._state_playersdownload,
                    self._tab_playersdownload,
                ],
                (
                    self._state_playersdownload,
                    ratedplayers.RatedPlayers._btn_closeratedplayers,
                ): [self._state_dbopen, self._tab_control],
                (
                    self._state_ecfeventdetail,
                    control.Control._btn_closedatabase,
                ): [self._state_dbclosed, None],
                (
                    self._state_importecfdata,
                    control.Control._btn_closedatabase,
                ): [self._state_dbclosed, None],
                (
                    self._state_importfeedback,
                    control.Control._btn_closedatabase,
                ): [self._state_dbclosed, None],
                (
                    self._state_importfeedbackmonthly,
                    control.Control._btn_closedatabase,
                ): [self._state_dbclosed, None],
                (
                    self._state_joineventplayers,
                    control.Control._btn_closedatabase,
                ): [self._state_dbclosed, None],
            },
        )

    def get_ecf_event_detail_context(self):
        """Return the ECF event page."""
        return self.get_tab_data(self._tab_ecfevents)

    def set_ecfdataimport_module(self, enginename):
        """Import the ECF reference data import module."""
        self._ecfdataimport_module = importlib.import_module(
            ECF_DATA_IMPORT_MODULE[enginename], "chessresults.gui"
        )

    def set_knownnamesdatasource_module(self, enginename):
        """Import the known names datasource module."""
        self._knownnamesdatasource_module = importlib.import_module(
            KNOWN_NAME_DATASOURCE_MODULE[enginename], "chessresults.gui"
        )

    def set_ecf_url_defaults(self):
        """Set URL defaults for ECF website.

        Create a file, if it does not exist, with URL defaults as sibling of
        results folder.

        """
        if self.database_folder is None:
            return
        default = os.path.join(
            self.database_folder,
            os.path.basename(self.database_folder).join(
                (constants.URL_NAMES, ".txt")
            ),
        )
        if not os.path.exists(default):
            urls = "\n".join([" ".join(u) for u in constants.DEFAULT_URLS])
            of = open(default, "w")
            try:
                of.write(urls)
                of.write("\n")
            except Exception as exc:
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            "Unable to write URL defaults to ",
                            default,
                        )
                    ),
                    title="Open Database",
                )
                return
            finally:
                of.close()

    def _add_ecf_url_item(self, menu):
        """Override to provide edit ECF URL defaults."""
        menu.add_command(
            label="ECF URLs",
            underline=4,
            command=self.try_command(self.edit_ecf_url_defaults, menu),
        )
        menu.add_separator()

    def edit_ecf_url_defaults(self):
        """Edit URL defaults for ECF website if the defaults file exists."""
        if self.database_folder is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="Database must be open to edit ECF URL defaults",
                title="Edit ECF URL Defaults",
            )
            return
        default = os.path.join(
            self.database_folder,
            os.path.basename(self.database_folder).join(
                (constants.URL_NAMES, ".txt")
            ),
        )
        if not os.path.exists(default):
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        default,
                        "\n\ndoes not exist.  Try closing and opening ",
                        "the database to cause it to be created with default ",
                        "values.",
                    )
                ),
                title="Edit ECF URL Defaults",
            )
            return
        if not os.path.isfile(default):
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        default,
                        "\n\nis not a file: it cannot be the defaults.",
                    )
                ),
                title="Edit ECF URL Defaults",
            )
            return
        of = open(default)
        try:
            config_text = of.read()
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    ("Unable to read from\n\n", default, "\n\n", str(exc))
                ),
                title=dialog_title,
            )
            return
        finally:
            of.close()

        # An unresolved bug is worked around by this 'try ... except' block.
        # The initial exception can be exposed by commenting the 'return'
        # statement near the end of the 'except KeyError as exc:' block.
        try:
            edited_text = ConfigureDialog(
                self.get_widget(),
                configuration=config_text,
                dialog_title="Edit ECF URL Defaults",
            ).config_text
        except KeyError as exc:
            if str(exc) == "'#!menu'":
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    message="".join(
                        (
                            "The sufficient and necessary actions to reach ",
                            "this point are:\n\n",
                            "Close a database\n",
                            "Use the 'Results | ECF URLs' menu option.\n\n",
                            "The cause is probably an unresolved bug.\n\n",
                            "The best action now is close and restart the ",
                            "ChessResults application; but there may be ",
                            "nothing wrong with manually destroying the bare ",
                            "widget created to edit the ECF URLs.",
                        )
                    ),
                    title="Edit ECF URL Defaults",
                )
                return
            raise

        if edited_text is None:
            return
        of = open(default, "w")
        try:
            of.write(edited_text)
        except Exception as exc:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="".join(
                    (
                        "Unable to write to\n\n",
                        default,
                        "\n\n",
                        str(exc),
                    )
                ),
                title=dialog_title,
            )
            return
        finally:
            of.close()

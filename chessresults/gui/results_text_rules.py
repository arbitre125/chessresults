# results_text_rules.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""User Interface to display and edit rules for extracting results from text.

"""

import os
import tkinter
import tkinter.messagebox
import tkinter.filedialog

from solentware_misc.gui.exceptionhandler import ExceptionHandler
from solentware_misc.gui import textreadonly

from . import help
from .. import APPLICATION_NAME
from .configuredialog import ConfigureDialog

startup_minimum_width = 340
startup_minimum_height = 400


class ResultsTextRules(ExceptionHandler):

    """Define and use a results from text rules configuration file."""

    def __init__(self, folder=None, **kargs):
        """Create the database and GUI objects.

        **kargs - passed to tkinter Toplevel widget

        """
        self.root = tkinter.Toplevel(**kargs)
        try:
            appname = " ".join((APPLICATION_NAME, "(Rules)"))
            if folder is not None:
                self.root.wm_title(" - ".join((appname, folder)))
            else:
                self.root.wm_title(appname)
            self.root.wm_minsize(
                width=startup_minimum_width, height=startup_minimum_height
            )

            self._configuration = None
            self._configuration_edited = False

            menubar = tkinter.Menu(self.root)

            menufile = tkinter.Menu(menubar, name="file", tearoff=False)
            menubar.add_cascade(label="File", menu=menufile, underline=0)
            menufile.add_command(
                label="Open",
                underline=0,
                command=self.try_command(self.file_open, menufile),
            )
            menufile.add_command(
                label="New",
                underline=0,
                command=self.try_command(self.file_new, menufile),
            )
            menufile.add_separator()
            # menufile.add_command(
            #    label='Save',
            #    underline=0,
            #    command=self.try_command(self.file_save, menufile))
            menufile.add_command(
                label="Save Copy As...",
                underline=7,
                command=self.try_command(self.file_save_copy_as, menufile),
            )
            menufile.add_separator()
            menufile.add_command(
                label="Close",
                underline=0,
                command=self.try_command(self.file_close, menufile),
            )
            menufile.add_separator()
            menufile.add_command(
                label="Quit",
                underline=0,
                command=self.try_command(self.file_quit, menufile),
            )

            menuactions = tkinter.Menu(menubar, name="actions", tearoff=False)
            menubar.add_cascade(label="Actions", menu=menuactions, underline=0)
            menuactions.add_separator()
            menuactions.add_command(
                label="Option editor",
                underline=0,
                command=self.try_command(
                    self.configure_result_text_rules, menuactions
                ),
            )

            menuhelp = tkinter.Menu(menubar, name="help", tearoff=False)
            menubar.add_cascade(label="Help", menu=menuhelp, underline=0)
            menuhelp.add_command(
                label="Guide",
                underline=0,
                command=self.try_command(self.help_guide, menuhelp),
            )
            menuhelp.add_command(
                label="Notes",
                underline=0,
                command=self.try_command(self.help_notes, menuhelp),
            )
            menuhelp.add_command(
                label="About",
                underline=0,
                command=self.try_command(self.help_about, menuhelp),
            )

            self.root.configure(menu=menubar)

            self.statusbar = Statusbar(self.root)
            frame = tkinter.PanedWindow(
                self.root,
                background="cyan2",
                opaqueresize=tkinter.FALSE,
                orient=tkinter.HORIZONTAL,
            )
            frame.pack(fill=tkinter.BOTH, expand=tkinter.TRUE)

            toppane = tkinter.PanedWindow(
                master=frame,
                opaqueresize=tkinter.FALSE,
                orient=tkinter.HORIZONTAL,
            )
            originalpane = tkinter.PanedWindow(
                master=toppane,
                opaqueresize=tkinter.FALSE,
                orient=tkinter.VERTICAL,
            )
            self.configctrl = textreadonly.make_text_readonly(
                master=originalpane, width=80
            )
            originalpane.add(self.configctrl)
            toppane.add(originalpane)
            toppane.pack(side=tkinter.TOP, expand=True, fill=tkinter.BOTH)
            self._folder = folder

        except:
            self.root.destroy()
            del self.root

    def __del__(self):
        """ """
        if self._configuration:
            self._configuration = None

    def help_about(self):
        """Display information about text result rules."""
        help.help_about(self.root)

    def help_guide(self):
        """Display brief User Guide for text result rules."""
        help.help_guide(self.root)

    def help_notes(self):
        """Display technical notes about text result rules."""
        help.help_notes(self.root)

    def get_toplevel(self):
        """Return the toplevel widget."""
        return self.root

    def file_new(self):
        """Create and open a new text result rules configuration file."""
        if self._configuration is not None:
            tkinter.messagebox.showinfo(
                parent=self.get_toplevel(),
                title="New Text Result Rules",
                message="Close the current text result rules first.",
            )
            return
        config_file = tkinter.filedialog.asksaveasfilename(
            parent=self.get_toplevel(),
            title="New Text Result Rules",
            defaultextension=".conf",
            filetypes=(("Text Result Rules", "*.conf"),),
            initialfile="textrules.conf",
            initialdir="~",
        )
        if not config_file:
            return
        self.configctrl.delete("1.0", tkinter.END)
        self.configctrl.insert(
            tkinter.END,
            "".join(
                ("# ", os.path.basename(config_file), " text result rules")
            )
            + os.linesep,
        )
        fn = open(config_file, "w", encoding="utf8")
        try:
            fn.write(
                self.configctrl.get("1.0", " ".join((tkinter.END, "-1 chars")))
            )
        finally:
            fn.close()
        self._configuration = config_file
        self._folder = os.path.dirname(config_file)

    def file_open(self):
        """Open an existing text result rules file."""
        if self._configuration is not None:
            tkinter.messagebox.showinfo(
                parent=self.get_toplevel(),
                title="Text Result Rules",
                message="Close the current text result rules first.",
            )
            return
        config_file = tkinter.filedialog.askopenfilename(
            parent=self.get_toplevel(),
            title="Open Text Result Rules",
            defaultextension=".conf",
            filetypes=(("Text Result Rules", "textrules*.conf"),),
            initialfile="",
            initialdir="~",
        )
        if not config_file:
            return
        fn = open(config_file, "r", encoding="utf8")
        try:
            self.configctrl.delete("1.0", tkinter.END)
            self.configctrl.insert(tkinter.END, fn.read())
        finally:
            fn.close()
        self._configuration = config_file
        self._folder = os.path.dirname(config_file)

    def file_close(self):
        """Close the open text result rules file."""
        if self._configuration is None:
            tkinter.messagebox.showinfo(
                parent=self.get_toplevel(),
                title="Text Result Rules",
                message="Cannot close.\n\nThere is no database open.",
            )
            return
        closemsg = "Confirm Close.\n\nChanges not already saved will be lost."
        dlg = tkinter.messagebox.askquestion(
            parent=self.get_toplevel(), title="Close", message=closemsg
        )
        if dlg == tkinter.messagebox.YES:
            self.configctrl.delete("1.0", tkinter.END)
            self.statusbar.set_status_text()
            self._configuration = None
            self._configuration_edited = False

    def file_quit(self):
        """Quit the text result rules application."""
        quitmsg = "Confirm Quit.\n\nChanges not already saved will be lost."
        dlg = tkinter.messagebox.askquestion(
            parent=self.get_toplevel(), title="Quit", message=quitmsg
        )
        if dlg == tkinter.messagebox.YES:
            self.root.destroy()

    # Probably not going to be used because 'Actions | Option editor' does it.
    def file_save(self):
        """Save the open text result rules file."""
        if self._configuration is None:
            tkinter.messagebox.showinfo(
                parent=self.get_toplevel(),
                title="Save",
                message="Cannot save.\n\nText result rules file not open.",
            )
            return
        if (
            tkinter.messagebox.askquestion(
                parent=self.get_toplevel(),
                title="Save",
                message="".join(
                    (
                        "Confirm save text result rules to\n",
                        self._configuration,
                    )
                ),
            )
            != tkinter.messagebox.YES
        ):
            return
        fn = open(self._configuration, "w")
        try:
            fn.write(
                self.configctrl.get("1.0", " ".join((tkinter.END, "-1 chars")))
            )
            self._configuration_edited = False
        finally:
            fn.close()
        return True

    def file_save_copy_as(self):
        """Save copy of open text result rules and keep current open."""
        if self._configuration is None:
            tkinter.messagebox.showinfo(
                parent=self.get_toplevel(),
                title="Save Copy As",
                message="Cannot save.\n\nText result rules file not open.",
            )
            return
        config_file = tkinter.filedialog.asksaveasfilename(
            parent=self.get_toplevel(),
            title="Save Text Result Rules As",
            defaultextension=".conf",
            filetypes=(("Text Result Rules", "textrules*.conf"),),
            initialfile=os.path.basename(self._configuration),
            initialdir=os.path.dirname(self._configuration),
        )
        if not config_file:
            return
        if config_file == self._configuration:
            tkinter.messagebox.showinfo(
                parent=self.get_toplevel(),
                title="Save Copy As",
                message="".join(
                    (
                        'Cannot use "Save Copy As" to overwite the open ',
                        "text result rules file.",
                    )
                ),
            )
            return
        fn = open(config_file, "w")
        try:
            fn.write(
                self.configctrl.get("1.0", " ".join((tkinter.END, "-1 chars")))
            )
        finally:
            fn.close()

    def configure_result_text_rules(self):
        """Set rules for extracting results from text from emails."""
        if self._configuration is None:
            tkinter.messagebox.showinfo(
                parent=self.get_toplevel(),
                title="Configure Text Result Rules",
                message="Open a text result rules file.",
            )
            return
        config_text = ConfigureDialog(
            self.root,
            self.configctrl.get("1.0", " ".join((tkinter.END, "-1 chars"))),
        ).config_text
        if config_text is None:
            return
        self._configuration_edited = True
        self.configctrl.delete("1.0", tkinter.END)
        self.configctrl.insert(tkinter.END, config_text)
        fn = open(self._configuration, "w", encoding="utf-8")
        try:
            fn.write(config_text)
            self.statusbar.set_status_text()
            self._configuration_edited = False
        finally:
            fn.close()


class Statusbar(object):

    """Status bar for Text Result Rules Toplevel."""

    def __init__(self, root):
        """Create status bar widget."""
        self.status = tkinter.Text(
            root,
            height=0,
            width=0,
            background=root.cget("background"),
            relief=tkinter.FLAT,
            state=tkinter.DISABLED,
            wrap=tkinter.NONE,
        )
        self.status.pack(side=tkinter.BOTTOM, fill=tkinter.X)

    def get_status_text(self):
        """Return text displayed in status bar."""
        return self.status.cget("text")

    def set_status_text(self, text=""):
        """Display text in status bar."""
        self.status.configure(state=tkinter.NORMAL)
        self.status.delete("1.0", tkinter.END)
        self.status.insert(tkinter.END, text)
        self.status.configure(state=tkinter.DISABLED)

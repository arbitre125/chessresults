# configuredialog_hack.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""A workaround for a problem encountered in ConfigureDialog class.

"""

import tkinter

from solentware_misc.gui.configuredialog import ConfigureDialog


class ConfigureDialogHack(ConfigureDialog):

    """Configuration file text editor in a dialogue.

    Update methods are defined but do not change database.  Subclasses must
    override as needed.

    """

    def __init__(
        self,
        parent,
        configuration="",
        dialog_title="Text editor dialogue",
        dialog_cancel_hint="Quit without applying changes",
        dialog_update_hint="Apply changes",
        cnf=dict(),
        **kargs
    ):
        """Create a configuration file text editor dialogue."""

        # Skip to ConfigureDialog superclass' __init__() method.
        super(ConfigureDialog, self).__init__()

        self._config_text = None
        self.dialog = tkinter.Toplevel(parent)

        # Removed compared with solentware_misc version.
        # self.restore_focus = self.dialog.focus_get()

        self.dialog.wm_title(dialog_title)
        self.configuration = tkinter.Text(master=self.dialog)
        self.configuration.insert(tkinter.END, configuration)
        buttons_frame = tkinter.Frame(master=self.dialog)
        buttons_frame.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        buttonrow = buttons_frame.pack_info()["side"] in ("top", "bottom")
        for i, b in enumerate(
            (
                ("Cancel", dialog_cancel_hint, True, 0, self.on_cancel),
                ("Update", dialog_update_hint, True, 0, self.on_update),
            )
        ):
            button = tkinter.Button(
                master=buttons_frame,
                text=b[0],
                underline=b[3],
                command=self.try_command(b[4], buttons_frame),
            )
            if buttonrow:
                buttons_frame.grid_columnconfigure(i * 2, weight=1)
                button.grid_configure(column=i * 2 + 1, row=0)
            else:
                buttons_frame.grid_rowconfigure(i * 2, weight=1)
                button.grid_configure(row=i * 2 + 1, column=0)
        if buttonrow:
            buttons_frame.grid_columnconfigure(len(b * 2), weight=1)
        else:
            buttons_frame.grid_rowconfigure(len(b * 2), weight=1)

        self.configuration.pack(
            side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.TRUE
        )

        self.dialog.wait_visibility()
        self.dialog.grab_set()
        self.dialog.wait_window()

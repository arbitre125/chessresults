# reports.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Customise solentware_misc.gui.reports AppSysReport class.
"""

import tkinter.filedialog
import os

from solentware_misc.gui.reports import AppSysReport

from ..core import (
    constants,
    configuration,
)


# The need for this class demonstrates the show_report() method in
# solentware_misc.gui.reports is useless.
class ChessResultsReport(AppSysReport):
    """Provide initialdir argument for the Save dialogue.

    Subclasses must define a suitable attribute named configuration_item.

    AppSysReport provides the other instance attributes.

    """

    def on_save(self, event=None):
        """Override to support initialdir argument."""
        filepath = tkinter.filedialog.asksaveasfilename(
            parent=self._toplevel,
            title=self._save_title,
            initialdir=configuration.get_configuration_value(
                self.configuration_item
            ),
            defaultextension=".txt",
        )
        if not filepath:
            return
        configuration.set_configuration_value(
            self.configuration_item,
            configuration.convert_home_directory_to_tilde(
                os.path.dirname(filepath)
            ),
        )
        outfile = open(filepath, mode="wb")
        try:
            outfile.write(
                self.textreport.get("1.0", tkinter.END).encode("utf8")
            )
        finally:
            outfile.close()

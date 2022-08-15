# resultsroot.py
# Copyright 2010 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database application.
"""

from solentware_misc.gui.exceptionhandler import ExceptionHandler

import chessvalidate.gui.resultsroot

from .. import APPLICATION_NAME
from . import help_
from . import configure
from . import selectemail

# Cannot set by set_application_name() because chessvalidate.gui.resultsroot
# has already done a call to this method.
# ExceptionHandler.set_application_name(APPLICATION_NAME)
ExceptionHandler._application_name = APPLICATION_NAME


class Results(chessvalidate.gui.resultsroot.Results):

    """Results application."""

    def make_tools_menu(self, menubar):
        """Extend.  Return Tools menu with URL entry."""
        menu3 = super().make_tools_menu(menubar)
        self.app_module._add_ecf_url_item(menu3)
        return menu3

    def make_help_menu(self, menubar):
        """Extend.  Return Help menu with database entries."""
        menu4 = super().make_help_menu(menubar)
        menu4.insert_command(
            6,  # Before Notes.
            label="File size",
            underline=0,
            command=self.try_command(self.help_file_size, menu4),
        )
        return menu4

    def help_about(self):
        """Display information about Results application."""
        help_.help_about(self.root)

    def help_file_size(self):
        """Display brief instructions for file size dialogue."""
        help_.help_file_size(self.root)

    def help_guide(self):
        """Display brief User Guide for Results application."""
        help_.help_guide(self.root)

    def help_keyboard(self):
        """Display list of keyboard actions for Results application."""
        help_.help_keyboard(self.root)

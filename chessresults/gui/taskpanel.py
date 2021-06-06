# taskpanel.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database background task panel class.

Use this panel for background tasks which inhibit database actions yet allow
interaction with the task log when no obvious display is available.

"""

import tkinter

from solentware_misc.gui import logpanel


class TaskPanel(logpanel.TextAndLogPanel):

    """The background task panel for a Results database."""

    _btn_closebackgroundtask = "taskpanel_close"

    def __init__(self, parent=None, starttaskmsg=None, cnf=dict(), **kargs):
        """Extend and define the results ECF reference data import tab."""
        super(TaskPanel, self).__init__(parent=parent, cnf=cnf, **kargs)

        if starttaskmsg is not None:
            self.tasklog.append_text(starttaskmsg)
            self.tasklog.append_text_only("")

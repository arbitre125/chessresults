# control_lite.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Control panel class.

Open and close databases and import and export data functions are available
on this panel.

"""

from .. import control_database


class Control(control_database.Control):

    """The Control panel for a Results database."""

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database control panel."""
        super(Control, self).__init__(parent=parent, cnf=cnf, **kargs)

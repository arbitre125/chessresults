# events_ogd.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database Event panel class.
"""

from . import events_lite


class Events(events_lite.Events):

    """The Events panel for a Results database."""

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database events panel."""
        super(Events, self).__init__(parent=parent, cnf=cnf, **kargs)

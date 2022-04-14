# configure.py
# Copyright 2014 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Describe the emails and attachments containing event results."""
from chessvalidate.gui import configure

from ..core import configuration


class Configure(configure.Configure):
    """Define and use an event result's extraction configuration file."""

    _READ_FILE_TITLE = "Results Extraction Rules"

    def file_new(self, conf=None):
        """Set configuration then delegate."""
        if conf is None:
            conf = configuration
        super().file_new(conf=conf)

    def file_open(self, conf=None):
        """Set configuration then delegate."""
        if conf is None:
            conf = configuration
        super().file_open(conf=conf)

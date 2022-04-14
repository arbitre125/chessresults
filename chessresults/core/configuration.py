# configuration.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Access and update names of last used database and configuration files.

The initial values are taken from file named in self._RESULTS_CONF in the
user's home directory if the file exists.

"""

from chessvalidate.core import configuration

from ..core import constants


class Configuration(configuration.Configuration):
    """Identify configuration and recent files and delegate to superclass."""

    _RESULTS_CONF = ".chessresults.conf"
    _DEFAULT_RECENTS = (
        (constants.RECENT_DATABASE, "~"),
        (constants.RECENT_EMAIL_SELECTION, "~"),
        (constants.RECENT_EMAIL_EXTRACTION, "~"),
        (constants.RECENT_DOCUMENT, "~"),
        (constants.RECENT_SUBMISSION, "~"),
        (constants.RECENT_SOURCE_SUBMISSION, "~"),
        (constants.RECENT_FEEDBACK, "~"),
        (constants.RECENT_FEEDBACK_EMAIL, "~"),
        (constants.RECENT_MASTERFILE, "~"),
        (constants.RECENT_IMPORT_EVENTS, "~"),
        (constants.RECENT_EXPORT_EVENTS, "~"),
        (constants.RECENT_PERFORMANCES, "~"),
        (constants.RECENT_PREDICTIONS, "~"),
        (constants.RECENT_POPULATION, "~"),
        (constants.RECENT_GAME_SUMMARY, "~"),
        (constants.RECENT_EVENT_SUMMARY, "~"),
        (constants.RECENT_GRADING_LIST, "~"),
        (constants.RECENT_RATING_LIST, "~"),
    )

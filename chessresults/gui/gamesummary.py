# gamesummary.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Display game summary for selected events.
"""

import tkinter
import os

from solentware_misc.gui.exceptionhandler import ExceptionHandler
from solentware_misc.core.utilities import AppSysPersonName

from chessvalidate.core.gameresults import (
    displayresult as DISPLAYRESULT,
)

from . import reports
from ..core import resultsrecord
from ..core import filespec
from ..core import constants

INVERT_RESULT = {
    constants.HWIN: constants.AWIN,
    constants.DRAW: constants.DRAW,
    constants.AWIN: constants.HWIN,
}


class _GameSummaryReport(reports.ChessResultsReport):
    """Provide initialdir argument for the Save dialogue."""

    configuration_item = constants.RECENT_GAME_SUMMARY


class GameSummary(ExceptionHandler):
    """Game summary report for an event."""

    def __init__(self, parent, database, event):
        """Create widget to display game summary for event."""
        super(GameSummary, self).__init__()
        self.event = event
        rv = resultsrecord.get_event_from_record_value(
            database.get_primary_record(filespec.EVENT_FILE_DEF, event[-1])
        ).value

        self.summary = _GameSummaryReport(
            parent,
            "".join(
                (
                    "Game Summary for ",
                    rv.name,
                    " on ",
                    rv.startdate,
                )
            ),
            save=(
                "Save",
                "Save Game Summary",
                True,
            ),
            close=(
                "Close",
                "Close Game Summary",
                True,
            ),
            wrap=tkinter.WORD,
            tabstyle="tabular",
        )
        self.summary.append(
            "".join(
                (
                    "Game Summary for ",
                    rv.name,
                    " from ",
                    rv.startdate,
                    " to ",
                    rv.enddate,
                )
            )
        )
        eventgames = resultsrecord.get_games_for_event(
            database, resultsrecord.get_event(database, event[-1])
        )
        self.summary.append(
            "".join(
                (
                    "\n\n",
                    str(len(eventgames)),
                    " games for grading.",
                )
            )
        )
        eventaliases = resultsrecord.get_aliases_for_games(
            database, eventgames
        )
        eventplayers = resultsrecord.get_persons(database, eventaliases)
        self.summary.append(
            "".join(
                (
                    "\n\n",
                    str(
                        len(set([p.key.recno for p in eventplayers.values()]))
                    ),
                    " players with games for grading.",
                )
            )
        )
        games = []
        incomplete = False
        for g in eventgames:
            for ak in (g.value.homeplayer, g.value.awayplayer):
                if ak in eventplayers:
                    games.append(
                        (
                            AppSysPersonName(eventaliases[ak].value.name).name,
                            g.value.date,
                            eventplayers[ak].key.recno,
                            g,
                        )
                    )
                else:
                    incomplete = True
        if incomplete:
            self.summary.append(
                "".join(
                    (
                        "\n\nSome players are still on the NewPlayers tab ",
                        "waiting to be merged.  Games are not listed under the ",
                        "names of these players, but may be listed under the ",
                        "names of their opponents.\n",
                    )
                )
            )
        self.summary.append("\n\nGames listed by each player and date.\n")
        current_name = None
        for g in sorted(games):
            if current_name != g[-2]:
                self.summary.append("\n")
                current_name = g[-2]
            gv = g[-1].value
            if gv.homeplayerwhite is False:
                self.summary.append(
                    "".join(
                        (
                            eventaliases[gv.awayplayer].value.name,
                            "\t\t\t",
                            DISPLAYRESULT[
                                INVERT_RESULT.get(gv.result, gv.result)
                            ],
                            "\t",
                            eventaliases[gv.homeplayer].value.name,
                            "\t\t\t",
                            gv.date,
                            "\n",
                        )
                    )
                )
            else:
                self.summary.append(
                    "".join(
                        (
                            eventaliases[gv.homeplayer].value.name,
                            "\t\t\t",
                            DISPLAYRESULT[gv.result],
                            "\t",
                            eventaliases[gv.awayplayer].value.name,
                            "\t\t\t",
                            gv.date,
                            "\n",
                        )
                    )
                )

# takeoncollation.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Class to reconcile event schedule (eg. fixture list) with reported results.
"""
from chessvalidate.core import gameobjects

from . import importcollation, constants
from .importresults import get_player_identifier_from_game


class TakeonCollation(importcollation.ImportCollation):

    """Results extracted from a generic event report."""

    def __init__(self, reports, fixtures, importdata):
        """Extend, allow for noting merges."""

        self.merges = dict()
        super().__init__(importdata)

        self.reports = reports
        self.schedule = fixtures
        self.report_order = []  # merge report orders for schedule and results

        self.error.extend(reports.error)

    def collate_game_players(self, game):
        """Return a list of gameobjects.Player instances for a game.

        Differs from superclass method in two ways:
        Add the Player instances into the self.merge dictionary.
        game has a different structure.

        """
        pl = []
        for player, pin, affiliation in (
            (
                constants._homeplayer,
                constants._homepin,
                constants._homeaffiliation,
            ),
            (
                constants._awayplayer,
                constants._awaypin,
                constants._awayaffiliation,
            ),
        ):
            pk = get_player_identifier_from_game(game, player, pin)
            p = self.players.get(pk)
            if p is None:
                p = gameobjects.Player(
                    name=game[player],
                    event=game[constants._event],
                    startdate=game[constants._startdate],
                    enddate=game[constants._enddate],
                    section=game[constants._section],
                    pin=game[pin],
                )
                if constants._board in game:
                    p.affiliation = game[affiliation]
                self.players[pk] = p
            pl.append(p)
            merge = self.merges.setdefault(game[pin], dict())
            merge[pk] = merge.setdefault(pk, 0) + 1
        return pl

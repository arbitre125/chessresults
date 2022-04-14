# importcollation.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Collate results imported from another results database.
"""

from chessvalidate.core import gameobjects

from . import constants
from .importreports import get_player_identifier

homeplayercolour = {"yes": True, "no": False}


class ImportCollation(gameobjects.GameCollation):

    """Results extracted from an export file from a results database."""

    def __init__(self, importreport):
        """Extend, collate results from a results database export file.

        importreport - an importreports.ImportReports instance

        """
        super().__init__()

        # Restore error attribute removed from GameCollation because main
        # subclass does not want it now.
        # round=game.get(constants._round) is ok, compared with SwissGame,
        # because ImportReports class sets the game value to a str if at all.
        self.error = []

        self.importreport = importreport
        for k, game in importreport.game.items():
            if (
                constants._hometeam not in game
                or constants._awayteam not in game
            ):
                sectionkey = game[constants._section]
                section = self.games.setdefault(
                    sectionkey,
                    gameobjects.Section(
                        competition=game[constants._section], games=[]
                    ),
                )
            else:
                sectionkey = (
                    game[constants._section],
                    (
                        game[constants._hometeam],
                        game[constants._awayteam],
                        " ".join(
                            (
                                game[constants._section],
                                game[constants._date],
                            )
                        ),
                    ),
                )
                section = self.games.setdefault(
                    sectionkey,
                    gameobjects.MatchReport(
                        competition=game[constants._section],
                        hometeam=game[constants._hometeam],
                        awayteam=game[constants._awayteam],
                        round=game.get(constants._round),
                        games=[],
                    ),
                )
            hp, ap = self.collate_game_players(game)
            hpw = homeplayercolour.get(game.get(constants._homeplayerwhite))
            if constants._round in game:
                if constants._board in game:
                    section.games.append(
                        gameobjects.SwissMatchGame(
                            round=game[constants._round],
                            board=game[constants._board],
                            result=game[constants._result],
                            date=game[constants._date],
                            homeplayerwhite=hpw,
                            homeplayer=hp,
                            awayplayer=ap,
                        )
                    )
                else:
                    section.games.append(
                        gameobjects.SwissGame(
                            round=game[constants._round],
                            result=game[constants._result],
                            date=game[constants._date],
                            homeplayerwhite=hpw,
                            homeplayer=hp,
                            awayplayer=ap,
                        )
                    )
            elif constants._board in game:
                section.games.append(
                    gameobjects.MatchGame(
                        board=game[constants._board],
                        result=game[constants._result],
                        date=game[constants._date],
                        homeplayerwhite=hpw,
                        homeplayer=hp,
                        awayplayer=ap,
                    )
                )
            else:
                section.games.append(
                    gameobjects.Game(
                        result=game[constants._result],
                        date=game[constants._date],
                        homeplayerwhite=hpw,
                        homeplayer=hp,
                        awayplayer=ap,
                    )
                )

    def collate_game_players(self, game):
        """Return list of gameobjects.Player for players in game."""
        pl = []
        for player, pin, affiliation, team, reportedcodes in (
            (
                constants._homename,
                constants._homepin,
                constants._homeaffiliation,
                constants._hometeam,
                constants._homereportedcodes,
            ),
            (
                constants._awayname,
                constants._awaypin,
                constants._awayaffiliation,
                constants._awayteam,
                constants._awayreportedcodes,
            ),
        ):
            pk = get_player_identifier(game, player, pin, affiliation)
            p = self.players.get(pk)
            if p is None:
                if game[team] is not None:
                    section = None
                else:
                    section = game[constants._section]
                attr = dict(
                    name=pk[0],
                    event=pk[1],
                    startdate=pk[2],
                    enddate=pk[3],
                    section=section,
                    pin=pk[5],
                    reported_codes=game[reportedcodes],
                )
                if game[team]:
                    p = gameobjects.Player(club=pk[4], **attr)
                else:
                    p = gameobjects.Player(**attr)
                if constants._board in game:
                    p.affiliation = game[affiliation]
                self.players[pk] = p
            pl.append(p)
        return pl

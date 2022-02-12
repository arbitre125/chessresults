# newplayers.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database NewPlayers panel class for ECF monthly rating.

Identify new players.  Declare the new player to be the same as one already
on database or to be new to this database.

This module did the job of newplayers_lite before version 5.1 of ChessResults.

This module now customises newplayers_lite for use with the ECF monthly
rating system.

"""
from . import newplayers_lite


class NewPlayers(newplayers_lite.NewPlayers):

    """New Players panel for Results database with ECF monthly rating.

    Customise user interface for use with ECF monthly rating system.

    """

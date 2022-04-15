# newplayers_lite.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database NewPlayers panel class.

Identify new players.  Declare the new player to be the same as one already
on database or to be new to this database.

This module was called newplayers before version 5.1 of ChessResults.

This module customises newplayers_database, starting with version 6.0 of
ChessResults, for use with the ECF monthly rating system.  Between these
versions it did the job of newplayers_database.

"""
from .. import newplayers_database


class NewPlayers(newplayers_database.NewPlayers):

    """New Players panel for Results database with Online Grading Database.

    Customise newplayers_database user interface for use with published
    grading list.

    """

# newplayers_ogd.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database NewPlayers panel class for Online Grading Database.

Identify new players.  Declare the new player to be the same as one already
on database or to be new to this database.

"""
from . import newplayers_database


class NewPlayers(newplayers_database.NewPlayers):

    """New Players panel for Results database with Online Grading Database.

    Customise newplayers_database user interface for use with published
    grading list.

    """

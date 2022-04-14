# help_.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Functions to create Help widgets for ChessResults.

The varieties of ChessResults are:

ChessResultsLite
ChessResultsOGD
ChessResultsECF

"""

import tkinter

from solentware_misc.gui.help import help_widget

from chessvalidate import help_ as chessvalidate_help_

from .. import help_


def help_about(master):
    """Display About document"""

    help_widget(master, help_.ABOUT, help_)


def help_file_size(master):
    """Display File Size document"""

    help_widget(master, help_.FILESIZE, help_)


def help_guide(master):
    """Display Guide document"""

    help_widget(master, help_.GUIDE, help_)


def help_keyboard(master):
    """Display Keyboard actions document"""

    help_widget(master, help_.ACTIONS, help_)


def help_samples(master):
    """Display Samples document"""

    help_widget(master, chessvalidate_help_.SAMPLES, chessvalidate_help_)


def help_tablespecs(master):
    """Display csv file layouts document"""

    help_widget(master, chessvalidate_help_.TABLESPECS, chessvalidate_help_)


def help_notes(master):
    """Display Notes document"""

    help_widget(master, chessvalidate_help_.NOTES, chessvalidate_help_)


if __name__ == "__main__":
    # Display all help_ documents without running ChessResults application

    root = tkinter.Tk()
    help_about(root)
    help_file_size(root)
    help_guide(root)
    help_keyboard(root)
    help_notes(root)
    help_samples(root)
    help_tablespecs(root)
    root.mainloop()

# resultsdb_lite.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database application using Lite interface: no ECF connections."""

if __name__ == "__main__":

    import chessresults.gui.resultsroot
    import chessresults.gui.leagues_lite

    app = chessresults.gui.resultsroot.Results(
        title="ChessResults",
        gui_module=chessresults.gui.leagues_lite.Leagues,
        width=400,
        height=200,
    )
    app.root.mainloop()

# resultsdb_ogd.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database application using OGD interface."""

if __name__ == "__main__":

    import chessresults.gui.resultsroot
    import chessresults.gui.leagues_ogd

    app = chessresults.gui.resultsroot.Results(
        title="ChessResultsOGD",
        gui_module=chessresults.gui.leagues_ogd.Leagues,
        width=400,
        height=200,
    )
    app.root.mainloop()

# resultsdb.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database application using ECF grading interface."""

if __name__ == "__main__":

    import chessresults.gui.resultsroot
    import chessresults.gui.leagues

    app = chessresults.gui.resultsroot.Results(
        title="ChessResultsGrading",
        gui_module=chessresults.gui.leagues.Leagues,
        width=400,
        height=200,
    )
    app.root.mainloop()

# results_ecf.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Chess results database application with ECF results submission"""

if __name__=='__main__':

    from . import APPLICATION_NAME

    # Keep the 'Grading' name because a 'Rating' version may be built using
    # SQL in a natural way, without options to use database engines other
    # than SQLite3.
    application_name = ''.join((APPLICATION_NAME, 'Grading'))
    try:
        from solentware_misc.gui.startstop import (
            start_application_exception,
            stop_application,
            application_exception,
            )
    except Exception as error:
        import tkinter.messagebox
        try:
           tkinter.messagebox.showerror(
               title='Start Exception',
               message='.\n\nThe reported exception is:\n\n'.join(
                   ('Unable to import solentware_misc.gui.startstop module',
                    str(error))),
               )
        except:
            pass
        raise SystemExit('Unable to import start application utilities')
    try:
        from .gui.resultsroot import Results
        from .gui.leagues import Leagues
    except Exception as error:
        start_application_exception(
            error,
            appname=application_name,
            action='import')
        raise SystemExit(' import '.join(('Unable to', application_name)))
    try:
        app = Results(
            title=application_name,
            gui_module=Leagues,
            width=400,
            height=200)
    except Exception as error:
        start_application_exception(
            error,
            appname=application_name,
            action='initialise')
        raise SystemExit(' initialise '.join(('Unable to', application_name)))
    try:
        app.root.mainloop()
    except SystemExit:
        stop_application(app, app.root)
        raise
    except Exception as error:
        application_exception(
            error,
            app,
            app.root,
            title=application_name,
            appname=application_name)

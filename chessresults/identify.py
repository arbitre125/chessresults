# identify.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Identify players sent to remote database who are reported as new players.

"""

if __name__ == '__main__':

    application_name = 'Identify'
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
        from .gui.identities import Identities
    except Exception as error:
        start_application_exception(
            error,
            appname=application_name,
            action='import')
        raise SystemExit(' import '.join(('Unable to', application_name)))
    try:
        app = Identities()
    except Exception as error:
        start_application_exception(
            error,
            appname=application_name,
            action='initialise')
        raise SystemExit(' initialise '.join(('Unable to', application_name)))
    try:
        if app.open_import():
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

# ecferrors.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Class for displaying reports.
"""

import tkinter

from solentware_misc.gui.exceptionhandler import ExceptionHandler


class ECFErrorFrame(ExceptionHandler):

    """Display error reports."""

    def __init__(self, parent, title, header, reports, cnf=dict(), **kargs):
        """Create the error reports and display them."""
        super(ECFErrorFrame, self).__init__()
        self.document = document = tkinter.Toplevel(master=parent)
        document.wm_title(title)
        caption = tkinter.Label(master=document, text=header)
        buttons_frame = tkinter.Frame(master=document)
        buttons_frame.pack(side=tkinter.BOTTOM, fill=tkinter.X)

        buttonrow = buttons_frame.pack_info()["side"] in ("top", "bottom")
        for i, b in enumerate(
            (("Ok", "Delete the report", True, 0, self.on_ok),)
        ):
            button = tkinter.Button(
                master=buttons_frame,
                text=b[0],
                underline=b[3],
                command=self.try_command(b[4], buttons_frame),
            )
            if buttonrow:
                buttons_frame.grid_columnconfigure(i * 2, weight=1)
                button.grid_configure(column=i * 2 + 1, row=0)
            else:
                buttons_frame.grid_rowconfigure(i * 2, weight=1)
                button.grid_configure(row=i * 2 + 1, column=0)
        if buttonrow:
            buttons_frame.grid_columnconfigure(len(b * 2), weight=1)
        else:
            self.buttons_frame.grid_rowconfigure(len(b * 2), weight=1)

        caption.pack(side=tkinter.TOP, fill=tkinter.X)
        section = tkinter.Frame(master=document)
        section.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=tkinter.TRUE)
        section.grid_rowconfigure(0, weight=1)

        for n, r in enumerate(reports):
            rep = ErrorReport(section, r, cnf=cnf, **kargs)
            section.grid_columnconfigure(n, uniform="rep", weight=1)
            rep.frame.grid(row=0, column=n, sticky=tkinter.NSEW)

    def on_ok(self, event=None):
        """Destroy the report"""
        self.document.destroy()


# This class may get moved to rmappsys
# Renamed as ErrorReport to avoid name clash with Report in core.report module.
class ErrorReport(ExceptionHandler):

    """Create an error report."""

    def __init__(self, parent, report, cnf=dict(), **kargs):
        """Create an error report."""
        super().__init__()
        self.frame = frame = tkinter.Frame(master=parent)
        frame.pack(fill=tkinter.BOTH, expand=tkinter.TRUE)
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=1)
        frame.grid_rowconfigure(2, weight=0)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=0)
        vscroll = tkinter.Scrollbar(master=frame, orient=tkinter.VERTICAL)
        vscroll.grid(row=1, column=1, sticky=tkinter.NS)
        hscroll = tkinter.Scrollbar(master=frame, orient=tkinter.HORIZONTAL)
        hscroll.grid(row=2, column=0, sticky=tkinter.EW)
        text = tkinter.Text(master=frame, cnf=cnf, **kargs)
        text.grid(row=1, column=0, sticky=tkinter.NSEW)
        text["xscrollcommand"] = self.try_command(hscroll.set, text)
        text["yscrollcommand"] = self.try_command(vscroll.set, text)
        hscroll["command"] = self.try_command(text.xview, text)
        vscroll["command"] = self.try_command(text.yview, text)

        header, items = report
        caption = tkinter.Label(master=frame, text=header)
        caption.grid(row=0, column=0, sticky=tkinter.NSEW)

        for line in items:
            text.insert(tkinter.END, "".join((line, "\n")))

        text.configure(state="disabled")

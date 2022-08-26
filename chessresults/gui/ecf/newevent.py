# newevent.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Panel for editing details of an Event for submission to ECF.
"""

import tkinter
import tkinter.messagebox

from solentware_misc.gui import panel, frame

from ...core.ecf import ecfrecord
from ...core import resultsrecord
from ...core import filespec
from .ecfeventcopy import ECFEventCopy


class NewEvent(panel.PlainPanel):

    """The NewEvent panel for a Results database."""

    _btn_ok = "newevent_ok"
    _btn_copy = "newevent_copy"
    _btn_refresh = "newevent_refresh"
    _btn_cancel = "newevent_cancel"

    def __init__(self, parent=None, cnf=dict(), **kargs):
        """Extend and define the results database new event panel."""
        super(NewEvent, self).__init__(parent=parent, cnf=cnf, **kargs)
        self.show_panel_buttons(
            (self._btn_ok, self._btn_copy, self._btn_refresh, self._btn_cancel)
        )
        self.create_buttons()

        self.newevent = tkinter.Frame(master=self.get_widget())
        self.newevent.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=True)

        self.newevent.grid_columnconfigure(0, uniform="col", weight=3)
        self.newevent.grid_columnconfigure(1, uniform="col", weight=3)
        self.newevent.grid_columnconfigure(2, uniform="col", weight=1)
        self.newevent.grid_rowconfigure(0, uniform="row", weight=1)
        self.newevent.grid_rowconfigure(1, uniform="row", weight=2)
        self.newevent.grid_rowconfigure(2, uniform="row", weight=2)
        self.newevent.grid_rowconfigure(3, uniform="row", weight=2)
        self.newevent.grid_rowconfigure(4, uniform="row", weight=2)

        self.event = tkinter.LabelFrame(master=self.newevent, text="Event")
        self.gradingofficer = tkinter.LabelFrame(
            master=self.newevent, text="Rating Officer"
        )
        self.gamefeeinvoice = tkinter.LabelFrame(
            master=self.newevent, text="Send Game Fee Invoice to"
        )
        self.colour = tkinter.LabelFrame(master=self.newevent, text="Colour")
        self.rateofplay = tkinter.LabelFrame(
            master=self.newevent, text="Rate of Play"
        )
        self.inform = tkinter.LabelFrame(master=self.newevent, text="Inform")
        self.adjudicate = tkinter.LabelFrame(
            master=self.newevent, text="Adjudicate"
        )

        self.event.grid(row=0, column=0, columnspan=3, sticky=tkinter.NSEW)
        self.gradingofficer.grid(
            row=1, column=0, rowspan=2, sticky=tkinter.NSEW
        )
        self.gamefeeinvoice.grid(
            row=3, column=0, rowspan=2, sticky=tkinter.NSEW
        )
        self.colour.grid(row=1, column=1, rowspan=1, sticky=tkinter.NSEW)
        self.rateofplay.grid(row=2, column=1, rowspan=2, sticky=tkinter.NSEW)
        self.adjudicate.grid(row=4, column=1, rowspan=1, sticky=tkinter.NSEW)
        self.inform.grid(row=1, column=2, rowspan=4, sticky=tkinter.NSEW)

        self.event.grid_columnconfigure(0, uniform="cole", weight=3)
        self.event.grid_columnconfigure(1, uniform="cole", weight=1)
        self.event.grid_columnconfigure(2, uniform="cole", weight=1)
        self.event.grid_columnconfigure(3, uniform="cole", weight=1)
        self.event.grid_rowconfigure(0, uniform="rowe", weight=1)
        self.event.grid_rowconfigure(1, uniform="rowe", weight=1)

        self.eventname = tkinter.Entry(
            master=self.event, state="readonly", takefocus=0
        )
        self.eventstartdate = tkinter.Entry(
            master=self.event, state="readonly", takefocus=0
        )
        self.eventenddate = tkinter.Entry(
            master=self.event, state="readonly", takefocus=0
        )
        self.eventcode = tkinter.Entry(master=self.event)

        self.eventname.grid(row=1, column=0, sticky=tkinter.EW)
        self.eventstartdate.grid(row=1, column=1, sticky=tkinter.EW)
        self.eventenddate.grid(row=1, column=2, sticky=tkinter.EW)
        self.eventcode.grid(row=1, column=3, sticky=tkinter.EW)

        label = tkinter.Label(master=self.event, text="Name")
        label.grid(row=0, column=0, sticky=tkinter.W)
        label = tkinter.Label(master=self.event, text="Start Date")
        label.grid(row=0, column=1, sticky=tkinter.W)
        label = tkinter.Label(master=self.event, text="End Date")
        label.grid(row=0, column=2, sticky=tkinter.W)
        label = tkinter.Label(master=self.event, text="Event Code")
        label.grid(row=0, column=3, sticky=tkinter.W)

        self.gradingofficer.grid_columnconfigure(0, uniform="colg", weight=1)
        self.gradingofficer.grid_rowconfigure(0, uniform="rowg", weight=1)
        self.gradingofficer.grid_rowconfigure(1, uniform="rowg", weight=1)
        self.gradingofficer.grid_rowconfigure(2, uniform="rowg", weight=1)
        self.gradingofficer.grid_rowconfigure(3, uniform="rowg", weight=1)
        self.gradingofficer.grid_rowconfigure(4, uniform="rowg", weight=1)
        self.gradingofficer.grid_rowconfigure(5, uniform="rowg", weight=2)
        self.gradingofficer.grid_rowconfigure(6, uniform="rowg", weight=1)
        self.gradingofficer.grid_rowconfigure(7, uniform="rowg", weight=1)

        self.gradername = tkinter.Entry(master=self.gradingofficer)
        self.graderemail = tkinter.Entry(master=self.gradingofficer)
        self.graderaddress = tkinter.Text(master=self.gradingofficer, height=2)
        self.graderpostcode = tkinter.Entry(master=self.gradingofficer)

        self.gradername.grid(row=1, column=0, sticky=tkinter.EW)
        self.graderemail.grid(row=3, column=0, sticky=tkinter.EW)
        self.graderaddress.grid(row=5, column=0, sticky=tkinter.NSEW)
        self.graderpostcode.grid(row=7, column=0, sticky=tkinter.EW)

        label = tkinter.Label(master=self.gradingofficer, text="Name")
        label.grid(row=0, column=0, sticky=tkinter.SW)
        label = tkinter.Label(master=self.gradingofficer, text="email")
        label.grid(row=2, column=0, sticky=tkinter.SW)
        label = tkinter.Label(master=self.gradingofficer, text="Address")
        label.grid(row=4, column=0, sticky=tkinter.SW)
        label = tkinter.Label(master=self.gradingofficer, text="Post Code")
        label.grid(row=6, column=0, sticky=tkinter.SW)

        self.gamefeeinvoice.grid_columnconfigure(0, uniform="colg", weight=1)
        self.gamefeeinvoice.grid_rowconfigure(0, uniform="rowg", weight=1)
        self.gamefeeinvoice.grid_rowconfigure(1, uniform="rowg", weight=1)
        self.gamefeeinvoice.grid_rowconfigure(2, uniform="rowg", weight=1)
        self.gamefeeinvoice.grid_rowconfigure(3, uniform="rowg", weight=2)
        self.gamefeeinvoice.grid_rowconfigure(4, uniform="rowg", weight=1)
        self.gamefeeinvoice.grid_rowconfigure(5, uniform="rowg", weight=1)

        self.treasurername = tkinter.Entry(master=self.gamefeeinvoice)
        self.treasureraddress = tkinter.Text(
            master=self.gamefeeinvoice, height=2
        )
        self.treasurerpostcode = tkinter.Entry(master=self.gamefeeinvoice)

        self.treasurername.grid(row=1, column=0, sticky=tkinter.EW)
        self.treasureraddress.grid(row=3, column=0, sticky=tkinter.NSEW)
        self.treasurerpostcode.grid(row=5, column=0, sticky=tkinter.EW)

        label = tkinter.Label(master=self.gamefeeinvoice, text="Name")
        label.grid(row=0, column=0, sticky=tkinter.SW)
        label = tkinter.Label(master=self.gamefeeinvoice, text="Address")
        label.grid(row=2, column=0, sticky=tkinter.SW)
        label = tkinter.Label(master=self.gamefeeinvoice, text="Post Code")
        label.grid(row=4, column=0, sticky=tkinter.SW)

        self.colour.grid_columnconfigure(0, uniform="colc", weight=1)
        self.colour.grid_columnconfigure(1, uniform="colc", weight=1)
        self.colour.grid_columnconfigure(2, uniform="colc", weight=1)
        self.colour.grid_rowconfigure(0, uniform="rowc", weight=1)
        self.colour.grid_rowconfigure(1, uniform="rowc", weight=1)

        self.defaultcolour = tkinter.IntVar()

        radiobutton = tkinter.Radiobutton(
            master=self.colour,
            text="Unset",
            variable=self.defaultcolour,
            value=0,
        )
        radiobutton.grid(row=0, column=0, sticky=tkinter.NSEW)
        radiobutton = tkinter.Radiobutton(
            master=self.colour,
            text="Black on All",
            variable=self.defaultcolour,
            value=1,
        )
        radiobutton.grid(row=0, column=1, sticky=tkinter.NSEW)
        radiobutton = tkinter.Radiobutton(
            master=self.colour,
            text="Black on Odd",
            variable=self.defaultcolour,
            value=2,
        )
        radiobutton.grid(row=0, column=2, sticky=tkinter.NSEW)
        radiobutton = tkinter.Radiobutton(
            master=self.colour,
            text="None",
            variable=self.defaultcolour,
            value=3,
        )
        radiobutton.grid(row=1, column=0, sticky=tkinter.NSEW)
        radiobutton = tkinter.Radiobutton(
            master=self.colour,
            text="White on All",
            variable=self.defaultcolour,
            value=4,
        )
        radiobutton.grid(row=1, column=1, sticky=tkinter.NSEW)
        radiobutton = tkinter.Radiobutton(
            master=self.colour,
            text="White on Odd",
            variable=self.defaultcolour,
            value=5,
        )
        radiobutton.grid(row=1, column=2, sticky=tkinter.NSEW)

        self.adjudicate.grid_columnconfigure(0, uniform="cola", weight=1)
        self.adjudicate.grid_columnconfigure(1, uniform="cola", weight=1)
        self.adjudicate.grid_columnconfigure(2, uniform="cola", weight=1)
        self.adjudicate.grid_columnconfigure(3, uniform="cola", weight=1)
        self.adjudicate.grid_rowconfigure(0, uniform="rowa", weight=1)

        self.adjudication = tkinter.IntVar()

        radiobutton = tkinter.Radiobutton(
            master=self.adjudicate,
            text="Unset",
            variable=self.adjudication,
            value=0,
        )
        radiobutton.grid(row=0, column=0, sticky=tkinter.NSEW)
        radiobutton = tkinter.Radiobutton(
            master=self.adjudicate,
            text="Maybe",
            variable=self.adjudication,
            value=1,
        )
        radiobutton.grid(row=0, column=1, sticky=tkinter.NSEW)
        radiobutton = tkinter.Radiobutton(
            master=self.adjudicate,
            text="No",
            variable=self.adjudication,
            value=2,
        )
        radiobutton.grid(row=0, column=2, sticky=tkinter.NSEW)
        radiobutton = tkinter.Radiobutton(
            master=self.adjudicate,
            text="Yes",
            variable=self.adjudication,
            value=3,
        )
        radiobutton.grid(row=0, column=3, sticky=tkinter.NSEW)

        self.inform.grid_columnconfigure(0, uniform="coli", weight=1)
        self.inform.grid_rowconfigure(0, uniform="rowi", weight=1)
        self.inform.grid_rowconfigure(1, uniform="rowi", weight=1)
        self.inform.grid_rowconfigure(2, uniform="rowi", weight=1)
        self.inform.grid_rowconfigure(3, uniform="rowi", weight=1)
        self.inform.grid_rowconfigure(4, uniform="rowi", weight=1)
        self.inform.grid_rowconfigure(5, uniform="rowi", weight=1)
        self.inform.grid_rowconfigure(6, uniform="rowi", weight=1)
        self.inform.grid_rowconfigure(7, uniform="rowi", weight=1)
        self.inform.grid_rowconfigure(8, uniform="rowi", weight=1)
        self.inform.grid_rowconfigure(9, uniform="rowi", weight=1)

        self.informchessmoves = tkinter.IntVar()
        self.informfide = tkinter.IntVar()
        self.informgrandprix = tkinter.IntVar()
        self.informeast = tkinter.IntVar()
        self.informmidlands = tkinter.IntVar()
        self.informnorth = tkinter.IntVar()
        self.informsouth = tkinter.IntVar()
        self.informwest = tkinter.IntVar()

        checkbutton = tkinter.Checkbutton(
            master=self.inform,
            text="ChessMoves",
            variable=self.informchessmoves,
        )
        checkbutton.grid(row=0, column=0, sticky=tkinter.W)
        checkbutton = tkinter.Checkbutton(
            master=self.inform, text="FIDE", variable=self.informfide
        )
        checkbutton.grid(row=1, column=0, sticky=tkinter.W)
        checkbutton = tkinter.Checkbutton(
            master=self.inform,
            text="Grand Prix",
            variable=self.informgrandprix,
        )
        checkbutton.grid(row=2, column=0, sticky=tkinter.W)
        checkbutton = tkinter.Checkbutton(
            master=self.inform, text="East", variable=self.informeast
        )
        checkbutton.grid(row=5, column=0, sticky=tkinter.W)
        checkbutton = tkinter.Checkbutton(
            master=self.inform, text="Midlands", variable=self.informmidlands
        )
        checkbutton.grid(row=6, column=0, sticky=tkinter.W)
        checkbutton = tkinter.Checkbutton(
            master=self.inform, text="North", variable=self.informnorth
        )
        checkbutton.grid(row=7, column=0, sticky=tkinter.W)
        checkbutton = tkinter.Checkbutton(
            master=self.inform, text="South", variable=self.informsouth
        )
        checkbutton.grid(row=8, column=0, sticky=tkinter.W)
        checkbutton = tkinter.Checkbutton(
            master=self.inform, text="West", variable=self.informwest
        )
        checkbutton.grid(row=9, column=0, sticky=tkinter.W)

        label = tkinter.Label(master=self.inform, text="Unions")
        label.grid(row=4, column=0, sticky=tkinter.SW)

        self.rateofplay.grid_columnconfigure(0, uniform="colr", weight=1)
        self.rateofplay.grid_columnconfigure(1, uniform="colr", weight=1)
        self.rateofplay.grid_columnconfigure(2, uniform="colr", weight=1)
        self.rateofplay.grid_columnconfigure(3, uniform="colr", weight=1)
        self.rateofplay.grid_columnconfigure(4, uniform="colr", weight=1)
        self.rateofplay.grid_rowconfigure(0, uniform="rowr", weight=1)
        self.rateofplay.grid_rowconfigure(1, uniform="rowr", weight=1)
        self.rateofplay.grid_rowconfigure(2, uniform="rowr", weight=1)
        self.rateofplay.grid_rowconfigure(3, uniform="rowr", weight=1)

        self.movesfirst = tkinter.Entry(master=self.rateofplay)
        self.moveslater = tkinter.Entry(master=self.rateofplay)
        self.minutesonly = tkinter.Entry(master=self.rateofplay)
        self.minutesfirst = tkinter.Entry(master=self.rateofplay)
        self.minuteslater = tkinter.Entry(master=self.rateofplay)
        self.minuteslast = tkinter.Entry(master=self.rateofplay)
        self.secondspermove = tkinter.Entry(master=self.rateofplay)

        self.movesfirst.grid(row=1, column=2, sticky=tkinter.EW)
        self.moveslater.grid(row=1, column=3, sticky=tkinter.EW)
        self.minutesonly.grid(row=2, column=1, sticky=tkinter.EW)
        self.minutesfirst.grid(row=2, column=2, sticky=tkinter.EW)
        self.minuteslater.grid(row=2, column=3, sticky=tkinter.EW)
        self.minuteslast.grid(row=2, column=4, sticky=tkinter.EW)
        self.secondspermove.grid(row=3, column=4, sticky=tkinter.EW)

        label = tkinter.Label(master=self.rateofplay, text="Session")
        label.grid(row=0, column=0, sticky=tkinter.NSEW)
        label = tkinter.Label(master=self.rateofplay, text="Only")
        label.grid(row=0, column=1, sticky=tkinter.NSEW)
        label = tkinter.Label(master=self.rateofplay, text="First")
        label.grid(row=0, column=2, sticky=tkinter.NSEW)
        label = tkinter.Label(master=self.rateofplay, text="Later")
        label.grid(row=0, column=3, sticky=tkinter.NSEW)
        label = tkinter.Label(master=self.rateofplay, text="Last")
        label.grid(row=0, column=4, sticky=tkinter.NSEW)
        label = tkinter.Label(master=self.rateofplay, text="Moves")
        label.grid(row=1, column=0, sticky=tkinter.NSEW)
        label = tkinter.Label(master=self.rateofplay, text="All")
        label.grid(row=1, column=1, sticky=tkinter.NSEW)
        label = tkinter.Label(master=self.rateofplay, text="Rest")
        label.grid(row=1, column=4, sticky=tkinter.NSEW)
        label = tkinter.Label(master=self.rateofplay, text="Minutes")
        label.grid(row=2, column=0, sticky=tkinter.NSEW)
        label = tkinter.Label(
            master=self.rateofplay, text="Seconds added per Move"
        )
        label.grid(row=3, column=2, sticky=tkinter.NSEW, columnspan=2)

        (
            self.eventrecord,
            self.ecfeventrecord,
        ) = self._get_event_and_ecf_event_records(
            self.get_appsys()
            .get_ecf_event_detail_context()
            .eventgrid.selection
        )
        self.populate_event_control()

    def close(self):
        """Close resources prior to destroying this instance.

        Used, at least, as callback from AppSysFrame container.

        """
        pass

    def describe_buttons(self):
        """Define all action buttons that may appear on events page."""
        super().describe_buttons()
        self.define_button(
            self._btn_ok,
            text="Save",
            tooltip="Put the event details on the database.",
            underline=2,
            command=self.on_ok,
        )
        self.define_button(
            self._btn_copy,
            text="Copy from list",
            tooltip=" ".join(
                (
                    "Display event list and select event from which details ",
                    "are copied.",
                )
            ),
            switchpanel=True,
            underline=0,
            command=self.on_copy,
        )
        self.define_button(
            self._btn_refresh,
            text="Show Original Data",
            tooltip="Clear the form and start again.",
            underline=5,
            command=self.on_refresh,
        )
        self.define_button(
            self._btn_cancel,
            text="Back to list",
            tooltip=" ".join(
                (
                    "Return to the previous display. Event details are NOT ",
                    "put on database.",
                )
            ),
            underline=0,
            switchpanel=True,
            command=self.on_cancel,
        )

    def event_details_ok(self):
        """Return response from update validation and confirmation dialogue."""

        def _change_value(control, value):
            control.delete("1.0", tkinter.END)
            control.insert(tkinter.END, value)

        def get_value(control):
            return control.get("1.0", tkinter.END).rstrip()

        errors = []
        if len(self.eventname.get()) == 0:
            errors.append("Event name not specified.")
        if len(self.eventname.get()) == 0:
            errors.append("Event start date not specified.")
        if len(self.eventname.get()) == 0:
            errors.append("Event end date not specified.")
        if len(self.gradername.get()) == 0:
            errors.append("Grader's name not specified.")
        if (
            len(self.graderemail.get()) == 0
            and len(get_value(self.graderaddress)) == 0
            and len(self.graderpostcode.get()) == 0
        ):
            errors.append("Give grader's email or postal address.")
        elif len(self.graderemail.get()) != 0 and (
            len(get_value(self.graderaddress)) != 0
            or len(self.graderpostcode.get()) != 0
        ):
            errors.append("Give one of grader's email and postal address.")
        elif len(self.graderemail.get()) == 0 and (
            len(get_value(self.graderaddress)) == 0
            or len(self.graderpostcode.get()) == 0
        ):
            errors.append("Give grader's postal address and post code.")
        if self.defaultcolour.get() == 0:
            errors.append("Colour rule not specified.")
        if (
            len(self.movesfirst.get()) == 0
            and len(self.moveslater.get()) == 0
            and len(self.minutesonly.get()) == 0
            and len(self.minutesfirst.get()) == 0
            and len(self.minuteslater.get()) == 0
            and len(self.minuteslast.get()) == 0
            and len(self.secondspermove.get()) == 0
        ):
            errors.append("Rate of Play not specified")
        elif (
            len(self.movesfirst.get()) != 0
            or len(self.moveslater.get()) != 0
            or len(self.minutesfirst.get()) != 0
            or len(self.minuteslater.get()) != 0
            or len(self.minuteslast.get()) != 0
        ) and (
            len(self.minutesonly.get()) != 0
            or len(self.secondspermove.get()) != 0
        ):
            errors.append(
                " ".join(
                    (
                        "Specify rate of play using 'Only session' column",
                        "or 'First Later and Last' session columns.",
                    )
                )
            )
        elif (
            len(self.minutesonly.get()) == 0
            and len(self.secondspermove.get()) == 0
        ):
            if (
                len(self.movesfirst.get()) == 0
                or len(self.minutesfirst.get()) == 0
            ):
                errors.append("First session rate of play not specified.")
            if (
                len(self.moveslater.get()) == 0
                and len(self.minuteslater.get()) == 0
                and len(self.minuteslast.get()) != 0
            ):
                pass
            elif (
                len(self.moveslater.get()) != 0
                and len(self.minuteslater.get()) != 0
            ):
                pass
            else:
                errors.append("Later session rate of play not specified.")
        elif len(self.minutesonly.get()) == 0:
            errors.append("Only session rate of play not specified.")
        if self.adjudication.get() == 0:
            errors.append("Adjudication option not specified.")
        if len(errors):
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="\n".join(errors),
                title="Event Detail",
            )
            return False

        for rop in (
            self.movesfirst,
            self.moveslater,
            self.minutesonly,
            self.minutesfirst,
            self.minuteslater,
            self.minuteslast,
            self.secondspermove,
        ):
            v = rop.get().strip()
            if len(v) != 0:
                if not v.isdigit():
                    errors.append("Rate of Play specifications must be digits")
                else:
                    # _change_value(rop, v)
                    rop.delete(0, tkinter.END)
                    rop.insert(tkinter.END, v)
        if len(errors):
            dlg = tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                message="\n".join(errors),
                title="Event Detail",
            )
            return False

        return tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="Confirm request to update event details",
            title="Event Detail",
        )

    def new_event_update(self):
        """Return response from insert validation and confirmation dialogue."""

        def get_value(control):
            return control.get("1.0", tkinter.END).rstrip()

        if self.ecfeventrecord is None:
            newrecord = ecfrecord.ECFrefDBrecordEvent()
            newrecord.value.eventname = self.eventname.get()
            newrecord.value.eventstartdate = self.eventstartdate.get()
            newrecord.value.eventenddate = self.eventenddate.get()
            newrecord.value.submission = 0
        else:
            newrecord = self.ecfeventrecord.clone()

        v = newrecord.value
        v.gradername = self.gradername.get()
        v.graderemail = self.graderemail.get()
        v.graderaddress = get_value(self.graderaddress)
        v.graderpostcode = self.graderpostcode.get()
        v.movesfirst = self.movesfirst.get()
        v.moveslater = self.moveslater.get()
        v.minutesonly = self.minutesonly.get()
        v.minutesfirst = self.minutesfirst.get()
        v.minuteslater = self.minuteslater.get()
        v.minuteslast = self.minuteslast.get()
        v.secondspermove = self.secondspermove.get()
        v.treasurername = self.treasurername.get()
        v.treasureraddress = get_value(self.treasureraddress)
        v.treasurerpostcode = self.treasurerpostcode.get()
        v.eventcode = self.eventcode.get()
        v.informfide = self.informfide.get()
        v.informchessmoves = self.informchessmoves.get()
        v.informgrandprix = self.informgrandprix.get()
        v.informeast = self.informeast.get()
        v.informmidlands = self.informmidlands.get()
        v.informnorth = self.informnorth.get()
        v.informsouth = self.informsouth.get()
        v.informwest = self.informwest.get()
        v.defaultcolour = self.defaultcolour.get()
        v.adjudication = self.adjudication.get()

        self.get_appsys().get_results_database().start_transaction()
        if self.ecfeventrecord is None:
            newrecord.key.recno = None
            newrecord.put_record(
                self.get_appsys().get_results_database(),
                filespec.ECFEVENT_FILE_DEF,
            )
        else:
            self.ecfeventrecord.edit_record(
                self.get_appsys().get_results_database(),
                filespec.ECFEVENT_FILE_DEF,
                filespec.ECFEVENT_FIELD_DEF,
                newrecord,
            )
        self.get_appsys().get_results_database().commit()

    def on_cancel(self, event=None):
        """Cancel event details amendment."""
        del event
        if tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            message="Confirm request to cancel event details amendment",
            title="Event Detail",
        ):
            return
        self.inhibit_context_switch(self._btn_cancel)

    def on_refresh(self, event=None):
        """Clear event details form."""
        del event
        if self.ecfeventrecord is None:
            msg = "Confirm request to clear event details form"
        else:
            msg = " ".join(
                ("Confirm request to put event details", "from record on form")
            )
        if tkinter.messagebox.askyesno(
            parent=self.get_widget(), message=msg, title="Event Detail"
        ):
            self.populate_event_control()

    def on_ok(self, event=None):
        """Update event details."""
        del event
        if self.event_details_ok():
            self.new_event_update()
            return

    def on_copy(self, event=None):
        """Switch to copy details from event panel."""
        del event

    def populate_event_control(self):
        """Populate new event widget with data from record."""

        if self.ecfeventrecord:
            v = self.ecfeventrecord.value
            _change_fixed_value(self.eventname, v.eventname)
            _change_fixed_value(self.eventstartdate, v.eventstartdate)
            _change_fixed_value(self.eventenddate, v.eventenddate)
            _change_value(self.eventcode, v.eventcode)
            _change_value(self.graderemail, v.graderemail)
            _change_value(self.gradername, v.gradername)
            _change_text_value(self.graderaddress, v.graderaddress)
            _change_value(self.graderpostcode, v.graderpostcode)
            _change_value(self.movesfirst, v.movesfirst)
            _change_value(self.moveslater, v.moveslater)
            _change_value(self.minutesonly, v.minutesonly)
            _change_value(self.minutesfirst, v.minutesfirst)
            _change_value(self.minuteslater, v.minuteslater)
            _change_value(self.minuteslast, v.minuteslast)
            _change_value(self.secondspermove, v.secondspermove)
            _change_value(self.treasurername, v.treasurername)
            _change_text_value(self.treasureraddress, v.treasureraddress)
            _change_value(self.treasurerpostcode, v.treasurerpostcode)
            self.informfide.set(v.informfide)
            self.informchessmoves.set(v.informchessmoves)
            self.informgrandprix.set(v.informgrandprix)
            self.informeast.set(v.informeast)
            self.informmidlands.set(v.informmidlands)
            self.informnorth.set(v.informnorth)
            self.informsouth.set(v.informsouth)
            self.informwest.set(v.informwest)
            self.defaultcolour.set(v.defaultcolour)
            self.adjudication.set(v.adjudication)
        else:
            _change_fixed_value(self.eventname, self.eventrecord.value.name)
            _change_fixed_value(
                self.eventstartdate, self.eventrecord.value.startdate
            )
            _change_fixed_value(
                self.eventenddate, self.eventrecord.value.enddate
            )
            _change_value(self.eventcode, "")
            _change_value(self.graderemail, "")
            _change_value(self.gradername, "")
            _change_text_value(self.graderaddress, "")
            _change_value(self.graderpostcode, "")
            _change_value(self.movesfirst, "")
            _change_value(self.moveslater, "")
            _change_value(self.minutesonly, "")
            _change_value(self.minutesfirst, "")
            _change_value(self.minuteslater, "")
            _change_value(self.minuteslast, "")
            _change_value(self.secondspermove, "")
            _change_value(self.treasurername, "")
            _change_text_value(self.treasureraddress, "")
            _change_value(self.treasurerpostcode, "")
            self.informfide.set(0)
            self.informchessmoves.set(0)
            self.informgrandprix.set(0)
            self.informeast.set(0)
            self.informmidlands.set(0)
            self.informnorth.set(0)
            self.informsouth.set(0)
            self.informwest.set(0)
            self.defaultcolour.set(0)
            self.adjudication.set(0)

    def copy_event_detail(self, selection):
        """Copy event detail from record to widget excluding event identity.

        Event identity includes event code and submission as well as name,
        start date, and end date.

        """
        (
            eventrecord,
            ecfeventrecord,
        ) = self._get_event_and_ecf_event_records(selection)
        if eventrecord is None or ecfeventrecord is None:
            return False
        v = ecfeventrecord.value
        _change_value(self.graderemail, v.graderemail)
        _change_value(self.gradername, v.gradername)
        _change_text_value(self.graderaddress, v.graderaddress)
        _change_value(self.graderpostcode, v.graderpostcode)
        _change_value(self.movesfirst, v.movesfirst)
        _change_value(self.moveslater, v.moveslater)
        _change_value(self.minutesonly, v.minutesonly)
        _change_value(self.minutesfirst, v.minutesfirst)
        _change_value(self.minuteslater, v.minuteslater)
        _change_value(self.minuteslast, v.minuteslast)
        _change_value(self.secondspermove, v.secondspermove)
        _change_value(self.treasurername, v.treasurername)
        _change_text_value(self.treasureraddress, v.treasureraddress)
        _change_value(self.treasurerpostcode, v.treasurerpostcode)
        self.informfide.set(v.informfide)
        self.informchessmoves.set(v.informchessmoves)
        self.informgrandprix.set(v.informgrandprix)
        self.informeast.set(v.informeast)
        self.informmidlands.set(v.informmidlands)
        self.informnorth.set(v.informnorth)
        self.informsouth.set(v.informsouth)
        self.informwest.set(v.informwest)
        self.defaultcolour.set(v.defaultcolour)
        self.adjudication.set(v.adjudication)
        return True

    def _get_event_and_ecf_event_records(self, selection):
        db = self.get_appsys().get_results_database()
        eventrecord = resultsrecord.get_event_from_record_value(
            db.get_primary_record(
                filespec.EVENT_FILE_DEF,
                selection[0][-1],
            )
        )
        ecfeventrecord = ecfrecord.get_ecf_event(
            db.get_primary_record(
                filespec.ECFEVENT_FILE_DEF,
                db.database_cursor(
                    filespec.ECFEVENT_FILE_DEF,
                    filespec.ECFEVENTIDENTITY_FIELD_DEF,
                ).get_unique_primary_for_index_key(
                    db.encode_record_number(
                        eventrecord.value.get_event_identity()
                    )
                ),
            )
        )
        return (eventrecord, ecfeventrecord)


def _change_text_value(control, value):
    control.delete("1.0", tkinter.END)
    control.insert(tkinter.END, value)


def _change_value(control, value):
    control.delete(0, tkinter.END)
    control.insert(tkinter.END, value)


def _change_fixed_value(control, value):
    control.configure(state=tkinter.NORMAL)
    _change_value(control, value)
    control.configure(state="readonly")

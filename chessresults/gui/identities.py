# identities.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Identify players sent to remote database who are reported as new players.

The remote database compares the player names included on the results file
with the names already known and reports any that cannot be matched back to
the submitter. This report includes all the player names on the remote
database.

This module allows the submitter to identify the new players as ones already
on the remote database or to confirm that they are new players.

These decisions are added to the report which should be returned to the
remote database.

"""

import os
import tkinter
import tkinter.messagebox
import tkinter.filedialog
import bz2
from functools import reduce

from solentware_misc.core.utilities import AppSysPersonName
from solentware_misc.gui.exceptionhandler import ExceptionHandler

from ..core import constants
from ..core import importreports


class Identities(ExceptionHandler):
    """List local new players and remote known players for identification."""

    def __init__(self):

        super(Identities, self).__init__()

        self.format_error = None
        self.importdata = None
        self.map_lbii_rem_new = []  # Listbox line index is 0-based integer
        self.map_lbki_remote = []
        self.map_lbni_newplayer = []
        self.remote = []  # players on importing database sorted by name
        self.local = []  # exported players unidentified on importing database

        self.lbidentified = None
        self.lbnew = None
        self.lbknown = None

        self.root = tkinter.Tk()
        self.root.wm_title(string="Identify New Players")
        self.root.wm_iconify()

    def get_widget(self):
        return self.root

    def break_identity(self):

        selection = self.lbidentified.curselection()
        if len(selection) == 0:
            tkinter.messagebox.showerror(
                parent=self.get_widget(),
                title="Break New Player Identification",
                message="Please select an Identified Player",
            )
            return
        elif len(selection) > 1:
            tkinter.messagebox.showerror(
                parent=self.get_widget(),
                title="Break New Player Identification",
                message="Please select just one Identified Player",
            )
            return
        elif not reduce(lambda a, b: a == b, selection):
            tkinter.messagebox.showerror(
                parent=self.get_widget(),
                title="Break New Player Identification",
                message="The selection is not an Identified Player",
            )
            return
        elif not tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            title="Break New Player Identification",
            message="Please confirm break identification",
        ):
            return

        index = selection[0][0]
        name_text, new, known = self.map_lbii_rem_new[int(index)]
        self._unmap_known_to_new(known, new)
        self.lbidentified.delete(index)
        self._get_new_and_identified_players()

    def identify_new_player(self):
        def ambiguous_identification(new, known):

            """if new == known:
            return False"""
            if (
                known
                in importdata.localplayer[importdata.gameplayermerge[new]]
            ):
                if known in importdata.gameplayer:
                    return False

            """if known in self.importdata.gameplayer:
                return True
            
            # not convinced this is correct - and it does not work
            # did refer to remoteplayermerge deleted a while ago
            if not isinstance(self.importdata.remoteplayer[known], set):
                known = self.importdata.remoteplayer[known]
            if self.importdata.known_to_new.get(known):
                return True"""

            return True

        def is_ambiguous_identification(new, known):

            if (
                known
                in importdata.localplayer[importdata.gameplayermerge[new]]
            ):
                # implies known in importdata is True
                if known not in importdata.gameplayer:
                    return True

        def is_new_player(new, known):

            if (
                known
                in importdata.localplayer[importdata.gameplayermerge[new]]
            ):
                # implies known in importdata is True
                if known in importdata.gameplayer:
                    return True

        importdata = self.importdata
        if (
            len(self.lbnew._selection) == 0
            and len(self.lbknown._selection) == 0
        ):
            tkinter.messagebox.showerror(
                parent=self.get_widget(),
                title="Identify New Players",
                message=" ".join(
                    ("Please select a New Player", "and a Known Player.")
                ),
            )
            return
        elif len(self.lbnew._selection) == 0:
            tkinter.messagebox.showerror(
                parent=self.get_widget(),
                title="Identify New Players",
                message="Please select a New Player.",
            )
            return
        elif len(self.lbknown._selection) == 0:
            tkinter.messagebox.showerror(
                parent=self.get_widget(),
                title="Identify New Players",
                message="Please select a Known Player.",
            )
            return

        new = self.map_lbni_newplayer[int(self.lbnew._selection[0])]
        known = self.map_lbki_remote[int(self.lbknown._selection[0])]
        if known in importdata.localplayer[importdata.gameplayermerge[new]]:
            # implies known in importdata.localplayer is True
            if known in importdata.gameplayer:
                if not tkinter.messagebox.askyesno(
                    parent=self.get_widget(),
                    title="Identify New Players",
                    message="".join(
                        (
                            "Please confirm that player is a New Player.\n\n",
                            "Have you checked other ways of presenting name.",
                        )
                    ),
                ):
                    return
            elif not tkinter.messagebox.askyesno(
                parent=self.get_widget(),
                title="Identify New Players",
                message=" ".join(
                    (
                        "Attempting to declare different New Players from",
                        "the same source to be the same player.\n\nThis",
                        "can, and should, be done on the source database",
                        "and the results resubmitted.\n\nProceeding with",
                        "the identification is allowed but will likely",
                        "cause problems in future that can be resolved",
                        "only by correcting the source identification.",
                    )
                ),
            ):
                return
        elif known in importdata.localplayer:
            tkinter.messagebox.showerror(
                parent=self.get_widget(),
                title="Identify New Players",
                message=" ".join(
                    (
                        "Attempting to declare different New Players from",
                        "the same source to be the same player.\n\nThis",
                        "can, and should, be done on the source database",
                        "and the results resubmitted.",
                    )
                ),
            )
            return
        elif known in importdata.known_to_new:
            tkinter.messagebox.showerror(
                parent=self.get_widget(),
                title="Identify New Players",
                message=" ".join(
                    (
                        "Attempting to declare different New Players from",
                        "the same source to be the same player.\n\nMaybe",
                        "this known player selection is wrong, or an earlier",
                        "selection listed under Identified New Players is",
                        "wrong.\n\nOtherwise some identifications on the source",
                        "or destination databases are wrong.",
                    )
                ),
            )
            return
        elif not tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            title="Identify New Players",
            message="Please confirm identification as known player",
        ):
            return

        self.importdata.map_known_to_new(known, new)

        for lb in self.lbnew, self.lbknown:
            lb._set_select_background_color(lb._selection, color=lb._bgcolor)
            selection = list(lb.curselection())
            selection.reverse()
            for s in selection:
                lb.selection_clear(s)
            lb._selection = ()

        self._get_new_and_identified_players()
        for e, v in enumerate(self.lbidentified.get(0, tkinter.END)):
            if v[0] == self.player_text(new):
                self.lbidentified.see(e)
                self.lbidentified.selection_clear(0, tkinter.END)
                self.lbidentified.selection_set(e)

    def open_import(self):

        filename = tkinter.filedialog.askopenfilename(
            parent=self.get_widget(),
            title="Import Reports",
            defaultextension=".bz2",
            filetypes=(("bz2 compressed", "*.bz2"),),
            initialdir="~",
        )

        self.format_error = []
        if filename:
            self.root.wm_title(
                string="Please wait while processing selected report"
            )
            self.root.wm_deiconify()
            self.root.update_idletasks()
            inputfile = bz2.open(filename, mode="rt", encoding="utf8")
            data = inputfile.read().split("\n")
            inputfile.close()
            self.importdata = importreports.ImportReports(data)
            if self.importdata.translate_results_format():
                del self.format_error[:]
            else:
                self.format_error.append(self.importdata)
        else:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title="Import Reports",
                message="File not specified",
            )
            self.root.destroy()
            self.root = None

        msg = []
        for fe in self.format_error:
            description, line_number, line_text = fe.error
            msg.append(
                "\n".join(
                    (
                        description,
                        " ".join(("Line", str(line_number))),
                        line_text,
                    )
                )
            )

        if len(self.format_error):
            tkinter.messagebox.showerror(
                parent=self.get_widget(),
                title="Import Reports",
                message="\n".join(msg),
            )
            self.root.destroy()
            self.root = None
        elif self.root is not None:
            self.root.wm_title(string=filename)
            fbuttons = tkinter.Frame(master=self.root)
            bbreak = tkinter.Button(
                master=fbuttons,
                text="Break",
                command=self.try_command(self.break_identity, fbuttons),
            )
            bbreak.pack(side=tkinter.LEFT, expand=tkinter.TRUE)
            bidentify = tkinter.Button(
                master=fbuttons,
                text="Identify",
                command=self.try_command(self.identify_new_player, fbuttons),
            )
            bidentify.pack(side=tkinter.LEFT, expand=tkinter.TRUE)
            bquit = tkinter.Button(
                master=fbuttons,
                text="Quit",
                command=self.try_command(self.quit_identify, fbuttons),
            )
            bquit.pack(side=tkinter.LEFT, expand=tkinter.TRUE)
            bsave = tkinter.Button(
                master=fbuttons,
                text="Save",
                command=self.try_command(self.save_report, fbuttons),
            )
            bsave.pack(side=tkinter.LEFT, expand=tkinter.TRUE)
            bsubmit = tkinter.Button(
                master=fbuttons,
                text="Submit",
                command=self.try_command(self.submit_report, fbuttons),
            )
            bsubmit.pack(side=tkinter.LEFT, expand=tkinter.TRUE)
            fbuttons.pack(side=tkinter.BOTTOM, fill=tkinter.X)
            fplayers = tkinter.Frame(master=self.root)
            fplayers.pack(
                side=tkinter.TOP, expand=tkinter.TRUE, fill=tkinter.BOTH
            )
            self.lbidentified = MatchListbox(
                master=self.root,
                caption="Identified New Players",
                labels=("New Player", "Known Player"),
            )
            self.lbnew = IdListbox(master=fplayers, lblabel="New Players")
            self.lbknown = IdListbox(master=fplayers, lblabel="Known Players")
            # get exporting database new players and importing database matches
            self._get_new_and_identified_players()
            # get players on importing database
            for player, v in self.importdata.remoteplayer.items():
                merge, alias = v
                if merge is not None:
                    self.remote.append(
                        (AppSysPersonName(player[0]).name, player, player)
                    )
                    for a in alias:
                        self.remote.append(
                            (AppSysPersonName(a[0]).name, a, player)
                        )
            self.remote.sort()
            # populate listbox
            lbk = self.lbknown
            for n, a, p in self.remote:
                lbk.insert(tkinter.END, self.player_text(a))
                self.map_lbki_remote.append(a)  # maybe p or (a, p)
            self.lbidentified.pack(
                side=tkinter.TOP, expand=tkinter.TRUE, fill=tkinter.BOTH
            )
            self.lbnew.frame.pack(
                side=tkinter.LEFT, expand=tkinter.TRUE, fill=tkinter.BOTH
            )
            lbk.frame.pack(
                side=tkinter.LEFT, expand=tkinter.TRUE, fill=tkinter.BOTH
            )
        if self.root is None:
            return None
        return bool(filename)

    def player_text(self, player):

        n, e, sd, ed, s, p = player
        if s is None:
            s = ""
        if p is False:
            p = ""
        else:
            p = str(p)
        return "  ".join((n, e, sd, ed, s, p))

    def quit_identify(self):

        if tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            title="Identify New Players",
            message="Do you really want to Quit",
        ):
            self.root.destroy()

    def save_report(self):

        self._save_report("Save")

    def submit_report(self):

        if self.lbnew.size():
            tkinter.messagebox.showerror(
                parent=self.get_widget(),
                title="Submit Identified New Players",
                message=" ".join(
                    (
                        "Cannot submit while there are unidentified",
                        "New Players.\n\n(The New Players list must be empty.",
                        "Use Identify to move these to the Identified",
                        "New Players list.)",
                    )
                ),
            )
            return

        self._save_report("Submit")

    def _get_new_and_identified_players(self):
        """Build new and identified player maps at start and after change."""

        gameplayermerge = self.importdata.gameplayermerge
        # get new players on exporting database
        new_players = self.importdata.get_new_players()
        # get matches made between new players on exporting database
        # and players on importing database
        self.map_lbii_rem_new = []
        matchedplayers = set()
        for new, known in self.importdata.new_to_known.items():
            self.map_lbii_rem_new.append(
                (AppSysPersonName(new[0]).name, new, known)
            )
            matchedplayers.add(new)
            if not isinstance(new, type(gameplayermerge[new])):
                for a in gameplayermerge[new]:
                    matchedplayers.add(new)
        self.map_lbii_rem_new.sort()
        # get unmatched new players on exporting database
        self.local = []
        for np in new_players:
            if np not in matchedplayers:
                if np in gameplayermerge:
                    self.local.append((AppSysPersonName(np[0]).name, np, np))
                    for a in gameplayermerge[np]:
                        if a in new_players:
                            self.local.append(
                                (AppSysPersonName(a[0]).name, a, np)
                            )
        self.local.sort()
        # populate listboxes
        self.map_lbni_newplayer = []
        lbn = self.lbnew
        lbn.delete(0, tkinter.END)
        for n, a, p in self.local:
            lbn.insert(tkinter.END, self.player_text(a))
            self.map_lbni_newplayer.append(a)  # maybe p or (a, p)
        lbi = self.lbidentified
        lbi.delete(0, tkinter.END)
        for n, new, known in self.map_lbii_rem_new:
            lbi.insert(
                tkinter.END, (self.player_text(new), self.player_text(known))
            )

    def _save_report(self, caption):

        importdata = self.importdata
        if importdata is None:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title=" ".join((caption, "Identified New Players")),
                message="No reported new players to process",
            )
            return

        def append_player(es):

            n, e, sd, ed, s, p = player
            identified.append("=".join((constants._event, e)))
            identified.append("=".join((constants._startdate, sd)))
            identified.append("=".join((constants._enddate, ed)))
            for x in es:
                identified.append("=".join((constants._eventsection, x)))
            if s:
                identified.append("=".join((constants._section, s)))
            if p:
                identified.append("=".join((constants._pin, str(p))))
            elif p is False:
                identified.append("=".join((constants._pinfalse, "true")))
            identified.append("=".join((identity, n)))

        get_event_from_player = importreports.get_event_from_player
        identified = []
        for t in importdata.textlines:
            if t.startswith(constants._identified):
                break
            identified.append(t)
        if self.map_lbii_rem_new:
            identified.append("=".join((constants._identified, "true")))
        for n, new, known in self.map_lbii_rem_new:
            for identity, player, events in (
                (constants._newidentity, new, importdata.localevents),
                (constants._knownidentity, known, importdata.remoteevents),
            ):
                append_player(events[get_event_from_player(player)])

        filename = tkinter.filedialog.asksaveasfilename(
            parent=self.get_widget(),
            title=" ".join((caption, "Identified New Players")),
            defaultextension=".bz2",
            filetypes=(("bz2 compressed", "*.bz2"),),
        )
        self.root.update()
        if filename:
            outputfile = bz2.open(filename, mode="wt", encoding="utf8")
            outputfile.write("\n".join(identified))
            outputfile.close()
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title=" ".join((caption, "Identified New Players")),
                message="\n".join(
                    ("Identified New Players saved in", filename)
                ),
            )
        else:
            tkinter.messagebox.showwarning(
                parent=self.get_widget(),
                title=" ".join((caption, "Identified New Players")),
                message="Identified New Players not saved",
            )

    def _unmap_known_to_new(self, known, new):
        """Remove new player from known player map."""

        del self.importdata.known_to_new[known]
        del self.importdata.new_to_known[new]
        self._get_new_and_identified_players()


class IdListbox(tkinter.Listbox, ExceptionHandler):
    """Custom listbox for selecting one item from each of several lists."""

    def __init__(self, master, lblabel):

        self.frame = f = tkinter.Frame(master=master)
        tkinter.Label(master=f, text=lblabel).pack(
            side=tkinter.TOP, fill=tkinter.X
        )
        hsb = tkinter.Scrollbar(master=f, orient=tkinter.HORIZONTAL)
        hsb.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        vsb = tkinter.Scrollbar(master=f, orient=tkinter.VERTICAL)
        vsb.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        tkinter.Listbox.__init__(
            self, master=f, selectmode="single", selectbackground="yellow"
        )
        self._bgcolor = self["background"]
        self._selection = ()
        self._lbwidget = None
        self.pack(side=tkinter.TOP, expand=tkinter.YES, fill=tkinter.BOTH)
        self["yscrollcommand"] = self.try_command(vsb.set, self)
        self["xscrollcommand"] = self.try_command(hsb.set, self)
        vsb.configure(command=self.try_command(self.yview, vsb))
        hsb.configure(command=self.try_command(self.xview, hsb))
        for sequence, function in (
            ("<Button-1>", self._button_1),
            ("<space>", self._space),
            ("<Control-backslash>", self._clear_selection),
        ):
            self.bind(sequence, self.try_event(function))

    def _button_1(self, event):
        self._remove_select_color(event)
        self._set_select_color(event)

    def _space(self, event):
        if self._selection:
            self._remove_select_color(event)
        elif self._selection != self.curselection():
            self._selection = self.curselection()

    def _remove_select_color(self, event):

        if not self._selection:
            return
        self._set_select_background_color(self._selection, color=self._bgcolor)
        self._selection = ()

    def _set_select_background_color(self, selection, color=None):

        try:
            for i in selection:
                self.itemconfigure(i, background=color)
        except tkinter.TclError as exc:
            if self.curselection():
                tkinter.messagebox.showinfo(
                    parent=self.get_widget(),
                    title="Tcl Error",
                    message="".join(
                        (
                            "Reported error is:\n\n'",
                            str(exc),
                            "'.\n\nSelection cancelled.",
                        )
                    ),
                )
            self._selection = ()

    def _set_select_color(self, event):

        self._selection = (
            self.index("@" + str(event.x) + "," + str(event.y)),
        )
        self._set_select_background_color(self._selection, color="yellow")

    def _clear_selection(self, event):

        if self._selection:
            self._remove_select_color(event)
        self.selection_clear(0, tkinter.END)


class MatchListbox(tkinter.Frame, ExceptionHandler):
    """Custom frame for displaying matches.

    Following the multi-listbox example in Python Cookbook.

    """

    def __init__(self, master, caption, labels):

        tkinter.Frame.__init__(self, master)

        self.lists = []
        tkinter.Label(master=self, text=caption).pack()
        for l in labels:
            frame = tkinter.Frame(self)
            frame.pack(
                side=tkinter.LEFT, expand=tkinter.YES, fill=tkinter.BOTH
            )
            if isinstance(l, str):
                tkinter.Label(frame, text=l).pack(fill=tkinter.X)
            sb = tkinter.Scrollbar(frame, orient=tkinter.HORIZONTAL)
            sb.pack(side=tkinter.BOTTOM, fill=tkinter.X)
            lb = tkinter.Listbox(
                frame,
                selectmode="single",
                # width=w,
                borderwidth=0,
                selectborderwidth=0,
                relief=tkinter.FLAT,
                exportselection=tkinter.FALSE,
            )
            lb.pack(expand=tkinter.YES, fill=tkinter.BOTH)
            self.lists.append(lb)
            sb.configure(command=self.try_command(lb.xview, sb))
            lb.configure(xscrollcommand=self.try_command(sb.set, lb))
            for sequence, function in (
                ("<ButtonPress-1>", self._select_item),
                ("<Key-Up>", self._synchronize_listbox_items),
                ("<Key-Down>", self._synchronize_listbox_items),
                ("<Control-Home>", self._activate_item_home),
                ("<Control-End>", self._activate_item_end),
                ("<Control-Next>", lambda e: None),
                ("<Control-Prior>", lambda e: None),
                ("<Next>", self._synchronize_listbox_items),
                ("<Prior>", self._synchronize_listbox_items),
                ("<space>", self._select_active_item),
                ("<Select>", self._select_active_item),
                ("<Control-slash>", self._select_active_item),
                ("<Control-backslash>", self._clear_selection),
                # auto-scroll dragging button-1 breaks list synchronization
                ("<Leave>", lambda e: "break"),
            ):
                lb.bind(sequence, self.try_event(function))

        frame = tkinter.Frame(self)
        frame.pack(side=tkinter.LEFT, fill=tkinter.Y)
        tkinter.Label(frame, borderwidth=1).pack(fill=tkinter.X)
        sb = tkinter.Scrollbar(
            frame,
            orient=tkinter.VERTICAL,
            command=self.try_command(self._scroll, frame),
        )
        sb.pack(expand=tkinter.YES, fill=tkinter.Y)
        self.lists[0]["yscrollcommand"] = sb.set

    def _scroll(self, *args):

        for l in self.lists:
            l.yview(*args)
        return "break"

    def _select_item(self, event):

        self.selection_clear(0, tkinter.END)
        self.selection_set(event.widget.nearest(event.y))
        return "break"

    def _synchronize_listbox_items(self, event):

        self._lbwidget = event.widget
        self.after_idle(self._set_top_item)

    def _activate_item_home(self, event):

        self.selection_clear(0, tkinter.END)
        self.selection_set(0)
        self.see(0)
        return "break"

    def _activate_item_end(self, event):

        self.selection_clear(0, tkinter.END)
        self.selection_set(tkinter.END)
        self.see(tkinter.END)
        return "break"

    def _clear_selection(self, event):

        self.selection_clear(0, tkinter.END)
        return "break"

    def _select_active_item(self, event):

        self.selection_clear(0, tkinter.END)
        self.selection_set(event.widget.index(tkinter.ACTIVE))
        self.see(event.widget.index(tkinter.ACTIVE))
        return "break"

    def _set_top_item(self):

        top = self._lbwidget.nearest(0)
        for l in self.lists:
            l.yview(top)

    def curselection(self):

        result = []
        for l in self.lists:
            result.append(l.curselection())
        return list(zip(*result))

    def delete(self, first, last=None):

        for l in self.lists:
            l.delete(first, last)

    def get(self, first, last=None):

        result = []
        for l in self.lists:
            result.append(l.get(first, last))
        return result

    def insert(self, index, *elements):

        for e in elements:
            i = 0
            for l in self.lists:
                l.insert(index, e[i])
                i = i + 1

    def see(self, index):

        for l in self.lists:
            l.see(index)

    def selection_clear(self, first, last=None):

        for l in self.lists:
            l.selection_clear(first, last)

    def selection_set(self, first, last=None):

        for l in self.lists:
            l.selection_set(first, last)

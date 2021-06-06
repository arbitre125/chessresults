# prepare.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Prepare ECF submission files and League database dumps for Results input.

The user interface for copying submission files and database dumps from where
they were put by the generating applications to the places where the Results
application will look for them.

"""

import os
import tkinter
import tkinter.messagebox
import tkinter.filedialog

from solentware_misc.gui.exceptionhandler import ExceptionHandler

from ..core import constants as cc


class Prepare(ExceptionHandler):
    """Convert from League or ECF submission format to Results format."""

    def __init__(self, format_class):
        super(Prepare, self).__init__()
        self.format_class = format_class
        self.format_error = None
        self.importdata = None
        self.folder = None
        self.root = tkinter.Tk()
        self.root.wm_title(string="Prepare data for Results database")
        self.root.wm_iconify()

    def get_widget(self):
        return self.root

    def open_submission(self, folder):

        self.format_error = []
        if folder:
            print(folder)
            self.root.wm_title(
                string="Please wait while processing selected folder"
            )
            self.root.wm_deiconify()
            self.root.update_idletasks()
            self.importdata = self.format_class(folder)
            extract = self.importdata.translate_results_format()
            if not self.importdata.error:
                del self.format_error[:]
            else:
                self.format_error.append(self.importdata)
            self.root.wm_title(string=folder)
            msg = []
            for fe in self.format_error:
                for f, e in fe.error:
                    msg.append("".join(e))
                    fp, fc = f
                    msg.append("".join(("Processing ", fc)))
                    if fp is None:
                        msg.append("First file.\n")
                    else:
                        msg.append("".join(("Previous file is ", fp, "\n")))
            if len(msg):
                msg[:0] = [
                    "Errors found processing the listed files.\n",
                    "The first error found is reported for each file.\n",
                    " ".join(
                        (
                            "The previous file is given because the fault",
                            "could be there",
                        )
                    ),
                    " ".join(
                        (
                            "if the error is detected before the current file's",
                            "event is",
                        )
                    ),
                    "found.\n",
                ]
                msg.append("\n")
                msg.append(
                    " ".join(
                        (
                            "Note that mixing files of different types is an error:",
                            "probably reporting affilateECODE and #EVENT DETAILS",
                            "keywords if the processed files are otherwise ok",
                        )
                    )
                )
                fbuttons = tkinter.Frame(master=self.root)
                bquit = tkinter.Button(
                    master=fbuttons,
                    text="Quit",
                    command=self.try_command(self.quit_submission, fbuttons),
                )
                bquit.pack(side=tkinter.LEFT, expand=tkinter.TRUE)
                fbuttons.pack(side=tkinter.BOTTOM, fill=tkinter.X)
                text = tkinter.Text(master=self.root, wrap=tkinter.WORD)
                text.insert(tkinter.END, "\n".join(msg))
                text.pack(fill=tkinter.BOTH, expand=tkinter.TRUE)
                tkinter.messagebox.showerror(
                    parent=self.get_widget(),
                    title="Prepare data for Results database",
                    message="Errors found processing files",
                )
            else:
                self.folder = folder
                toplevel = tkinter.Toplevel(master=self.root)
                toplevel.wm_title(string="Import Files")
                text = tkinter.Text(master=toplevel)
                text.insert(
                    tkinter.END,
                    "\n\n\n\n".join(
                        self.importdata.extract_data_from_import_files(
                            importfiles=extract
                        )
                    ),
                )
                text.pack(fill=tkinter.BOTH, expand=tkinter.TRUE)
                text = "".join(
                    (
                        "Summary of derivation.",
                        "\n\n",
                        "ECF submission files and League database dumps in the ",
                        "selected folder and any subfolders have been copied and ",
                        "any items not needed for the Results database removed. ",
                        "This includes ECF codes and dates of birth which may be ",
                        "present on the imported files.",
                        "\n\n",
                        "The Pin can be used to merge players on import to the ",
                        "new database. All players with the same Pin in the ",
                        "selected folder, and subfolders, are assumed to be the ",
                        "same player. ",
                        "But where the ECF grading code is used as the Pin then ",
                        "players from different submission files will not be ",
                        "merged for you.",
                        "\n\n",
                        "A player's Pin after import will almost certainly be ",
                        "different to the Pin before import.",
                    )
                )
                fbuttons = tkinter.Frame(master=self.root)
                bquit = tkinter.Button(
                    master=fbuttons,
                    text="Quit",
                    command=self.try_command(self.quit_submission, fbuttons),
                )
                bsave = tkinter.Button(
                    master=fbuttons,
                    text="Save",
                    command=self.try_command(self.save_submission, fbuttons),
                )
                bsave.pack(side=tkinter.LEFT, expand=tkinter.TRUE)
                bquit.pack(side=tkinter.LEFT, expand=tkinter.TRUE)
                fbuttons.pack(side=tkinter.BOTTOM, fill=tkinter.X)
                helptext = tkinter.Text(master=self.root, wrap=tkinter.WORD)
                helptext.insert(tkinter.END, text)
                helptext.pack(fill=tkinter.BOTH, expand=tkinter.TRUE)
            return True
        else:
            tkinter.messagebox.showinfo(
                parent=self.get_widget(),
                title="Prepare data for Results database",
                message="Folder containining import data not specified",
            )
            self.root.destroy()
            self.root = None

    def quit_submission(self):
        if tkinter.messagebox.askyesno(
            parent=self.get_widget(),
            title="Prepare data for Results database",
            message="Do you really want to Quit",
        ):
            self.root.destroy()

    def save_submission(self):
        def save_ok():
            if not os.path.exists(folder):
                msg = " ".join(
                    (
                        "Confirm the folder",
                        folder,
                        "is to be created and the listed files saved there",
                    )
                )
            else:
                msg = "Confirm that the listed files are to be saved"
            if tkinter.messagebox.askyesno(
                parent=self.get_widget(), title="Save Files", message=msg
            ):
                for s in savefiles:
                    self.importdata.write_file(s, savefiles[s], folder)
                toplevel.destroy()

        folder = tkinter.filedialog.askdirectory(
            parent=self.root, initialdir="~"
        )
        if not folder:
            return
        savefiles = dict()
        allexist = True
        noneexist = True
        for f in self.importdata.files:
            p = self.importdata.generate_file_name(f, self.folder, folder)
            e = os.path.exists(p)
            savefiles[f] = (p, e)
            if e:
                noneexist = False
            else:
                allexist = False
        report = []
        if allexist:
            report.append(
                "All files already exist - they will be overwritten.\n"
            )
        elif noneexist:
            report.append("All files will be created - they do not exist.\n")
        else:
            report.append(
                " ".join(
                    (
                        "Some files already exist.  Those that do will be",
                        "overwritten and the others will be created.\n",
                    )
                )
            )
        for s in sorted(savefiles):
            p, e = savefiles[s]
            if e:
                report.append("      ".join((p, "exists")))
            else:
                report.append(p)
        toplevel = tkinter.Toplevel(master=self.root)
        toplevel.wm_title(string="Save Files")
        fbuttons = tkinter.Frame(master=toplevel)
        bcancel = tkinter.Button(
            master=fbuttons,
            text="Cancel",
            command=self.try_command(toplevel.destroy, fbuttons),
        )
        bok = tkinter.Button(
            master=fbuttons,
            text="Ok",
            command=self.try_command(save_ok, fbuttons),
        )
        bok.pack(side=tkinter.LEFT, expand=tkinter.TRUE)
        bcancel.pack(side=tkinter.LEFT, expand=tkinter.TRUE)
        fbuttons.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        text = tkinter.Text(master=toplevel)
        text.insert(tkinter.END, "\n".join(report))
        text.pack(fill=tkinter.BOTH, expand=tkinter.TRUE)


class PrepareECF(Prepare):
    """Convert from ECF submission format to Results format."""

    def open_submission(self):
        folder = tkinter.filedialog.askdirectory(
            parent=self.root, initialdir="~"
        )
        return super(PrepareECF, self).open_submission(folder)


class PrepareLeague(Prepare):
    """Convert from League format to Results format."""

    def open_submission(self):
        folder = tkinter.filedialog.askopenfilename(
            parent=self.root, initialdir="~"
        )
        return super(PrepareLeague, self).open_submission(folder)

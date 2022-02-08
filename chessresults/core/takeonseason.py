# takeonseason.py
# Copyright 2010 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Take-on data from prepared ECF submission files and League database dumps.

This module does not process valid ECF submission files (2006 definition).

Preparation consists of removing grading code and club data in particular and
any other data that this database does not want or want from these sources.

The data is assumed to be correct.  However team names need to be derived from
the MATCH RESULTS fields but it is not always possible to do this correctly
because there is no prior list of valid team names.  Given reasonable team
names the players involved can be identified as 'AN Other who played for
Anytown in the 2002 Homecounty league' and so on.  Typically AN Other will
have several entries (one for each season's league) and these entries can be
assumed to refer to the same player if the PIN fields have the same value.

The data can be processed with the assumption that equality of PIN value in
different files means it is the same player or with the assumption that it is
not the same player.

"""

import difflib
import os
import tkinter.messagebox

from .takeonschedule import TakeonSchedule
from .takeonreport import TakeonSubmission, TakeonLeagueDump
from .takeonresults import TakeonSubmissionFile, TakeonLeagueDumpFile
from .takeoncollation import TakeonCollation
from .importresults import get_import_event_results
from . import constants


class TakeonSeasonError(Exception):
    pass


class TakeonSeason(object):

    """Default management of source and derived data files for an event.

    Assume that the initial schedule and results files are empty and that
    the user creates these by entering all data.  The alternative, left to
    other subclasses of Season defined as required, is to populate these
    files with data from source files and perform additional consistency
    checks between the versions when updating or extracting data.  Use this
    class when there is no need for audit of the data.

    """

    _sourcefiles = (constants.TAKEON_SCHEDULE, constants.TAKEON_REPORTS)

    def __init__(self, folder):
        """Override, note the configuration details for event.

        folder - contains files of event data

        """
        self.folder = folder
        self.config = "conf"
        self.fixtures = None
        self.fixturesfile = None
        self.results = None
        self.resultsfile = None
        self._fixtures = None
        self._collation = None
        self.takeonfiles = []

    @property
    def collation(self):
        """ """
        return self._collation

    def get_data_file_names(self, config):
        """Return list of data files named in configuration file.

        Source files and difference files are in the list.  Caller is expected
        to check that all source files exist before creating any difference
        files that should exist.

        """
        cf = open(config, "r")
        lines = [s.strip().split("=", 1) for s in cf.readlines()]
        cf.close()
        srcfiles = dict()
        for sf in self._sourcefiles:
            srcfiles[sf] = None
        for s in lines:
            if len(s) == 2:
                k, v = s
                if k in srcfiles:
                    srcfiles[k] = os.path.join(self.folder, v)
        return srcfiles

    def get_folder_contents(self, folder, takeonfiles):
        """Update takeonfiles set with take-on file names in folder.

        Each folder containing a file with take-on data will have a file named
        takeon_conf (constants.TAKEON_ECF_FORMAT) or league_database_data.txt
        (constants.LEAGUE_DATABASE_DATA). LEAGUE_DATABASE_DATA will be in folder
        but TAKEON_ECF_FORMAT may be in subdirectories of folder as well or
        instead. The files containing the take-on data for TAKEON_ECF_FORMAT
        will be named <take-on>/<take-on>.txt (perhaps .TXT).
        LEAGUE_DATABASE_DATA is the data file.

        """
        fn = os.path.join(folder, constants.LEAGUE_DATABASE_DATA)
        if os.path.isfile(fn):
            takeonfiles.add(fn)
            return
        takeon_conf_isfile = os.path.isfile(
            os.path.join(folder, constants.TAKEON_ECF_FORMAT)
        )
        for f in os.listdir(folder):
            fn = os.path.join(folder, f)
            if os.path.isfile(fn):
                if takeon_conf_isfile:
                    tfd, tff = os.path.split(fn)
                    tf, te = os.path.splitext(tff)
                    if tf != os.path.split(tfd)[-1]:
                        continue
                    if te.lower() not in constants.TAKEON_EXT:
                        continue
                    takeonfiles.add(fn)
            elif os.path.isdir(fn):
                self.get_folder_contents(fn, takeonfiles)

    def get_folder_contents_for_merge(self, folder):
        """Return TakeonLeagueDumpFile or TakeonSubmissionFile object.

        Pick off special cases (league database dump format) otherwise
        look for ecf format files.

        """
        league = os.path.join(folder, constants.LEAGUE_DATABASE_DATA)
        guard = os.path.join(folder, constants.TAKEON_LEAGUE_FORMAT)
        if os.path.isfile(league) and os.path.isfile(guard):
            merge = TakeonLeagueDumpFile(folder)
        else:
            merge = TakeonSubmissionFile(folder)
        merge.get_folder_contents(folder)
        return merge

    def get_results_from_file(self):
        """Override, create Collation object from text files.

        The Schedule and Report objects deal with various ways of laying out
        the data in text files.  The Collation object holds the data in
        a format convenient for comparison with existing contents of results
        database and subsequent updates.
        """
        if self._collation == None:
            self.get_schedule_from_file(TakeonSchedule)
            textlines = [t for t in difflib.restore(self.results, 2)]
            if (
                len(self.takeonfiles.files) == 1
                and os.path.join(self.folder, constants.LEAGUE_DATABASE_DATA)
                in self.takeonfiles.files
            ):
                results = TakeonLeagueDump()
            else:
                results = TakeonSubmission()
            results.build_results(
                textlines,
                self._fixtures,
                os.path.splitext(os.path.basename(self.folder))[0],
            )
            # The next two lines are a relic of the two steps being done in
            # separate consecutive processes, possibly days apart.  Nothing is
            # actually exported in the first step but the second step expects
            # stuff in that format.
            exportgames = results.export_games(pins=True)
            importdata = get_import_event_results(exportgames, "")
            self._collation = TakeonCollation(
                results, self._fixtures, importdata
            )
            # Following is a poor comment but it suggests I think PDLCollation
            # has the inferior way of doing this.
            # rather than follow lead of class PDLCollation with Collation
            # self._collation.error.extend(results.error)
            # self._collation.collate_matches()
            # self._collation.collate_players()

    def open_documents(self, parent):
        """Override, extract data from text files and return True if ok."""
        merge = self.get_folder_contents_for_merge(self.folder)
        if not len(merge.files):
            tkinter.messagebox.showinfo(
                parent=parent,
                message=" ".join(
                    [
                        "Folder",
                        os.path.split(self.folder)[-1],
                        "and its sub-folders, if any, do not contain any data",
                        "files marked for addition to a Results database.",
                    ]
                ),
                title="Open results take-on data",
            )
            return
        if not merge.translate_results_format():
            tkinter.messagebox.showerror(
                parent=parent,
                title="Results data take-on",
                message=" ".join(
                    (
                        "Format error found while processing data in",
                        self.folder,
                    )
                ),
            )
            return

        config = os.path.join(self.folder, self.config)
        if not os.path.exists(config):
            cf = open(config, "w")
            for sf in self._sourcefiles:
                cf.writelines(
                    (
                        "".join((sf, "=")),
                        os.path.join(
                            "".join(
                                (sf, os.path.basename(self.folder), ".txt")
                            )
                        ),
                        os.linesep,
                    )
                )
            cf.close()

            tkinter.messagebox.showinfo(
                parent=parent,
                message=" ".join(
                    [
                        "Configuration file",
                        config,
                        "created with",
                        "default file names for event schedule and",
                        "reports. Edit now, if necessary, to match",
                        "actual file names. Click OK when ready.",
                    ]
                ),
                title="Open results take-on data",
            )

        srcfiles = self.get_data_file_names(config)
        if not self.source_documents_exist(srcfiles, config, parent):
            return False

        # Get the fixtures
        schedule = srcfiles[constants.TAKEON_SCHEDULE]
        fixtures = self.get_difference_file(
            [mn for mn in merge.matchnames],
            schedule,
            "Schedule Files",
            parent,
            "Open take-on schedule data",
        )
        if not isinstance(fixtures, list):
            return False

        # Get the reports
        reports = srcfiles[constants.TAKEON_REPORTS]
        results = self.get_difference_file(
            merge.get_lines_for_difference_file(),
            reports,
            "Report Files",
            parent,
            "Open take-on reports data",
        )
        if not isinstance(results, list):
            return False

        self.fixturesfile = schedule
        self.resultsfile = reports
        self.fixtures = fixtures
        self.results = results
        self.takeonfiles = merge
        return True

    def source_documents_exist(self, sourcefiles, config, parent):
        """Check that all source files exist and return True.

        sourcefiles will contain names of difference files to be generated or
        updated from source files.  Existence of these files is not checked.

        """
        ok = True
        for s in sourcefiles:
            if sourcefiles[s] == None:
                ok = False
                tkinter.messagebox.showinfo(
                    parent=parent,
                    message=" ".join(
                        ["Specification for", s, "not in", config]
                    ),
                    title="Open results take-on data",
                )
        if not ok:
            return False
        return True

    # Copy code from original season.py instead of delegating to superclass
    def extract_schedule(self, newfixtures):
        """Update the Schedule object getfixtures from newfixtures text lines."""
        oldfixtures = list(difflib.restore(self.fixtures, 1))
        self.fixtures = list(difflib.ndiff(oldfixtures, newfixtures))
        self._fixtures = None
        self.get_schedule_from_file(TakeonSchedule)

    # Copied methods from here on (rescued from original season.py)

    def save_difference_files(self, newfixtures, newresults):
        """Update event files with new fixture and result data.

        newfixtures - list of text lines being new fixtures file
        newresults - list of text lines being new results file

        The difference files are updated to recorded the differnce between
        the file as originally stored and the current text in newfixtures
        and newresults.  In other words the old version of current text is
        replaced by the new version of current text while retaining the
        original text entered into the file.

        """
        oldfixtures = list(difflib.restore(self.fixtures, 1))
        self.fixtures = list(difflib.ndiff(oldfixtures, newfixtures))
        oldresults = list(difflib.restore(self.results, 1))
        self.results = list(difflib.ndiff(oldresults, newresults))
        try:
            ff = open(self.fixturesfile, "wb")
            ff.write("\n".join(self.fixtures).encode("utf8"))
        finally:
            ff.close()
        try:
            fr = open(self.resultsfile, "wb")
            fr.write("\n".join(self.results).encode("utf8"))
        finally:
            fr.close()

    def extract_results(self, newresults):
        """Call get_results_from_file method to process newresults text lines.

        It is assumed that get_results_from_file call will update a Results
        object.

        """
        oldresults = list(difflib.restore(self.results, 1))
        self.results = list(difflib.ndiff(oldresults, newresults))
        self._collation = None
        self.get_results_from_file()

    def close(self):
        """Discard references to the event data."""
        self.fixtures = None
        self.fixturesfile = None
        self.results = None
        self.resultsfile = None
        self._fixtures = None
        self._collation = None

    def datafiles_exist(self):
        """Return True if files named in configuration file exist.

        Subclasses must override this method and should check that the files
        in self.folder are consistent with the files created by the
        open_documents method of that subclass.
        """
        raise TakeonSeasonError("datafiles_exist not implemented")

    def get_collated_games(self):
        """Return the Collation.games object"""
        return self._collation.games

    def get_difference_file(self, lines, diff, orig, parent, dlgcaption):
        """Return list of text lines in file managed using difflib.

        lines - the text to be put in file if it does not yet exist
        diff - the file containing current version of event data
        orig - source of data being added to diff
        parent - master widget for create file information dialogue
        dlgcaption - title for dialogue

        """
        if not os.path.exists(diff):
            difflines = list(difflib.ndiff(lines, lines))
            fo = open(diff, "wb")
            fo.write("\n".join(difflines).encode("utf8"))
            fo.close()
            if len(lines):
                tkinter.messagebox.showinfo(
                    parent=parent,
                    message=" ".join(
                        ["Data extracted from", orig, "into", diff]
                    ),
                    title=dlgcaption,
                )
            else:
                tkinter.messagebox.showinfo(
                    parent=parent,
                    message=" ".join(["Empty", diff, "created"]),
                    title=dlgcaption,
                )
            return difflines
        else:
            fd = open(diff, "rb")
            diffbytes = fd.read()
            fd.close()
            # Early versions of program did not use utf-8 and in practice
            # assumed iso-8859-1 encoding.
            try:
                difflines = diffbytes.decode("utf8").splitlines()
            except UnicodeDecodeError:
                difflines = diffbytes.decode("iso-8859-1").splitlines()
            origlines = list(difflib.restore(difflines, 1))
            if len(origlines) > len(lines):
                tkinter.messagebox.showinfo(
                    parent=parent,
                    message="".join(
                        [
                            orig,
                            ", ignoring editing since creation, contains more ",
                            "data than the source documents.",
                            os.linesep,
                            "To use the new data delete ",
                            diff,
                            os.linesep,
                            "(losing any editing done), or provide source ",
                            "documents consistent with earlier versions.",
                        ]
                    ),
                    title=dlgcaption,
                )
                return False
            elif origlines != lines[: len(origlines)]:
                tkinter.messagebox.showinfo(
                    parent=parent,
                    message="".join(
                        [
                            orig,
                            ", ignoring editing since creation, is not ",
                            "consistent with the new source documents.",
                            os.linesep,
                            "To use the new data delete ",
                            diff,
                            os.linesep,
                            "(losing any editing done), or provide source ",
                            "documents consistent with earlier versions.",
                        ]
                    ),
                    title=dlgcaption,
                )
                return False
            elif len(lines) > len(origlines):
                fd = open(diff, "wb")
                newlines = lines[len(origlines) :]
                newdifflines = difflib.ndiff(newlines, newlines)
                difflines.extend(newdifflines)
                fd.write("\n".join(difflines).encode("utf8"))
                fd.close()
                tkinter.messagebox.showinfo(
                    parent=parent,
                    message="".join(
                        [
                            "Extended source documents consistent with earlier ",
                            "versions have been supplied.",
                            os.linesep,
                            orig,
                            " is extended and previous edits have been retained.",
                        ]
                    ),
                    title=dlgcaption,
                )
                return difflines
            else:
                return difflines

    def get_schedule_from_file(self, getfixtures):
        """Extract schedule from text file using getfixtures.build_schedule.

        getfixtures - the Schedule class or a subclass

        """
        if self._fixtures == None:
            f = list(difflib.restore(self.fixtures, 2))
            self._fixtures = getfixtures()
            self._fixtures.build_schedule(f)

# takeonresults.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Split ECF submission files into schedule and reports files.

The contents of a submission file have to be assumed correct.  But it is not
always possible to pick out useful team names from the assumed match names in
MATCH RESULTS, MNAME in league format, fields.  The match names are extracted
into the schedule file for ease of finding the data to edit.  The schedule
file contains lines like 'match_213=Fareham - Cosham'.  'match_213' replaces
the corresponding instance of 'Fareham - Cosham' in the reports file.

Lines such as 'match_213=(Cup) Fareham - Cosham' will cause problems that are
resolved by removing '(Cup) ' from the match name.  If the extra text occurs
in lots of match names it may be possible to preserve the annotation and get
useful team names with lines like 'match_213=Fareham (Cup) Cosham'.

"""

import os
import collections

from . import constants as cc


class TakeonResults(object):
    """Class for importing results data.
    """
    
    def __init__(self, folder):
        super(TakeonResults, self).__init__()
        self.folder = folder
        self.files = set()
        self.converterror = None
        self.matchnames = []
        self.textlines = []

    def empty_extract(self):
        self.matchnames[:] = []
        self.textlines[:] = []
        return False

    def translate_results_format(
        self,
        keymap=None,
        tidyup=None):
        """Extract results into a common format.

        Provide rules in context and keymap arguments.

        """

        if keymap is None:
            keymap = dict()

        data = dict()
        for t in self.get_lines():
            ts = t.split('=', 1)
            key, value = ts[0], ts[-1]
            if key not in keymap:
                self.textlines.append(t)
            else:
                keymap[key](data, key, value)

        if len(data):
            if isinstance(tidyup, collections.Callable):
                tidyup(data)

        return True

    def get_folder_contents(self, folder):
        """Add all files in folder and its subdirectories to self.files."""
        for f in os.listdir(folder):
            fn = os.path.join(folder, f)
            if os.path.isfile(fn):
                self.files.add(fn)
            elif os.path.isdir(fn):
                self.get_folder_contents(fn)
                
    def get_lines(self):
        """Return lines of text from file.

        Extend get_lines method in subclass if self.textlines needs
        transforming before being processed by translate_results_format method.

        """
        self.get_folder_contents(self.folder)
        text = []
        for f in sorted(self.files):
            ofile = open(f, 'r')
            text.extend([t.rstrip() for t in ofile.readlines()])
            ofile.close()
        return text
                
    def get_lines_for_difference_file(self):
        """Return lines of text formatted for results difference file."""
        return [t for t in self.textlines]


class TakeonSubmissionFile(TakeonResults):
    """Import data from file formatted as ECF results submission file.
    """

    def get_folder_contents(self, folder):
        """Get files in folder and subdirectories expected to hold ecf data."""
        guard_found = False
        datafile = None
        for f in os.listdir(folder):
            fn = os.path.join(folder, f)
            if os.path.isfile(fn):
                guard_found = guard_found or (f == cc.TAKEON_ECF_FORMAT)
                if os.path.splitext(f)[0] == os.path.basename(folder):
                    datafile = fn
            elif os.path.isdir(fn):
                self.get_folder_contents(fn)
        if guard_found:
            if datafile:
                self.files.add(datafile)
                
    def get_lines(self):
        """Delimiter is # optionally preceded by newline sequence."""
        columns = []
        row = []
        table = False
        text = []

        for t in ''.join(
            super(TakeonSubmissionFile, self).get_lines()).split('#'):
            ts = t.split('=', 1)
            key, value = ts[0], ts[-1]
            if key == cc.TABLE_END:
                if len(row):
                    text.append(key)
                table = False
                columns = []
            elif key == cc.TABLE_START:
                if table:
                    text.append(key)
                table = True
                row = []
            elif table:
                if len(row) == 0:
                    row = columns[:]
                text.append('='.join((row.pop(0), t)))
            elif key == cc.COLUMN:
                columns.append(value)
            elif key is value:
                if len(t):
                    text.append(key)
            else:
                text.append('='.join((key, value)))
        return text

    def translate_results_format(self):

        def set_match(data, key, value):
            field = '_'.join((
                cc.TAKEON_MATCH,
                str(len(self.matchnames) + 1),
                ))
            self.matchnames.append('='.join((field, value)))
            self.textlines.append('='.join((key, field)))

        keymap = {
            cc.MATCH_RESULTS: set_match,
            }

        extract = super(TakeonSubmissionFile, self).translate_results_format(
            keymap=keymap,
            tidyup=None)

        if not extract:
            return False

        return extract

    def get_lines_for_difference_file(self):
        """Return lines of text formatted for results difference file."""
        end_group = {
            cc.EVENT_DETAILS,
            cc.PLAYER_LIST,
            cc.SECTION_RESULTS,
            cc.MATCH_RESULTS,
            cc.OTHER_RESULTS,
            cc.FINISH}
        start_group = {
            cc.EVENT_CODE,
            cc.PIN,
            cc.PIN1}
        filetext = []
        linetext = []
        group = False
        for t in self.textlines:
            k = t.split('=', 1)[0]
            if k in start_group:
                if linetext:
                    filetext.append(''.join(linetext))
                linetext = [''.join(('#', t))]
                group = True
            elif k in end_group:
                if linetext:
                    filetext.append(''.join(linetext))
                linetext = []
                filetext.append(''.join(('#', t)))
                group = False
            elif group:
                linetext.append(''.join(('#', t)))
            else:
                filetext.append(''.join(('#', t)))
        if linetext:
            filetext.append(''.join(linetext))

        return filetext


class TakeonLeagueDumpFile(TakeonResults):
    """Import data from dump of League program database.
    """

    def get_folder_contents(self, folder):
        """Add the league database data file in folder to self.files."""
        for f in os.listdir(folder):
            if f == cc.LEAGUE_DATABASE_DATA:
                fn = os.path.join(folder, f)
                if os.path.isfile(fn):
                    self.files.add(fn)
                
    def translate_results_format(self):

        def get_match(data, key, value):
            data[key] = value

        def set_match(data, key, value):
            tidyup(data)
            self.textlines.append(key)

        def tidyup(data):
            if cc.MNAME in data:
                if cc.MTYPE in data:
                    if data[cc.MTYPE] == cc.LEAGUE_MATCH_TYPE:
                        field = '_'.join((
                            cc.TAKEON_MATCH,
                            str(len(self.matchnames) + 1),
                            ))
                        self.matchnames.append(
                            '='.join((field, data[cc.MNAME])))
                        self.textlines.append(
                            '='.join((cc.MTYPE, data[cc.MTYPE])))
                        self.textlines.append(
                            '='.join((cc.MNAME, field)))
                    else:
                        self.textlines.append(
                            '='.join((cc.MTYPE, data[cc.MTYPE])))
                        self.textlines.append(
                            '='.join((cc.MNAME, data[cc.MNAME])))
                else:
                    self.textlines.append('='.join((cc.MNAME, data[cc.MNAME])))
            elif cc.MTYPE in data:
                self.textlines.append('='.join((cc.MTYPE, data[cc.MTYPE])))
            data.clear()

        keymap = {
            cc.player: set_match,
            cc.game: set_match,
            cc.team: set_match,
            cc.event: set_match,
            cc.match: set_match,
            cc.MNAME: get_match,
            cc.MTYPE: get_match,
            }

        extract = super(TakeonLeagueDumpFile, self).translate_results_format(
            keymap=keymap,
            tidyup=tidyup)

        if not extract:
            return False

        return extract

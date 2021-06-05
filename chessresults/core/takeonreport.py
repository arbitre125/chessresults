# takeonreport.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Generate a report comparing results with schedule.
"""

import collections

from . import constants as cc
from . import convertresults


class TakeonReport(convertresults.ConvertResults):

    """Game results extracted from data take-on file.

    Subclasses will deal with particular input formats.
    
    """

    def __init__(self, **kargs):

        super().__init__(pinprefix='')
        self.textlines = None
        self.error = []
        self.match_names = set()

    def build_results(
        self, textlines, schedule, pinprefix, keymap=None, tidyup=None):
        """Populate the event report from self.textlines."""
        self.pinprefix = pinprefix
        self.textlines = []

        if keymap is None:
            keymap = dict()

        data = dict()
        plist = {cc.MNAME, cc.MTYPE}
        for t in textlines:
            ts = t.rstrip().split('=', 1)
            key, value = ts[0], ts[-1]
            if key not in keymap:
                self.textlines.append(t)
            else:
                keymap[key](data, key, value, schedule.match_names)

        if len(data):
            if isinstance(tidyup, collections.Callable):
                tidyup(data, schedule.match_names)

        for smn in schedule.match_names:
            if smn not in self.match_names:
                self.error.append(''.join((
                    'Match name "',
                    smn,
                    '" not used in results"')))
        for rmn in self.match_names:
            if rmn not in schedule.match_names:
                self.error.append(''.join((
                    'Match name "',
                    rmn,
                    '" not defined in schedule"')))
        if self.error:
            return
        
        self.translate_results_format()
        
    def get_lines(self):
        """Return lines of text from file.

        Extend get_lines method in subclass if self.textlines needs
        transforming before being processed by translate_results_format method.

        """
        return [t.rstrip() for t in self.textlines]

    def report_games(self, master=None):
        er, par, pgr, gr = super(TakeonReport, self).report_games()
        return (
            (('Inconsistent Affiliations and Team Names', pgr),),
            (('Events', er),
             ('Players and Affiliations', par),
             ('Games by Event Section', gr),),
            )


class TakeonSubmission(
    convertresults.ConvertSubmissionFile,
    TakeonReport):
    """Import data from file formatted as ECF results submission file
    """

    def build_results(self, textlines, schedule, pinprefix):
        """Populate the event report from self.textlines."""

        def set_match(data, key, value, matchnames):
            if value in schedule.match_names:
                self.textlines.append(
                    '='.join((key, schedule.match_names[value])))
                if value in self.match_names:
                    self.error.append(''.join((
                        'Match name "',
                        value,
                        '" translation "',
                        schedule.match_names[value],
                        '" is a duplicate')))
                else:
                    self.match_names.add(value)
            else:
                self.textlines.append('='.join((key, value)))
                if value in self.match_names:
                    self.error.append(''.join((
                        'Match name "',
                        value,
                        '" is a duplicate with no translation')))
                else:
                    self.match_names.add(value)

        keymap = {
            cc.TAKEON_MATCH_RESULTS: set_match,
            }

        super(TakeonSubmission, self).build_results(
            textlines, schedule, pinprefix, keymap=keymap)

    def get_lines(self):
        """Delimiter is # optionally preceded by newline sequence."""
        text = []
        for t in ''.join(
            super(TakeonSubmission, self).get_lines()).split('#'):
            ts = t.split('=', 1)
            key, value = ts[0], ts[-1]
            # replace match name placeholder with edited name
            text.append('='.join((key, value)))
        return text


class TakeonLeagueDump(
    convertresults.ConvertLeagueDump,
    TakeonReport):
    """Import data from dump of League program database.
    """

    def __init__(self):
        super(TakeonLeagueDump, self).__init__(pinprefix='')

    def build_results(self, textlines, schedule, pinprefix):
        """Populate the event report from self.textlines."""

        def get_match(data, key, value, matchnames):
            data[key] = value
            if cc.MTYPE in data:
                tidyup(data, matchnames)

        def get_matchtype(data, key, value, matchnames):
            data[key] = value
            if cc.MNAME in data:
                tidyup(data, matchnames)

        def set_context(data, key, value, matchnames):
            self.textlines.append(key)

        def tidyup(data, matchnames):
            if cc.MTYPE in data:
                self.textlines.append('='.join((cc.MTYPE, data[cc.MTYPE])))
                value = data[cc.MNAME]
                if data[cc.MTYPE] == cc.LEAGUE_MATCH_TYPE:
                    if value in schedule.match_names:
                        self.textlines.append(
                            '='.join((cc.MNAME, schedule.match_names[value])))
                        if value in self.match_names:
                            self.error.append(''.join((
                                'Match name "',
                                value,
                                '" translation "',
                                schedule.match_names[value],
                                '" is a duplicate')))
                        else:
                            self.match_names.add(value)
                    else:
                        self.textlines.append('='.join((cc.MNAME, value)))
                        if value in self.match_names:
                            self.error.append(''.join((
                                'Match name "',
                                value,
                                '" is a duplicate with no translation')))
                        else:
                            self.match_names.add(value)
                else:
                    self.textlines.append('='.join((cc.MNAME, value)))
            elif cc.MNAME in data:
                self.textlines.append('='.join((cc.MNAME, data[cc.MNAME])))
            data.clear()

        keymap = {
            cc.player: set_context,
            cc.game: set_context,
            cc.team: set_context,
            cc.event: set_context,
            cc.match: set_context,
            cc.MNAME: get_match,
            cc.MTYPE: get_matchtype,
            }

        super(TakeonLeagueDump, self).build_results(
            textlines, schedule, pinprefix, keymap=keymap, tidyup=tidyup)

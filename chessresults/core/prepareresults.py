# prepareresults.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Prepare ECF submission files and League database dumps for Results input.

This module allows event data held on a League database to be prepared for
input into a Berkeley DB or DPT results database.  The ECF submission file
format is used to transfer the data because it is the only output generated
by any grading program in a known and fit for purpose format.

The assumption necessary is that a PIN value refers to the same player
across submission files.

A restriction is that use of a PIN that looks like an ECF grading code is
sufficient to prevent this module making the assumption for the player.
(The League program does not use the grading code as PIN.)

BCF CODE; CLUB NAME; CLUB (non-standard for CLUB NAME); CLUB CODE;
and CLUB COUNTY fields on submission files are removed.

(There is a data dump program for League databases and that format is
supported here. The data dump program is available to graders on request.
The only advantage from using this program is that all the data is in
a single file making it difficult to forget some data.)

"""

import os
import collections

from . import constants as cc


class PrepareResults(object):
    """Class for importing results data.
    """
    
    def __init__(self, container):
        super(PrepareResults, self).__init__()
        self.container = container
        self.pinprefix = os.path.splitext(os.path.basename(container))[0]
        self.files = set()
        self.keeppinvaluemap = dict()
        self.filenewtextmap = dict()
        self.error = []

    def empty_extract(self):
        return False

    def translate_results_format(
        self,
        context=None,
        keymap=None,
        validmap=None,
        pinreadmap=None,
        pinmap=None,
        gradingcodemap=None,
        discardmap=None,
        copy_lines=True):
        """Extract results into a common format.

        Provide rules in context and keymap arguments.

        """

        def null(lines, text):
            pass

        def null_extend(lines, text, data):
            pass

        def copy_text(lines, text):
            lines.append(text)

        def copy_text_extend(lines, text, data):
            lines.extend(text)

        if copy_lines:
            process = copy_text
        else:
            process = null
            
        if context is None:
            context = dict()
        for c in context:
            if not isinstance(context[c], collections.Callable):
                if context[c] is True:
                    context[c] = copy_text_extend
                else:
                    context[c] = null_extend
        if keymap is None:
            keymap = dict()
        if validmap is None:
            validmap = dict()
        if pinreadmap is None:
            pinreadmap = set()
        if pinmap is None:
            pinmap = set()
        if gradingcodemap is None:
            gradingcodemap = set()
        if discardmap is None:
            discardmap = set()

        pinvaluemap = dict()
        keeppins = pinreadmap - pinmap
        cc_gccc = cc._grading_code_check_characters  # avoid long line later
        extract = []
        filesprocessed = [None]
        for f, text in self.get_lines():
            fault = False
            filesprocessed.append(f)
            lines = []
            record = []
            data = dict()
            for t in text:
                ts = t.split('=', 1)
                key, value = ts[0], ts[-1]
                if key not in validmap:
                    if len(key) != 0:
                        self.error.append((
                            filesprocessed[-2:],
                            ('Keyword not expected : ',
                             key)))
                        fault = True
                        break
                else:
                    vm = validmap[key]
                    if isinstance(vm, str):
                        if contextkey != vm:
                            self.error.append((
                                filesprocessed[-2:],
                                ('Keyword ',
                                 key,
                                 ' not expected after keyword ',
                                 contextkey)))
                            fault = True
                            break
                    elif isinstance(vm, dict):
                        if contextkey not in vm:
                            self.error.append((
                                filesprocessed[-2:],
                                ('Keyword ',
                                 key,
                                 ' not expected after keyword ',
                                 contextkey)))
                            fault = True
                            break
                    elif vm is not None:
                        self.error.append((
                            filesprocessed[-2:],
                            ('Unable to determine validity of keyword ',
                             key)))
                        fault = True
                        break
                if key in context:
                    if len(record):
                        context[contextkey](lines, record, data)
                    contextkey = key
                    data.clear()
                    record = []
                # keymap values may make the discard map superfluous
                # GCODE is in keymap but BCF_CODE is not and so on
                if key in keymap:
                    if key in pinmap:
                        if value not in pinvaluemap:
                            if len(value) != cc._grading_code_length:
                                pinvaluemap[value] = value
                            elif (
                                value[-1] in cc_gccc and
                                value[:-1].isdigit()):
                                pinvaluemap[value] = '-'.join((
                                    self.pinprefix,
                                    str(len(pinvaluemap))))
                            else:
                                pinvaluemap[value] = value
                    if key in pinreadmap:
                        try:
                            process(
                                record, '='.join((key, pinvaluemap[value])))
                        except KeyError:
                            self.error.append((
                                filesprocessed[-2:],
                                ('PIN ', value,
                                 ' for field ', key,
                                 ' is not in PIN map')))
                            fault = True
                            break
                        data[keymap[key]] = pinvaluemap[value]
                        if key in keeppins:
                            if value not in self.keeppinvaluemap:
                                self.keeppinvaluemap[
                                    value] = pinvaluemap[value]
                    elif key not in discardmap:
                        process(record, t)
                        data[keymap[key]] = value
                elif key in gradingcodemap:
                    if cc._pcode in data:
                        if len(value) == cc._grading_code_length:
                            if value[:-1] in data[cc._pcode]:
                                self.error.append((
                                    filesprocessed[-2:],
                                    ('Grading code ',
                                     value,
                                     ' is included in player pin ',
                                     data[cc._pcode])))
                                fault = True
                                break
                elif key in context:
                    process(record, t)
            if fault:
                continue
            if len(record):
                context[contextkey](lines, record, data)
            extract.append((f, lines))

        return extract

    def get_folder_contents(self, container):
        for f in os.listdir(container):
            fn = os.path.join(container, f)
            if os.path.isfile(fn):
                self.files.add(fn)
            elif os.path.isdir(fn):
                self.get_folder_contents(fn)
                
    def get_lines(self):
        """Return lines of text from file.

        Extend get_lines method in subclass if self.textlines needs
        transforming before being processed by translate_results_format method.

        """
        self.get_folder_contents(self.container)
        filetext = []
        for f in self.files:
            ofile = open(f, 'r') # 'rb'?
            filetext.append((f, [t.rstrip() for t in ofile.readlines()]))
            ofile.close()
        return filetext

    def extract_data_from_import_files(self, importfiles=None):
        """Return list containing processed import file contents."""
        if importfiles is None:
            importfiles = [('No files to display', [])]
        return [self.report_file(f, t) for f, t in importfiles]


class PrepareSubmissionFile(PrepareResults):
    """Import data from file formatted as ECF results submission file.
    """

    def translate_results_format(self):

        # context copied from merges.py and value part of key:value
        # changed as necessary
        context = {
            cc.EVENT_DETAILS: True,
            cc.PLAYER_LIST: True,
            cc.OTHER_RESULTS: True,
            cc.MATCH_RESULTS: True,
            cc.SECTION_RESULTS: True,
            cc.FINISH: True,
            cc.PIN: True,
            cc.PIN1: True,
            }

        # keymap copied from merges.py unchanged but it could be a set here
        keymap = {
            cc.EVENT_CODE: cc._ecode,
            cc.EVENT_NAME: cc._ename,
            cc.EVENT_DATE: cc._edate,
            cc.FINAL_RESULT_DATE: cc._efinaldate,
            cc.PIN: cc._pcode,
            cc.NAME: cc._pname,
            cc.OTHER_RESULTS: cc._mname,
            cc.MATCH_RESULTS: cc._mname,
            cc.SECTION_RESULTS: cc._mname,
            cc.RESULTS_DATE: cc._mdate,
            cc.PIN1: cc._pcode1,
            cc.PIN2: cc._pcode2,
            cc.ROUND: cc._ground,
            cc.BOARD: cc._gboard,
            cc.COLOUR: cc._gcolor,
            cc.SCORE: cc._gresult,
            cc.GAME_DATE: cc._gdate,
            cc.WHITE_ON: cc._mcolor,
            #cc.CLUB:cc._cname, #League program for CLUB NAME
            #cc.CLUB_NAME:cc._cname,
            cc.SURNAME: cc._surname,
            cc.INITIALS: cc._initials,
            cc.FORENAME: cc._forename,
            }

        # validmap copied from merges.py unchanged but it could be a set here
        '''
        validmap accepts a few field sequences that are not accepted by the
        ECF Checker program to simplify spotting field group boundaries and
        presence of invalid fields.
        COLUMN; TABLE END; and TABLE START expanded in get_lines so removed
        from validmap. Appearance in return value indicates a table format
        error.
        '''
        validmap = {
            cc.ADJUDICATED: cc.EVENT_DETAILS,
            cc.BCF_CODE: cc.PIN,
            cc.BCF_NO: cc.PIN,
            cc.BOARD: {
                cc.MATCH_RESULTS: None,
                cc.PIN1: None,
                },
            cc.CLUB: cc.PIN, #League program for CLUB NAME
            cc.CLUB_CODE: cc.PIN,
            cc.CLUB_COUNTY: cc.PIN,
            cc.CLUB_NAME: cc.PIN,
            cc.COLOUR: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                cc.OTHER_RESULTS: None,
                cc.PIN1: None,
                },
            cc.COMMENT: {
                cc.PIN: None,
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                },
            cc.DATE_OF_BIRTH: cc.PIN,
            cc.EVENT_CODE: cc.EVENT_DETAILS,
            cc.EVENT_DATE: cc.EVENT_DETAILS,
            cc.EVENT_DETAILS: None,
            cc.EVENT_NAME: cc.EVENT_DETAILS,
            cc.FIDE_NO: cc.PIN,
            cc.FINAL_RESULT_DATE: cc.EVENT_DETAILS,
            cc.FINISH: None,
            cc.FORENAME: cc.PIN,
            cc.GAME_DATE: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                cc.OTHER_RESULTS: None,
                cc.PIN1: None,
                },
            cc.GENDER: cc.PIN,
            cc.INFORM_CHESSMOVES: cc.EVENT_DETAILS,
            cc.INFORM_FIDE: cc.EVENT_DETAILS,
            cc.INFORM_GRAND_PRIX: cc.EVENT_DETAILS,
            cc.INFORM_UNION: cc.EVENT_DETAILS,
            cc.INITIALS: cc.PIN,
            cc.MATCH_RESULTS: None,
            cc.MINUTES_FIRST_SESSION: cc.EVENT_DETAILS,
            cc.MINUTES_FOR_GAME: cc.EVENT_DETAILS,
            cc.MINUTES_REST_OF_GAME: cc.EVENT_DETAILS,
            cc.MINUTES_SECOND_SESSION: cc.EVENT_DETAILS,
            cc.MOVES_FIRST_SESSION: cc.EVENT_DETAILS,
            cc.MOVES_SECOND_SESSION: cc.EVENT_DETAILS,
            cc.NAME: cc.PIN,
            cc.OTHER_RESULTS: None,
            cc.PIN: {
                cc.PLAYER_LIST: None,
                cc.PIN: None,
                },
            cc.PIN1: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                cc.OTHER_RESULTS: None,
                cc.PIN1: None,
                },
            cc.PIN2: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                cc.OTHER_RESULTS: None,
                cc.PIN1: None,
                },
            cc.PLAYER_LIST: None,
            cc.RESULTS_DATE: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                },
            cc.RESULTS_DUPLICATED: cc.EVENT_DETAILS,
            cc.RESULTS_OFFICER: cc.EVENT_DETAILS,
            cc.RESULTS_OFFICER_ADDRESS: cc.EVENT_DETAILS,
            cc.ROUND: {
                cc.SECTION_RESULTS: None,
                cc.PIN1: None,
                },
            cc.SCORE: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                cc.OTHER_RESULTS: None,
                cc.PIN1: None,
                },
            cc.SECONDS_PER_MOVE: cc.EVENT_DETAILS,
            cc.SECTION_RESULTS: None,
            cc.SUBMISSION_INDEX: cc.EVENT_DETAILS,
            cc.SURNAME: cc.PIN,
            cc.TITLE: cc.PIN,
            cc.TREASURER: cc.EVENT_DETAILS,
            cc.TREASURER_ADDRESS: cc.EVENT_DETAILS,
            cc.WHITE_ON: {
                cc.MATCH_RESULTS: None,
                cc.SECTION_RESULTS: None,
                cc.OTHER_RESULTS: None,
                },
            }

        return super(PrepareSubmissionFile, self).translate_results_format(
            context=context,
            keymap=keymap,
            validmap=validmap,
            pinreadmap={cc.PIN, cc.PIN1, cc.PIN2},
            pinmap={cc.PIN},
            gradingcodemap=set([cc.BCF_CODE],),
            discardmap={cc.CLUB, cc.CLUB_CODE, cc.CLUB_COUNTY, cc.CLUB_NAME,
                 cc.BCF_CODE, cc.BCF_NO, cc.FIDE_NO, cc.DATE_OF_BIRTH},
            )

    def get_lines(self):
        """Delimiter is # optionally preceded by newline sequence."""
        filetext = []

        for f, ft in super(PrepareSubmissionFile, self).get_lines():
            columns = []
            row = []
            table = False
            text = []
            for t in ''.join(ft).split('#'):
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
                    text.append(key)
                else:
                    text.append('='.join((key, value)))
            filetext.append((f, text))
        return filetext

    def report_file(self, file_, text):
        """Return string containing filename and text in file."""
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
        for t in text:
            k = t.split('=', 1)[0]
            if k in start_group:
                if linetext:
                    filetext.append('#'.join(linetext))
                linetext = [t]
                group = True
            elif k in end_group:
                if linetext:
                    filetext.append('#'.join(linetext))
                linetext = []
                filetext.append(t)
                group = False
            elif group:
                linetext.append(t)
            else:
                filetext.append(t)
        if linetext:
            filetext.append('#'.join(linetext))
        linetext = []

        self.filenewtextmap[file_] = '#'.join(('', '\n#'.join(filetext)))
        return '\n'.join((
            ''.join((file_, '\n')),
            self.filenewtextmap[file_],
            ))

    def write_file(self, inpath, outpath, folder):
        d, f = os.path.split(outpath[0])
        nd = os.path.join(folder, d)
        if not os.path.exists(nd):
            os.makedirs(nd)
        nf = open(outpath[0], 'w') # 'wb'?
        try:
            nf.write(self.filenewtextmap[inpath])
            cf = open(os.path.join(nd, cc.TAKEON_ECF_FORMAT), 'w') # 'wb'?
            cf.close()
        finally:
            nf.close()

    @staticmethod
    def generate_file_name(inpath, infolder, outfolder):
        m = os.path.split(inpath[len(infolder) + 1:])
        d = os.path.splitext(m[-1])
        return os.path.join(outfolder, m[0], d[0], m[-1])


class PrepareLeagueDump(PrepareResults):
    """Import data from dump of League program database.
    """

    def __init__(self, container):
        super(PrepareLeagueDump, self).__init__(container)

    def empty_extract(self):
        return super(PrepareLeagueDump, self).empty_extract()

    def translate_results_format(self):

        def copy_player_filter(lines, text, data):
            if cc.PCODE in data:
                if data[cc.PCODE] in self.keeppinvaluemap:
                    lines.extend(text)

        # context copied from merges.py and value part of key:value
        # changed as necessary
        context = {
            cc.represent: None,
            cc.club: None,
            cc.player: copy_player_filter,
            cc.game: True,
            cc.affiliate: None,
            cc.team: True,
            cc.event: True,
            cc.match: True,
            }

        # keymap copied from merges.py unchanged but it could be a set here
        keymap = {
            cc.ECODE: cc._ecode,
            cc.ENAME: cc._ename,
            cc.EDATE: cc._edate,
            cc.EFINALDATE: cc._efinaldate,
            cc.PCODE: cc._pcode,
            cc.PNAME: cc._pname,
            cc.MCODE: cc._mcode,
            cc.MNAME: cc._mname,
            cc.MDATE: cc._mdate,
            cc.PCODE1: cc._pcode1,
            cc.PCODE2: cc._pcode2,
            cc.GCODE: cc._gcode,
            cc.GROUND: cc._ground,
            cc.GBOARD: cc._gboard,
            cc.GCOLOR: cc._gcolor,
            cc.GRESULT: cc._gresult,
            cc.GDATE: cc._gdate,
            cc.MCOLOR: cc._mcolor,
            cc.MTYPE: cc._mtype,
            #cc.CCODE:cc._ccode,
            #cc.CNAME:cc._cname,
            cc.TCODE: cc._tcode,
            cc.TNAME: cc._tname,
            #cc.RPAIRING:cc._rpairing,
            cc.TCODE1: cc._tcode1,
            cc.TCODE2: cc._tcode2,
            cc.PLENFORENAME: cc._plenforename,
            cc.PLENNICKNAME: cc._plennickname,
            }

        # validmap copied from merges.py unchanged but it could be a set here
        validmap = {
            cc.ECODE: {cc.event:None, cc.match:None, cc.affiliate:None},
            cc.ENAME: cc.event,
            cc.EBCF: cc.event,
            cc.EDATE: {cc.event:None, cc.affiliate:None},
            cc.EFINALDATE: cc.event,
            cc.ESUBMISSION: cc.event,
            cc.ETREASURER: cc.event,
            cc.EADDRESS1: cc.event,
            cc.EADDRESS2: cc.event,
            cc.EADDRESS3: cc.event,
            cc.EADDRESS4: cc.event,
            cc.EPOSTCODE: cc.event,
            cc.EGRADER: cc.event,
            cc.EGADDRESS1: cc.event,
            cc.EGADDRESS2: cc.event,
            cc.EGADDRESS3: cc.event,
            cc.EGADDRESS4: cc.event,
            cc.EGPOSTCODE: cc.event,
            cc.EFIRSTMOVES: cc.event,
            cc.EFIRSTMINUTES: cc.event,
            cc.ENEXTMOVES: cc.event,
            cc.ENEXTMINUTES: cc.event,
            cc.ERESTMINUTES: cc.event,
            cc.EALLMINUTES: cc.event,
            cc.ESECPERMOVE: cc.event,
            cc.EADJUDICATED: cc.event,
            cc.EGRANDPRIX: cc.event,
            cc.EFIDE: cc.event,
            cc.ECHESSMOVES: cc.event,
            cc.EEAST: cc.event,
            cc.EMIDLAND: cc.event,
            cc.ENORTH: cc.event,
            cc.ESOUTH: cc.event,
            cc.EWEST: cc.event,
            cc.ECOLOR: cc.event,
            cc.CCODE: {cc.club:None, cc.team:None, cc.affiliate:None},
            cc.CNAME: cc.club,
            cc.CBCF: cc.club,
            cc.CBCFCOUNTY: cc.club,
            cc.PCODE: {cc.player:None, cc.affiliate:None, cc.represent:None},
            cc.PNAME: {cc.player:None, cc.affiliate:None, cc.represent:None},
            cc.PBCF: cc.player,
            cc.PDOB: cc.player,
            cc.PGENDER: cc.player,
            cc.PDIRECT: cc.player,
            cc.PTITLE: cc.player,
            cc.PFIDE: cc.player,
            cc.PLENFORENAME: cc.player,
            cc.PLENNICKNAME: cc.player,
            cc.MCODE: {cc.match:None, cc.game:None},
            cc.MNAME: cc.match,
            cc.MDATE: cc.match,
            cc.MTYPE: cc.match,
            cc.MCOLOR: cc.match,
            cc.MUSEEVENTDATE: cc.match,
            cc.TCODE1: cc.match,
            cc.TCODE2: cc.match,
            cc.GROUND: cc.game,
            cc.GBOARD: cc.game,
            cc.GCODE: cc.game,
            cc.PCODE1: cc.game,
            cc.PCODE2: cc.game,
            cc.GCOLOR: cc.game,
            cc.GRESULT: cc.game,
            cc.GDATE: cc.game,
            cc.GUSEMATCHDATE: cc.game,
            cc.TCODE: {cc.team:None, cc.represent:None},
            cc.TNAME: cc.team,
            cc.RPAIRING: cc.represent,
            cc.represent: None,
            cc.club: None,
            cc.player: None,
            cc.game: None,
            cc.affiliate: None,
            cc.team: None,
            cc.event: None,
            cc.match: None,
            }

        # there may be PCODE values not used as PCODE1 or PCODE2 values
        # the extra translate_results_format call with the copy_lines=False
        # argument allows the excess PCODEs to be lost.
        # PCODE1 and PCODE2 appear before PCODE in dump file. Corresponding
        # fields in submission format are other way round.
        # pinmap argument is PCODE1 and PCODE2 in mergesource.py
        super(PrepareLeagueDump, self).translate_results_format(
            context=context,
            keymap=keymap,
            validmap=validmap,
            pinreadmap={cc.PCODE, cc.PCODE1, cc.PCODE2},
            pinmap={cc.PCODE},
            gradingcodemap={cc.PBCF},
            discardmap={cc.PBCF, cc.CNAME, cc.CBCF, cc.CBCFCOUNTY},
            copy_lines=False,
            )

        return super(PrepareLeagueDump, self).translate_results_format(
            context=context,
            keymap=keymap,
            validmap=validmap,
            pinreadmap={cc.PCODE, cc.PCODE1, cc.PCODE2},
            pinmap={cc.PCODE},
            gradingcodemap={cc.PBCF},
            discardmap={cc.PBCF, cc.CNAME, cc.CBCF, cc.CBCFCOUNTY},
            )

    def report_file(self, file_, text):
        """Return string containing filename and text in file."""
        self.filenewtextmap[file_] = '\n'.join(text)
        return '\n'.join((
            file_,
            '\n',
            self.filenewtextmap[file_],
            ))

    def write_file(self, inpath, outpath, folder):
        d, f = os.path.split(outpath[0])
        nd = os.path.join(folder, d)
        if not os.path.exists(nd):
            os.makedirs(nd)
        nf = open(outpath[0], 'w') # 'wb'?
        try:
            nf.write(self.filenewtextmap[inpath])
            cf = open(os.path.join(nd, cc.TAKEON_LEAGUE_FORMAT), 'w') # 'wb'?
            cf.close()
        finally:
            nf.close()

    @staticmethod
    def generate_file_name(inpath, infolder, outfolder):
        return os.path.join(
            outfolder,
            os.path.splitext(os.path.split(inpath)[-1])[0],
            cc.LEAGUE_DATABASE_DATA)

    def get_folder_contents(self, container):
        self.files.add(container)

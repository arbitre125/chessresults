# upgrade_from_0_33_7_to_0_34.py
# Copyright 2016 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Upgrade record definitions for ECF reference data files.

The ECF reference data files are derived from the ECF Master File available to
graders.  The volume of data on master files, and the frequency of change, has
increased significantly since first produced on CD in 1999.

The significant change is to the master file of players.

In 1999 it contained those players who had played at least one graded game in
the previous three seasons, and was published once a year.

The CD was replaced by a file which could be downloaded around 2007.

By 2010 it contained all players known to have a grading code, and published
once a month.

The reference data files were designed to retain grading codes, even if these
disappeared from later master lists, because the grading code might have been
used to report a result for grading.  Change dates for each grading code were
recorded too.

The combination of old design and recent volume leads to an update run taking
about 2.5 hours.  Tolerable with annual, or even six-monthly, grading; but the
possibility of monthly grading means something must be done.

Change dates are no longer recorded: just whether or not the grading code is
present on the currently loaded master file.  This leads to update runs taking
2 or 3 minutes.

"""

from ast import literal_eval

from solentware_base.core.record import KeyData
from solentware_base.core.record import Value, ValueList, Record
from solentware_base.core.constants import (
    PRIMARY, SECONDARY, DEFER,
    BTOD_FACTOR, DEFAULT_RECORDS, DEFAULT_INCREASE_FACTOR, BTOD_CONSTANT,
    DDNAME, FILE, FOLDER, FIELDS, FILEDESC,
    FLT, INV, UAE, ORD, ONM, SPT, EO, RRN,
    BSIZE, BRECPPG, BRESERVE, BREUSE,
    DSIZE, DRESERVE, DPGSRES, FILEORG,
    DPT_PRIMARY_FIELD_LENGTH,
    )
import solentware_base.core.filespec

from ..core.filespec import (
    ECFPLAYER_FILE_DEF,
    ECFPLAYER_FIELD_DEF,
    ECFPLAYERCODE_FIELD_DEF,
    ECFPLAYERNAME_FIELD_DEF,
    ECFCURRENTPLAYER_FIELD_DEF,
    ECFCURRENTPLAYERCODE_FIELD_DEF,
    ECFCLUB_FILE_DEF,
    ECFCLUB_FIELD_DEF,
    ECFCLUBCODE_FIELD_DEF,
    ECFCLUBNAME_FIELD_DEF,
    ECFCURRENTCLUB_FIELD_DEF,
    ECFCURRENTCLUBCODE_FIELD_DEF,
    )
from ..core import ecfrecord

# The two deleted indexes
ECFPLAYERDATE_FIELD_DEF = 'ECFplayerdate'
ECFCLUBDATE_FIELD_DEF = 'ECFclubdate'

_Old = 'Old'

UPGRADE_FIELDS = (
    ECFPLAYERDATE_FIELD_DEF,
    ECFCLUBDATE_FIELD_DEF,
    ECFPLAYER_FIELD_DEF,
    ECFPLAYERCODE_FIELD_DEF,
    ECFPLAYERNAME_FIELD_DEF,
    ECFCURRENTPLAYER_FIELD_DEF,
    ECFCURRENTPLAYERCODE_FIELD_DEF,
    ECFCLUB_FIELD_DEF,
    ECFCLUBCODE_FIELD_DEF,
    ECFCLUBNAME_FIELD_DEF,
    ECFCURRENTCLUB_FIELD_DEF,
    ECFCURRENTCLUBCODE_FIELD_DEF,
    )


class FileSpec(solentware_base.core.filespec.FileSpec):

    """Specify the parts of the results database being upgraded.

    Methods added:

    None
    
    Methods overridden:

    None
    
    Methods extended:

    __init__

    """

    def __init__(self, use_specification_items=None, dpt_records=None, **kargs):

        dptfn = FileSpec.dpt_dsn
        fn = FileSpec.field_name
        
        super(FileSpec, self).__init__(
            use_specification_items=use_specification_items,
            dpt_records=dpt_records,
            **{
                ECFPLAYER_FILE_DEF: {
                    DDNAME: 'ECFPLAYR',
                    FILE: dptfn(ECFPLAYER_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 75,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 1.0,
                    BTOD_CONSTANT: 100,
                    DEFAULT_RECORDS: 15000,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(ECFPLAYER_FIELD_DEF),
                    SECONDARY: {
                        ECFPLAYERCODE_FIELD_DEF: None,
                        ECFPLAYERNAME_FIELD_DEF: None,
                        ECFPLAYERDATE_FIELD_DEF: None,
                        ECFCURRENTPLAYER_FIELD_DEF: None,
                        ECFCURRENTPLAYERCODE_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(ECFPLAYER_FIELD_DEF): None,
                        fn(ECFPLAYERCODE_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFPLAYERNAME_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFPLAYERDATE_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFCURRENTPLAYER_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFCURRENTPLAYERCODE_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                ECFCLUB_FILE_DEF: {
                    DDNAME: 'ECFCLUB',
                    FILE: dptfn(ECFCLUB_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 100,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 1.5,
                    BTOD_CONSTANT: 50,
                    DEFAULT_RECORDS: 5000,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(ECFCLUB_FIELD_DEF),
                    SECONDARY: {
                        ECFCLUBCODE_FIELD_DEF: None,
                        ECFCLUBNAME_FIELD_DEF: None,
                        ECFCLUBDATE_FIELD_DEF: None,
                        ECFCURRENTCLUB_FIELD_DEF: None,
                        ECFCURRENTCLUBCODE_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(ECFCLUB_FIELD_DEF): None,
                        fn(ECFCLUBCODE_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFCLUBNAME_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFCLUBDATE_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFCURRENTCLUB_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFCURRENTCLUBCODE_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                }
            )


class ECFrefDBkeyECFclub(KeyData):

    """Primary key of club from ECF

    Methods added:

    None
    
    Methods overridden:

    None
    
    Methods extended:

    None

    """

    pass
        

class ECFrefDBvalueECFclub(Value):

    """Club data from ECF

    Methods added:

    calculate_ecf_active_club
    
    Methods overridden:

    load
    pack_value
    
    Methods extended:

    __init__
    pack

    """

    def __init__(self):

        super(ECFrefDBvalueECFclub, self).__init__()
        self.ECFcode = None
        self.ECFactivecode = None
        self.ECFactivename = None
        self.ECFtxns = dict()

    def load(self, value):
        """Override, extract ECF club data from value into attributes."""
        (self.ECFcode,
         self.ECFactivecode,
         self.ECFactivename,
         txns) = literal_eval(value)
        self.ECFtxns = dict()
        for t in txns:
            date, name, txntype, countycode = t
            self.ECFtxns[date] = dict(name=name,
                                      txntype=txntype,
                                      countycode=countycode)
        
    def pack(self):
        """Extend, return ECF club record and index data."""
        v = super(ECFrefDBvalueECFclub, self).pack()
        index = v[1]
        if self.ECFactivename:
            index[ECFCURRENTCLUB_FIELD_DEF] = [self.ECFactivename]
        if self.ECFactivecode:
            index[ECFCURRENTCLUBCODE_FIELD_DEF] = [self.ECFactivecode]
        index[ECFCLUBCODE_FIELD_DEF] = [self.ECFcode]
        cn = index[ECFCLUBNAME_FIELD_DEF] = []
        cnd = dict()
        cd = index[ECFCLUBDATE_FIELD_DEF] = []
        for date in self.ECFtxns:
            cd.append(date)
            cnd[self.ECFtxns[date]['name']] = None
        for n in cnd:
            cn.append(n)
        return v
        
    def pack_value(self, *a):
        """Override, return tuple of self attributes."""
        txns = self.ECFtxns
        p = []
        for d in txns:
            t = txns[d]
            q = (d, t.get('name'), t.get('txntype'), t.get('countycode'))
            p.append(q)
        return repr((self.ECFcode, self.ECFactivecode, self.ECFactivename, p))

    def calculate_ecf_active_club(self):
        """Calculate the active ECF club name for ECF club code."""
        mrc = ECFrefDBrecordECFdate.most_recent_club_master_file_date
        ECFtxndates = sorted(list(self.ECFtxns.keys()))
        mrtxn = ECFtxndates[-1]
        if mrc is not None:
            if mrc > mrtxn:
                self.ECFactivename = None
                self.ECFactivecode = None
                return
            elif mrc == mrtxn:
                self.ECFactivename = self.ECFtxns[mrtxn]['name']
                self.ECFactivecode = self.ECFcode
                return
        if self.ECFtxns[mrtxn]['txntype'] != _Old:
            self.ECFactivename = self.ECFtxns[mrtxn]['name']
            self.ECFactivecode = self.ECFcode
        else:
            self.ECFactivename = None
            self.ECFactivecode = None
        

class ECFrefDBrecordECFclub(Record):

    """Club record from ECF

    Methods added:

    None
    
    Methods overridden:

    None
    
    Methods extended:

    __init__

    """

    def __init__(self,
                 keyclass=ECFrefDBkeyECFclub,
                 valueclass=ECFrefDBvalueECFclub):

        super(ECFrefDBrecordECFclub, self).__init__(
            keyclass,
            valueclass)


class ECFrefDBkeyECFplayer(KeyData):

    """Primary key of player from ECF

    Methods added:

    None
    
    Methods overridden:

    None
    
    Methods extended:

    None

    """

    pass
        

class ECFrefDBvalueECFplayer(Value):

    """Player data from ECF

    Methods added:

    calculate_ecf_active_player
    
    Methods overridden:

    load
    pack_value
    
    Methods extended:

    __init__
    pack

    """

    def __init__(self):

        super(ECFrefDBvalueECFplayer, self).__init__()
        self.ECFcode = None
        self.ECFactivecode = None
        self.ECFactivename = None
        self.ECFtxns = dict()
        self.ECFmerge = None

    def load(self, value):
        """Override, extract ECF player data from value into attributes."""
        (self.ECFcode,
         self.ECFactivecode,
         self.ECFactivename,
         txns,
         self.ECFmerge,
         ) = literal_eval(value)
        self.ECFtxns = dict()
        for t in txns:
            date, name, txntype, clubcodes = t
            self.ECFtxns[date] = dict(name=name,
                                      txntype=txntype,
                                      clubcodes=clubcodes)

    def pack(self):
        """Extend, return ECF player record and index data."""
        v = super(ECFrefDBvalueECFplayer, self).pack()
        index = v[1]
        if self.ECFactivename:
            index[ECFCURRENTPLAYER_FIELD_DEF] = [self.ECFactivename]
        if self.ECFactivecode:
            index[ECFCURRENTPLAYERCODE_FIELD_DEF] = [self.ECFactivecode]
        index[ECFPLAYERCODE_FIELD_DEF] = [self.ECFcode]
        cn = index[ECFPLAYERNAME_FIELD_DEF] = []
        cnd = dict()
        cd = index[ECFPLAYERDATE_FIELD_DEF] = []
        for date in self.ECFtxns:
            cd.append(date)
            cnd[self.ECFtxns[date]['name']] = None
        for n in cnd:
            cn.append(n)
        return v

    def pack_value(self, *a):
        """Override, return tuple of self attributes."""
        txns = self.ECFtxns
        p = []
        for d in txns:
            t = txns[d]
            q = (d, t.get('name'), t.get('txntype'), t.get('clubcodes'))
            p.append(q)
        return repr((
            self.ECFcode,
            self.ECFactivecode,
            self.ECFactivename,
            p,
            self.ECFmerge))
        
    def calculate_ecf_active_player(self):
        """Calculate the active ECF player name for ECF grading code."""
        mrp = ECFrefDBrecordECFdate.most_recent_player_master_file_date
        ECFtxndates = sorted(list(self.ECFtxns.keys()))
        mrtxn = ECFtxndates[-1]
        if mrp is not None:
            if mrp > mrtxn:
                self.ECFactivename = None
                self.ECFactivecode = None
                return
            elif mrp == mrtxn:
                self.ECFactivename = self.ECFtxns[mrtxn]['name']
                self.ECFactivecode = self.ECFcode
                return
        if self.ECFtxns[mrtxn]['txntype'] != _Old:
            self.ECFactivename = self.ECFtxns[mrtxn]['name']
            self.ECFactivecode = self.ECFcode
        else:
            self.ECFactivename = None
            self.ECFactivecode = None
        

class ECFrefDBrecordECFplayer(Record):

    """Player record from ECF

    Methods added:

    None
    
    Methods overridden:

    None
    
    Methods extended:

    __init__

    """

    def __init__(self,
                 keyclass=ECFrefDBkeyECFplayer,
                 valueclass=ECFrefDBvalueECFplayer):

        super(ECFrefDBrecordECFplayer, self).__init__(
            keyclass,
            valueclass)


def do_upgrade(database):
    """Replace dated names and ECF codes with current flag in ECF data extract.

    Caller is responsible for checking it is valid to run this function using
    database engine specific code.

    """
    database.open_database()
    database.start_transaction()

    players = database.database_cursor(ECFPLAYER_FILE_DEF, ECFPLAYER_FIELD_DEF)
    data = players.first()
    while data:
        record = ECFrefDBrecordECFplayer()
        newrecord = ecfrecord.ECFrefDBrecordECFplayer()
        record.load_instance(
            database, ECFPLAYER_FILE_DEF, ECFPLAYER_FIELD_DEF, data)
        nrv = newrecord.value
        rv = record.value
        txn = sorted(rv.ECFtxns.items())[-1][-1]
        nrv.ECFactive = True if rv.ECFactivecode else None
        nrv.ECFmerge = rv.ECFmerge
        nrv.ECFcode = rv.ECFcode
        nrv.ECFname = txn['name']
        nrv.ECFclubcodes = txn['clubcodes']
        newrecord.key.recno = record.key.recno
        record.edit_record(
            database, ECFPLAYER_FILE_DEF, ECFPLAYER_FIELD_DEF, newrecord)
        data = players.next()
    players.close()
    
    clubs = database.database_cursor(ECFCLUB_FILE_DEF, ECFCLUB_FIELD_DEF)
    data = clubs.first()
    while data:
        record = ECFrefDBrecordECFclub()
        newrecord = ecfrecord.ECFrefDBrecordECFclub()
        record.load_instance(
            database, ECFCLUB_FILE_DEF, ECFCLUB_FIELD_DEF, data)
        nrv = newrecord.value
        rv = record.value
        txn = sorted(rv.ECFtxns.items())[-1][-1]
        nrv.ECFactive = True if rv.ECFactivecode else None
        nrv.ECFcode = rv.ECFcode
        nrv.ECFname = txn['name']
        nrv.ECFcountycode = txn['countycode']
        newrecord.key.recno = record.key.recno
        record.edit_record(
            database, ECFCLUB_FILE_DEF, ECFCLUB_FIELD_DEF, newrecord)
        data = clubs.next()
    clubs.close()

    database.commit()
    database.close_database()

# oldrecords_0_23.py
# Copyright 2010 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Record definitions for databases created by results-0-23 and earlier but
later than results-0-10.
        
These classes are provided to allow upgrade of databases to latest version
of record definition.

Changes that appear in next version are addition of attributes:

clubecfcode
clubecfname

to ECFmapDBvalueClub class

ECFmerge

to ECFrefDBvalueECFplayer class

"""

from solentware_base.core.record import KeyData
from solentware_base.core.record import Value, ValueList, Record

from . import filespec


class ECFmapDBkeyClub(KeyData):

    """Primary key of club data for player in event.
    """
    
    pass


class ECFmapDBvalueClub(ValueList):

    """ECF club for player in event.
    """

    attributes = dict(playerkey=None,
                      playername=None,
                      clubcode=None,
                      )
    _attribute_order = tuple(sorted(attributes.keys()))

    def pack(self):
        """Extend, return player to ECF club record and index data."""
        v = super(ECFmapDBvalueClub, self).pack()
        index = v[1]
        index[filespec.PLAYERALIASID_FIELD_DEF] = [self.playerkey]
        if self.clubcode is None:
            index[filespec.PLAYERALIASMAP_FIELD_DEF] = [self.playername]
        elif self.clubcode is False:
            pass
        else:
            index[filespec.CLUBCODE_FIELD_DEF] = [self.clubcode]
        return v


class ECFmapDBrecordClub(Record):

    """Player in event associated with ECF club.

    For each ResultsDBrecordPlayer record there are 0 or 1
    ECFmapDBrecordClub records.

    """

    def __init__(self,
                 keyclass=ECFmapDBkeyClub,
                 valueclass=ECFmapDBvalueClub):

        super(ECFmapDBrecordClub, self).__init__(
            keyclass,
            valueclass)

    def empty(self):
        """(Re)Initialize value attribute."""
        self.value.playerkey = ''
        self.value.playername = ''
        self.value.clubcode = None
        

class ECFrefDBkeyECFplayer(KeyData):

    """Primary key of player from ECF.
    """

    pass
        

class ECFrefDBvalueECFplayer(Value):

    """Player data from ECF.
    """

    def __init__(self):

        super(ECFrefDBvalueECFplayer, self).__init__()
        self.ECFcode = None
        self.ECFactivecode = None
        self.ECFactivename = None
        self.ECFtxns = dict()

    def load(self, value):
        """Override, extract ECF player data from value into attributes."""
        self.ECFcode, self.ECFactivecode, self.ECFactivename, txns = value
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
            index[filespec.ECFCURRENTPLAYER_FIELD_DEF] = [self.ECFactivename]
        if self.ECFactivecode:
            index[filespec.ECFCURRENTPLAYERCODE_FIELD_DEF] = [
                self.ECFactivecode]
        index[filespec.ECFPLAYERCODE_FIELD_DEF] = [self.ECFcode]
        cn = index[filespec.ECFPLAYERNAME_FIELD_DEF] = []
        cnd = dict()
        cd = index[filespec.ECFPLAYERDATE_FIELD_DEF] = []
        for date in self.ECFtxns:
            cd.append(date)
            cnd[self.ECFtxns[date]['name']] = None
        for n in cnd:
            cn.append(n)
        return v

    def pack_value(self):
        """Override, return tuple of self attributes."""
        txns = self.ECFtxns
        p = []
        for d in txns:
            t = txns[d]
            q = (d, t.get('name'), t.get('txntype'), t.get('clubcodes'))
            p.append(q)
        return (self.ECFcode, self.ECFactivecode, self.ECFactivename, p)
        
    def calculate_ecf_active_player(self):
        """Calculate the active ECF player name for ECF grading code."""
        mrp = ECFrefDBrecordECFdate.most_recent_player_master_file_date
        ECFtxndates = sorted(list(self.ECFtxns.keys()))
        mrtxn = ECFtxndates[-1]
        if mrp > mrtxn:
            self.ECFactivename = None
            self.ECFactivecode = None
        elif mrp == mrtxn:
            self.ECFactivename = self.ECFtxns[mrtxn]['name']
            self.ECFactivecode = self.ECFcode
        elif self.ECFtxns[mrtxn]['txntype'] != _Old:
            self.ECFactivename = self.ECFtxns[mrtxn]['name']
            self.ECFactivecode = self.ECFcode
        else:
            self.ECFactivename = None
            self.ECFactivecode = None
        

class ECFrefDBrecordECFplayer(Record):

    """Player record from ECF.
    """

    def __init__(self,
                 keyclass=ECFrefDBkeyECFplayer,
                 valueclass=ECFrefDBvalueECFplayer):

        super(ECFrefDBrecordECFplayer, self).__init__(
            keyclass,
            valueclass)

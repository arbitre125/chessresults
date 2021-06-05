# oldrecords_0_24.py
# Copyright 2012 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Record definitions for databases created by results-0-25 and earlier but
later than results-0-23.
        
These classes are provided to allow upgrade of databases to latest version
of record definition.

Changes that appear in next version are addition of attributes:

clubecfcode
clubecfname

to ECFmapDBvalueClub class

ECFmerge

to ECFrefDBvalueECFplayer class

"""

from pickle import dumps

from solentware_base.core.record import KeyData
from solentware_base.core.record import Value, ValueList, Record

from . import filespec


class ResultsDBkeyEvent(KeyData):
    
    """Primary key of event.
    """

    pass
        

class ResultsDBvalueEvent(Value):
    
    """Event data.
    """

    def __init__(self):

        super(ResultsDBvalueEvent, self).__init__()
        self.name = None
        self.startdate = None
        self.enddate = None
        self.sections = [] # section codes : Name record for name

    def get_event_identity(self):
        """Return tab separated event identity."""
        return b'\t'.join((
            self.name,
            self.startdate,
            self.enddate))

    def pack(self):
        """Extend, return event record and index data."""
        v = super(ResultsDBvalueEvent, self).pack()
        index = v[1]
        index[filespec.EVENTNAME_FIELD_DEF] = [self.name]
        index[filespec.STARTDATE_FIELD_DEF] = [self.startdate]
        index[filespec.ENDDATE_FIELD_DEF] = [self.enddate]
        index[filespec.EVENTIDENTITY_FIELD_DEF] = [self.get_event_identity()]
        return v


class ResultsDBrecordEvent(Record):
    
    """Event record.
    """

    def __init__(self,
                 keyclass=ResultsDBkeyEvent,
                 valueclass=ResultsDBvalueEvent):

        super(ResultsDBrecordEvent, self).__init__(
            keyclass,
            valueclass)

    def get_keys(self, datasource=None, partial=None):
        """Override, return [(key, value), ...] by partial key in datasource."""
        try:
            if partial != None:
                return []

            srkey = datasource.dbhome.get_packed_key(datasource.dbset, self)

            if datasource.primary:
                return [(srkey, self.srvalue)]
            else:
                dbname = datasource.dbname
                if dbname == filespec.EVENTNAME_FIELD_DEF:
                    return [(self.value.eventname, srkey)]
                elif dbname == filespec.STARTDATE_FIELD_DEF:
                    return [(self.value.startdate, srkey)]
                elif dbname == filespec.ENDDATE_FIELD_DEF:
                    return [(self.value.enddate, srkey)]
                elif dbname == filespec.EVENTIDENTITY_FIELD_DEF:
                    return [(self.value.get_event_identity(), srkey)]
                else:
                    return []
        except:
            return []

        
class ResultsDBkeyPlayer(KeyData):

    """Primary key of player.
    """

    pass
        

class ResultsDBvaluePlayer(ValueList):

    """Player data.
    """

    attributes = dict(
        name=None,
        event=None,
        section=None,
        pin=None,
        affiliation=None,
        alias=None,
        merge=None,
        )
    _attribute_order = tuple(sorted(attributes.keys()))

    def __init__(self):

        super(ResultsDBvaluePlayer, self).__init__()
        self.name = None
        self.event = None
        self.section = None
        self.pin = None
        self.affiliation = None # (ecf club)
        self.alias = [] # event startdate endate pin are equal, implies merge
        self.merge = None # cannot break merge if in alias as well

    def empty(self):
        """(Re)Initialize value attribute."""
        self.name = None
        self.event = None
        self.section = None
        self.pin = None
        self.affiliation = None
        self.alias = []
        self.merge = None
            
    def get_alias_list(self):
        """Return list of aliases for this record.

        None False and True mean this record is an alias, merge is an integer,
        so there are no aliases for this record. Value is that of merge in the
        aliased record.
        
        """
        if self.alias is None:
            return []
        elif self.alias is False:
            return []
        elif self.alias is True:
            return []
        return self.alias

    def identity(self):
        """Return tab separated player identity."""
        return b'\t'.join((
            self.name,
            dumps((self.event, self.section, self.pin))))

    def pack(self):
        """Generate player record and index data.

        Notes

        merge is None: local unidentified player
        merge is True: imported unidentified player
        merge is False: identified player
        merge is an integer: link to a merge is None True or False player

        alias is a list: merge is None True or False
        alias is None: merge is reference to player with merge is None
        alias is True: merge is reference to player with merge is True
        alias is False: merge is reference to player with merge is False

        """
        v = super(ResultsDBvaluePlayer, self).pack()
        index = v[1]
        identity = self.identity()
        index[filespec.PLAYERALIAS_FIELD_DEF] = [identity]
        if self.merge is None:
            name = AppSysPersonName(self.name)
            index[filespec.PLAYERNAMENEW_FIELD_DEF] = [name.name]
            index[filespec.PLAYERNEW_FIELD_DEF] = [identity]
        elif self.merge is True:
            name = AppSysPersonName(self.name)
            index[filespec.PLAYERNAMENEW_FIELD_DEF] = [name.name]
            index[filespec.PLAYERNEW_FIELD_DEF] = [identity]
        else:
            name = AppSysPersonNameParts(self.name)
            index[filespec.PLAYERPARTIALNAME_FIELD_DEF] = [
                pn for pn in name.partialnames]
            if self.merge is False:
                index[filespec.PLAYERIDENTITY_FIELD_DEF] = [identity]
                index[filespec.PLAYERNAMEIDENTITY_FIELD_DEF] = [name.name]
                index[filespec.PLAYERNAME_FIELD_DEF] = [name.name]
            elif self.alias is False:
                index[filespec.PLAYERNAME_FIELD_DEF] = [name.name]
            else:
                index[filespec.PLAYERNAMENEW_FIELD_DEF] = [name.name]
        return v


class ResultsDBrecordPlayer(Record):

    """Player record.
    """

    #handle changes to related records when alias and merge modified by
    #overriding Record methods delete_record edit_record put_record?

    def __init__(self,
                 keyclass=ResultsDBkeyPlayer,
                 valueclass=ResultsDBvaluePlayer):

        super(ResultsDBrecordPlayer, self).__init__(
            keyclass,
            valueclass)

    def get_keys(self, datasource=None, partial=None):
        """Override, return [(key, value), ...] by partial key in datasource."""
        try:
            if partial != None:
                return []
            srkey = datasource.dbhome.get_packed_key(datasource.dbset, self)
            if datasource.primary:
                return [(srkey, self.srvalue)]
            dbname = datasource.dbname
            if dbname == filespec.PLAYERALIAS_FIELD_DEF:
                return [(self.value.identity(), srkey)]
            elif dbname == filespec.PLAYERNEW_FIELD_DEF:
                if self.value.merge is None:
                    return [(self.value.identity(), srkey)]
                elif self.value.merge is True:
                    return [(self.value.identity(), srkey)]
            elif dbname == filespec.PLAYERIDENTITY_FIELD_DEF:
                if self.value.merge is False:
                    return [(self.value.identity(), srkey)]
            elif dbname == filespec.PLAYERNAMEIDENTITY_FIELD_DEF:
                if self.value.merge is False:
                    return [(AppSysPersonName(self.value.name).name, srkey)]
            elif dbname == filespec.PLAYERNAME_FIELD_DEF:
                if self.merge is None:
                    return []
                elif self.merge is True:
                    return []
                elif self.merge is False:
                    return [(AppSysPersonName(self.value.name).name, srkey)]
                elif self.alias is False:
                    return [(AppSysPersonName(self.value.name).name, srkey)]
            elif dbname == filespec.PLAYERNAMENEW_FIELD_DEF:
                if self.value.merge is None:
                    return [(AppSysPersonName(self.value.name).name, srkey)]
                elif self.value.merge is True:
                    return [(AppSysPersonName(self.value.name).name, srkey)]
                elif self.value.merge is not False:
                    if self.alias is not False:
                        return [(AppSysPersonName(self.value.name).name, srkey)]
            elif dbname == filespec.PLAYERPARTIALNAME_FIELD_DEF:
                if self.merge is None:
                    return []
                elif self.merge is True:
                    return []
                else:
                    return [(k, srkey) for k in AppSysPersonNameParts(
                        self.value.name).partialnames]
            return []
        except:
            return []


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
                      clubecfname=None,
                      clubecfcode=None,
                      )
    _attribute_order = (
        'clubcode', #ecf club code from ecf club file
        'playerkey', # internal key for player on current database
        'playername', # name reported on results input
        'clubecfname', #ecf club name entered for new club
        'clubecfcode', #ecf club code entered for new club
        )

    def empty(self):
        """(Re)Initialize value attribute."""
        self.playerkey = b''
        self.playername = b''
        self.clubcode = None
        self.clubecfname = None
        self.clubecfcode = None
        
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

        
class ECFmapDBkeyPlayer(KeyData):

    """Primary key of player.
    """

    pass
        

class ECFmapDBvaluePlayer(ValueList):

    """ECF name and grading code for player in event.
    """

    attributes = dict(playerkey=None,
                      playername=None,
                      playercode=None,
                      playerecfname=None,
                      playerecfcode=None,
                      )
    _attribute_order = (
        'playercode', #ecf grading code from ecf master file
        'playerkey', # internal key for player on current database
        'playername', # name reported on results input
        'playerecfname', #ecf version of name entered for new player
        'playerecfcode', #ecf grading code for new player from feedback
        )

    def empty(self):
        """(Re)Initialize value attribute."""
        self.playerkey = b''
        self.playername = b''
        self.playercode = None
        self.playerecfname = None
        self.playerecfcode = None
    
    def pack(self):
        """Extend, return player to ECF grading code record and index data."""
        v = super(ECFmapDBvaluePlayer, self).pack()
        index = v[1]
        index[filespec.PERSONID_FIELD_DEF] = [self.playerkey]
        if self.playercode is None:
            index[filespec.PERSONMAP_FIELD_DEF] = [self.playername]
        else:
            index[filespec.PERSONCODE_FIELD_DEF] = [self.playercode]
            if self.playerecfcode is not None:
                index[filespec.PERSONMAP_FIELD_DEF] = [self.playername]
        return v


class ECFmapDBrecordPlayer(Record):
    """Player in event linked to ECF name and grading code.

    For each ResultsDBrecordPlayer record where merge is False
    there are 0 or 1 ECFmapDBrecordPlayer records.
    The merge and alias attributes of other ResultsDBrecordPlayer
    instances may imply a link to this record.

    """

    def __init__(self,
                 keyclass=ECFmapDBkeyPlayer,
                 valueclass=ECFmapDBvaluePlayer):

        super(ECFmapDBrecordPlayer, self).__init__(
            keyclass,
            valueclass)


class ECFmapOGDkeyPlayer(KeyData):

    """Primary key of player.
    """

    pass
        

class ECFmapOGDvaluePlayer(ValueList):

    """ECF name and grading code for player in event.
    """

    attributes = dict(playerkey=None,
                      playercode=None,
                      )
    _attribute_order = (
        'playercode', #ecf grading code from ecf online grading database
        'playerkey', # internal key for player on current database
        )

    def empty(self):
        """(Re)Initialize value attribute."""
        self.playerkey = b''
        #self.playername = b''
        self.playercode = None
        #self.ecfname = b''
            
    def pack(self):
        """Extend, return player to ECF grading code record and index data."""
        v = super(ECFmapOGDvaluePlayer, self).pack()
        index = v[1]
        index[filespec.OGDPERSONID_FIELD_DEF] = [self.playerkey]
        index[filespec.OGDPERSONCODE_FIELD_DEF] = [self.playercode]
        return v


class ECFmapOGDrecordPlayer(Record):
    """Player in event linked to ECF grading code.

    For each ResultsDBrecordPlayer record where merge is False
    there are 0 or 1 ECFmapOGDrecordPlayer records.
    The merge and alias attributes of other ResultsDBrecordPlayer
    instances may imply a link to this record.

    """

    def __init__(self,
                 keyclass=ECFmapOGDkeyPlayer,
                 valueclass=ECFmapOGDvaluePlayer):

        super(ECFmapOGDrecordPlayer, self).__init__(
            keyclass,
            valueclass)

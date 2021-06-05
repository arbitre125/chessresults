# oldrecords_0_10.py
# Copyright 2010 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Record definitions for databases created by results-0-10 and earlier but
later than results-0-4.
        
These classes are provided to allow upgrade of databases to latest version
of record definition.

Changes that appear in next version are addition of indexes:

playername
playerpartialname
playernamenew
playernameidentity

to ResultsDBrecordValue class

and removal of indexes:

personname from ECFmapDBrecordPlayer
playeraliasname from ECFmapDBrecordClub

"""

from pickle import dumps

from solentware_base.core.record import KeyData
from solentware_base.core.record import Value, ValueList, Record

from . import filespec

#see note in ResultsDBrecordPlayer about possible modification


class ResultsDBkeyEvent(KeyData):
    
    """Primary key of event.
    """

    pass
        

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

        """
        v = super(ResultsDBvaluePlayer, self).pack()
        index = v[1]
        identity = self.identity()
        index[filespec.PLAYERALIAS_FIELD_DEF] = [identity]
        if self.merge is None:
            index[filespec.PLAYERNEW_FIELD_DEF] = [identity]
        elif self.merge is True:
            index[filespec.PLAYERNEW_FIELD_DEF] = [identity]
        elif self.merge is False:
            index[filespec.PLAYERIDENTITY_FIELD_DEF] = [identity]
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

    def empty(self):
        """(Re)Initialize value attribute."""
        self.value.name = None
        self.value.event = None
        self.value.section = None
        self.value.pin = None
        self.value.affiliation = None
        self.value.alias = []
        self.value.merge = None
            
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
                return []
        except:
            return []

        
class FileSpec(filespec.FileSpec):

    """Specify the results database.
    """

    def __init__(self, **kargs):
        """Modify database specification to results-0-10 version."""

        super(FileSpec, self).__init__(**kargs)

        del self['ECFOGDplayer']
        del self['mapECFOGDplayer']
        self['mapECFclub'][filespec.SECONDARY].update({'playeraliasname':None})
        self['mapECFclub'][filespec.FIELDS].update({'Playeraliasname':{
            filespec.INV:True, filespec.ORD:True}})
        self['mapECFplayer'][filespec.SECONDARY].update({'personname':None})
        self['mapECFplayer'][filespec.FIELDS].update({'Personname':{
            filespec.INV:True, filespec.ORD:True}})
        del self['player'][filespec.SECONDARY]['playername']
        del self['player'][filespec.FIELDS]['Playername']
        del self['player'][filespec.SECONDARY]['playerpartialname']
        del self['player'][filespec.FIELDS]['Playerpartialname']
        del self['player'][filespec.SECONDARY]['playernamenew']
        del self['player'][filespec.FIELDS]['Playernamenew']
        del self['player'][filespec.SECONDARY]['playernameidentity']
        del self['player'][filespec.FIELDS]['Playernameidentity']

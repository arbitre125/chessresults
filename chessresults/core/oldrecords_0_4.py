# oldrecords_0_4.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Record definitions for databases created by results-0-4 and earlier.

These classes are provided to allow upgrade of databases to latest version
of record definition.

Changes that appear in next version are
from:
class ResultsDBvalueName(Value):
to:
class ResultsDBvalueName(ValueList):
from:
class ResultsDBvaluePlayer(Value):
to:
class ResultsDBvaluePlayer(ValueList):

and consequential changes.

"""

from pickle import dumps

from solentware_base.core.record import KeyData
from solentware_base.core.record import Value, ValueList, Record

from . import filespec

#see note in ResultsDBrecordPlayer about possible modification


class ResultsDBkeyName(KeyData):

    """Primary key of name.
    """
    
    pass


class ResultsDBvalueName(Value):

    """Name data.

    Any value, usually used as a name, can be put on a name record and the
    key stored on the main record rather than the name. User must ensure
    that reference_count is adjusted as required.

    """

    def __init__(self):

        super(ResultsDBvalueName, self).__init__()
        self.name = None
        self.reference_count = None

    def pack(self):
        """Return name record and index data."""
        v = super(ResultsDBvalueName, self).pack()
        index = v[1]
        index[filespec.NAMETEXT_FIELD_DEF] = self.name
        return v


class ResultsDBrecordName(Record):

    """Name record. A lookup for text used many times in other records.
    """

    def __init__(self,
                 keyclass=ResultsDBkeyName,
                 valueclass=ResultsDBvalueName):

        super(ResultsDBrecordName, self).__init__(
            keyclass,
            valueclass)

    def empty(self):
        """(Re)Initialize value attribute."""
        self.value.name = ''
        self.value.reference_count = ''
        
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
                if dbname == filespec.NAMETEXT_FIELD_DEF:
                    return [(self.value.name, srkey)]
                else:
                    return []
        except:
            return []

        
class ResultsDBkeyPlayer(KeyData):

    """Primary key of player.
    """

    pass
        

class ResultsDBvaluePlayer(Value):

    """Player data.
    """

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
        """Return player record and index data."""
        v = super(ResultsDBvaluePlayer, self).pack()
        index = v[1]
        identity = self.identity()
        index[filespec.PLAYERALIAS_FIELD_DEF] = identity
        if len(self.alias) == 0 and self.merge is None:
            index[filespec.PLAYERNEW_FIELD_DEF] = identity
        elif len(self.alias) or self.merge is False:
            index[filespec.PLAYERIDENTITY_FIELD_DEF] = identity
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
                    if len(self.value.alias) == 0 and self.value.merge is None:
                        return [(self.value.identity(), srkey)]
                elif dbname == filespec.PLAYERIDENTITY_FIELD_DEF:
                    if len(self.value.alias) or self.value.merge is False:
                        return [(self.value.identity(), srkey)]
                return []
        except:
            return []

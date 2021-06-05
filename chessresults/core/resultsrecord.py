# resultsrecord.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Record definition classes for chess results data.
"""

from ast import literal_eval

from solentware_base.core.record import KeyData
from solentware_base.core.record import Value, ValueList, Record

from solentware_misc.api.utilities import (AppSysPersonNameParts,
                                           AppSysPersonName)
# Hack while some non-ISO format dates survive on game records
from solentware_misc.api.utilities import AppSysDate

from . import filespec
from .gameresults import ecfresult, awin, draw, hwin

#see note in ResultsDBrecordPlayer about possible modification


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
        return (
            self.name,
            self.startdate,
            self.enddate)

    def pack(self):
        """Extend, return event record and index data."""
        v = super(ResultsDBvalueEvent, self).pack()
        index = v[1]
        index[filespec.EVENTNAME_FIELD_DEF] = [self.name]
        index[filespec.STARTDATE_FIELD_DEF] = [self.startdate]
        index[filespec.ENDDATE_FIELD_DEF] = [self.enddate]
        index[filespec.EVENTIDENTITY_FIELD_DEF
              ] = [repr(self.get_event_identity())]
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

            srkey = datasource.dbhome.encode_record_number(self.key.pack())

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
                    #return [(self.value.get_event_identity(), srkey)]
                    return [(repr(self.value.get_event_identity()), srkey)]
                else:
                    return []
        except:
            return []

        
class ResultsDBkeyGame(KeyData):

    """Primary key of game.
    """

    pass
        

class ResultsDBvalueGame(ValueList):
    
    """Game data.
    """

    attributes = dict(
        homeplayer=None,
        awayplayer=None,
        result=None,
        date=None,
        homeplayerwhite=None,
        board=None,
        round=None,
        event=None,
        section=None,
        hometeam=None,
        awayteam=None,
        )
    _attribute_order = tuple(sorted(attributes.keys()))

    def pack(self):
        """Extend, return game record and index data."""
        v = super(ResultsDBvalueGame, self).pack()
        index = v[1]
        index[filespec.GAMEEVENT_FIELD_DEF] = [repr(self.event)]
        index[filespec.GAMEPLAYER_FIELD_DEF] = [
            repr(self.homeplayer), repr(self.awayplayer)]
        index[filespec.GAMESECTION_FIELD_DEF] = [
            repr((self.event, self.section))]
        index[filespec.GAMEDATE_FIELD_DEF] = [self.date]
        return v

    def __eq__(self, other):
        """Return True if attributes of self and other are same."""
        s = self.__dict__
        o = other.__dict__
        if len(s) != len(o):
            return False
        for i in s:
            if i not in o:
                return False
            if not isinstance(s[i], type(o[i])):
                return False
            if s[i] != o[i]:
                return False
        return True

    def __ge__(self, other):
        """Return True always (consistent with __gt__)."""
        return True

    def __gt__(self, other):
        """Return True if __ne__ is True."""
        return self.__ne__(other)

    def __le__(self, other):
        """Return True always (consistent with __lt__)."""
        return True

    def __lt__(self, other):
        """Return True if __ne__ is True."""
        return self.__ne__(other)

    def __ne__(self, other):
        """Return True if attributes of self and other are different."""
        s = self.__dict__
        o = other.__dict__
        if len(s) != len(o):
            return True
        for i in s:
            if i not in o:
                return True
            if not isinstance(s[i], type(o[i])):
                return True
            if s[i] != o[i]:
                return True
        return False
    

class ResultsDBrecordGame(Record):
    
    """Game record.
    """

    def __init__(self,
                 keyclass=ResultsDBkeyGame,
                 valueclass=ResultsDBvalueGame):

        super(ResultsDBrecordGame, self).__init__(
            keyclass,
            valueclass)

    def get_keys(self, datasource=None, partial=None):
        """Override, return [(key, value), ...] by partial key in datasource."""
        try:
            if partial != None:
                return []

            srkey = datasource.dbhome.encode_record_number(self.key.pack())

            if datasource.primary:
                return [(srkey, self.srvalue)]
            else:
                dbname = datasource.dbname
                if dbname == filespec.GAMEEVENT_FIELD_DEF:
                    return [(self.value.event, srkey)]
                elif dbname == filespec.GAMESECTION_FIELD_DEF:
                    return [(''.join((self.value.event, self.value.section)),
                             srkey)]
                elif dbname == filespec.GAMEDATE_FIELD_DEF:
                    return [(self.value.date, srkey)]
                elif dbname == filespec.GAMEPLAYER_FIELD_DEF:
                    return [(self.value.homeplayer, srkey),
                            (self.value.awayplayer, srkey)]
                else:
                    return []
        except:
            return []

        
class ResultsDBkeyName(KeyData):

    """Primary key of name.
    """
    
    pass


class ResultsDBvalueName(ValueList):

    """Name data.

    Any value, usually used as a name, can be put on a name record and the
    key stored on the main record rather than the name. User must ensure
    that reference_count is adjusted as required.

    """

    attributes = dict(
        name=None,
        reference_count=None,
        )
    _attribute_order = tuple(sorted(attributes.keys()))

    def __init__(self):

        super(ResultsDBvalueName, self).__init__()
        self.name = None
        self.reference_count = None
        
    def empty(self):
        """(Re)Initialize value attribute."""
        self.name = ''
        self.reference_count = ''
            
    def pack(self):
        """Extend, return name record and index data."""
        v = super(ResultsDBvalueName, self).pack()
        index = v[1]
        index[filespec.NAMETEXT_FIELD_DEF] = [self.name]
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

        
    def get_keys(self, datasource=None, partial=None):
        """Override, return [(key, value), ...] by partial key in datasource."""
        try:
            if partial != None:
                return []

            srkey = datasource.dbhome.encode_record_number(self.key.pack())

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
        reported_codes=None,
        )

    # The new attribute, reported_codes, is after others to keep disruption to
    # a minimum when wrong version of ChessResults is used with a database.
    _attribute_order = sorted(attributes.keys())
    _attribute_order.append(_attribute_order.pop(-2))
    _attribute_order = tuple(_attribute_order)

    def __init__(self):

        super(ResultsDBvaluePlayer, self).__init__()
        self.name = None
        self.event = None
        self.section = None
        self.pin = None
        self.affiliation = None # (ecf club)
        self.alias = [] # event startdate endate pin are equal, implies merge
        self.merge = None # cannot break merge if in alias as well
        self.reported_codes = None

    def empty(self):
        """(Re)Initialize value attribute."""
        self.name = None
        self.event = None
        self.section = None
        self.pin = None
        self.affiliation = None
        self.alias = []
        self.merge = None
        self.reported_codes = None
            
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
        """Return player identity."""
        return (self.name, (self.event, self.section, self.pin))

    def identity_packed(self):
        """Return bytes of tab separated player identity."""
        return repr((self.name, (self.event, self.section, self.pin)))

    def pack(self):
        """Generate player record and index data.

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
        identity = self.identity_packed()
        index[filespec.PLAYERALIAS_FIELD_DEF] = [identity]
        nameparts = AppSysPersonNameParts(self.name)
        if self.merge is None:
            index[filespec.PLAYERNAMENEW_FIELD_DEF] = [
                AppSysPersonName(self.name).name]
            index[filespec.PLAYERNEW_FIELD_DEF] = [identity]
            index[filespec.PLAYERPARTIALNEW_FIELD_DEF] = [
                pn for pn in nameparts.partialnames]
        elif self.merge is True:
            index[filespec.PLAYERNAMENEW_FIELD_DEF] = [
                AppSysPersonName(self.name).name]
            index[filespec.PLAYERNEW_FIELD_DEF] = [identity]
            index[filespec.PLAYERPARTIALNEW_FIELD_DEF] = [
                pn for pn in nameparts.partialnames]
        else:
            index[filespec.PLAYERPARTIALNAME_FIELD_DEF] = [
                pn for pn in nameparts.partialnames]
            if self.merge is False:
                index[filespec.PLAYERIDENTITY_FIELD_DEF] = [identity]
                index[filespec.PLAYERNAMEIDENTITY_FIELD_DEF] = [nameparts.name]
                index[filespec.PLAYERNAME_FIELD_DEF] = [nameparts.name]
            elif self.alias is False:
                index[filespec.PLAYERNAME_FIELD_DEF] = [nameparts.name]
            else:
                index[filespec.PLAYERNAMENEW_FIELD_DEF] = [nameparts.name]
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
            srkey = datasource.dbhome.encode_record_number(self.key.pack())
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


def get_affiliation_details(database, affiliation):
    """Return ResultsDBrecordName instance for affiliation."""
    if affiliation is None:
        return ''
    return get_name_from_record_value(
        database.get_primary_record(
            filespec.NAME_FILE_DEF, affiliation)).value.name

        
def get_alias(database, key):
    """Return ResultsDBrecordPlayer instance for key."""
    a = database.get_primary_record(filespec.PLAYER_FILE_DEF, key)
    if a is not None:
        ar = ResultsDBrecordPlayer()
        ar.load_record(a)
        return ar
    

def get_alias_details(database, srkey):
    """Return (name, event, section, affiliation) for alias."""
    pr = get_alias(database, literal_eval(srkey))
    return (
        pr.value.name,
        get_event_details(database, pr.value.event),
        get_section_details(database, pr.value.section, pr.value.pin),
        get_affiliation_details(database, pr.value.affiliation)
        )
    

def get_alias_for_player(database, name):
    """Return ResultsDBrecordPlayer instance for name."""
    name = database.encode_record_selector(name)
    cursor = database.database_cursor(
        filespec.PLAYER_FILE_DEF, filespec.PLAYERALIAS_FIELD_DEF)
    try:
        r = cursor.nearest(name)
        if r:
            av, ak = r
            if database.encode_record_selector(av) == name:
                a = database.get_primary_record(filespec.PLAYER_FILE_DEF, ak)
                if a is not None:
                    alias = ResultsDBrecordPlayer()
                    alias.load_record(a)
                    return alias
    finally:
        cursor.close()
    

def get_aliases_for_event(database, event):
    """Return {record key : ResultsDBrecordPlayer(), ...} for event."""
    return get_aliases_for_games(
        database,
        get_games_for_event(database, event))


def get_aliases_for_games(database, games):
    """Return {record key : ResultsDBrecordPlayer(), ...} for games."""
    aliases = dict()
    for g in games:
        for ak in (g.value.homeplayer, g.value.awayplayer):
            if ak not in aliases:
                aliases[ak] = get_alias(database, ak)
    return aliases


def get_event(database, key):
    """Return ResultsDBrecordEvent instance for key."""
    e = database.get_primary_record(filespec.EVENT_FILE_DEF, key)
    if e is not None:
        er = ResultsDBrecordEvent()
        er.load_record(e)
        return er
    

def get_event_from_record_value(value):
    """Return ResultsDBrecordEvent instance for value on database or None."""
    if value:
        er = ResultsDBrecordEvent()
        er.load_record(value)
    else:
        er = None
    return er
    

def get_event_details(database, event):
    """Return tab separated event identity for event."""
    record = get_event_from_record_value(
        database.get_primary_record(filespec.EVENT_FILE_DEF, event))
    return '\t'.join((
        record.value.startdate,
        record.value.enddate,
        record.value.name))


def get_events_matching_event_identity(database, eventidentity):
    """Return [ResultsDBrecordEvent(), ...] for eventidentity."""
    events = dict()
    eventidentity = database.encode_record_number(eventidentity)
    cursor = database.database_cursor(
        filespec.EVENT_FILE_DEF, filespec.EVENTIDENTITY_FIELD_DEF)
    try:
        r = cursor.nearest(eventidentity)
        while r:
            ev, ek = r
            if database.encode_record_selector(ev) != eventidentity:
                break
            e = database.get_primary_record(filespec.EVENT_FILE_DEF, ek)
            if e is not None:
                events[ek] = ResultsDBrecordEvent()
                events[ek].load_record(e)
            r = cursor.next()
    finally:
        cursor.close()
    return events


def get_games_for_event(database, event):
    """Return [ResultsDBrecordGame(), ...] for event."""
    games = []
    cursor = database.database_cursor(
        filespec.GAME_FILE_DEF, filespec.GAMEEVENT_FIELD_DEF)
    try:
        evkey = database.encode_record_number(event.key.recno)
        r = cursor.nearest(evkey)
        while r:
            ge, gk = r
            if database.encode_record_selector(ge) != evkey:
                break
            g = database.get_primary_record(filespec.GAME_FILE_DEF, gk)
            if g is not None:
                games.append(ResultsDBrecordGame())
                games[-1].load_record(g)
            r = cursor.next()
    finally:
        cursor.close()
    return games


def get_name(database, key):
    """Return ResultsDBrecordName instance for key."""
    n = database.get_primary_record(filespec.NAME_FILE_DEF, key)
    if n is not None:
        nr = ResultsDBrecordName()
        nr.load_record(n)
        return nr
    

def get_name_from_record_value(value):
    """Return ResultsDBrecordName instance for value from database or None."""
    if value:
        nr = ResultsDBrecordName()
        nr.load_record(value)
    else:
        nr = None
    return nr
    

def get_names_for_games(database, games):
    """Return {record key : ResultsDBrecordName(), ...} for games."""
    names = dict()
    for g in games:
        for v in (g.value.hometeam, g.value.awayteam, g.value.section):
            if v is not None:
                if v not in names:
                    names[v] = get_name_from_record_value(
                        database.get_primary_record(filespec.NAME_FILE_DEF, v))
    return names


def get_new_aliases(database, aliases):
    """Return {record key : ResultsDBrecordPlayer(), ...} for aliases."""
    identified = dict()
    for a in aliases:
        if a not in identified:
            if aliases[a].value.merge is None:
                identified[a] = aliases[a].clone()
    return identified


def get_player_name_text(database, playername):
    """Return newline separated player identity for playername."""
    name, e = playername
    kevent, ksection, tpin = e
    return '\n'.join((
        name,
        get_event_details(database, kevent),
        get_section_details(database, ksection, tpin),
        ))


def get_player_name_text_tabs(database, playername):
    """Return tab separated player identity for playername."""
    name, e = playername
    kevent, ksection, tpin = e
    return '\t'.join((
        name,
        get_event_details(database, kevent),
        get_section_details(database, ksection, tpin),
        ))


def get_players(database, aliases):
    """Return {record key : ResultsDBrecordPlayer(), ...} for aliases."""
    players = dict()
    for a in aliases:
        if a not in players:
            if aliases[a].value.merge is not None:
                players[a] = aliases[a].clone()
    return players


def get_players_excluding_person(database, aliases):
    """Return {record key : ResultsDBrecordPlayer(), ...} for aliases."""
    players = dict()
    for a in aliases:
        if a not in players:
            m = aliases[a].value.merge
            if m is True:
                continue
            elif m is False:
                continue
            elif isinstance(m, int):
                players[a] = aliases[a].clone()
    return players


def get_persons(database, aliases):
    """Return map alias to person {alias : ResultsDBrecordPlayer(), ...}."""
    persons = dict()
    merge = dict()
    for a in aliases:
        if a not in persons:
            m = aliases[a].value.merge
            if m is not None:
                """Six possibilities for setting persons:
                merge[m] = aliases[a].clone()
                merge[m] = get_alias(database, m)
                merge[m] = aliases[a]
                Three more by setting persons[a] directly
                Not sure which, if any, is best - depends on use."""
                if m is False:
                    m = database.encode_record_number(aliases[a].key.recno)
                    merge[m] = aliases[a].clone()
                elif m is True:
                    m = database.encode_record_number(aliases[a].key.recno)
                    merge[m] = aliases[a].clone()
                if m not in merge:
                    merge[m] = get_alias(database, m)
                persons[a] = merge[m]
    return persons


def get_person_from_alias(database, record):
    """Return ResultsDBrecordPlayer instance."""
    m = record.value.merge
    if m is True:
        pr = record.clone()
    elif m is False:
        pr = record.clone()
    elif isinstance(m, int):
        pr = get_alias(database, m)
    else:
        pr = record.clone()
    return pr


def get_person_from_player(database, record):
    """Return ResultsDBrecordPlayer instance unless record is NewAlias."""
    m = record.value.merge
    if m is False:
        pr = record.clone()
    elif isinstance(m, int):
        pr = get_alias(database, m)
    else:
        pr = None
    return pr


def get_persons_for_players(database, aliases):
    """Return {record key : ResultsDBrecordPlayer(), ...} for aliases."""
    persons = dict()
    for a in aliases:
        p = get_person_from_player(database, aliases[a])
        if p:
            k = database.encode_record_number(p.key.recno)
            if k not in persons:
                persons[k] = p
    return persons


def get_players_for_event(database, event):
    """Return {record key : ResultsDBrecordPlayer(), ...} for event."""
    return get_players(
        database,
        get_aliases_for_event(database, event))


def get_players_for_games(database, games):
    """Return {record key : ResultsDBrecordPlayer(), ...} for games."""
    return get_players(
        database,
        get_aliases_for_games(database, games))


def get_alias_for_player_import(database, player, sections, lookupevent=None):
    """Return ResultsDBrecordPlayer instance for player in data import."""
    pv = ResultsDBvaluePlayer()
    pv.name, name, startdate, enddate, pv.section, pv.pin = player
    if pv.section:
        pv.section = get_encoded_section_key(database, pv.section)
    if lookupevent:
        for s in sections:
            e = (name, startdate, enddate, s)
            event = lookupevent.get(e)
            if event:
                pv.event = event
                return get_alias_for_player(database, pv.identity_packed())

    ev = ResultsDBvalueEvent()
    ev.name, ev.startdate, ev.enddate = name, startdate, enddate
    for s in sections:
        sectionkey = get_encoded_section_key(database, s)
        if sectionkey is not None:
            for v in get_events_matching_event_identity(
                database, ev.get_event_identity()).values():
                if sectionkey in v.value.sections:
                    pv.event = v.key.recno
                    alias = get_alias_for_player(database, pv.identity_packed())
                    if lookupevent:
                        if alias:
                            lookupevent[
                                (name, startdate, enddate, s)] = pv.event
                    return alias


def get_alias_for_player_takeon(database, player, lookupevent=None):
    """Return ResultsDBrecordPlayer instance for player in data take-on."""
    pv = ResultsDBvaluePlayer()
    if lookupevent:
        event_section = lookupevent.get(player[1:-1])
        if event_section:
            pv.name = player[0]
            pv.pin = player[-1]
            pv.event, pv.section = event_section
            return get_alias_for_player(database, pv.identity_packed())

    ev = ResultsDBvalueEvent()
    pv.name, ev.name, ev.startdate, ev.enddate, section, pv.pin = player
    sectionkey = get_encoded_section_key(database, section)
    if sectionkey is not None:
        for v in get_events_matching_event_identity(
            database, ev.get_event_identity()).values():
            if sectionkey in v.value.sections:
                pv.event = v.key.recno
                pv.section = sectionkey
                alias = get_alias_for_player(database, pv.identity_packed())
                if lookupevent:
                    if alias:
                        lookupevent[event_section] = (ev.name, sectionkey)
                return alias


def get_encoded_section_key(database, section):
    """Return section key as stored on index or None if no record."""
    s = get_name_from_record_value(
        database.get_primary_record(
            filespec.NAME_FILE_DEF,
            database.database_cursor(
                filespec.NAME_FILE_DEF,
                filespec.NAMETEXT_FIELD_DEF
                ).get_unique_primary_for_index_key(
                    database.encode_record_selector(section))))
    if s:
        return s.key.recno


def get_section_details(database, section, pin):
    """Return section name. Format depends on pin."""
    if section is None:
        return ''
    record = get_name_from_record_value(
        database.get_primary_record(filespec.NAME_FILE_DEF, section))
    if pin:
        return '\t'.join((record.value.name, str(pin)))
    else:
        return record.value.name


def get_alias_identity(record):
    """Return alias as tuple with key attributes converted to values.

    Tuple has 7 elements in order:
    Player name
    Event start date
    Event end date
    Event name
    Sorted tuple of event sections
    Player section (may be a club if event is a league)
    Player pin (usually the pairing number in a swiss event section)
    
    The event sections are included to associate the player with the event
    record rather than the event. The player identity does not include the
    event sections when comparing players between exporting and importing
    databases.
    
    """
    v = record.value
    db = record.database
    event = get_event_from_record_value(
        db.get_primary_record(
            filespec.EVENT_FILE_DEF,
            v.event)).value
    sections = set()
    for s in event.sections:
        sections.add(
            get_name_from_record_value(
                db.get_primary_record(
                    filespec.NAME_FILE_DEF,
                    s)).value.name)
    if v.section:
        section = get_name_from_record_value(
            db.get_primary_record(
                filespec.NAME_FILE_DEF,
                v.section)).value.name
    else:
        section = v.section
    return (
        v.name,
        event.startdate,
        event.enddate,
        event.name,
        sections,
        section,
        v.pin,
        )


def get_events_for_performance_calculation(database, events):
    """Return calculation data from database records for events."""
    games = dict()
    players = dict()
    game_opponent = dict()
    opponents = dict()
    names = dict()
    for e in events:
        eventgames = get_games_for_event(
            database,
            get_event(database, e[-1]))
        eventaliases = get_aliases_for_games(
            database,
            eventgames)
        eventpersons = get_persons(database, eventaliases)
        alias = dict()
        for k in eventaliases.keys():
            v = eventpersons.get(k)
            if v is None:
                return
            alias[k] = v.key.recno
            names[alias[k]] = v.value.name
        for g in eventgames:
            if g.value.result in ecfresult: # 'a', 'd', 'h'
                for a in (g.value.homeplayer, g.value.awayplayer):
                    p = alias[a]
                    if p not in players:
                        players[p] = {g.key.recno}
                    else:
                        players[p].add(g.key.recno)
                    if p not in opponents:
                        opponents[p] = set()
                game_opponent[g.key.recno] = {
                    alias[g.value.homeplayer]: alias[g.value.awayplayer],
                    alias[g.value.awayplayer]: alias[g.value.homeplayer],
                    }
                opponents[alias[g.value.homeplayer]].add(
                    alias[g.value.awayplayer])
                opponents[alias[g.value.awayplayer]].add(
                    alias[g.value.homeplayer])
                result = dict()
                if g.value.result == awin:
                    result[alias[g.value.awayplayer]] = 1
                    result[alias[g.value.homeplayer]] = -1
                elif g.value.result == hwin:
                    result[alias[g.value.awayplayer]] = -1
                    result[alias[g.value.homeplayer]] = 1
                elif g.value.result == draw:
                    result[alias[g.value.awayplayer]] = 0
                    result[alias[g.value.homeplayer]] = 0
                games[g.key.recno] = result
    return (games, players, game_opponent, opponents, names)


def get_events_for_performance_prediction(database, events):
    """Return calculation data from database records for events."""
    (games,
     players,
     game_opponent,
     opponents,
     names,
     ) = get_events_for_performance_calculation(database, events)
    seasons = {}
    game = ResultsDBrecordGame()
    asd = AppSysDate()
    for gk in sorted(games):
        game.load_record(
            database.get_primary_record(filespec.GAME_FILE_DEF, gk))
        # Hack to deal with surviving non-ISO format dates
        #y, m, d = [int(e) for e in game.value.date.split('-')]
        if asd.parse_date(game.value.date) > 0:
            y, m, d = [int(e) for e in asd.iso_format_date().split('-')]
        else:
            y, m, d = (1950, 1, 1)
        # End hack
        if m < 7:
            y -= 1
        seasons.setdefault('-'.join((str(y), '12', '25')), set()).add(gk)
    return (seasons, games, players, game_opponent, opponents, names)


def get_unpacked_player_identity(identity):
    """Return player identity tuple for packed identity."""
    return literal_eval(identity)


def get_events_matching_event_name(database, eventname, sections):
    """Return (key,ResultsDBrecordEvent()),[(key,ResultsDBrecordEvent()), ...]

    the event being processed and a list of earlier events with same name.

    """
    events = []
    event = None
    if database is None:
        return event, events
    if len(eventname) != 1:
        return event, events
    sections = {get_encoded_section_key(database, s) for s in sections}
    eventname = eventname.pop()
    cursor = database.database_cursor(
        filespec.EVENT_FILE_DEF, filespec.EVENTNAME_FIELD_DEF)
    try:
        r = cursor.nearest(database.encode_record_selector(eventname[0]))
        while r:
            ev, ek = r
            if ev != eventname[0]:
                break
            e = database.get_primary_record(filespec.EVENT_FILE_DEF, ek)
            if e is not None:
                er = ResultsDBrecordEvent()
                er.load_record(e)
                if (er.value.startdate == eventname[1] and
                    er.value.enddate == eventname[2] and
                    sections.issubset(er.value.sections)):
                    event = ek, er
                else:
                    events.append(
                        (er.value.startdate, er.value.enddate, ek, er))
            r = cursor.next()
    finally:
        cursor.close()
    return event, [e[-2:] for e in reversed(sorted(events))]

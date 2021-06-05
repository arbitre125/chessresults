# takeoncollationdb.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Database update for collated results imported by the 'take-on' route.

A separate class is used because it is reasonable to use the TakeonCollation
class without database support for the collation data.

The collated results from the results import replace any existing results on
the database for the imported events.

"""

from . import collationdb
from . import constants
from . import filespec
from . import resultsrecord


class TakeonCollationDB(collationdb.CollationDB):

    """Results extracted from a file of imported games.
    """

    def __init__(self, collation, database):

        super().__init__(collation.games, database)
        self.merges = collation.merges
        self.players = collation.players

    def merge_players(self):
        """Merge imported players with matching records on database.

        Caller is responsible for commit or backout action.

        """
        # For league matches a club name is held as the section value on the
        # database for native records.  On these imports section is always the
        # arbitrary value 'Event Matches' and pin is unique.  But pin is not
        # used in native league player identifiers.  Thus section has to be
        # modified if losing pin would generate duplicate player identifiers.
        namemanager = collationdb.NameManager(self._database)
        affiliations = dict()
        for s, gms in self._games.items():
            if s[0] == 'Event Matches':
                for g in gms.games:
                    for p in g.homeplayer, g.awayplayer:
                        if p._identity not in affiliations:
                            affiliations[p._identity] = p.affiliation
        duplicates = set()
        names = set()
        for pg in self.merges.values():
            for player in pg:
                if player[4] == constants._event_matches:
                    identifier = player[:-1]
                    if identifier in names:
                        duplicates.add(identifier)
                    names.add(identifier)
        del names
        lookup = dict()
        for pg in self.merges.values():
            ip = None
            ap = dict()
            for player, gamecount in pg.items():
                identifier = player[:-1]
                section = identifier[-1]
                if ip is None:
                    ip = player
                    ips = section
                    ipg = gamecount
                elif (ips == constants._event_matches and
                      section != constants._event_matches):
                    ap[player] = None
                elif (ips != constants._event_matches and
                      section == constants._event_matches):
                    ap[ip] = None
                    ip = player
                    ips = section
                    ipg = gamecount
                elif gamecount > ipg:
                    ap[ip] = None
                    ip = player
                    ips = section
                    ipg = gamecount
                else:
                    ap[player] = None
            ipr = resultsrecord.get_alias_for_player_takeon(
                self._database, ip, lookupevent=lookup)
            newipr = ipr.clone()
            if newipr.value.merge is None:
                newipr.value.merge = False
            for p in ap:
                ap[p] = resultsrecord.get_alias_for_player_takeon(
                    self._database, p)
                newap = ap[p].clone()
                newipr.value.alias.append(newap.key.recno)
                newap.value.merge = newipr.key.recno
                newap.value.alias = newipr.value.merge
                if duplicates:
                    if p[:-1] in duplicates:
                        newap.value.name = ' '.join(
                            (newap.value.name,
                             str(newap.value.pin).join(('(', ')')),
                             ))
                if p[4] == constants._event_matches:
                    namemanager.unset_name(newap.value.section)
                    namemanager.set_name(affiliations[p])
                    newap.value.section = namemanager.get_code(affiliations[p])
                    newap.value.pin = None
                ap[p].edit_record(
                    self._database,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYER_FIELD_DEF,
                    newap)
            if duplicates:
                if ip[:-1] in duplicates:
                    newipr.value.name = ' '.join(
                        (newipr.value.name,
                         str(newipr.value.pin).join(('(', ')')),
                         ))
            if ips == constants._event_matches:
                namemanager.unset_name(newipr.value.section)
                namemanager.set_name(affiliations[ip])
                newipr.value.section = namemanager.get_code(affiliations[ip])
                newipr.value.pin = None
            ipr.edit_record(
                self._database,
                filespec.PLAYER_FILE_DEF,
                filespec.PLAYER_FIELD_DEF,
                newipr)
        namemanager.update_names()

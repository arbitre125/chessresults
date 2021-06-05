# importcollationdb.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Database update for imported event results.

A separate class is used because it is reasonable to use the CollationEvents
class without database support for the collation data.

The import may take two passes.  The first pass will usually generate a
response to the exporting database if the import contains new players.  This
will include all players known to the importing database.  The second pass
should have the new players confirmed as new or linked to one of the players
added in the first pass response.  The database is then updated on the second
pass.

"""

from . import collationdb
from . import resultsrecord
from . import constants
from . import filespec
from .importreports import convert_alias_to_transfer_format
from .importreports import get_event_from_player


class ImportCollationDB(Exception):
    pass


class ImportCollationDB(collationdb.CollationDB):
    
    """Update results database from games in a CollationEvents instance.
    """

    def __init__(self, collation, database):
        """"""

        super().__init__(collation.games, database)

        self.collation = collation
        self.dbplayer = set()
        self.dbplayermerge = dict()
        self.mergeplausible = dict()

    def export_players_on_database(self):
        """"""

        # get all aliases on importing database
        # note identity with embedded keys translated and merge structure
        players = dict()
        gai = resultsrecord.get_alias_identity
        pr = resultsrecord.ResultsDBrecordPlayer()
        pk = pr.key
        pv = pr.value
        db = self._database
        pr.set_database(db)
        cursor = db.database_cursor(
            filespec.PLAYER_FILE_DEF, filespec.PLAYER_FIELD_DEF)
        try:
            r = cursor.first()
            while r:
                pr.load_record(r)
                players[pk.recno] = (
                    gai(pr), pv.merge, pv.alias, pv.affiliation)
                r = cursor.next()
        finally:
            cursor.close()
        # add all aliases to export data
        main_alias_values = {type(True), type(False), type(None)}
        exportdata = []
        for pi, pm, pa, paff in players.values():
            if type(pm) in main_alias_values:
                for a in pa:
                    exportdata.extend(
                        convert_alias_to_transfer_format(
                            players[a][0],
                            constants._player))
                exportdata.extend(
                    convert_alias_to_transfer_format(pi, constants._player))
                exportdata.append(
                    '='.join(
                        (constants._aliases, repr(pm))))

        return exportdata

    def identify_players(self):
        """Identify player records as specified in import collation.

        Caller is responsible for commit or backout action.

        """
        ir = self.collation.importreport
        for p, ps in ir.get_game_players().items():
            gefp = get_event_from_player(p)
            pr = resultsrecord.get_alias_for_player_import(
                self._database,
                p,
                ir.localevents[get_event_from_player(p)])
            prc = pr.clone()
            alias = set(pr.value.alias)
            for a in ps:
                ar = resultsrecord.get_alias_for_player_import(
                    self._database,
                    a,
                    ir.localevents[get_event_from_player(a)])
                if ar.key.recno not in alias:
                    arc = ar.clone()
                    arc.value.merge = pr.key.recno
                    arc.value.alias = False
                    prc.value.alias.append(ar.key.recno)
                    ar.edit_record(
                        self._database,
                        filespec.PLAYER_FILE_DEF,
                        filespec.PLAYER_FIELD_DEF,
                        arc)
            prc.value.merge = False
            pr.edit_record(
                self._database,
                filespec.PLAYER_FILE_DEF,
                filespec.PLAYER_FIELD_DEF,
                prc)

    def is_player_identification_inconsistent(self):
        """Return True if player identifications inconsistent with database."""

        def check_person(rec):
            if rec is None:
                return None
            if rec.key.recno in examined:
                return True
            examined.add(rec.key.recno)
            e = resultsrecord.get_event(
                self._database,
                rec.value.event)
            # list of sections in event not used in ir.localplayer, but
            # perhaps it should be
            #es = tuple(sorted([
                #resultsrecord.get_name(
                    #self._database,
                    #self._database.decode_record_number(s)).value.name
                #for s in e.value.sections]))
            ps = resultsrecord.get_name(
                self._database, rec.value.section).value.name
            pi = (rec.value.name, e.value.name, e.value.startdate,
                  e.value.enddate, ps, rec.value.pin)#es, ps, rec.value.pin)
            if pi in aliases:
                return True
            elif pi in ir.localplayer:
                return pi
            else:
                return False

        def get_person(am):
            ar = resultsrecord.get_alias_for_player_import(
                self._database,
                am,
                ir.localevents[get_event_from_player(am)])
            if ar:
                return resultsrecord.get_person_from_alias(self._database, ar)
        
        ir = self.collation.importreport
        checked = set()
        for gp in ir.gameplayer:
            examined = set()
            aliases = ir.localplayer[ir.gameplayermerge[gp]]
            for p in aliases:
                checked.add(check_person(get_person(p)))
        for v in (True, False, None):
            checked.discard(v)
        return checked

    def is_database_empty_of_players(self):

        cursor = self._database.database_cursor(
            filespec.PLAYER_FILE_DEF, filespec.PLAYER_FIELD_DEF)
        try:
            r = cursor.first()
        finally:
            cursor.close()
        return r is None

    def merge_players(self):
        """Merge player records as specified in import collation.

        Caller is responsible for commit or backout action.

        """
        # do the merges implied by similarities in exporting and importing
        # database player merges

        def get_known_person(am):
            ar = resultsrecord.get_alias_for_player_import(
                self._database,
                am,
                ir.knownevents[get_event_from_player(am)])
            if ar:
                return resultsrecord.get_person_from_alias(self._database, ar)
        
        def get_person(am):
            ar = resultsrecord.get_alias_for_player_import(
                self._database,
                am,
                ir.localevents[get_event_from_player(am)])
            if ar:
                return resultsrecord.get_person_from_alias(self._database, ar)
        
        ir = self.collation.importreport
        for gp in ir.gameplayer:
            aliases = ir.localplayer[ir.gameplayermerge[gp]]
            for a in aliases:
                dbp = get_person(a)
                if dbp:
                    if dbp.value.merge is False:
                        break
                    if dbp.value.merge is True:
                        break
            else:
                dbp = None
            if dbp:
                dbgp = resultsrecord.get_alias_for_player_import(
                    self._database,
                    gp,
                    ir.localevents[get_event_from_player(gp)])
                if dbgp.value.merge == dbp.key.recno:
                    # assume a previous run has done the record edits
                    continue
                elif gp in ir.known_to_new:
                    # let exporter defined merges loop process record
                    # {in case the import file is reprocessed (by mistake)}
                    continue
                elif dbp.key == dbgp.key:
                    # assume new player or exporter defined merge
                    # (mainalias = gp path taken above)
                    continue
                dbgpc = dbgp.clone()
                dbpc = dbp.clone()
                try:
                    alias = set(dbpc.value.alias)
                except TypeError:
                    if dbpc.value.alias not in {None, True, False}:
                        raise ImportCollationDB('Record alias value')
                    elif dbgpc.value.merge != dbpc.value.alias:
                        raise ImportCollationDB('Record merge value')
                    alias = set()
                alias.add(dbgpc.key.recno)
                dbpc.value.alias = sorted(alias)
                dbgpc.value.merge = dbpc.key.recno
                dbgpc.value.alias = dbpc.value.merge
                dbp.edit_record(
                    self._database,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYER_FIELD_DEF,
                    dbpc)
                dbgp.edit_record(
                    self._database,
                    filespec.PLAYER_FILE_DEF,
                    filespec.PLAYER_FIELD_DEF,
                    dbgpc)
        # do the merges the exporter has defined
        for k, nset in ir.known_to_new.items():
            pr = get_known_person(k)
            if pr is None:
                if get_event_from_player(k) in ir.knownevents:
                    # Maybe used an identification response to generate a new
                    # database missing some of the records that are, or were,
                    # on the original importing database; and these records are
                    # the main records for those persons.
                    continue
            prc = pr.clone()
            alias = set(pr.value.alias)
            newaliases = set()
            for n in nset - {k}:
                ar = resultsrecord.get_alias_for_player_import(
                    self._database,
                    n,
                    ir.localevents[get_event_from_player(n)])
                if ar is None:
                    # alias on remote database not on local database.
                    # local database does not have the games for this alias.
                    continue
                if ar.key.recno not in alias:
                    arc = ar.clone()
                    arc.value.merge = pr.key.recno
                    arc.value.alias = False
                    newaliases.add(ar.key.recno)
                    ar.edit_record(
                        self._database,
                        filespec.PLAYER_FILE_DEF,
                        filespec.PLAYER_FIELD_DEF,
                        arc)
            prc.value.merge = False
            if (pr.value.merge == prc.value.merge and
                len(newaliases) == 0):
                continue
            prc.value.alias = sorted(alias.union(newaliases))
            pr.edit_record(
                self._database,
                filespec.PLAYER_FILE_DEF,
                filespec.PLAYER_FIELD_DEF,
                prc)

    def is_new_player_inconsistent(self):
        """Return set of (new, known) players inconsistent with database."""
        
        def get_known_person(am):
            ar = resultsrecord.get_alias_for_player_import(
                self._database,
                am,
                ir.knownevents[get_event_from_player(am)])
            if ar:
                return resultsrecord.get_person_from_alias(self._database, ar)
        
        def get_person(am):
            ar = resultsrecord.get_alias_for_player_import(
                self._database,
                am,
                ir.localevents[get_event_from_player(am)])
            if ar:
                return resultsrecord.get_person_from_alias(self._database, ar)

        inconsistent = set()
        ir = self.collation.importreport
        for new, known in ir.new_to_known.items():
            p = get_person(new)
            if p:
                if p.value.merge is None:
                    continue
                np = get_known_person(known)
                if np:
                    if np.key.recno != p.key.recno:
                        inconsistent.add((new, known))
        return inconsistent

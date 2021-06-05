# knownnames.py
# Copyright 2017 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Interface to results database for player names known in other
editions of event.
"""

from .playerfind import find_player_names_in_other_editions_of_event


class KnownNames:
    
    """Extend to represent subset of games on file that match a postion.
    """

    def __init__(self, *a, **k):
        """Extend to provide placeholder for position used to select games.
        """
        super().__init__()
        
        # Event used to select player names in other editions of event.
        self.event = None

        # Map alias record for name, in other event editions, to person record.
        self.map_newplayer_to_knownplayer = {}

    def get_known_names(self, event):
        """Find records with same player name in other editions of event and
        put them on the recordset for display.
        """
        recordset = self.dbhome.recordlist_nil(self.dbset)
        if event:
            map_np_to_kp = find_player_names_in_other_editions_of_event(
                self.dbhome, event)
            for alias_recno in map_np_to_kp:
                recordset.place_record_number(alias_recno)
        else:
            map_np_to_kp = {}
        self.set_recordset(recordset)
        self.event = event
        self.map_newplayer_to_knownplayer = map_np_to_kp

    def remove_record_from_recordset(self, record_number):
        """Remove record_number from self.recordset.

        Method exists for compatibility with DPT.
        """
        self.recordset.remove_record_number(record_number)

# takeonschedule.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Take on events schedule class.
"""


class TakeonSchedule(object):

    """Schedule extracted from event schedule file.

    Team names are derived from match names.  This class supports editing of
    match names extracted from the take-on data file in the 'fixtures' area
    while remaining data can be edited in 'results' area.  All the processing
    is done in the 'results' class but the name mapping is done here.

    The objects used to implement this are not quite the natural ones but is
    done this way to keep code structure same as the event in a season case.

    """

    def __init__(self):
        """Override, initialise schedule data items."""
        super().__init__()
        self.textlines = None
        self.error = []
        self.match_names = {}

    def build_schedule(self, textlines):
        """Populate the event schedule from textlines."""

        def get_match_name(text):
            """Extract match name from text and return state indicator."""
            mn = text.split("=", 1)
            if len(mn) != 2:
                self.error.append(
                    "".join(
                        (
                            '"',
                            text,
                            '" is not a match name translation.',
                        )
                    )
                )
                return get_match_name
            name, translation = mn
            if name in self.match_names:
                self.error.append(
                    "".join(
                        (
                            'Match name "',
                            name,
                            '" in "',
                            text,
                            '" is a duplicate',
                        )
                    )
                )
                return get_match_name
            self.match_names[name] = translation
            return get_match_name

        self.textlines = textlines
        state = None
        process = get_match_name
        for tl in self.textlines:
            tl = tl.strip()
            if len(tl) == 0:
                continue
            state = process
            process = process(tl)

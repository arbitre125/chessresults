# playerfind.py
# Copyright 2017 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Find player names which are used in other editions of an event.

A player is likely referred to using the same name from year to year in an
event.  An ECF grading code will have been used to report the results for
grading.

The option to merge the name from the current event with the earlier editions
is offered, which will cause the same ECF grading code to be used to report
results for the current event.

"""

from ..core import resultsrecord
from ..core.ecf import ecfmaprecord, ecfrecord


def find_player_names_in_other_editions_of_event(db, event):
    """Return list of alias and person records whose name is in other editions
    of event.

    The list contains (name, alias record number, person record number) tuples,
    where name includes event and section identifiers to pick a bundle of game
    results.

    The list is used to display the players who identity is probably correct,
    and to drive the merge of new alias in person for those players selected
    on the display.

    """
    aliases_for_event = resultsrecord.get_aliases_for_event(db, event)
    alias_map = {}
    for k, va in aliases_for_event.items():
        v = va.value
        alias_map[(v.name, v.event, v.section, v.pin, v.affiliation)] = k
    names = set()
    for k, v in aliases_for_event.items():
        vv = v.value
        if not (vv.merge is None and not vv.alias):
            continue
        names.add((vv.name, vv.event, vv.section, vv.pin, vv.affiliation))
    sections = [resultsrecord.get_name(db, es) for es in event.value.sections]
    event_editions = resultsrecord.get_events_matching_event_name(
        db,
        {(event.value.name, event.value.startdate, event.value.enddate)},
        {v.value.name for v in sections},
    )
    event_key = event.key.recno
    editions_for_aliases = {}
    persons_for_aliases = {}
    for ee in event_editions[1]:
        evkey = ee[1].key.recno
        for afe in resultsrecord.get_aliases_for_event(db, ee[1]).items():
            v = afe[1].value
            name = (v.name, event_key, v.section, v.pin, v.affiliation)
            if name in names:
                person = resultsrecord.get_person_from_alias(db, afe[1])
                if person is not None:
                    persons_for_aliases.setdefault(name, set()).add(
                        person.key.recno
                    )
                else:
                    persons_for_aliases.setdefault(name, set()).add(None)
                editions_for_aliases.setdefault(name, set()).add(evkey)
    for afe in alias_map:
        if afe in editions_for_aliases:
            if afe not in persons_for_aliases:
                del editions_for_aliases[afe]
            elif len(persons_for_aliases[afe]) > 1:
                del editions_for_aliases[afe]
    return {
        alias_map[efa]: (efa, persons_for_aliases[efa].pop())
        for efa in editions_for_aliases
    }

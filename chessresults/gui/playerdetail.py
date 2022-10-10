# playerdetail.py
# Copyright 2014 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Results database display Player detail.

Show all identities for a player, derived from event competitions, and ECF
code if available.

"""
import tkinter
import tkinter.messagebox

from solentware_misc.gui import dialogue

from ..core import mergeplayers
from ..core import resultsrecord
from ..core import filespec
from ..core.ecf import ecfmaprecord
from ..core.ecf import ecfrecord
from ..core.ogd import ecfgcodemaprecord
from ..core.ogd import ecfogdrecord


def display_player_details(myself, selections, title):
    """ """
    db = myself.get_appsys().get_results_database()
    entries = dict()
    mainnotfound = dict()
    for s in selections:
        for k, v in s:
            e = mergeplayers.get_person_for_alias_key(db, (k, v))
            if e is None:
                mainnotfound[v] = resultsrecord.get_alias(db, v)
            elif e.key.recno not in entries:
                entries[e.key.recno] = (e, (k, v))
    if len(entries) == 0:
        dlg = tkinter.messagebox.showinfo(
            parent=myself.get_widget(),
            message=" ".join(
                (
                    "None of the selected player aliases is, or has, a main",
                    "alias.\n\nAll the selected aliases should be new",
                    "players.",
                )
            ),
            title=title,
        )
        return
    if len(mainnotfound):
        dlg = tkinter.messagebox.showinfo(
            parent=myself.get_widget(),
            message=" ".join(
                (
                    "At least one of the selected player aliases does not",
                    "have a main alias.\n\nDetails for the other selected",
                    "aliases will be shown on dismissing this dialogue.",
                )
            ),
            title=title,
        )

    for selected, selection in entries.values():
        if selected.value.merge is None:
            pass
        elif selected.value.merge is False:
            detail = _alias_details(myself, selection, title)
            if detail is None:
                continue
            identity, ecf, ogd, caption, aliases = detail
            if ecf or ogd:
                header = "".join(
                    (
                        "Full details for\n",
                        identity,
                        "\n",
                        "are below, including ECF information.",
                    )
                )
            else:
                header = "".join(
                    (
                        "Full details for\n",
                        identity,
                        "\n",
                        "are below.",
                    )
                )
        elif selected.value.merge is True:
            detail = _alias_details(myself, selection, title)
            if detail is None:
                continue
            identity, ecf, ogd, caption, aliases = detail
            if ecf or ogd:
                header = "".join(
                    (
                        "Full details for\n",
                        identity,
                        "\n",
                        "are below, including ECF information.\n",
                        "These details are from an imported event ",
                        "and confirmation of identity is awaited.",
                    )
                )
            else:
                header = "".join(
                    (
                        "Full details for\n",
                        identity,
                        "\n",
                        "are below.\n",
                        "These details are from an imported event ",
                        "and confirmation of identity is awaited.",
                    )
                )
        else:
            detail = _alias_details(myself, selection, title)
            if detail is None:
                continue
            identity, ecf, ogd, caption, aliases = detail
            if ecf or ogd:
                header = "".join(
                    (
                        "Full details for\n",
                        resultsrecord.get_player_name_text_tabs(
                            db, selected.value.identity()
                        ),
                        "\n",
                        "via the identity",
                        "\n",
                        identity,
                        "\n",
                        "are below, including ECF information.",
                    )
                )
            else:
                header = "".join(
                    (
                        "Full details for\n",
                        identity,
                        "\n",
                        "are below.",
                    )
                )
        text = []
        if ecf:
            text.extend((ecf, "\n\n"))
        if ogd:
            text.extend((ogd, "\n\n"))
        text.extend(
            (
                "Alias entries for this identity are:",
                "\n\n",
                "\n".join(aliases),
            )
        )
        dialogue.Report(
            parent=myself,
            title=title,
            action_titles={"Save": "Save Player Details"},
            wrap=tkinter.WORD,
            tabstyle="tabular",
        ).append("\n\n".join((header, "".join(text))))


def _alias_details(myself, selection, title):
    """Return (<identity name>, <ecf detail>, [<alias name>, ...])."""
    db = myself.get_appsys().get_results_database()
    mainentry = mergeplayers.get_person_for_alias_key(db, selection)
    if mainentry is None:
        dlg = tkinter.messagebox.showinfo(
            parent=myself.get_widget(),
            message="Cannot find identified player for selection.",
            title=title,
        )
        return

    ecfline = ""
    caption = ""
    ogdline = ""
    if myself.get_appsys().show_master_list_grading_codes:
        playermap = ecfmaprecord.get_person_for_player(db, mainentry.key.recno)
        if playermap is None:
            ecfline = "Player is not linked to an ECF master list code."
        elif playermap.value.playercode:
            playerecf = ecfrecord.get_ecf_player_for_grading_code(
                db, playermap.value.playercode
            )
            if playerecf.value.ECFmerge:
                mergecode = "".join(
                    (
                        "\n\nThe most recently applied ECF feedback notes ",
                        "a merge into ",
                        playerecf.value.ECFmerge,
                    )
                )
                caption = "".join(
                    (
                        "Results submissions for this player will use the ",
                        playermap.value.playercode,
                        " grading code.\nThis is certain to be our player ",
                        "and the ECF will redirect the results.\nIf the ECF ",
                        "removes a merge we are not informed directly ever.",
                    )
                )
            else:
                mergecode = ""
            if playerecf.value.ECFactive:
                ecfline = "".join(
                    (
                        "The information from the ECF Master List is:\n\n",
                        playerecf.value.ECFcode,
                        "   ",
                        playerecf.value.ECFname,
                        "\n\n",
                        mergecode,
                    )
                )
            else:
                ecfline = "".join(
                    (
                        "No Master List data recorded. ECF grading code ",
                        "recorded is ",
                        playerecf.value.ECFcode,
                        mergecode,
                    )
                )
        elif playermap.value.playerecfcode:
            ecfline = "".join(
                (
                    "An ECF grading code and name have been entered. ",
                    "These are:\n\n",
                    playermap.value.playerecfcode,
                    "   ",
                    playermap.value.playerecfname,
                    "\n\n",
                    "Be sure that the ECF grading code is correct before ",
                    "including it on a results submission file.",
                )
            )
        elif playermap.value.playerecfname:
            ecfline = "".join(
                (
                    "No information from ECF for this player is available ",
                    "on this database.\n",
                    "An ECF format name, but no grading code, has been ",
                    "entered. Name is:\n\n",
                    playermap.value.playerecfname,
                    "\n\n",
                    "This player will be treated as a new player if ",
                    "included on a results submission file.",
                )
            )
        else:
            ecfline = "".join(
                (
                    "No information from ECF for this player is available ",
                    "on this database.\n",
                    "Neither an ECF format name nor grading code has been ",
                    "entered.\n",
                    "At least a name will have to be entered before this ",
                    "player can be included on a results submission file.",
                )
            )
    if myself.get_appsys().show_grading_list_grading_codes:
        playermap = ecfgcodemaprecord.get_person_for_player(
            db, mainentry.key.recno
        )
        if playermap:
            playerecf = ecfogdrecord.get_ecf_ogd_player_for_grading_code(
                db, playermap.value.playercode
            )
            if playerecf:
                ogdline = "".join(
                    (
                        "The information from the available ECF Grading List ",
                        "is:\n\n",
                        playerecf.value.ECFOGDcode,
                        "   ",
                        playerecf.value.ECFOGDname,
                    )
                )
            else:
                ogdline = "".join(
                    (
                        "No ECF grading list available to provide detail for ",
                        "this player.  Code is ",
                        playermap.value.playercode,
                        ",",
                    )
                )
        else:
            ogdline = "Player is not linked to an ECF grading list code."
    asel = []
    pr = resultsrecord.ResultsDBrecordPlayer()
    for a in mainentry.value.get_alias_list():
        r = db.get_primary_record(filespec.PLAYER_FILE_DEF, a)
        if r is None:
            dlg = tkinter.messagebox.showinfo(
                parent=myself.get_widget(),
                message="".join(
                    (
                        "Alias for player\n",
                        resultsrecord.get_player_name_text(db, ""),
                        "\ndoes not exist in alias list.",
                    )
                ),
                title=title,
            )
            return
        pr.load_record(r)
        asel.append(
            resultsrecord.get_player_name_text_tabs(db, pr.value.identity())
        )

    return (
        resultsrecord.get_player_name_text_tabs(
            db, mainentry.value.identity()
        ),
        ecfline,
        ogdline,
        caption,
        asel,
    )

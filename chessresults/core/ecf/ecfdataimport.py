# ecfdataimport.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Extract player and club data from ECF reference files.

ECF (formerly BCF) provided reference files on CD from the end of the 1998
season as a matter of routine.  These contained the active players from the
most recent three seasons.  From the end of the 2006 season smaller updates
were provided during the season but these were soon replaced by more frequent
issuing of reference files including new, or re-activated, players.  From the
middle of the 2011 season the reference files included all players who had
ever played a graded game (since early 1990s in practice).

"""

from . import filespec


def _do_ecf_downloaded_data_import(
    import_method,
    widget,
    logwidget=None,
    specification_items=None,
    ecfdata=None,
    downloaddate=None,
):
    """ """

    results = widget.get_appsys().get_results_database()
    if not results:
        return False

    results.do_database_task(
        import_method,
        logwidget=logwidget,
        taskmethodargs=dict(
            ecfdata=ecfdata,
            parent=widget.get_widget(),
            downloaddate=downloaddate,
        ),
        use_specification_items=specification_items,
    )

    return True


def _do_ecf_reference_data_import(
    import_method,
    widget,
    logwidget=None,
    specification_items=None,
    ecfdate=None,
    datecontrol=None,
):
    """Import a new ECF club file.

    widget - the manager object for the ecf data import tab

    """
    ecffile = widget.datagrid.get_data_source().dbhome

    # The commented code fails if tkinter is compiled without --enable-threads
    # as in OpenBSD 5.7 i386 packages.  The standard build from FreeBSD ports
    # until early 2015 at least, when this change was introduced, is compiled
    # with --enable-threads so the commented code worked.  Not sure if the
    # change in compiler on FreeBSD from gcc to clang made a difference.  The
    # Microsoft Windows' Pythons seem to be compiled with --enable-threads
    # because the commented code works in that environment.  The situation on
    # OS X, and any GNU-Linux distribution, is not known.
    # Comparison with the validate_and_copy_ecf_ogd_players_post_2006_rules()
    # method in the sibling module sqlite3ecfogddataimport, which worked on
    # OpenBSD 5.7 as it stood, highlighted the changes needed.
    # ecfdate = widget.get_ecf_date()

    if not ecffile:
        return False
    if not ecfdate:
        return False

    results = widget.get_appsys().get_results_database()
    if not results:
        return False

    results.do_database_task(
        import_method,
        logwidget=logwidget,
        taskmethodargs=dict(
            ecffile=ecffile,
            ecfdate=ecfdate,
            parent=widget.get_widget(),
            # datecontrol=widget.ecfdatecontrol.get(),
            datecontrol=datecontrol,  # See --enable-threads comment just above.
        ),
        use_specification_items=specification_items,
    )

    return True


def copy_ecf_players_post_2020_rules(
    widget, logwidget=None, ecfdata=None, downloaddate=None
):
    """Import a new ECF player file.

    widget - the manager object for the ecf data import tab

    """
    return _do_ecf_downloaded_data_import(
        widget.get_appsys()
        .get_ecfdataimport_module()
        .copy_ecf_players_post_2020_rules,
        widget,
        logwidget=logwidget,
        specification_items={
            filespec.ECFPLAYER_FILE_DEF,
            filespec.MAPECFPLAYER_FILE_DEF,
            filespec.ECFTXN_FILE_DEF,
        },
        ecfdata=ecfdata,
        downloaddate=downloaddate,
    )


def copy_ecf_clubs_post_2020_rules(
    widget, logwidget=None, ecfdata=None, downloaddate=None
):
    """Import a new ECF club file.

    widget - the manager object for the ecf data import tab

    """
    return _do_ecf_downloaded_data_import(
        widget.get_appsys()
        .get_ecfdataimport_module()
        .copy_ecf_clubs_post_2020_rules,
        widget,
        logwidget=logwidget,
        specification_items={
            filespec.ECFCLUB_FILE_DEF,
            filespec.ECFTXN_FILE_DEF,
        },
        ecfdata=ecfdata,
        downloaddate=downloaddate,
    )


def copy_ecf_players_post_2011_rules(
    widget, logwidget=None, ecfdate=None, datecontrol=None
):
    """Import a new ECF player file.

    widget - the manager object for the ecf data import tab

    """
    return _do_ecf_reference_data_import(
        widget.get_appsys()
        .get_ecfdataimport_module()
        .copy_ecf_players_post_2011_rules,
        widget,
        logwidget=logwidget,
        specification_items={
            filespec.ECFPLAYER_FILE_DEF,
            filespec.MAPECFPLAYER_FILE_DEF,
            filespec.ECFTXN_FILE_DEF,
        },
        ecfdate=ecfdate,
        datecontrol=datecontrol,
    )


def copy_ecf_clubs_post_2011_rules(
    widget, logwidget=None, ecfdate=None, datecontrol=None
):
    """Import a new ECF club file.

    widget - the manager object for the ecf data import tab

    """
    return _do_ecf_reference_data_import(
        widget.get_appsys()
        .get_ecfdataimport_module()
        .copy_ecf_clubs_post_2011_rules,
        widget,
        logwidget=logwidget,
        specification_items={
            filespec.ECFCLUB_FILE_DEF,
            filespec.ECFTXN_FILE_DEF,
        },
        ecfdate=ecfdate,
        datecontrol=datecontrol,
    )

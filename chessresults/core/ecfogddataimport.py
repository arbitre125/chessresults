# ecfogddataimport.py
# Copyright 2013 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Extract player data from ECF Online Grading Database download files.

The Online Grading Database download file is roughly equivalent in content to
the printed Grading List.  It contains all players who have played at least
one graded game in the most recent three completed seasons.  Toward the end of
the 2012-2013 season the downloadable online membership list became available
in a reliable form.  This module follows the ecfdataimport.py style to allow
addition of this source to the menu.

"""

from . import filespec


def _do_ecf_ogd_data_import(
    import_method, widget, logwidget=None, specification_items=None):
    """Import a new ECF club file.

    widget - the manager object for the ecf data import tab

    """
    ecffile = widget.datagrid.get_data_source().dbhome

    if not ecffile: return False

    results = widget.get_appsys().get_results_database()
    if not results: return False

    results.do_database_task(
        import_method,
        logwidget=logwidget,
        taskmethodargs=dict(
            ecffile=ecffile,
            parent=widget.get_widget(),
            ),
        use_specification_items=specification_items,
        )

    return True


def copy_ecf_ogd_players_post_2006_rules(widget, logwidget=None):
    """Import a new ECF downloadable OGD player file.

    widget - the manager object for the ecf data import tab

    """
    return _do_ecf_ogd_data_import(
        widget.get_appsys().get_ecfogddataimport_module(
            ).copy_ecf_ogd_players_post_2006_rules,
        widget,
        logwidget=logwidget,
        specification_items={
            filespec.ECFOGDPLAYER_FILE_DEF,
            filespec.MAPECFOGDPLAYER_FILE_DEF,
            },
        )

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

from .. import filespec
from .. import constants


def _do_ecf_ogd_data_import(
    import_method,
    widget,
    playercode_field=None,
    playername_field=None,
    playerclubs_fields=None,
    logwidget=None,
    specification_items=None,
):
    """Import a new ECF club file.

    widget - the manager object for the ecf data import tab

    """
    ecffile = widget.datagrid.get_data_source().dbhome

    if not ecffile:
        return False

    results = widget.get_appsys().get_results_database()
    if not results:
        return False

    results.do_database_task(
        import_method,
        logwidget=logwidget,
        taskmethodargs=dict(
            ecffile=ecffile,
            parent=widget.get_widget(),
            playercode_field=playercode_field,
            playername_field=playername_field,
            playerclubs_fields=playerclubs_fields,
        ),
        use_specification_items=specification_items,
    )

    return True


def validate_and_copy_ecf_ogd_players_post_2006_rules(widget, logwidget=None):
    """Import a new ECF downloadable OGD grading list csv file.

    widget - the manager object for the ecf data import tab.

    Downloads were produced in this format until mid-2020.

    """
    return _do_ecf_ogd_data_import(
        widget.get_appsys()
        .get_ecfogddataimport_module()
        .validate_and_copy_ecf_ogd_players_post_2006_rules,
        widget,
        playercode_field=constants.ECF_OGD_PLAYERCODE_FIELD,
        playername_field=constants.ECF_OGD_PLAYERNAME_FIELD,
        playerclubs_fields=constants.ECF_OGD_PLAYERCLUBS_FIELDS,
        logwidget=logwidget,
        specification_items={
            filespec.ECFOGDPLAYER_FILE_DEF,
            filespec.MAPECFOGDPLAYER_FILE_DEF,
        },
    )


def copy_ecf_ord_players_post_2006_rules(widget, logwidget=None):
    """Import a new ECF downloadable OGD rating list csv file.

    widget - the manager object for the ecf data import tab.

    Downloads have been produced in this format since mid-2020.

    These are available for all lists since 1994 according to
    ecfrating.org.uk/v2/help/help_api.php at 20 March 2022,

    """
    return _do_ecf_ogd_data_import(
        widget.get_appsys()
        .get_ecfogddataimport_module()
        .validate_and_copy_ecf_ogd_players_post_2006_rules,
        widget,
        playercode_field=constants.ECF_ORD_PLAYERCODE_FIELD,
        playername_field=constants.ECF_ORD_PLAYERNAME_FIELD,
        playerclubs_fields=constants.ECF_ORD_PLAYERCLUBS_FIELDS,
        logwidget=logwidget,
        specification_items={
            filespec.ECFOGDPLAYER_FILE_DEF,
            filespec.MAPECFOGDPLAYER_FILE_DEF,
        },
    )

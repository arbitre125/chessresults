# filespec.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Files and fields for results database.

Specification for Berkeley DB, DPT, and Sqlite3, databases.

"""

from solentware_base.core.constants import (
    PRIMARY, SECONDARY, DEFER,
    BTOD_FACTOR, DEFAULT_RECORDS, DEFAULT_INCREASE_FACTOR, BTOD_CONSTANT,
    DDNAME, FILE, FOLDER, FIELDS, FILEDESC,
    FLT, INV, UAE, ORD, ONM, SPT, EO, RRN,
    BSIZE, BRECPPG, BRESERVE, BREUSE,
    DSIZE, DRESERVE, DPGSRES, FILEORG,
    DPT_PRIMARY_FIELD_LENGTH,
    )
import solentware_base.core.filespec

# Names used to refer to files fields and indexes in Python code.
# The primary field name is used as the file name.
# file descriptions
EVENT_FILE_DEF = 'event'
GAME_FILE_DEF = 'game'
NAME_FILE_DEF = 'name'
PLAYER_FILE_DEF = 'player'
ECFPLAYER_FILE_DEF = 'ECFplayer'
ECFCLUB_FILE_DEF = 'ECFclub'
ECFTXN_FILE_DEF = 'ECFtxn'
MAPECFCLUB_FILE_DEF = 'mapECFclub'
MAPECFPLAYER_FILE_DEF = 'mapECFplayer'
ECFEVENT_FILE_DEF = 'ECFevent'
ECFOGDPLAYER_FILE_DEF = 'ECFOGDplayer'
MAPECFOGDPLAYER_FILE_DEF = 'mapECFOGDplayer'
# event file
EVENT_FIELD_DEF = EVENT_FILE_DEF
EVENTIDENTITY_FIELD_DEF = 'eventidentity'
EVENTNAME_FIELD_DEF = 'eventname'
EVENTCODE_FIELD_DEF = 'eventcode'
STARTDATE_FIELD_DEF = 'startdate'
ENDDATE_FIELD_DEF = 'enddate'
# game file
GAME_FIELD_DEF = GAME_FILE_DEF
GAMEEVENT_FIELD_DEF = 'gameevent'
GAMEPLAYER_FIELD_DEF = 'gameplayer'
GAMESECTION_FIELD_DEF = 'gamesection'
GAMEDATE_FIELD_DEF = 'gamedate'
# name file (lookup for encoded text values)
NAME_FIELD_DEF = NAME_FILE_DEF
CODE_FIELD_DEF = 'code'
NAMETEXT_FIELD_DEF = 'nametext'
# player file
PLAYER_FIELD_DEF = PLAYER_FILE_DEF
PLAYERIDENTITY_FIELD_DEF = 'playeridentity'
PLAYERALIAS_FIELD_DEF = 'playeralias'
PLAYERNEW_FIELD_DEF = 'playernew'
PLAYERPARTIALNEW_FIELD_DEF = 'playerpartialnew'
PLAYERPARTIALNAME_FIELD_DEF = 'playerpartialname'
PLAYERNAME_FIELD_DEF = 'playername'
PLAYERNAMENEW_FIELD_DEF = 'playernamenew'
PLAYERNAMEIDENTITY_FIELD_DEF = 'playernameidentity'
# ECFplayer file
ECFPLAYER_FIELD_DEF = ECFPLAYER_FILE_DEF
ECFPLAYERCODE_FIELD_DEF = 'ECFplayercode'
ECFPLAYERNAME_FIELD_DEF = 'ECFplayername'
ECFCURRENTPLAYER_FIELD_DEF = 'ECFcurrentplayer'
ECFCURRENTPLAYERCODE_FIELD_DEF = 'ECFcurrentplayercode'
# ECFclub file
ECFCLUB_FIELD_DEF = ECFCLUB_FILE_DEF
ECFCLUBCODE_FIELD_DEF = 'ECFclubcode'
ECFCLUBNAME_FIELD_DEF = 'ECFclubname'
ECFCURRENTCLUB_FIELD_DEF = 'ECFcurrentclub'
ECFCURRENTCLUBCODE_FIELD_DEF = 'ECFcurrentclubcode'
# ECFtxn file
ECFTXN_FIELD_DEF = ECFTXN_FILE_DEF
ECFDATE_FIELD_DEF = 'ECFdate'
# mapECFclub file
MAPECFCLUB_FIELD_DEF = MAPECFCLUB_FILE_DEF
CLUBCODE_FIELD_DEF = 'clubcode'
PLAYERALIASID_FIELD_DEF = 'playeraliasid'
PLAYERALIASMAP_FIELD_DEF = 'playeraliasmap'
# mapECFplayer file
MAPECFPLAYER_FIELD_DEF = MAPECFPLAYER_FILE_DEF
PERSONCODE_FIELD_DEF = 'personcode'
PERSONID_FIELD_DEF = 'personid'
PERSONMAP_FIELD_DEF = 'personmap'
# ECFevent file
ECFEVENT_FIELD_DEF = ECFEVENT_FILE_DEF
ECFEVENTIDENTITY_FIELD_DEF = 'ECFeventidentity'
# ECFOGDplayer file
ECFOGDPLAYER_FIELD_DEF = ECFOGDPLAYER_FILE_DEF
OGDPLAYERCODE_FIELD_DEF = 'OGDplayercode'
OGDPLAYERCODEPUBLISHED_FIELD_DEF = 'OGDplayercodepublished'
OGDPLAYERNAME_FIELD_DEF = 'OGDplayername'
# mapECFOGDplayer file
MAPECFOGDPLAYER_FIELD_DEF = MAPECFOGDPLAYER_FILE_DEF
OGDPERSONCODE_FIELD_DEF = 'OGDpersoncode'
#OGDpersonid = 'OGDpersonid'
OGDPERSONID_FIELD_DEF = 'OGDpersonid'


class FileSpec(solentware_base.core.filespec.FileSpec):

    """Specify the results database.
    """

    def __init__(self, use_specification_items=None, dpt_records=None, **kargs):

        dptfn = FileSpec.dpt_dsn
        fn = FileSpec.field_name
        
        super(FileSpec, self).__init__(
            use_specification_items=use_specification_items,
            dpt_records=dpt_records,
            **{
                EVENT_FILE_DEF: {
                    DDNAME: 'EVENT',
                    FILE: dptfn(EVENT_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 10,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 1,
                    BTOD_CONSTANT: 30,
                    DEFAULT_RECORDS: 200,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(EVENT_FIELD_DEF),
                    SECONDARY: {
                        EVENTIDENTITY_FIELD_DEF: None,
                        EVENTNAME_FIELD_DEF: None,
                        EVENTCODE_FIELD_DEF: None,
                        STARTDATE_FIELD_DEF: None,
                        ENDDATE_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(EVENT_FIELD_DEF): None,
                        fn(EVENTIDENTITY_FIELD_DEF): {INV:True, ORD:True},
                        fn(EVENTNAME_FIELD_DEF): {INV:True, ORD:True},
                        fn(EVENTCODE_FIELD_DEF): {INV:True, ORD:True},
                        fn(STARTDATE_FIELD_DEF): {INV:True, ORD:True},
                        fn(ENDDATE_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                GAME_FILE_DEF: {
                    DDNAME: 'GAME',
                    FILE: dptfn(GAME_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 45,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 0.2,
                    BTOD_CONSTANT: 30,
                    DEFAULT_RECORDS: 40000,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(GAME_FIELD_DEF),
                    SECONDARY: {
                        GAMEEVENT_FIELD_DEF: None,
                        GAMEPLAYER_FIELD_DEF: None,
                        GAMESECTION_FIELD_DEF: None,
                        GAMEDATE_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(GAME_FIELD_DEF): None,
                        fn(GAMEEVENT_FIELD_DEF): {INV:True, ORD:True},
                        fn(GAMEPLAYER_FIELD_DEF): {INV:True, ORD:True},
                        fn(GAMESECTION_FIELD_DEF): {INV:True, ORD:True},
                        fn(GAMEDATE_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                NAME_FILE_DEF: {
                    DDNAME: 'NAME',
                    FILE: dptfn(NAME_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 100,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 1,
                    BTOD_CONSTANT: 30,
                    DEFAULT_RECORDS: 500,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(NAME_FIELD_DEF),
                    SECONDARY: {
                        CODE_FIELD_DEF: None,
                        NAMETEXT_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(NAME_FIELD_DEF): None,
                        fn(CODE_FIELD_DEF): {INV:True, ORD:True},
                        fn(NAMETEXT_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                PLAYER_FILE_DEF: {
                    DDNAME: 'PLAYER',
                    FILE: dptfn(PLAYER_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 80,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 2.0,
                    BTOD_CONSTANT: 50,
                    DEFAULT_RECORDS: 100000,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(PLAYER_FIELD_DEF),
                    SECONDARY: {
                        PLAYERIDENTITY_FIELD_DEF: None,
                        PLAYERALIAS_FIELD_DEF: None,
                        PLAYERNEW_FIELD_DEF: None,
                        PLAYERPARTIALNEW_FIELD_DEF: None,
                        PLAYERPARTIALNAME_FIELD_DEF: None,
                        PLAYERNAME_FIELD_DEF: None,
                        PLAYERNAMENEW_FIELD_DEF: None,
                        PLAYERNAMEIDENTITY_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(PLAYER_FIELD_DEF): None,
                        fn(PLAYERIDENTITY_FIELD_DEF): {INV:True, ORD:True},
                        fn(PLAYERALIAS_FIELD_DEF): {INV:True, ORD:True},
                        fn(PLAYERNEW_FIELD_DEF): {INV:True, ORD:True},
                        fn(PLAYERPARTIALNEW_FIELD_DEF): {INV:True, ORD:True},
                        fn(PLAYERPARTIALNAME_FIELD_DEF): {INV:True, ORD:True},
                        fn(PLAYERNAME_FIELD_DEF): {INV:True, ORD:True},
                        fn(PLAYERNAMENEW_FIELD_DEF): {INV:True, ORD:True},
                        fn(PLAYERNAMEIDENTITY_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                ECFPLAYER_FILE_DEF: {
                    DDNAME: 'ECFPLAYR',
                    FILE: dptfn(ECFPLAYER_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 75,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 1.0,
                    BTOD_CONSTANT: 100,
                    DEFAULT_RECORDS: 15000,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(ECFPLAYER_FIELD_DEF),
                    SECONDARY: {
                        ECFPLAYERCODE_FIELD_DEF: None,
                        ECFPLAYERNAME_FIELD_DEF: None,
                        ECFCURRENTPLAYER_FIELD_DEF: None,
                        ECFCURRENTPLAYERCODE_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(ECFPLAYER_FIELD_DEF): None,
                        fn(ECFPLAYERCODE_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFPLAYERNAME_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFCURRENTPLAYER_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFCURRENTPLAYERCODE_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                ECFCLUB_FILE_DEF: {
                    DDNAME: 'ECFCLUB',
                    FILE: dptfn(ECFCLUB_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 100,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 1.5,
                    BTOD_CONSTANT: 50,
                    DEFAULT_RECORDS: 5000,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(ECFCLUB_FIELD_DEF),
                    SECONDARY: {
                        ECFCLUBCODE_FIELD_DEF: None,
                        ECFCLUBNAME_FIELD_DEF: None,
                        ECFCURRENTCLUB_FIELD_DEF: None,
                        ECFCURRENTCLUBCODE_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(ECFCLUB_FIELD_DEF): None,
                        fn(ECFCLUBCODE_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFCLUBNAME_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFCURRENTCLUB_FIELD_DEF): {INV:True, ORD:True},
                        fn(ECFCURRENTCLUBCODE_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                ECFTXN_FILE_DEF: {
                    DDNAME: 'ECFTXN',
                    FILE: dptfn(ECFTXN_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 80,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 1,
                    BTOD_CONSTANT: 800,
                    DEFAULT_RECORDS: 800,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(ECFTXN_FIELD_DEF),
                    SECONDARY: {
                        ECFDATE_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(ECFTXN_FIELD_DEF): None,
                        fn(ECFDATE_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                MAPECFCLUB_FILE_DEF: {
                    DDNAME: 'MAPCLUB',
                    FILE: dptfn(MAPECFCLUB_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 50,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 6,
                    BTOD_CONSTANT: 800,
                    DEFAULT_RECORDS: 10000,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(MAPECFCLUB_FIELD_DEF),
                    SECONDARY: {
                        CLUBCODE_FIELD_DEF: None,
                        PLAYERALIASID_FIELD_DEF: None,
                        PLAYERALIASMAP_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(MAPECFCLUB_FIELD_DEF): None,
                        fn(CLUBCODE_FIELD_DEF): {INV:True, ORD:True},
                        fn(PLAYERALIASID_FIELD_DEF): {INV:True, ORD:True},
                        fn(PLAYERALIASMAP_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                MAPECFPLAYER_FILE_DEF: {
                    DDNAME: 'MAPPLAYR',
                    FILE: dptfn(MAPECFPLAYER_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 50,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 6,
                    BTOD_CONSTANT: 800,
                    DEFAULT_RECORDS: 10000,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(MAPECFPLAYER_FIELD_DEF),
                    SECONDARY: {
                        PERSONCODE_FIELD_DEF: None,
                        PERSONID_FIELD_DEF: None,
                        PERSONMAP_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(MAPECFPLAYER_FIELD_DEF): None,
                        fn(PERSONCODE_FIELD_DEF): {INV:True, ORD:True},
                        fn(PERSONID_FIELD_DEF): {INV:True, ORD:True},
                        fn(PERSONMAP_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                ECFEVENT_FILE_DEF: {
                    DDNAME: 'ECFEVENT',
                    FILE: dptfn(ECFEVENT_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 10,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 2,
                    BTOD_CONSTANT: 800,
                    DEFAULT_RECORDS: 200,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(ECFEVENT_FIELD_DEF),
                    SECONDARY: {
                        ECFEVENTIDENTITY_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(ECFEVENT_FIELD_DEF): None,
                        fn(ECFEVENTIDENTITY_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                ECFOGDPLAYER_FILE_DEF: {
                    DDNAME: 'OGDPLAYR',
                    FILE: dptfn(ECFOGDPLAYER_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 75,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 1.0,
                    BTOD_CONSTANT: 200,
                    DEFAULT_RECORDS: 15000,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(ECFOGDPLAYER_FIELD_DEF),
                    SECONDARY: {
                        OGDPLAYERCODE_FIELD_DEF: None,
                        OGDPLAYERCODEPUBLISHED_FIELD_DEF: None,
                        OGDPLAYERNAME_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(ECFOGDPLAYER_FIELD_DEF): None,
                        fn(OGDPLAYERCODE_FIELD_DEF): {INV:True, ORD:True},
                        fn(OGDPLAYERCODEPUBLISHED_FIELD_DEF): {
                            INV:True, ORD:True},
                        fn(OGDPLAYERNAME_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                MAPECFOGDPLAYER_FILE_DEF: {
                    DDNAME: 'MAPOGDPL',
                    FILE: dptfn(MAPECFOGDPLAYER_FILE_DEF),
                    FILEDESC: {
                        BRECPPG: 50,
                        FILEORG: RRN,
                        },
                    BTOD_FACTOR: 6,
                    BTOD_CONSTANT: 800,
                    DEFAULT_RECORDS: 10000,
                    DEFAULT_INCREASE_FACTOR: 0.01,
                    PRIMARY: fn(MAPECFOGDPLAYER_FIELD_DEF),
                    SECONDARY: {
                        OGDPERSONCODE_FIELD_DEF: None,
                        OGDPERSONID_FIELD_DEF: None,
                        },
                    FIELDS: {
                        fn(MAPECFOGDPLAYER_FIELD_DEF): None,
                        fn(OGDPERSONCODE_FIELD_DEF): {INV:True, ORD:True},
                        fn(OGDPERSONID_FIELD_DEF): {INV:True, ORD:True},
                        },
                    },
                }
            )

# constants.py
# Copyright 2008 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Constants used in Results application.
"""

# Keys in <key>=<value> in data transfer files. Value ended by '\n'.
_event = "event"
_startdate = "startdate"
_enddate = "enddate"
_eventsection = "eventsection"
_eventsections = "eventsections"
_homeplayerwhite = "homeplayerwhite"
_date = "date"
_board = "board"
_round = "round"
_hometeam = "hometeam"
_awayteam = "awayteam"
_section = "section"
_sections = "sections"
_homeplayer = "homeplayer"
_homename = "homename"
_homepin = "homepin"
_homepinfalse = "homepinfalse"
_homeaffiliation = "homeaffiliation"
_homereportedcodes = "homereportedcodes"
_awayplayer = "awayplayer"
_awayname = "awayname"
_awaypin = "awaypin"
_awaypinfalse = "awaypinfalse"
_awayaffiliation = "awayaffiliation"
_awayreportedcodes = "awayreportedcodes"
_result = "result"
_name = "name"
_pin = "pin"
_pinfalse = "pinfalse"
_affiliation = "affiliation"
_exportedeventplayer = "exportedeventplayer"
_exportedplayer = "exportedplayer"
_player = "player"
_aliases = "aliases"
_newidentity = "newidentity"
_knownidentity = "knownidentity"
_sectionname = "sectionname"
_uniquesection = "uniquesection"
_serial = "serial"
_homeserial = "homeserial"
_awayserial = "awayserial"
_identified = "identified"

# To figure out team names and affiliations'''
_names = "names"

# Chosen way of presenting game results in readable format.'''
_tbr = "tbr"
# _loss = '0-1'
# _draw = 'draw'
# _win = '1-0'
_awaydefault = "1-def"
_homedefault = "def-1"
_void = "void"
_winbye = "bye+"
_drawbye = "bye="
_white = "w"
_black = ""
_nocolor = ""
_white_on_all = "whiteonall"
_black_on_all = "blackonall"
_black_on_odd = "blackonodd"
_white_on_odd = "whiteonodd"
_color_not_specified = "notspecified"

# Encoding of values used on ECF submission files.
result_01 = "01"
result_55 = "55"
result_10 = "10"
colour_white = "white"
colour_black = "black"
colour_w = "w"
colour_b = ""
colourdefault_all = "all"
colourdefault_even = "even"
colourdefault_none = "none"
colourdefault_odd = "odd"
colourdefault_unknown = "unknown"
"""The Results File Field Definitions document (FieldDef.htm dated Oct 2006)
reserves PIN PIN1 and PIN2 value "0" for use with results encoded by the SCORE
values "d1" "d5" and "dd".

This conflicts with the use of database record numbers as PIN PIN1 and PIN2
values for database engines which use 0 as a record number (after use of the
standard conversion of integer to string).

The ECF submission file generator will replace "0" by "zero_not_0" in PIN PIN1
and PIN2 to comply with the convention.

It is hoped that this value will provide those who look at the submission file
with a sufficient clue to what is going on: and at least assure them that it
is not a mistake.

It is also hoped that "zero_not_0" is a sufficiently unusual value that it will
not be used by other grading programs as a valid PIN separate from "0".  Thus
avoiding problems that may arise from the conventional use of "zero_not_0" by
this program to cope with the ECF submission file conventional use of "0".
"""
zero_not_0 = "zero_not_0"

# Encoding of values used on league database extract.
result_0 = "0"
result_1 = "1"
result_2 = "2"
result_3 = "3"
result_4 = "4"
result_5 = "5"
result_6 = "6"
result_7 = "7"
result_8 = "8"
colour_0 = "0"
colour_1 = "1"
colour_2 = "2"
colourdefault_0 = "0"
colourdefault_1 = "1"
colourdefault_2 = "2"
colourdefault_3 = "3"
colourdefault_4 = "4"

# Games with following results are stored on database
# Maybe move to gameresults
# _storeresults = {_loss:None, _draw:None, _win:None}

# Keys used on league database extract
ECODE = "ECODE"
ENAME = "ENAME"
EBCF = "EBCF"
EDATE = "EDATE"
EFINALDATE = "EFINALDATE"
ESUBMISSION = "ESUBMISSION"
ETREASURER = "ETREASURER"
EADDRESS1 = "EADDRESS1"
EADDRESS2 = "EADDRESS2"
EADDRESS3 = "EADDRESS3"
EADDRESS4 = "EADDRESS4"
EPOSTCODE = "EPOSTCODE"
EGRADER = "EGRADER"
EGADDRESS1 = "EGADDRESS1"
EGADDRESS2 = "EGADDRESS2"
EGADDRESS3 = "EGADDRESS3"
EGADDRESS4 = "EGADDRESS4"
EGPOSTCODE = "EGPOSTCODE"
EFIRSTMOVES = "EFIRSTMOVES"
EFIRSTMINUTES = "EFIRSTMINUTES"
ENEXTMOVES = "ENEXTMOVES"
ENEXTMINUTES = "ENEXTMINUTES"
ERESTMINUTES = "ERESTMINUTES"
EALLMINUTES = "EALLMINUTES"
ESECPERMOVE = "ESECPERMOVE"
EADJUDICATED = "EADJUDICATED"
EGRANDPRIX = "EGRANDPRIX"
EFIDE = "EFIDE"
ECHESSMOVES = "ECHESSMOVES"
EEAST = "EEAST"
EMIDLAND = "EMIDLAND"
ENORTH = "ENORTH"
ESOUTH = "ESOUTH"
EWEST = "EWEST"
ECOLOR = "ECOLOR"
CCODE = "CCODE"
CNAME = "CNAME"
CBCF = "CBCF"
CBCFCOUNTY = "CBCFCOUNTY"
PCODE = "PCODE"
PNAME = "PNAME"
PBCF = "PBCF"
PDOB = "PDOB"
PGENDER = "PGENDER"
PDIRECT = "PDIRECT"
PTITLE = "PTITLE"
PFIDE = "PFIDE"
PLENFORENAME = "PLENFORENAME"
PLENNICKNAME = "PLENNICKNAME"
MCODE = "MCODE"
MNAME = "MNAME"
MDATE = "MDATE"
MTYPE = "MTYPE"
MCOLOR = "MCOLOR"
MUSEEVENTDATE = "MUSEEVENTDATE"
TCODE1 = "TCODE1"
TCODE2 = "TCODE2"
GROUND = "GROUND"
GBOARD = "GBOARD"
GCODE = "GCODE"
PCODE1 = "PCODE1"
PCODE2 = "PCODE2"
GCOLOR = "GCOLOR"
GRESULT = "GRESULT"
GDATE = "GDATE"
GUSEMATCHDATE = "GUSEMATCHDATE"
TCODE = "TCODE"
TNAME = "TNAME"
RPAIRING = "RPAIRING"
represent = "represent"
club = "clu"
player = "player"
game = "game"
affiliate = "affiliate"
team = "team"
event = "event"
match = "match"

# Dictionary key for values extracted from submission files or league
# database extract. These keys are the same as field names on League database
# unless the value is used in the results database structure
_ecode = ECODE
_ename = _event  # ENAME
_edate = _startdate  # EDATE
_efinaldate = _enddate  # EFINALDATE
_pcode = PCODE
_pname = _player  # PNAME
_mcode = MCODE
_mname = MNAME
_mdate = MDATE
_pcode1 = PCODE1
_pcode2 = PCODE2
_gcode = GCODE
_ground = _round  # GROUND
_gboard = _board  # GBOARD
_gcolor = GCOLOR
_gresult = _result  # GRESULT
_gdate = _date  # GDATE
_mcolor = MCOLOR
_mtype = MTYPE
_cname = CNAME
_ccode = CCODE
_tcode = TCODE
_tcode1 = TCODE1
_tcode2 = TCODE2
_tname = TNAME
_rpairing = RPAIRING
_plennickname = PLENNICKNAME
_plenforename = PLENFORENAME

# Keys used on ECF submission files

# Those used in ECF submissions generated by this package
EVENT_DETAILS = "EVENT DETAILS"
EVENT_CODE = "EVENT CODE"
EVENT_NAME = "EVENT NAME"
SUBMISSION_INDEX = "SUBMISSION INDEX"
EVENT_DATE = "EVENT DATE"
FINAL_RESULT_DATE = "FINAL RESULT DATE"
RESULTS_OFFICER = "RESULTS OFFICER"
RESULTS_OFFICER_ADDRESS = "RESULTS OFFICER ADDRESS"
TREASURER = "TREASURER"
TREASURER_ADDRESS = "TREASURER ADDRESS"
MOVES_FIRST_SESSION = "MOVES FIRST SESSION"
MINUTES_FIRST_SESSION = "MINUTES FIRST SESSION"
MOVES_SECOND_SESSION = "MOVES SECOND SESSION"
MINUTES_SECOND_SESSION = "MINUTES SECOND SESSION"
MINUTES_REST_OF_GAME = "MINUTES REST OF GAME"
MINUTES_FOR_GAME = "MINUTES FOR GAME"
SECONDS_PER_MOVE = "SECONDS PER MOVE"
ADJUDICATED = "ADJUDICATED"
INFORM_GRAND_PRIX = "INFORM GRAND PRIX"
INFORM_FIDE = "INFORM FIDE"
INFORM_CHESSMOVES = "INFORM CHESSMOVES"
INFORM_UNION = "INFORM UNION"
PLAYER_LIST = "PLAYER LIST"
PIN = "PIN"
BCF_CODE = "BCF CODE"
NAME = "NAME"
BCF_CODE = "BCF CODE"
CLUB = "CLUB"
CLUB_CODE = "CLUB CODE"
CLUB_COUNTY = "CLUB COUNTY"
MATCH_RESULTS = "MATCH RESULTS"
SECTION_RESULTS = "SECTION RESULTS"
OTHER_RESULTS = "OTHER RESULTS"
WHITE_ON = "WHITE ON"
PIN1 = "PIN1"
SCORE = "SCORE"
PIN2 = "PIN2"
ROUND = "ROUND"
GAME_DATE = "GAME DATE"
BOARD = "BOARD"
COLOUR = "COLOUR"
FINISH = "FINISH"

# Those available for use in ECF submissions (so merges.py must know)
RESULTS_DATE = "RESULTS DATE"
SURNAME = "SURNAME"
INITIALS = "INITIALS"
FORENAME = "FORENAME"
BCF_NO = "BCF NO"
CLUB_NAME = "CLUB NAME"
COMMENT = "COMMENT"
DATE_OF_BIRTH = "DATE OF BIRTH"
FIDE_NO = "FIDE NO"
GENDER = "GENDER"
RESULTS_DUPLICATED = "RESULTS DUPLICATED"
TITLE = "TITLE"
TABLE_END = "TABLE END"
TABLE_START = "TABLE START"
COLUMN = "COLUMN"

# Submission files earlier than about 2001 may use SURNAME FORENAME and
# INITIALS instead of NAME. Used to build PNAME if necessary.
_surname = SURNAME
_forename = FORENAME
_initials = INITIALS

# Used by control.py
_resultsdata = "games"
_ecfdata = "data"

# Used by merges.py preparesource.py mainly
_grading_code_length = 7
_grading_code_check_characters = "ABCDEFGHJKL"
_section_is_match = "M"
_event_matches = "Event Matches"
_yes = "yes"
_no = "no"
TAKEON_ECF_FORMAT = "takeon_ecf_format"
TAKEON_LEAGUE_FORMAT = "takeon_league_format"
TAKEON_EXT = {".txt"}
TAKEON_SCHEDULE = "takeon_schedule"
TAKEON_REPORTS = "takeon_reports"
TAKEON_MATCH_RESULTS = "#MATCH RESULTS"
TAKEON_MATCH = "match"
LEAGUE_DATABASE_DATA = "league_database_data.txt"
LEAGUE_MATCH_TYPE = "M"
TOURNAMENT_TYPE = "T"
OTHER_TYPE = "O"

# Event configuration file.  This file is used rather than EXTRACTED_CONF from
# emailextract package.
EVENT_CONF = "event.conf"

# Default URLs to access ECF website.
# These are copied to a file, paired with a database, which may need editing
# if the ECF URLs change.
URL_NAMES = "URLnames_"
ACTIVE_CLUBS_URL = "active_clubs_url"
PLAYERS_RATINGS_URL = "players_ratings_url"
PLAYER_INFO_URL = "player_info_url"
CLUB_INFO_URL = "club_info_url"
DEFAULT_URLS = (
    (
        ACTIVE_CLUBS_URL,
        "https://www.ecfrating.org.uk/v2/new/api.php?v2/clubs/all_active",
    ),
    (
        PLAYERS_RATINGS_URL,
        "https://www.ecfrating.org.uk/v2/new/api.php?v2/players_ratings",
    ),
    (
        PLAYER_INFO_URL,
        "https://www.ecfrating.org.uk/v2/new/api.php?v2/players/code/",
    ),
    (
        CLUB_INFO_URL,
        "https://www.ecfrating.org.uk/v2/new/api.php?v2/clubs/code/",
    ),
)

# Structure of ECF json downloads.
A_C_CLUBS = "clubs"
ACTIVE_CLUBS_KEYS = frozenset(
    [
        A_C_CLUBS,
        "success",
        "processing_time",
        "total_processing_time_today",
        "max_processing_time_daily",
    ]
)
ACTIVE_CLUBS_ROW_KEY_NAMES = (
    "club_code",
    "club_name",
    "comment",
    "assoc_code",
    "assoc_name",
)
P_R_COLUMN_NAMES = "column_names"
P_R_PLAYERS = "players"
PLAYERS_RATINGS_KEYS = frozenset(
    [
        "rating_effective_date",
        "prior_rating_effective_date",
        P_R_COLUMN_NAMES,
        P_R_PLAYERS,
        "success",
        "processing_time",
        "total_processing_time_today",
        "max_processing_time_daily",
    ]
)
PLAYERS_RATINGS_COLUMN_NAMES = (
    "ECF_code",
    "member_no",
    "FIDE_no",
    "full_name",
    "ECF_junior",
    "FIDE_junior",
    "gender",
    "nation",
    "nation2",
    "date_last_game",
    "standard_original_rating",
    "standard_revised_rating",
    "standard_category",
    "standard_games_12m",
    "standard_games_24m",
    "standard_games_36m",
    "prior_standard_revised_rating",
    "prior_standard_category",
    "rapid_original_rating",
    "rapid_revised_rating",
    "rapid_category",
    "rapid_games_12m",
    "rapid_games_24m",
    "rapid_games_36m",
    "prior_rapid_revised_rating",
    "prior_rapid_category",
    "club_code",
    "club_name",
)

# players_html.py
# Copyright 2022 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Extract ECF code for ECF membership number from list players request.
"""

from html.parser import HTMLParser
import re

_row_identifier_re = re.compile(r"^\d+\.$")
_ecf_code_re = re.compile(r"^\d{6}[ABCDEFGHJKL]$")
_ecf_membership_number_re = re.compile(r"^\d{6}$")


class PlayersHTMLfeedMethodNotCalled(Exception):
    pass


class PlayersHTMLTooManyECFCodes(Exception):
    pass


class PlayersHTML(HTMLParser):

    """Parse a response to a list players request.

    Eyeballing the response suggests the relevant sequence of data items
    is 'Row identifier', 'ECF code', and 'ECF membership number'.  The
    response has all records which match the query but the initial display
    shows only those with a rating.  All rows seem to have 'Row identifier'
    and 'ECF code' but many are likely missing the 'ECF membership number'.

    The 'ECF membership number', if present, seems to be the third data item
    consisting of six digits.  Often, if not always, the third data item is
    '99' if it is not a 'ECF membership number'.

    """

    def __init__(self, ecf_membership_number, *a, **k):
        super().__init__(*a, **k)
        self._ecf_membership_number = ecf_membership_number
        self._ignore_data = 0
        self._data_row = []
        self._ecf_membership_number_rows = []
        self._feed_method_called = False

    def feed(self, data):
        self._feed_method_called = True
        super().feed(data)

    def handle_starttag(self, tag, attrs):
        if tag.strip() in {"script", "style"}:
            self._ignore_data += 1

    def handle_endtag(self, tag):
        if tag.strip() in {"script", "style"}:
            self._ignore_data -= 1

    def handle_startendtag(self, tag, attrs):
        super().handle_startendtag(tag, attrs)

    def handle_data(self, tag):
        if self._ignore_data:
            return
        ts = tag.strip()
        if not ts:
            self._data_row = []
            return
        match = _row_identifier_re.match(ts)
        if match:
            self._data_row = []
            self._data_row.append(match)
            return
        match = _ecf_code_re.match(ts)
        if match:
            if len(self._data_row) != 1:
                self._data_row = []
                return
            self._data_row.append(match)
            return
        match = _ecf_membership_number_re.match(ts)
        if match:
            if len(self._data_row) != 2:
                self._data_row = []
                return
            self._data_row.append(match)
            if self._ecf_membership_number == match.group():
                self._ecf_membership_number_rows.append(self._data_row)
            self._data_row = []
            return
        self._data_row = []
        return

    def handle_entityref(self, tag):
        pass

    def handle_charref(self, tag):
        pass

    def handle_comment(self, tag):
        pass

    def handle_decl(self, tag):
        pass

    def handle_pi(self, tag):
        pass

    def handle_unknown_decl(self, tag):
        pass

    def get_ecf_code(self):
        """Return ECF code associated with ECF membership number.

        The ECF membership number is given on initialisation of this object
        and the 'feed' method is assumed to have been called.

        The PlayersHTMLTooManyECFCodes exception is raised if more than one
        ECF code is found for the ECF membership number.

        """
        if not self._feed_method_called:
            raise PlayersHTMLfeedMethodNotCalled(
                "ParserHTML feed(data) method must be called"
            )
        if not self._ecf_membership_number_rows:
            return None
        if len(self._ecf_membership_number_rows) > 1:
            raise PlayersHTMLTooManyECFCodes(
                " ".join(
                    (
                        "More than one ECF code found for ECF membership number",
                        self._ecf_membership_number,
                    )
                )
            )
        return self._ecf_membership_number_rows[0][1].group()

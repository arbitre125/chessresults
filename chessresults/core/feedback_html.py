# feedback_html.py
# Copyright 2020 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Classes to extract feedback from website responses for monthly grading.
"""

from html.parser import HTMLParser
import re

_whitespace_at_end_re = re.compile(r".*\s+\Z", flags=re.DOTALL)
_whitespace_at_start_re = re.compile(r"\A\s+.*", flags=re.DOTALL)
_feedback_player_list_re = re.compile(
    r"".join(
        (
            r"\s+Submitted\s+Players\s+",
            r"(.*?)",
            r"\s+Submitted\s+Games\s+",
        )
    ),
    flags=re.DOTALL,
)
_submission_player_list_re = re.compile(
    r"".join(
        (
            r"\s*#\s*PlayerList\s*",
            r"(#\s*.*?)",
            r"\s*#\s*",
            r"(?:SectionResults|OtherResults|MatchResults)",
            r"\s*=\s*",
        )
    ),
    flags=re.DOTALL,
)
_feedback_number_re = re.compile(r"\s+\d+\.\s+", flags=re.DOTALL)
_submission_pin_re = re.compile(r"#PIN=\d+", flags=re.DOTALL)

# Defined to redact expected date formats.
_yyyy_mm_dd_re = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", flags=re.DOTALL)
_dd_mm_yyyy_re = re.compile(r"[0-9]{2}/[0-9]{2}/[0-9]{4}", flags=re.DOTALL)

# If Issues exist the feedback should not be used to update local database.
# These seem to be identified with tag 'tr' attribute _CLASS_ISSUE.
_CLASS_ISSUE = ("class", "issue")


class FeedbackHTML(HTMLParser):

    """Parse a feedback file."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.feedbackdata = []
        self.feedbackstring = ""
        self.feedbacknumbers = None
        self.feedbackplayers = None
        self.submissionpins = None
        self.submissionplayers = None
        self._ignore_data = 0
        self.submission_file_name = None
        self.responsestring = None
        self.issues_exist = False

    def insert_whitespace_and_redact_dates(self):
        """Insert " " separator if needed and redact dates in feedbackstring.

        feedbackdata has the actual response from ECF, but feedbackstring
        must have whitespace between the elements from feedbackdata, and
        all dates nust be redacted to ensure any dates of birth are hidden.

        This application does not care about the dates, only the ECF codes.

        If you care about the dates, use a browser to do the action.

        Dates are expected to be patterns r'\d\d\d\d-\d\d-\d\d' or
        r'\d\d/\d\d/\d\d\d\d'.

        """
        fbd = self.feedbackdata
        if len(fbd):
            fbds = [fbd[0]]
        else:
            fbds = [""]
        for i in range(1, len(fbd) - 1):
            if (
                _whitespace_at_start_re.match(fbd[i]) is None
                and _whitespace_at_end_re.match(fbd[i - 1]) is None
            ):
                fbds.append(" ")
            fbds.append(fbd[i])
        self.feedbackstring = _dd_mm_yyyy_re.sub(
            "nn/nn/nnnn", _yyyy_mm_dd_re.sub("nnnn-nn-nn", r"".join(fbds))
        )

    def find_player_lists(self):
        fbpl = _feedback_player_list_re.search(self.feedbackstring)
        spl = _submission_player_list_re.search(self.feedbackstring)
        if fbpl:
            self.feedbacknumbers = _feedback_number_re.findall(fbpl.group(1))
            self.feedbackplayers = _feedback_number_re.split(fbpl.group(1))
        if spl:
            self.submissionpins = _submission_pin_re.findall(spl.group(1))
            self.submissionplayers = _submission_pin_re.split(spl.group(1))

    def handle_starttag(self, tag, attrs):
        if str(tag) == "tr" and _CLASS_ISSUE in attrs:
            self.issues_exist = True
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
            return
        self.feedbackdata.append(ts)

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

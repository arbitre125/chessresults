# matchteams.py
# Copyright 2009 Roger Marsh
# Licence: See LICENCE (BSD licence)

"""Pick team names out of match names.

Assumptions are:
Team names are almost consistent between match names.
A team name appears at least once as first named team without any prefixes.
A team name appears at least once as second named team without any suffixes.

Complete accurracy is not essential.  It will usually be good enough to get
the club name right, or at least in the guessed team name, to assist in
player identification.

"""


class MatchTeams(object):
    """List of all pairs of non-empty contiguous subsets of words in a string.

    The string 'a b c d e f' produces 70 pairs.  Samples are (a, b) (b c, e f)
    (a b c, d e f).  But never (c d, a b) or (b c d, d e) reversing word order
    or using a word more than once in a pair.

    """

    def __init__(self, string="", split=True):
        """ """
        super().__init__()
        if not isinstance(string, str):
            if isinstance(string, (list, tuple)):
                string = " ".join(string)
            else:
                string = ""
        if split and string:
            self.string = " ".join(string.split())
            self.sentence = sentence = self.string.split()
            self.phrases = phrases = dict()
            self.position = position = dict()
            clauses = []
            for i in range(len(sentence)):
                for j in range(i + 1, len(sentence) + 1):
                    s = " ".join(sentence[i:j])
                    phrases[s] = phrases.setdefault(s, 0) + 1
                    position.setdefault(s, i)
                    clauses.append(s)
            self.clauses = clauses
            if len(sentence) == 1:
                self.teamsplits = [(self.string, self.string)]
            else:
                teamsplits = []
                position = self.position
                for t1, p1 in position.items():
                    len1 = len(t1.split())
                    for t2, p2 in position.items():
                        len2 = len(t2.split())
                        if p1 < p2 and p1 + len1 <= p2:
                            teamsplits.append((len1 * len2, (t1, t2)))
                self.teamsplits = [t[-1] for t in sorted(teamsplits)]
        else:
            self.string = " ".join(string.split())
            self.sentence = self.string.split()
            self.phrases = {self.string: 1}
            self.clauses = [self.string]
            self.position = {self.string: 0}
            self.teamsplits = [(self.string, self.string)]

    def __contains__(self, string):
        return string in self.phrases

    def count(self, string):
        return self.phrases.get(string, 0)

    def index(self, string):
        return self.clauses.index(string)

    def find(self, string):
        return self.position.get(string, -1)

    def __iter__(self):
        return self.clauses.__iter__()


import re
import pdb
import logging

#   Custom
from .constants import REGEX_FLAGS
from .regex_patterns import WHITESPACE_MAYBE_PATTERN, PUNC_PATTERN, BOUNDARY_PATTERN, BOUNDARY_PATTERN_L, BOUNDARY_PATTERN_R


LOGGER = logging.getLogger("base.regex_base")

def strip_whitespace(text):
    return re.sub(ur'\s+$', '', re.sub(ur'^\s+', '', text))


def match_all(
        s, regexes, names_groups,
        shortcircuit=True, ignore_submatches=True,
        ignore_errors=False, **regex_options
    ):
    res = []
    pos_matched = set()
    seen = set()
    for regex_, name_regex in regexes:
        matches = list(regex_.finditer(s, **regex_options))
        # print matches
        for count, m in enumerate(matches):
            for name_group in names_groups:
                name = (
                    '{0}_{1}'.format(name_regex, name_group)
                        if name_regex else name_group
                )
                try:
                    g = m.group(name_group)
                except IndexError as e:
                    #######################
                    if not ignore_errors:
                        LOGGER.error(
                            "{0}\t{1} : {2}".format(name_regex, e, name_group)
                        )
                        # pdb.set_trace()
                    #######################
                else:
                    idxs = m.span(name_group)
                    if idxs in pos_matched:     #   Skip duplicates
                        continue
                    pos_matched.add(idxs)
                    res.append(dict(
                        name    = name,
                        text    = g,
                        pos     = idxs,
                    ))
        if shortcircuit and matches:
            break
    #   Ignore matches which are substrings of existing matches.
    if ignore_submatches:
        res_ = []
        while res:
            m = res.pop()
            s1, e1 = m['pos']
            submatch = False
            for s2, e2 in pos_matched:
                if s1 >= s2 and e1 <= e2:
                    if s1 != s2 or e1 != e2:
                        submatch = True
                        break
            if not submatch:
                res_.append(m)
        res = res_
    res = sorted(res, key=lambda d: d['pos'])
    return res


def make_bdry_regex(pat, name):
    pat = ur"""
    (?:
        (?= ^|\b|{bdry}+ )      # Lookahead, don't consume text
        (?P<{name}> {pat} )
        (?= $|\b|{bdry}+ )      # Lookahead, don't consume text
    )
    """.format(
        bdry=BOUNDARY_PATTERN,
        pat=pat,
        name=name
    )
    _regex = re.compile(pat, flags=REGEX_FLAGS)
    return _regex

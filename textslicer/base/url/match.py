
#   Stdlib
import logging
import itertools
import re
import string
import os
import urlparse
from collections import defaultdict

#   Custom
from .constants_url import THIS_DIR, DEBUG
from ..regex_ import match_all, REGEX_FLAGS

##  ==========================GLOBAL CONSTANTS==============================

COMMON_SUBDOMAINS = set(['www', 'www2'])
COMMON_SUBDOMAINS_PATTERN = r"|".join('{0}'.format(d) for d in COMMON_SUBDOMAINS)

COMMON_DOMAINS = set()
with open(os.path.join(THIS_DIR, 'data', 'domains_shorten.txt'), 'rbU') as f:
    SHORTENER_DOMAINS = set([i.strip().strip('\n').replace('.', '\.') for i in f])
COMMON_DOMAINS |= SHORTENER_DOMAINS
COMMON_DOMAINS_PATTERN = r"|".join('(?:{0})'.format(d) for d in COMMON_DOMAINS)


PATH_CHARS = r"[\+~%\/\.\w\-]"
QS_CHARS = r"[\-\+=&;%@\.\w]"
ANCHOR_CHARS = r"[\.\!\/\\\w]"
PATH_PATTERN = r"""
    (?:\/{path_chars}*)?            # allow optional /path
    \??(?:{qs_chars}*)              # allow optional query string starting with ?
    \#?(?:{anchor_chars}*)          # allow optional anchor #anchor
""".format(
    path_chars=PATH_CHARS,
    qs_chars=QS_CHARS,
    anchor_chars=ANCHOR_CHARS,
)

URL_PATTERN = r"""
(?P<url>
    (?:                                 # brackets covering match for protocol (optional) and domain
        (?:[A-Za-z]{{3,9}}:(?:\/\/)?)   # match protocol, allow in format http:// or mailto:
        (?:[\-;:&=\+\$,\w]+@)?          # allow something@ for email addresses
        [A-Za-z0-9\.\-]+                # anything looking at all like a domain, non-unicode domains
        |
        (?:                             # or instead of above
            (?:
                (?:{subdomain})\.|[\-;:&=\+\$,\w]+@)   # starting with something@ or www.
                [A-Za-z0-9\.\-]+              # anything looking at all like a domain
            )
        )
    (?P<path>                   # brackets covering match for path, query string and anchor
        {path}
    )?                          # make URL suffix optional
)""".format(
    subdomain=COMMON_SUBDOMAINS_PATTERN,
    path=PATH_PATTERN
)
##########
# print URL_PATTERN
##########
URL_REGEX = re.compile(URL_PATTERN, flags=REGEX_FLAGS)

URL_PATTERN_2 = r"""
    (?P<url>            # one of the domains that we know about and a path.
        (?: {domain} )
        (?: {path} )
    )
""".format(
    domain=COMMON_DOMAINS_PATTERN,
    path=PATH_PATTERN
)
##########
# print URL_PATTERN_2
##########
URL_REGEX_2 = re.compile(URL_PATTERN_2, flags=REGEX_FLAGS)


#:  Match url protocols
SCHEME_PATTERN = r"""
    ^(http[s]?|ftp|javascript|mailto|file):\/\/(\S+)
"""
SCHEME_REGEX = re.compile(SCHEME_PATTERN, flags=REGEX_FLAGS)


def match_url(url):
    res = match_all(
        url,
        [
            (URL_REGEX, ''),
            (URL_REGEX_2, '')
        ],
        ('url',),
        shortcircuit=False
    )
    return res


def test_match_all_url():
    urls = [
        (
            'aaaaaaaaa www.google.com aaaaaaaaaa',
            [
                dict(name='url', text='www.google.com', pos=(10, 24))
            ]
        ),
        (
            'aaaaaaaaa http://www.google.com/blah aaaaaaaaaa',
            [
                dict(name='url', text='http://www.google.com/blah', pos=(10, 36))
            ]
        ),
        (
            'aaaaaaaaa www.google.com t.co.wev/aslkdfjads aaaaaaaaaa',
            [
                dict(name='url', text='www.google.com', pos=(10, 24)),
                dict(name='url', text='t.co.wev/aslkdfjads', pos=(25, 44)),
            ]
        ),
        (
            'aaaaaaaaa http://t.co.wev/aslkdfjads/ aaaaaaaaaa',
            [
                dict(name='url', text='http://t.co.wev/aslkdfjads/', pos=(10, 37))
            ]
        ),
        (
            u'RT @Thegooglefactz: The iPhone is the second best selling product of all time, the 1st is the Rubik\u2019s Cube.',
            []
        )
    ]
    fail = False
    for url, expected in urls:
        res = match_url(url)
        print url, res
        try:
            assert res == expected
        except Exception as e:
            print "Failed:"
            print "\t", "Actual:", res
            print "\t", "Expected:", expected
            fail = True
        else:
            print "Passed:", url
        print
    if not fail:
        print 'test_match_all_url passed!'


def test():
    test_match_all_url()


if __name__ == '__main__':
    test()

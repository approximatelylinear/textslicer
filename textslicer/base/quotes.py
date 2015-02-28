
import re

from .regex_ import make_bdry_regex, match_all, REGEX_FLAGS

#   NB: Not a boundary regex, because quotes form boundary chars.
QUOTE_PATTERN = ur"""
    (['\"])                 # Starts with a quote char
    (?P<quote>(?:(?!\1).)*) # Anything other than the quote char
    \1                      # Ends with the quote char
"""
QUOTE_REGEX = re.compile(QUOTE_PATTERN, flags=REGEX_FLAGS)


def match_quotes(text):
    #   Find quotes
    regexes = [(QUOTE_REGEX, '')]
    res = match_all(
        text, regexes, ('quote',),
        shortcircuit=True, ignore_submatches=True
    )
    return res


def test_match_quotes():
    data = [
        #   Empty string
        ("", []),
        #   Sentence start, ' char
        ("""'this is quoted' but this is not""", [
            dict(name="quote", text="this is quoted", pos=(1, 15)),
        ]),
        #   Sentence start, " char
        (""" "this is also quoted" but this is not""", [
            dict(name="quote", text="this is also quoted", pos=(2, 21)),
        ]),
        #   Sentence medial, " char
        (""" this is not, but "this is quoted" but this is not""", [
            dict(name="quote", text="this is quoted", pos=(19, 33)),
        ]),
        #   Quote start/end only
        ("""'there are no quotes here.""", []),
        ("""or here" """, []),
    ]
    for text, expected in data:
        print "ORIG:", text
        print "\tEXPECTED:", expected
        res = match_quotes(text)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_match_quotes passed!'


def test():
    test_match_quotes()


if __name__ == '__main__':
    test()

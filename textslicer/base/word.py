
from .regex_ import make_bdry_regex, match_all


#:  Adapted from https://github.com/aritter/twitter_nlp/blob/master/python/TweetNLP.py

WORD_PATTERN = ur"""
        (?:
            # abbreviations, e.g. U.S.A., AT&T
            [A-Z]{{1,3}} (?: (?: \.|&)[A-Z]{{1,3}})+
        )+
    # words with optional internal hyphens
    |   (?: \w+ (?: -\w+)*)
    # ellipsis
    |   (?: \.\.\.)
""".format()
WORD_REGEX = make_bdry_regex(WORD_PATTERN, name='w')



def match_words(text):
    #   Find words
    regexes = [(WORD_REGEX, '')]
    res = match_all(
        text, regexes, ('w',),
        shortcircuit=True, ignore_submatches=True
    )
    return res


def test_match_words():
    data = [
        ("", []),
        ("abc def", [
            dict(name="w", text="abc", pos=(0, 3)),
            dict(name="w", text="def", pos=(4, 7))
        ]),
        ("abc.123 :)", [
            dict(name="w", text="abc", pos=(0, 3)),
            dict(name="w", text="123", pos=(4, 7))
        ]),
        ("abc-def 123 :)", [
            dict(name="w", text="abc-def", pos=(0, 7)),
            dict(name="w", text="123", pos=(8, 11))
        ]),
        ("AT&T 123 :)", [
            dict(name="w", text="AT&T", pos=(0, 4)),
            dict(name="w", text="123", pos=(5, 8))
        ]),
        ("a.b.c 123 :)", [
            dict(name="w", text="a.b.c", pos=(0, 5)),
            dict(name="w", text="123", pos=(6, 9))
        ]),
        ("a.b.c-d.e.f 123 :)", [
            dict(name="w", text="a.b.c", pos=(0, 5)),
            dict(name="w", text="d.e.f", pos=(6, 11)),
            dict(name="w", text="123", pos=(12, 15))
        ]),
    ]
    for text, expected in data:
        print "ORIG:", text
        print "\tEXPECTED:", expected
        res = match_words(text)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_match_words passed!'


def test():
    test_match_words()


if __name__ == '__main__':
    test()

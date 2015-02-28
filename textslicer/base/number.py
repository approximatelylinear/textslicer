
from .regex_patterns import CURRENCY_PATTERN, CURRENCY_CHARS, SPCHAR_BDRY_PATTERN_ASCII
from .regex_ import make_bdry_regex, match_all


"""
nums = [
    #   Fail
    'abc', '', '20',
    #   Pass
    '103,000', '50,000', '60.00', '100,000,000.53', '.100'
]
for s in nums: print s, NUMBER_REGEX.findall(s)
"""

NUMBER_PATTERN = ur"""
    # currency, percentages and numbers with commas,
    # e.g. $12.40, 82%, '100,000'
    (?: {curr})? \.? \d+ (?: [.,]\d+)* %?
""".format(
    curr=CURRENCY_PATTERN
)
NUMBER_REGEX = make_bdry_regex(NUMBER_PATTERN, name='num')


def match_numbers(text):
    #   Find words
    regexes = [(NUMBER_REGEX, '')]
    res = match_all(
        text, regexes, ('num',),
        shortcircuit=True, ignore_submatches=True
    )
    return res


def test_match_numbers():
    data = [
        ("", []),
        ("abc def", []),
        ("abc.123 :)", [
            dict(name="num", text=".123", pos=(3, 7))
        ]),
        ("***123***", [
            dict(name="num", text="123", pos=(3, 6))
        ]),
        ("123*456", [
            dict(name="num", text="123", pos=(0, 3)),
            dict(name="num", text="456", pos=(4, 7)),
        ]),
        ("abc 50.00. 123", [
            dict(name="num", text="50.00", pos=(4, 9)),
            dict(name="num", text="123", pos=(11, 14))
        ]),
        ("abc 103,000 123", [
            dict(name="num", text="103,000", pos=(4, 11)),
            dict(name="num", text="123", pos=(12, 15))
        ]),
        ("abc $50.00 123", [
            dict(name="num", text="$50.00", pos=(4, 10)),
            dict(name="num", text="123", pos=(11, 14))
        ]),
        ("abc .50 123", [
            dict(name="num", text=".50", pos=(4, 7)),
            dict(name="num", text="123", pos=(8, 11))
        ]),
        ("version 2.73.4", [
            dict(name="num", text="2.73.4", pos=(8, 14)),
        ])
    ]
    for text, expected in data:
        print "ORIG:", text
        print "\tEXPECTED:", expected
        res = match_numbers(text)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_match_numbers passed!'



def test():
    test_match_numbers()


if __name__ == '__main__':
    test()


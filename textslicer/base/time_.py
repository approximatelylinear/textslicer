
#   Stdlib
import datetime
import time
import pdb

#   3rd party
from dateutil.parser import parse as date_parse
import pytz

#   Custom
from .constants import THIS_DIR
from .regex_ import make_bdry_regex, match_all


"""
times = [
    '', 'abc', 'abc:def',  '4:3', '40:3',               #   Fail
    '09:50', '10:25', '3:30', '24:00', '24:50', '34:00' #   Pass
]
for t in times: print t, TIME_REGEX.findall(t)
"""

TIME_PATTERN = ur"""
    (?:
        (?: (?: [01]{,1}[0-9]) | (?: 2[0-4]) )  # Hours
        \:                                      # sep
        (?: (?: [0-5][0-9]) | 60 )              # Minutes
        (?:
            \:                                  # sep
            (?: [0-5][0-9]) | 60                # Seconds (optional)
        )?
    )
    (?:
        \s*(?: pm|am )
    )?
"""
TIME_REGEX = make_bdry_regex(TIME_PATTERN, name='time')


MONTHS_FULL = [
    "january", "february", "march", "april", "may",
    "june", "july", "august", "september",
    "october", "november", "december"
]
MONTHS_ABBR = [
    "jan", "feb", "mar",
    "apr", "may", "jun",
    "jul", "aug", "sep", "sept",
    "oct", "nov", "dec"
]
MONTHS_ALPHA = MONTHS_FULL + MONTHS_ABBR
MONTHS_ALPHA_PAT = ur"|".join([ur"(?:{0})".format(s) if len(s) > 1 else s for s in MONTHS_ALPHA])
MONTHS_NUM = [unicode(i) for i in range(1, 13)]
MONTHS_NUM += [ u"0" + unicode(i) for i in range(1, 10) ]
MONTHS_NUM_PAT = ur"|".join([ur"(?:{0})".format(s) if len(s) > 1 else s for s in MONTHS_NUM])
MONTHS = MONTHS_ALPHA + MONTHS_NUM
MONTHS_PAT = ur"|".join(MONTHS)

DAYS_NUM = [ unicode(i) for i in range(1, 32) ]
DAYS_NUM += [ u"0" + unicode(i) for i in range(4, 9) ]
DAYS_NUM_PAT = ur"|".join([ur"(?:{0})".format(s) if len(s) > 1 else s for s in DAYS_NUM])
DAYS_ALPHA = [ unicode(i) + u"st" for i in [u"01", u"1", u"21", u"31"] ]
DAYS_ALPHA += [ unicode(i) + u"nd" for i in [u"02", u"2", u"22"] ]
DAYS_ALPHA += [ unicode(i) + u"rd" for i in [u"03", u"3", u"23"] ]
DAYS_ALPHA += [ unicode(i) + u"th" for i in range(4, 21) + range(24, 31) ]
DAYS_ALPHA += [ u"0" + unicode(i) + u"th" for i in range(4, 9) ]
DAYS_ALPHALONG = [
    "first", "second", "third", "fourth", "fifth", "sixth",
    "seventh", "eigth", "ninth"
]
DAYS_ALPHA += DAYS_ALPHALONG
DAYS_ALPHA += [
    "tenth", "eleventh", "twelfth", "thirteenth", "fourteeth",
    "fifteenth", "sixteenth", "seventeenth", "eighteenth",
    "nineteenth", "twentieth", "thirtieth",
]
DAYS_ALPHA += [ "twenty-" + d for d in DAYS_ALPHALONG ]
DAYS_ALPHA += [ "twenty" + d for d in DAYS_ALPHALONG ]
DAYS_ALPHA += [ "thirty-" + d for d in DAYS_ALPHALONG ]
DAYS_ALPHA += [ "thirty" + d for d in DAYS_ALPHALONG ]


DAYS_ALPHA_PAT = ur"|".join(
    [ur"(?:{0})".format(s) if len(s) > 1 else s for s in DAYS_ALPHA]
)
DAYS = DAYS_NUM + DAYS_ALPHA
DAYS_PAT = ur"|".join([ur"(?:{0})".format(s) if len(s) > 1 else s for s in DAYS])

YEAR_2_PAT = ur'(?: \d{2})'
#   1500 - 1999, 2000 - 2199
YEAR_4_PAT = ur'(?: (?: 1[5-9]\d{2} ) | (?: 2[01]\d{2} ))'
YEAR_PAT = ur"(?: {0} | {1})".format(YEAR_2_PAT, YEAR_4_PAT)


"""
formats
    3 segment
        month   day     year
            jul[y][- ][0]4[th] 2014
            [0]7-[0]4[,] 2014
            [0]7-[0]4-[20]14

        day     month   year
            [0]4[th] jul[y][,] 2014
            [0]4-[0]7[,] 2014
            [0]4-[0]7-[20]14

        year    month   day
            2014[,] jul[y][- ][0]4[th]
            2014[,] [0]7-[0]4
            2014-[0]7-[0]4

        year    day     month
            2014[,] [0]4[-  ]jul[y]
            2014[,] [0]4-[0]7
            2014-[0]4-[0]7

    2 segment
        month   year
            jul[y][,- ]2014

        month   day
            jul[y][,- ][0]4[th]

        day     month
            [0]4[th][,- ]jul[y]

        year    month
            2014[,- ]jul[y]
            2014[,- ][0]7
"""

SEP_YEAR = ur'[\/\-, ]\s{,2}'
SEP_MONTH_DAY = ur'\s{,2}[\/\- ]\s{,2}'
SEP_GROUP = ur'\s{,2}(?P<sep>[\/\-])\s{,2}' #    Case where both separators should be the same.
SEP_GROUP_REF = ur'\s{,2}(?P=sep)\s{,2}'


DATE_MDY_PAT = ur"""
    (?P<month>
        (?: {month_alpha} ) | (?: {month_num} )
    )
    (?: {sep_md})
    (?P<day> {day} )
    (?: {sep_year} )
    (?P<year> {year_4})
""".format(
    month_alpha=MONTHS_ALPHA_PAT,
    day=DAYS_PAT,
    year_4=YEAR_4_PAT,
    month_num=MONTHS_NUM_PAT,
    sep_md=SEP_MONTH_DAY,
    sep_year=SEP_YEAR
)
import re
DATE_MDY_REGEX = make_bdry_regex(DATE_MDY_PAT, name='date')


DATE_MDY_2_PAT = ur"""
    (?P<month>
        (?: {month_alpha} ) | (?: {month_num} )
    )
    (?: {sep} )
    (?P<day> {day} )
    (?: {sep_ref} )
    (?P<year> {year})
""".format(
    month_alpha=MONTHS_ALPHA_PAT,
    day=DAYS_PAT,
    year=YEAR_PAT,
    month_num=MONTHS_NUM_PAT,
    sep=SEP_GROUP,
    sep_ref=SEP_GROUP_REF
)
DATE_MDY_2_REGEX = make_bdry_regex(DATE_MDY_2_PAT, name='date')


DATE_DMY_PAT = ur"""
    (?P<day> {day} )
    (?: {sep_md} )
    (?P<month>
        (?: {month_alpha} ) | (?: {month_num} )
    )
    (?: {sep_year} )
    (?P<year> {year_4})
""".format(
    month_alpha=MONTHS_ALPHA_PAT,
    day=DAYS_PAT,
    year_4=YEAR_4_PAT,
    month_num=MONTHS_NUM_PAT,
    sep_md=SEP_MONTH_DAY,
    sep_year=SEP_YEAR
)
DATE_DMY_REGEX = make_bdry_regex(DATE_DMY_PAT, name='date')


DATE_DMY_2_PAT = ur"""
    (?P<day> {day} )
    (?: {sep} )
    (?P<month>
        (?: {month_alpha} ) | (?: {month_num} )
    )
    (?: {sep_ref} )
    (?P<year> {year})
""".format(
    month_alpha=MONTHS_ALPHA_PAT,
    day=DAYS_PAT,
    year=YEAR_PAT,
    month_num=MONTHS_NUM_PAT,
    sep=SEP_GROUP,
    sep_ref=SEP_GROUP_REF
)
DATE_DMY_2_REGEX = make_bdry_regex(DATE_DMY_2_PAT, name='date')


DATE_YMD_PAT = ur"""
    (?P<year> {year_4})
    (?: {sep_year} )
    (?P<month>
        (?: {month_alpha} ) | (?: {month_num} )
    )
    (?: {sep_md} )
    (?P<day> {day} )
""".format(
    month_alpha=MONTHS_ALPHA_PAT,
    day=DAYS_PAT,
    year_4=YEAR_4_PAT,
    month_num=MONTHS_NUM_PAT,
    sep_md=SEP_MONTH_DAY,
    sep_year=SEP_YEAR
)
DATE_YMD_REGEX = make_bdry_regex(DATE_YMD_PAT, name='date')


DATE_YMD_2_PAT = ur"""
    (?P<year> {year})
    (?: {sep} )
    (?P<month>
        (?: {month_alpha} ) | (?: {month_num} )
    )
    (?: {sep_ref} )
    (?P<day> {day} )
""".format(
    month_alpha=MONTHS_ALPHA_PAT,
    day=DAYS_PAT,
    year=YEAR_PAT,
    month_num=MONTHS_NUM_PAT,
    sep=SEP_GROUP,
    sep_ref=SEP_GROUP_REF
)
DATE_YMD_2_REGEX = make_bdry_regex(DATE_YMD_2_PAT, name='date')


DATE_YDM_PAT = ur"""
    (?P<year> {year_4})
    (?: {sep_year} )
    (?P<day> {day} )
    (?: {sep_md} )
    (?P<month>
        (?: {month_alpha} ) | (?: {month_num} )
    )
""".format(
    month_alpha=MONTHS_ALPHA_PAT,
    day=DAYS_PAT,
    year_4=YEAR_4_PAT,
    month_num=MONTHS_NUM_PAT,
    sep_md=SEP_MONTH_DAY,
    sep_year=SEP_YEAR
)
DATE_YDM_REGEX = make_bdry_regex(DATE_YDM_PAT, name='date')


DATE_YDM_2_PAT = ur"""
    (?P<year> {year})
    (?: {sep} )
    (?P<day> {day} )
    (?: {sep_ref} )
    (?P<month>
        (?: {month_alpha} ) | (?: {month_num} )
    )
""".format(
    month_alpha=MONTHS_ALPHA_PAT,
    day=DAYS_PAT,
    year=YEAR_PAT,
    month_num=MONTHS_NUM_PAT,
    sep=SEP_GROUP,
    sep_ref=SEP_GROUP_REF
)
DATE_YDM_2_REGEX = make_bdry_regex(DATE_YDM_2_PAT, name='date')


DATE_MY_PAT = ur"""
    # jul[y][,- ]2014
    (?P<month>
        (?: {month_alpha} ) | (?: {month_num} )
    )
    (?: {sep_year} )
    (?P<year> {year_4})
""".format(
    month_alpha=MONTHS_ALPHA_PAT,
    month_num=MONTHS_NUM_PAT,
    year_4=YEAR_4_PAT,
    sep_year=SEP_YEAR
)
DATE_MY_REGEX = make_bdry_regex(DATE_MY_PAT, name='date')


DATE_YM_PAT = ur"""
    # 2014[,- ]jul[y]
    # 2014[,- ][0]7
    (?P<year> {year_4})
    (?: {sep_year} )
    (?P<month>
        (?: {month_alpha} ) | (?: {month_num} )
    )
""".format(
    month_alpha=MONTHS_ALPHA_PAT,
    month_num=MONTHS_NUM_PAT,
    year_4=YEAR_4_PAT,
    sep_year=SEP_YEAR
)
DATE_YM_REGEX = make_bdry_regex(DATE_YM_PAT, name='date')


DATE_MD_PAT = ur"""
    # jul[y][,- ][0]4[th]
    (?P<month> {month_alpha} )
    (?: {sep_md} )
    (?P<day> {day} )
""".format(
    month_alpha=MONTHS_ALPHA_PAT,
    day=DAYS_PAT,
    sep_md=SEP_MONTH_DAY,
)
DATE_MD_REGEX = make_bdry_regex(DATE_MD_PAT, name='date')


DATE_DM_PAT = ur"""
    # jul[y][,- ][0]4[th]
    (?P<day> {day})
    (?: {sep_md} )
    (?P<month> {month_alpha} )
""".format(
    month_alpha=MONTHS_ALPHA_PAT,
    day=DAYS_PAT,
    sep_md=SEP_MONTH_DAY,
)
DATE_DM_REGEX = make_bdry_regex(DATE_DM_PAT, name='date')



def match_dates(text):
    """
    >>> match_dates('The program starts at 1/1/2013 and goes to 3/3/14. Also, there's a meeting tomorrow (2012-5-12)')
        {'date_0': ('1/1/2013', (13, 27)), 'date_1': ('3/3/14', (31, 46)), 'date_2': ('12-5-12', (31, 46))}
    """
    regexes = [
        (DATE_MDY_REGEX, 'date_mdy_1'),
        (DATE_MDY_2_REGEX, 'date_mdy_2'),
        (DATE_DMY_REGEX, 'date_dmy_1'),
        (DATE_DMY_2_REGEX, 'date_dmy_2'),
        (DATE_YMD_REGEX, 'date_ymd_1'),
        (DATE_YMD_2_REGEX, 'date_ymd_2'),
        (DATE_YDM_REGEX, 'date_ydm_1'),
        (DATE_YDM_2_REGEX, 'date_ydm_2'),
        (DATE_YM_REGEX, 'date_ym'),
        (DATE_MY_REGEX, 'date_my'),
        (DATE_MD_REGEX, 'date_md'),
        (DATE_DM_REGEX, 'date_dm'),
    ]
    res = match_all(
        text, regexes, ('date', 'year', 'month', 'day'),
        shortcircuit=True, ignore_submatches=False, ignore_errors=True
    )
    return res


"""
dates = [
    '', 'abc', 'abc:def',  '4:3', '40:3',               #   Fail

    '1/1/2013', '2013/1/1', '01-01-2013', '2013-01-01'  #   Pass
    '2014/1', '2014/01', '14-01', ''
    '09:50', '10:25', '3:30', '24:00', '24:50', '34:00' #   Pass
]
for t in dates: print t, DATE_REGEX.findall(t)
"""


def test_match_date():
    dates = [
         # MDY
        ('july 4th 2014', [
                dict(name='date_mdy_1_date', text='july 4th 2014', pos=(0, 13)),
                dict(name='date_mdy_1_year', text='2014', pos=(9, 13)),
                dict(name='date_mdy_1_month', text='july', pos=(0, 4)),
                dict(name='date_mdy_1_day', text='4th', pos=(5, 8))
            ]
        ),
        ('july 4 2014', [
                dict(name='date_mdy_1_date', text='july 4 2014', pos=(0, 11)),
                dict(name='date_mdy_1_year', text='2014', pos=(7, 11)),
                dict(name='date_mdy_1_month', text='july', pos=(0, 4)),
                dict(name='date_mdy_1_day', text='4', pos=(5, 6))
            ]
        ),
        # ('jul-04th 2014', {'date_mdy_1_date_0': ('jul-04th 2014', (0, 13)), 'date_mdy_1_month_0': ('jul', (0, 3)), 'date_mdy_1_year_0': ('2014', (9, 13)), 'date_mdy_1_day_0': ('04th', (4, 8))}),
        # ('july 4 2014', {'date_mdy_1_date_0': ('july 4 2014', (0, 11)), 'date_mdy_1_month_0': ('july', (0, 4)), 'date_mdy_1_year_0': ('2014', (7, 11)), 'date_mdy_1_day_0': ('4', (5, 6))}),
        # ('jul 4 2014', {'date_mdy_1_date_0': ('jul 4 2014', (0, 10)), 'date_mdy_1_month_0': ('jul', (0, 3)), 'date_mdy_1_year_0': ('2014', (6, 10)), 'date_mdy_1_day_0': ('4', (4, 5))}),
        # ('7-4 2014', {'date_mdy_1_date_0': ('7-4 2014', (0, 8)), 'date_mdy_1_month_0': ('7', (0, 1)), 'date_mdy_1_year_0': ('2014', (4, 8)), 'date_mdy_1_day_0': ('4', (2, 3))}),
        # ('7-04, 2014', {'date_mdy_1_date_0': ('7-04, 2014', (0, 10)), 'date_mdy_1_month_0': ('7', (0, 1)), 'date_mdy_1_year_0': ('2014', (6, 10)), 'date_mdy_1_day_0': ('04', (2, 4))}),
        # ('7-4-2014', {'date_mdy_1_date_0': ('7-4-2014', (0, 8)), 'date_mdy_1_month_0': ('7', (0, 1)), 'date_mdy_1_year_0': ('2014', (4, 8)), 'date_mdy_1_day_0': ('4', (2, 3))}),
        # ('7-4-14', {'date_mdy_2_month_0': ('7', (0, 1)), 'date_mdy_2_day_0': ('4', (2, 3)), 'date_mdy_2_date_0': ('7-4-14', (0, 6)), 'date_mdy_2_year_0': ('14', (4, 6))}),
        # ('7-4th-2104', {'date_mdy_1_date_0': ('7-4th-2104', (0, 10)), 'date_mdy_1_month_0': ('7', (0, 1)), 'date_mdy_1_year_0': ('2104', (6, 10)), 'date_mdy_1_day_0': ('4th', (2, 5))}),

        # # DMY
        # ('4th july 2014', {'date_dmy_1_day_0': ('4th', (0, 3)), 'date_dmy_1_year_0': ('2014', (9, 13)), 'date_dmy_1_date_0': ('4th july 2014', (0, 13)), 'date_dmy_1_month_0': ('july', (4, 8))}),
        # ('4 july, 2014', {'date_dmy_1_day_0': ('4', (0, 1)), 'date_dmy_1_year_0': ('2014', (8, 12)), 'date_dmy_1_date_0': ('4 july, 2014', (0, 12)), 'date_dmy_1_month_0': ('july', (2, 6))}),
        # ('04th-jul 2014', {'date_dmy_1_day_0': ('04th', (0, 4)), 'date_dmy_1_year_0': ('2014', (9, 13)), 'date_dmy_1_date_0': ('04th-jul 2014', (0, 13)), 'date_dmy_1_month_0': ('jul', (5, 8))}),
        # ('4 july 2014', {'date_dmy_1_day_0': ('4', (0, 1)), 'date_dmy_1_year_0': ('2014', (7, 11)), 'date_dmy_1_date_0': ('4 july 2014', (0, 11)), 'date_dmy_1_month_0': ('july', (2, 6))}),
        # ('4 jul 2014', {'date_dmy_1_day_0': ('4', (0, 1)), 'date_dmy_1_year_0': ('2014', (6, 10)), 'date_dmy_1_date_0': ('4 jul 2014', (0, 10)), 'date_dmy_1_month_0': ('jul', (2, 5))}),
        # ('4-jul-2014', {'date_dmy_1_day_0': ('4', (0, 1)), 'date_dmy_1_year_0': ('2014', (6, 10)), 'date_dmy_1_date_0': ('4-jul-2014', (0, 10)), 'date_dmy_1_month_0': ('jul', (2, 5))}),
        # ('4th july, 2014', {'date_dmy_1_day_0': ('4th', (0, 3)), 'date_dmy_1_year_0': ('2014', (10, 14)), 'date_dmy_1_date_0': ('4th july, 2014', (0, 14)), 'date_dmy_1_month_0': ('july', (4, 8))}),

        # YMD
        # '2014 july 4th', '2014, july 4', '2014 jul-04th',
        # '2014 july 4', '2014 jul 4',
        # '2014-jul-4', '2014, july 4th',
        # '14-7-4', '2014-07-04',

        # YDM
        # '2014 4th july', '2014, 4 july', '2014 04th-jul',
        # '2014 4 july', '2014 4 jul',
        # '2014-4-jul', '2014, 4th july',
        # '14-4-7', '2014-04-07',

        # Fail
        # 'ju 4 2014', '14-07/4'
    ]
    # regexes = [
    #     ('mdy_1', DATE_MDY_REGEX),
    #     ('mdy_2', DATE_MDY_2_REGEX),
    #     ('dmy_1', DATE_DMY_REGEX),
    #     ('dmy_2', DATE_DMY_2_REGEX),
    #     ('ymd_1', DATE_YMD_REGEX),
    #     ('ymd_2', DATE_YMD_2_REGEX),
    #     ('ydm_1', DATE_YDM_REGEX),
    #     ('ydm_2', DATE_YDM_2_REGEX),
    # ]
    for text, expected in dates:
        print "ORIG:", text
        print "\tEXPECTED:", expected
        res = match_dates(text)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_match_date passed!'



def match_times(text):
    """
    >>> match_time('The meeting starts at 10:00 AM and goes to 3:52 PM. Also, there's a meeting tomorrow at 1:00')
        {'time_0': ('10:00 AM', (13, 27)), 'time_1': ('3:52 PM', (31, 46)), 'time_2': ('1:00', (31, 46))}
    """
    res = match_all(text, ((TIME_REGEX, None),), ('time',))
    return res


def test_match_times():
    data = [
        (
            "The meeting starts at 10:00 AM and goes to 3:52 PM. Also, there's a meeting tomorrow at 1:00",
            [
                dict(name="time", text="1:00", pos=(88, 92)),
                dict(name="time", text="3:52 PM", pos=(43, 50)),
                dict(name="time", text="10:00 AM", pos=(22, 30)),
            ]
        ),
        ('abc:def', []),
        ('4:3', []),
        ('40:3', []),
    ]
    # pdb.set_trace()
    for text, expected in data:
        print "ORIG:", text
        print "\tEXPECTED:", expected
        res = match_times(text)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_match_times passed!'


def test():
    test_match_date()
    test_match_times()


if __name__ == '__main__':
    test()




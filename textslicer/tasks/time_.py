
#   Stdlib
import re
import pdb
from pprint import pformat

#   3rd party
from dateutil.parser import parse as date_parse

#   Custom
from .constants_tasks import THIS_DIR
from .abc import Tokenizer
from ..base import time_
from ..base.tokenize import update_segments
from ..base.time_ import (
    to_localtime, get_day_of_week, get_hour_of_day, match_dates, match_times
)


class ToLocalTime(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, doc, **kwargs):
        tz = kwargs.get('tz')
        posted_time = doc['date_time']['posted_time']
        if posted_time is not None:
            local_time = to_localtime(posted_time, tz=tz)
            local_time_str = local_time.isoformat()
        else:
            local_time_str = None
        doc['date_time']['local_time'] = local_time_str
        return doc


def test_to_localtime():
    _to_localtime = ToLocalTime()
    data = [
        (
            dict(date_time=dict(posted_time="2014-02-07T09:19:59.000Z")),
            dict(date_time=dict(posted_time="2014-02-07T09:19:59.000Z", local_time='2014-02-07T03:19:59-06:00'))    #   Central (standard time) is 6 hours behind UTC
        )
    ]
    # pdb.set_trace()
    for doc, expected in data:
        print "ORIG:", doc
        print "\tEXPECTED:", expected
        res = _to_localtime(doc, tz='US/Central')
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_to_localtime passed!', '\n'



class DayOfWeek(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, doc, **kwargs):
        local_time = doc['date_time'].get('local_time')
        if local_time is not None:
            doc['date_time']['day_of_week'] = get_day_of_week(local_time)
        return doc


def test_get_day_of_week():
    _get_day_of_week = DayOfWeek()
    data = [
        (
            dict(date_time=dict(posted_time="2014-02-07T09:19:59.000Z", local_time="2014-02-07T09:19:59.000Z")),
            dict(date_time=dict(posted_time="2014-02-07T09:19:59.000Z", local_time="2014-02-07T09:19:59.000Z", day_of_week="Friday"))
        )
    ]
    # pdb.set_trace()
    for doc, expected in data:
        print "ORIG:", doc
        print "\tEXPECTED:", expected
        res = _get_day_of_week(doc)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_get_day_of_week passed!'



class HourOfDay(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, doc, **kwargs):
        local_time = doc['date_time'].get('local_time')
        if local_time is not None:
            doc['date_time']['hour_of_day'] = str(get_hour_of_day(local_time))
        return doc


def test_get_hour_of_day():
    _get_hour_of_day = HourOfDay()
    data = [
        (
            dict(date_time=dict(posted_time="2014-02-07T09:19:59.000Z", local_time="2014-02-07T09:19:59.000Z")),
            dict(date_time=dict(posted_time="2014-02-07T09:19:59.000Z", local_time="2014-02-07T09:19:59.000Z", hour_of_day="9"))
        )
    ]
    # pdb.set_trace()
    for doc, expected in data:
        print "ORIG:", doc
        print "\tEXPECTED:", expected
        res = _get_hour_of_day(doc)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_get_day_of_week passed!', '\n'



class GetDates(Tokenizer):
    @staticmethod
    def tokenizer_matcher(text):
        return match_dates(text)

    month_names = {
        "jan"   : "january",
        "feb"   : "february",
        "mar"   : "march",
        "apr"   : "april",
        "jun"   : "june",
        "jul"   : "july",
        "aug"   : "august",
        "sep"   : "september",
        "sept"  : "september",
        "oct"   : "october",
        "nov"   : "november",
        "dec"   : "december",
    }
    day_names = {
        "first" : 1,
        "second": 2,
        "third": 3,
        "fourth": 4,
        "fifth": 5,
        "sixth": 6,
        "seventh": 7,
        "eigth": 8,
        "ninth": 9,
        "tenth": 10,
        "eleventh": 11,
        "twelfth": 12,
        "thirteenth": 13,
        "fourteeth": 14,
        "fifteenth": 15,
        "sixteenth": 16,
        "seventeenth": 17,
        "eighteenth": 18,
        "nineteenth": 19,
        "twentieth": 20,
        'twenty-first': 21,
        'twenty-second': 22,
        'twenty-third': 23,
        'twenty-fourth': 24,
        'twenty-fifth': 25,
        'twenty-sixth': 26,
        'twenty-seventh': 27,
        'twenty-eigth': 28,
        'twenty-ninth': 29,
        'twentyfirst': 21,
        'twentysecond': 22,
        'twentythird': 23,
        'twentyfourth': 24,
        'twentyfifth': 25,
        'twentysixth': 26,
        'twentyseventh': 27,
        'twentyeigth': 28,
        'twentyninth': 29,
        "thirtieth": 30,
        'thirty-first': 31,
        'thirtyfirst': 31
    }

    def norm_month(self, text):
        return self.month_names.get(text.lower()) or ''

    def norm_day(self, text):
        text = text.strip()
        num = self.day_names.get(text.lower()) or ''
        if not num:
            try:
                num = re.sub(
                    ur"^(\d+)(?:(?:th)|(?:nd)|(?:d)|(?:rd)|(?:st))$",
                    ur"\1",
                    num,
                    flags=re.IGNORECASE|re.UNICODE|re.X|re.DOTALL|re.MULTILINE
                )
            except Exception as e:
                print e
                pdb.set_trace()
        return num

    def normalize(self, segments_, **params):
        for seg in segments_:
            if seg['name'] and seg['name'].startswith('date'):
                if seg['name'].endswith('date'):
                    try:
                        norm = date_parse(seg['text']).strftime("%Y-%m-%d")
                    except Exception as e:
                        ########
                        print e
                        ########
                        #   Not a date
                        # seg['name'] = None
                    else:
                        seg['norm'] = norm
                elif seg['name'].endswith('month'):
                    norm = self.norm_month(seg['text'])
                    if norm:
                        seg['norm'] = norm
                elif seg['name'].endswith('day'):
                    norm = self.norm_day(seg['text'])
                    if norm:
                        seg['norm'] = norm
        return segments_

    def process(self, doc, **params):
        field_out = params.get('field_out')  or 'current'
        doc = super(GetDates, self).process(doc, **params)
        doc['text'][field_out] = self.normalize(doc['text'][field_out], **params)
        return doc



def test_get_dates():
    get_dates = GetDates()
    data = [
        (
            dict(
                text=dict(
                    original = "Some holiday will fall on july 4th 2014.",
                    current = [
                        dict(pos=(0, 40), name=None, text="Some holiday will fall on july 4th 2014.")
                    ],
                )
            ),
            dict(
                text=dict(
                    original="Some holiday will fall on july 4th 2014.",
                    current = [
                        dict(pos=(0, 26), name=None, text="Some holiday will fall on "),
                        dict(pos=(26, 30), name='date_mdy_1_month', text="july"),
                        dict(pos=(26, 39), name='date_mdy_1_date', text="july 4th 2014"),
                        dict(pos=(30, 31), name=None, text=' '),
                        dict(pos=(31, 34), name='date_mdy_1_day', text="4th"),
                        dict(pos=(34, 35), name=None, text=' '),
                        dict(pos=(35, 39), name='date_mdy_1_year', text="2014"),
                        dict(pos=(39, 40), name=None, text='.')
                    ],
                    tokens=dict()
                )
            ),
        ),
        (
            dict(
                text=dict(
                    original = "Some holiday will fall on 7/4/2014.",
                    current = [
                        dict(pos=(0, 35), name=None, text="Some holiday will fall on 7/4/2014.")
                    ],
                )
            ),
            dict(
                text=dict(
                    original="Some holiday will fall on 7/4/2014.",
                    current = [
                        dict(pos=(0, 26), name=None, text="Some holiday will fall on "),
                        dict(pos=(26, 34), name='date_mdy_1_date', text="7/4/2014", norm='2014-07-04'),
                        dict(pos=(26, 27), name='date_mdy_1_month', text="7"),
                        dict(pos=(27, 28), name=None, text="/"),
                        dict(pos=(28, 29), name='date_mdy_1_day', text="4"),
                        dict(pos=(29, 30), name=None, text="/"),
                        dict(pos=(30, 34), name='date_mdy_1_year', text="2014"),
                        dict(pos=(34, 35), name=None, text='.')
                    ],
                    tokens=dict()
                )
            ),
        ),
    ]
    # pdb.set_trace()
    for doc, expected in data:
        print "ORIG:", doc
        print "\tEXPECTED:", pformat(expected)
        res = get_dates(doc)
        print '\tRESULT:', pformat(res)
        try:
            assert res == expected
        except Exception as e:
            print e
            pdb.set_trace()
            raise
        print
    print 'test_get_dates passed!', '\n'



class GetTimes(Tokenizer):
    @staticmethod
    def tokenizer_matcher(text):
        return match_times(text)


def test_get_times():
    get_times = GetTimes()
    data = [
        (
            dict(
                text=dict(
                    original="The meeting starts at 10:00 AM and goes to 3:52 PM. Also, there's a meeting tomorrow at 1:00",
                    current=[
                        dict(
                            pos=(0, 92), name=None, text="The meeting starts at 10:00 AM and goes to 3:52 PM. Also, there's a meeting tomorrow at 1:00"
                        )
                    ]
                )
            ),
            dict(
                text=dict(
                    original="The meeting starts at 10:00 AM and goes to 3:52 PM. Also, there's a meeting tomorrow at 1:00",
                    current=[
                        dict(pos=(0, 22), name=None, text="The meeting starts at "),
                        dict(pos=(22, 30), name='time', text="10:00 AM"),
                        dict(pos=(30, 43), name=None, text=" and goes to "),
                        dict(pos=(43, 50), name='time', text="3:52 PM"),
                        dict(pos=(50, 88), name=None, text=". Also, there's a meeting tomorrow at "),
                        dict(pos=(88, 92), name='time', text="1:00"),
                    ],
                    tokens=dict()
                )
            ),
        )
    ]
    # pdb.set_trace()
    for doc, expected in data:
        print "ORIG:", doc
        print "\tEXPECTED:", expected
        res = get_times(doc)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_get_times passed!', '\n'




class GetHoursElapsed(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, doc, **kwargs):
        doc['date_time']['hour_of_day'] = str(get_hour_of_day(doc['date_time']['local_time']))
        return doc


def test():
    test_to_localtime()
    test_get_day_of_week()
    test_get_hour_of_day()
    test_get_dates()
    test_get_times()


if __name__ == '__main__':
    test()

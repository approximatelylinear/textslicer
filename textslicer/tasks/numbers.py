

#   Stdlib
import pdb
from pprint import pformat

#   Custom
from .constants_tasks import THIS_DIR
from .abc import Tokenizer
from ..base.tokenize import update_segments
from ..base.number import match_numbers


class GetNumbers(Tokenizer):
    @staticmethod
    def tokenizer_matcher(text):
        return match_numbers(text)



def test_get_numbers():
    get_numbers = GetNumbers()

    """
    [
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
        ])
    ]
    """
    data = [
        (
            dict(
                text=dict(
                    original="",
                    current=[dict(pos=(0, 0), name=None, text="")]
                )
            ),
            dict(
                text=dict(
                    original="",
                    current=[dict(pos=(0, 0), name=None, text="")],
                    tokens=dict()
                )
            ),
        ),
        (
            dict(
                text=dict(
                    original="abc def",
                    current=[dict(pos=(0, 7), name=None, text="abc def")]
                )
            ),
            dict(
                text=dict(
                    original="abc def",
                    current=[dict(pos=(0, 7), name=None, text="abc def")],
                    tokens=dict()
                )
            ),
        ),
        (
            dict(
                text=dict(
                    original="abc 50.00. 123",
                    current=[dict(pos=(0, 14), name=None, text="abc 50.00. 123")]
                )
            ),
            dict(
                text=dict(
                    original="abc 50.00. 123",
                    current=[
                        dict(pos=(0, 4), name=None, text='abc '),
                        dict(pos=(4, 9), name='num', text='50.00'),
                        dict(pos=(9, 11), name=None, text='. '),
                        dict(pos=(11, 14), name='num', text='123')
                    ],
                    tokens=dict()
                )
            ),
        ),
        (
            dict(
                text=dict(
                    original="abc .50 123",
                    current=[dict(pos=(0, 10), name=None, text="abc .50 123")]
                )
            ),
            dict(
                text=dict(
                    original="abc .50 123",
                    current=[
                        dict(pos=(0, 4), name=None, text='abc '),
                        dict(pos=(4, 7), name='num', text='.50'),
                        dict(pos=(7, 8), name=None, text=' '),
                        dict(pos=(8, 11), name='num', text='123'),
                    ],
                    tokens=dict()
                )
            ),
        ),
        (
            dict(
                text=dict(
                    original="abc $50.00 123",
                    current=[dict(pos=(0, 10), name=None, text="abc $50.00 123")]
                )
            ),
            dict(
                text=dict(
                    original="abc $50.00 123",
                    current=[
                        dict(pos=(0, 4), name=None, text='abc '),
                        dict(pos=(4, 10), name='num', text='$50.00'),
                        dict(pos=(10, 11), name=None, text=' '),
                        dict(pos=(11, 14), name='num', text='123')
                    ],
                    tokens=dict()
                )
            ),
        )
    ]
    # pdb.set_trace()
    for doc, expected in data:
        print "ORIG:", doc
        print "\tEXPECTED:", pformat(expected)
        res = get_numbers(doc)
        print '\tRESULT:', pformat(res)
        assert res == expected
        print
    print 'test_get_numbers passed!', '\n'


def test():
    test_get_numbers()


if __name__ == '__main__':
    test()



from unicode_utils import remove_symbols, get_symbols

#   Custom
from .abc import Tokenizer, TokenFilter
from ..base.tokenize import update_segments


class RemoveSymbols(TokenFilter):
    type_ = 'symbol'


class GetSymbols(Tokenizer):
    @staticmethod
    def tokenizer_matcher(text):
        return list(get_symbols(text))



def test_get_symbols():
    _get_symbols = GetSymbols()
    data = [
        (
            dict(
                text=dict(
                    original=u'abcdefg',
                    current=[dict(pos=(0, 7), name=None, text=u'abcdefg')]
                )
            ),
            dict(
                text=dict(
                    original=u'abcdefg',
                    current=[dict(pos=(0, 7), name=None, text=u'abcdefg')],
                )
            )
        ),

        (
            dict(
                text=dict(
                    original=u'abcdefg \u00AE',
                    current=[dict(pos=(0, 9), name=None, text=u'abcdefg \u00AE')]
                )
            ),
            dict(
                text=dict(
                    original=u'abcdefg \u00AE',
                    current=[
                        dict(pos=(0, 8), name=None, text=u'abcdefg '),
                        dict(pos=(8, 9), name='symbol', text=u'\u00AE')
                    ],
                )
            )
        ),
        (
            dict(
                text=dict(
                    original=u'abc\u00A9defg \u00AE',
                    current=[dict(pos=(0, 10), name=None, text=u'abc\u00A9defg \u00AE')]
                )
            ),
            dict(
                text=dict(
                    original=u'abc\u00A9defg \u00AE',
                    current=[
                        dict(pos=(0, 3), name=None, text=u'abc'),
                        dict(pos=(3, 4), name='symbol', text=u'\u00A9'),
                        dict(pos=(4, 9), name=None, text=u'defg '),
                        dict(pos=(9, 10),name='symbol', text=u'\u00AE'),
                    ],
                )
            )
        ),
    ]
    for doc, expected in data:
        # pdb.set_trace()
        print "ORIG:", doc
        print "\tEXPECTED:", expected
        res = _get_symbols(doc)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_get_symbols passed!', '\n'


def test():
    test_get_symbols()


if __name__ == '__main__':
    test()


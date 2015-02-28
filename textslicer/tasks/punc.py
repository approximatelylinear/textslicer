
from unicode_utils import remove_punc, get_punc

from .abc import Tokenizer, TokenFilter
from ..base.tokenize import update_segments


class RemovePunc(TokenFilter):
    type_ = 'punc'



class GetPunc(Tokenizer):
    @staticmethod
    def tokenizer_matcher(text):
        return list(get_punc(text))




def test_get_punc():
    _get_punc = GetPunc()
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
                    original=u'abcdefg .',
                    current=[dict(pos=(0, 9), name=None, text=u'abcdefg .')]
                )
            ),
            dict(
                text=dict(
                    original=u'abcdefg .',
                    current=[
                        dict(pos=(0, 8), name=None, text=u'abcdefg '),
                        dict(pos=(8, 9), name='punc', text=u'.')
                    ],
                )
            )
        ),
        (
            dict(
                text=dict(
                    original=u'abc!defg .',
                    current=[dict(pos=(0, 10), name=None, text=u'abc!defg .')]
                )
            ),
            dict(
                text=dict(
                    original=u'abc!defg .',
                    current=[
                        dict(pos=(0, 3), name=None, text=u'abc'),
                        dict(pos=(3, 4), name='punc', text=u'!'),
                        dict(pos=(4, 9), name=None, text=u'defg '),
                        dict(pos=(9, 10), name='punc', text=u'.'),
                    ],
                )
            )
        ),
    ]
    for doc, expected in data:
        # pdb.set_trace()
        print "ORIG:", doc
        print "\tEXPECTED:", expected
        res = _get_punc(doc)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_get_punc passed!', '\n'


def test():
    test_get_punc()


if __name__ == '__main__':
    test()


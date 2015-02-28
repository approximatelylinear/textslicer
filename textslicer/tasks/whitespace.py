
import pdb

from .abc import TokenFilter
from ..base.regex_ import strip_whitespace
from ..base.tokenize import update_segments


class RemoveWhitespace(TokenFilter):
    """
    Remove all elements that consist entirely of whitespace
    (Pattern differs from above in that we identify whitespace in this method. )
    Strip whitespace from unidentified tokens
    """

    def process(self, doc, **kwargs):
        field_in = kwargs.get('field_in')  or 'current'
        field_out = kwargs.get('field_out')  or 'current'
        segments = doc['text'][field_in]
        for seg in segments:
            seg['text'] = strip_whitespace(seg['text'])
        segments_out = [
            seg for seg in segments if seg['name'] or (len(seg['text']) > 0)
        ]
        doc['text'][field_out] = segments_out
        return doc



def test_remove_whitespace():
    remove_whitespace = RemoveWhitespace()
    data = [
        (
            dict(
                text=dict(
                    original=u' abc defg ',
                    current=[
                        dict(pos=(0, 1), name=None, text=u' '),
                        dict(pos=(1, 4), name='w', text=u'abc'),
                        dict(pos=(4, 5), name=None, text=u' '),
                        dict(pos=(5, 9), name='w', text=u'defg'),
                        dict(pos=(9, 10), name=None, text=u' '),
                    ]
                )
            ),
            dict(
                text=dict(
                    original=u' abc defg ',
                    current=[
                        dict(pos=(1, 4), name='w', text=u'abc'),
                        dict(pos=(5, 9), name='w', text=u'defg'),
                    ],
                )
            )
        ),
    ]
    for doc, expected in data:
        # pdb.set_trace()
        print "ORIG:", doc
        print "\tEXPECTED:", expected
        res = remove_whitespace(doc)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_remove_whitespace passed!', '\n'


def test():
    test_remove_whitespace()


if __name__ == '__main__':
    test()


#   Stdlib
import pdb
from pprint import pformat

#   Custom
from .abc import Tokenizer
from ..base.emoticons.emoticon import match_emoticons
from ..base.tokenize import update_segments


class GetEmoticons(Tokenizer):
    @staticmethod
    def tokenizer_matcher(text):
        return match_emoticons(text)



def test_get_emoticons():
    get_emoticons = GetEmoticons()
    data = [
        (
            dict(
                text=dict(
                    original='blah blah :) blah blah',
                    current=[
                        dict(pos=(0, 22), name=None, text='blah blah :) blah blah')
                    ],
                )
            ),
            dict(
                text=dict(
                    original='blah blah :) blah blah',
                    current=[
                        dict(pos=(0, 10), name=None, text='blah blah '),
                        dict(pos=(10, 12), name='emo_happy_emo', text=':)'),
                        dict(pos=(12, 22), name=None, text=' blah blah')
                    ],
                )
            ),
        ),
        (
            dict(
                text=dict(
                    original='blah blah.(-: blah blah',
                    current=[
                        dict(pos=(0, 23), name=None, text='blah blah.(-: blah blah')
                    ],
                )
            ),
            dict(
                text=dict(
                    original='blah blah.(-: blah blah',
                    current=[
                        dict(pos=(0, 10), name=None, text='blah blah.'),
                        dict(pos=(10, 13), name='emo_happy_emo', text='(-:'),
                        dict(pos=(13, 23), name=None, text=' blah blah')
                    ],
                )
            ),
        ),
        (
            dict(
                text=dict(
                    original='blah blah.(-: blah blah',
                    current=[
                        dict(pos=(0, 10), name=None, text='blah blah.'),
                        dict(pos=(10, 23), name=None, text='(-: blah blah')
                    ],
                )
            ),
            dict(
                text=dict(
                    original='blah blah.(-: blah blah',
                    current=[
                        dict(pos=(0, 10), name=None, text='blah blah.'),
                        dict(pos=(10, 13), name='emo_happy_emo', text='(-:'),
                        dict(pos=(13, 23), name=None, text=' blah blah')
                    ],
                )
            ),
        ),
    ]
    failures = 0
    for doc, expected in data:
        # pdb.set_trace()
        print "ORIG:", doc
        print "\tEXPECTED:", expected
        res = get_emoticons(doc)
        print '\tRESULT:', res
        try:
            assert res == expected
        except Exception as e:
            failures += 1
            print "Failed"
        print
    if not failures:
        print 'test_get_emoticons passed!', '\n'




def test():
    test_get_emoticons()


if __name__ == '__main__':
    test()


#   Stdlib
import pdb
import itertools
from pprint import pformat

#   Custom
from ..base.ngram import get_all_ngrams


class GetNgrams(object):
    def __init__(self, *args, **kwargs):
        super(GetNgrams, self).__init__()
        #    Get 2 and 3 word ngrams by default.
        self.max_num = kwargs.get('max_num') or 3

    def process(self, doc, **kwargs):
        """
            Example:
                {
                    'current' : [
                        {'pos': (0, 2), 'name': 'w', 'text': 'ab'},
                        {'pos': (2, 4), 'name': 'w', 'text': 'cd'},
                        {'pos': (4, 6), 'name': 'w', 'text': 'ef'}
                    ]
                }

                    ==>

                {
                    'current' : [
                        {'pos': (0, 2), 'name': 'w', 'text': 'ab', 'len': 2},
                        {'pos': (0, 4), 'type': 'w_w', 'text': 'ab_cd', 'len': 2},
                        {'pos': (0, 6), 'type': 'w_w_w', 'text': 'ab_cd_ef', 'len': 3}
                        {'pos': (2, 4), 'name': 'w', 'text': 'cd', 'len': 2},
                        {'pos': (2, 6), 'type': 'w_w', 'text': 'cd_ef', 'len': 2},
                        {'pos': (4, 6), 'name': 'w', 'text': 'ef', 'len': 2},
                    ],
                }
        """
        #   ==========================================================
        def format_ngrams(ngrams_all):
            for num, ngrams in ngrams_all:
                #   Get current ngrams
                #   Add ngrams to 'current' field
                #   Convert ngram tuples to dicts and add to ngrams tokens.
                for ngram in ngrams:
                    if ngram['text']:
                        ngram['len'] = num
                        yield ngram
        #   ==========================================================
        field_in = kwargs.get('field_in')  or 'current'
        field_out = kwargs.get('field_out')  or 'current'
        process_types = kwargs.get('process_types') or set(['w'])
        tokens = doc['text'].setdefault('tokens', {})
        segments = doc['text'][field_in]
        segments_out = doc['text'][field_out]
        ngrams_all = get_all_ngrams(
            segments, self.max_num, process_types=process_types
        )
        for ngram in format_ngrams(ngrams_all):
            segments_out.append(ngram)
        doc['text'][field_out] = sorted(segments_out, key=lambda d: d['pos'])
        return doc

    def finalize(self):
        pass

    def __call__(self, doc, **kwargs):
        return self.process(doc, **kwargs)



def test_get_ngrams():
    get_ngrams = GetNgrams()
    data = [
        (
            dict(
                text=dict(
                    original="ab cd ef",
                    current=[
                        dict(pos=(0, 2), name='w', text='ab'),
                        dict(pos=(3, 5), name='w', text='cd'),
                        dict(pos=(6, 8), name='w', text='ef')
                    ]
                )
            ),
            dict(
                text=dict(
                    original="ab cd ef",
                    current = [
                        dict(pos=(0, 2), name='w', text='ab'),
                        dict(pos=(0, 5), name='ngram_w_w', text='ab_cd', len=2, children=[dict(pos=(0, 2), name='w', text='ab'), dict(pos=(3, 5), name='w', text='cd')]),
                        dict(pos=(0, 8), name='ngram_w_w_w', text='ab_cd_ef', len=3, children=[dict(pos=(0, 2), name='w', text='ab'), dict(pos=(3, 5), name='w', text='cd'), dict(pos=(6, 8), name='w', text='ef')]),
                        dict(pos=(3, 5), name='w', text='cd'),
                        dict(pos=(3, 8), name='ngram_w_w', text='cd_ef', len=2, children=[dict(pos=(3, 5), name='w', text='cd'), dict(pos=(6, 8), name='w', text='ef')]),
                        dict(pos=(6, 8), name='w', text='ef'),
                    ],
                    tokens=dict()
                )
            ),
        ),
        (
            dict(
                text=dict(
                    original="ab . cd ef .",
                    current=[
                        dict(pos=(0, 2), name='w', text='ab'),
                        dict(pos=(3, 4), name='punc', text='.'),
                        dict(pos=(5, 7), name='w', text='cd'),
                        dict(pos=(8, 10), name='w', text='ef'),
                        dict(pos=(11, 12), name='punc', text='.'),
                    ]
                )
            ),
            dict(
                text=dict(
                    original="ab . cd ef .",
                    current = [
                        dict(pos=(0, 2), name='w', text='ab'),
                        dict(pos=(3, 4), name='punc', text='.'),
                        dict(pos=(5, 7), name='w', text='cd'),
                        dict(pos=(5, 10), name='ngram_w_w', text='cd_ef', len=2, children=[dict(pos=(5, 7), name='w', text='cd'), dict(pos=(8, 10), name='w', text='ef')]),
                        dict(pos=(8, 10), name='w', text='ef'),
                        dict(pos=(11, 12), name='punc', text='.'),
                    ],
                    tokens=dict()
                )
            ),
        ),
    ]
    # pdb.set_trace()
    for doc, expected in data:
        print "ORIG:", pformat(doc)
        print "\tEXPECTED:", pformat(expected)
        res = get_ngrams(doc)
        print '\tRESULT:', pformat(res)
        assert res == expected
        print
    print 'test_get_ngrams passed!', '\n'


def test():
    test_get_ngrams()


if __name__ == '__main__':
    test()

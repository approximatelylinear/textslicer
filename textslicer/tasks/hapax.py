
import os
import pdb
from pprint import pformat

from .constants_tasks import THIS_DIR
from ..base.hapax import get_single_occurrences, remove_single_occurrences


class RemoveHapaxes(object):
    """
    Removes tokens that only appear once.
    """
    def fmt_tokens(self, tokens):
        #   Ignore ngrams
        return [
            text for _, tag, text in tokens
                if tag is None or "_" not in tag
        ]

    def get_hapaxes(self, tokens):
        tokens = [ w.strip() for words in tokens for w in words ]
        hapaxes = get_single_occurrences(tokens)
        return hapaxes

    def remove_hapaxes(self, docs, hapaxes):
        for doc in docs:
            tokens = doc['text']['tokens']['all']
            tokens = [
                (pos, tag, text) for pos, tag, text in tokens
                    if text not in hapaxes
            ]
            doc['text']['tokens']['all'] = tokens
            yield doc

    def __call__(self, doc, **kwargs):
        #   Cache to avoid lookups
        fmt_tokens = self.fmt_tokens
        docs = doc['docs']
        tokens = ( fmt_tokens(doc['text']['tokens']['all']) for doc in docs )
        hapaxes = self.get_hapaxes(tokens)
        docs = self.remove_hapaxes(docs, hapaxes)
        return docs



def test_remove_hapaxes():
    data = [
        (
            #   Input
            [
                dict(
                    text = dict(
                        tokens = dict(
                            all = [
                                ((0, 1), None, 'a'),
                                ((1, 2), None, 'b'),
                                ((2, 3), None, 'c'),
                            ]
                        )
                    )
                ),
                dict(
                    text = dict(
                        tokens = dict(
                            all = [
                                ((0, 1), None, 'b'),
                                ((1, 2), None, 'c'),
                                ((2, 3), None, 'd'),
                            ]
                        )
                    )
                ),
                dict(
                    text = dict(
                        tokens = dict(
                            all = [
                                ((0, 1), None, 'c'),
                                ((1, 2), None, 'd'),
                                ((2, 3), None, 'e'),
                            ]
                        )
                    )
                )
            ],
            #   Expected
            [
                dict(
                    text = dict(
                        tokens = dict(
                            all = [
                                ((1, 2), None, 'b'),
                                ((2, 3), None, 'c'),
                            ]
                        )
                    )
                ),
                dict(
                    text = dict(
                        tokens = dict(
                            all = [
                                ((0, 1), None, 'b'),
                                ((1, 2), None, 'c'),
                                ((2, 3), None, 'd'),
                            ]
                        )
                    )
                ),
                dict(
                    text = dict(
                        tokens = dict(
                            all = [
                                ((0, 1), None, 'c'),
                                ((1, 2), None, 'd'),
                            ]
                        )
                    )
                )
            ],
        )
    ]
    remove_hapaxes_ = RemoveHapaxes()
    for docs, expected in data:
        # pdb.set_trace()
        print "ORIG:", pformat(docs)
        print "\tEXPECTED:", pformat(expected)
        res = list(remove_hapaxes_(docs))
        print '\tRESULT:', pformat(res)
        assert res == expected
        print
    print 'test_remove_hapaxes passed!', '\n'


def test():
    test_remove_hapaxes()


if __name__ == '__main__':
    test()

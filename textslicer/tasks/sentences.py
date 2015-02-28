
#   Stdlib
import os
import re
import string
import itertools
import pdb
from pprint import pformat

#   3rd party
import nltk.data

#   Custom
from .abc import Tokenizer
from ..base.tokenize import update_segments

TOKENIZER_SENTS = nltk.data.load('tokenizers/punkt/english.pickle')


class GroupSentences(object):
    """
    Re-combine sentences after all tokens have been identified.
    This is important because sentence segmentation occurs prior to
    word-level segmentation, so we don't know the word-level
    constituents of each sentence until we combine them.
    """
    skip_tags = set(['ngram'])

    def __init__(self, **kwargs):
        skip_tags = kwargs.get('skip_tags') or self.skip_tags
        self.skip_regex = re.compile(ur'|'.join(list(skip_tags)))

    def process(self, doc, **kwargs):
        """
        segments_sent = [ seg for seg in segments if seg[1] is not None and not func.skip_regex.match(seg[1]) ]
        sents = sentences.regroup_sentences(segments_sent, skip=set([None]))
        sents = list(sents)
        sents_l, sents_d = sentences.join_sentences(sents)
        """
        field_in = kwargs.get('field_in')  or 'current'
        field_out = kwargs.get('field_out')  or 'current'
        tokens = doc['text'].setdefault('tokens', {})
        segments = doc['text'][field_in]
        #   Use individual words for sentences.
        segments_sent = (
            seg for seg in segments
                if seg['name'] is not None and
                not self.skip_regex.match(seg['name'])
        )
        sents = regroup_sentences(segments_sent, skip=set([None]))
        sents = [ s for s in sents if s ]
        sents_d = join_sentences(sents)
        # Replace the content of the `sents` field
        # tokens['sents'] = sents_d
        # Add the newly-combined sentences to the segments.
        segments.extend(sents_d)
        # Remove sentence boundaries.
        segments = ( seg for seg in segments if seg['name'] != '!S-END' )
        # Re-sort the segments by position.
        segments = sorted(segments, key=lambda d: d['pos'])
        doc['text'][field_in] = list(segments)
        return doc

    def finalize(self):
        pass

    def __call__(self, doc, **kwargs):
        return self.process(doc, **kwargs)



def _match_sentences(text):
    #   Tokenize
    tokens = TOKENIZER_SENTS.tokenize(text)
    #   Label position and name
    start = 0
    for token in tokens:
        #   Ignore whitespace when calculating boundaries in order to
        #   be consistent with the punkt tokenizer.
        while text[start] in string.whitespace: start += 1
        start, end = start, start + len(token)
        sent = dict(
            pos     = (start, end),
            #   Use None for the token label.
            name    = None,
            text    = token
        )
        yield sent
        bdry_end = dict(
            pos     = (end, end), # 0 width token
            #   Indicate sentence boundary.
            name    = '!S-END',
            text    = ''
        )
        yield bdry_end
        start = end


class GetSentences(Tokenizer):
    tokenizer_key = 'sents'
    tokenizer_name = 'sent'

    @staticmethod
    def tokenizer_matcher(text):
        return list(_match_sentences(text))




def regroup_sentences(tokens, skip=None):
    """
    Group tokens into sentences by splitting at each '!S-END' token.
    """
    skip = skip or set()
    tokens = iter(tokens)
    sent = []
    while tokens:
        try:
            token = tokens.next()
        except StopIteration:
            if sent:
                yield sent
            break
        else:
            if token['name'] == '!S-END':
                #   Tag marks sentence boundary
                yield sent
                sent = []
            else:
                if token['name'] not in skip:
                    sent.append(token)


def join_sentences(sents):
    """
    Merge sentence tokens into one unit.

    Returns the values in list and dictionary format.
    """
    # ============================================================
    def fmt_sent(sent):
        res_d = dict(
            pos=(sent[0]['pos'][0], sent[-1]['pos'][-1]),
            name='sent',
            text='_'.join([s['text'] for s in sent]),
            children=sent
        )
        return res_d
    # ============================================================
    # Group sentences by element.
    # sents_T = ( zip(*sent) for sent in sents )
    # Combine the original and grouped sentences.
    # sents = itertools.izip(sents, sents_T)
    sents_d = [ fmt_sent(sent) for sent in sents ]
    return sents_d



def test_group_sentences():
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
                    original="a b c x y z",
                    current = [
                        dict(pos=(0, 1), name='w', text='a'),
                        dict(pos=(2, 3), name='w', text='b'),
                        dict(pos=(4, 5), name='w', text='c'),
                        dict(pos=(5, 5), name='!S-END', text=''),
                        dict(pos=(6, 7), name='w', text='x'),
                        dict(pos=(8, 9), name='w', text='y'),
                        dict(pos=(10, 11), name='w', text='z')
                    ],
                    tokens=dict(
                        sents = []
                    )
                )
            ),
            dict(
                text=dict(
                    original="a b c x y z",
                    current = [
                        dict(pos=(0, 1), name='w', text='a'),
                        dict(pos=(0, 5), name='sent', text='a_b_c'),
                        dict(pos=(2, 3), name='w', text='b'),
                        dict(pos=(4, 5), name='w', text='c'),
                        dict(pos=(6, 7), name='w', text='x'),
                        dict(pos=(6, 11), name='sent', text='x_y_z'),
                        dict(pos=(8, 9), name='w', text='y'),
                        dict(pos=(10, 11), name='w', text='z')
                    ],
                    tokens=dict(
                        sents = [
                            [
                                ((0, 1), 'w', 'a'), ((2, 3), 'w', 'b'),
                                ((4, 5), 'w', 'c')
                            ],
                            [
                                ((6, 7), 'w', 'x'), ((8, 9), 'w', 'y'),
                                ((10, 11), 'w', 'z')
                            ],
                        ]
                    )
                )
            ),
        )
    ]
    # pdb.set_trace()
    group_sentences = GroupSentences()
    failed = []
    for idx, (doc, expected) in enumerate(data):
        print "ORIG:", doc
        print "\tEXPECTED:", pformat(expected)
        res = group_sentences(doc)
        print '\tRESULT:', pformat(res)
        try:
            assert res == expected
        except Exception as e:
            print e
            failed.append(idx)
        print
    if failed:
        print 'Failed these tests: {0}'.format(failed)
    else:
        print 'test_group_sentences passed!', '\n'


def test():
    test_group_sentences()

if __name__ == '__main__':
    test()

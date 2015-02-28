
#   Stdlib
import pdb
from pprint import pformat

#   Custom
from .abc import CharFilter
from ..base.contractions import (
    maybe_has_contraction,
    replace_contractions_sentence,
    replace_contractions_word
)
from ..base.tokenize import update_segments


class NormalizeContractions(CharFilter):
    def process_item(self, text, **kwargs):
        #   Run test regex
        if maybe_has_contraction(text):
            #   Replace each occurrence of a contraction.
            text = replace_contractions_sentence(text)
            text = text.strip()
        return text



def test_normalize_contractions():
    original = [
        "o' the morning aaaa beat 'em",
        "could of aaaa should of bbbb might of cccc must of dddd would of",
        "coulda aaaa shoulda bbbb mighta cccc musta dddd woulda",
        "lotsa aaaa kinda bbbb sorta",
        "d'ye aaaa c'mon bbbb 'tis cccc 'twas dddd betcha eeee gotcha",
        "gimme aaaa gonna bbbb gotta cccc lemme",
        "wanna aaaa imma bbbb dunno",
        "ain't aaaa won't bbbb can't cccc cant",
        "goin' aaaa fittin' bbbb waitin'",
        "I'll aaaa you'll bbbb she'll",
        "I'd aaaa you'd bbbb she'd",
        "it's aaaa life's",
        "you're aaaa they're bbbb we're",
        "I've aaaa you've bbbb they've cccc mor'n",
    ]
    original = [
        dict(
            original    = text,
            current     = [dict(pos=(0, len(text)), name=None, text=text)],
        )
            for text in original
    ]
    expected = [
        "of the morning aaaa beat 'em",
        "could have aaaa should have bbbb might have cccc must have dddd would have",
        "could have aaaa should have bbbb might have cccc must have dddd would have",
        "lots of aaaa kind of bbbb sort of",
        "do you aaaa come on bbbb it is cccc it was dddd bet you eeee got you",
        "give me aaaa going to bbbb got to cccc let me",
        "want to aaaa i am going to bbbb do not know",
        "am n't aaaa will n't bbbb can n't cccc can n't",
        "going aaaa fitting bbbb waiting",
        "I 'll aaaa you 'll bbbb she 'll",
        "I 'd aaaa you 'd bbbb she 'd",
        "it 's aaaa life 's",
        "you 're aaaa they 're bbbb we 're",
        "I 've aaaa you 've bbbb they 've cccc more 'n",
    ]
    expected = zip(original, expected)
    expected = [
        dict(
            original            = d['original'],
            current             = [dict(pos=(0, len(text_exp)), name=None, text=text_exp)],
        )
            for d, text_exp in expected
    ]
    data = zip(original, expected)
    data = [
        (dict(text=d_orig), dict(text=d_exp))
            for d_orig, d_exp in data
    ]
    normalize_contractions = NormalizeContractions()
    for doc, expected in data:
        print "ORIG:", doc
        print "\tEXPECTED:", pformat(expected)
        res = normalize_contractions(doc)
        print '\tRESULT:', pformat(res)
        try:
            assert res == expected
        except Exception as e:
            print e
            pdb.set_trace()
            raise
        print
    print 'test_normalize_contractions passed!', '\n'




def test():
    test_normalize_contractions()


if __name__ == '__main__':
    test()

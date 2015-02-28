
import pdb

from .abc import CharFilter
from ..base.truncation import (
    truncate_boundaries, truncate_special_chars,
    truncate_whitespace, truncate_chars
)


class NormalizeWordLength(CharFilter):
    def __init__(self, how=None, *args, **kwargs):
        super(NormalizeWordLength, self).__init__(*args, **kwargs)
        if how is None: how = ['boundaries', 'whitespace']
        method_map = {
            #   Reduce sequences of (non-ws) boundary characters to a single space.
            'boundaries'    :   truncate_boundaries,
            'boundary'      :   truncate_boundaries,
            #   Reduce sequences of identical punctuation and symbols to a length of 2.
            'special'       :   truncate_special_chars,
            #   Reduce sequences of whitespace to single spaces.
            'whitespace'    :   truncate_whitespace,
            #   Reduce sequences of identical nonwhitespace to a length of 3.
            'nonwhitespace' :   truncate_chars,
        }
        methods = ( method_map.get(m) for m in how )
        self.methods = [ m for m in methods if m ]

    def process_item(self, text, **kwargs):
        orig_text = text
        for method in self.methods:
            text = method(text)
        text = text.strip()
        return text



def test_normalize_wordlength():
    normalize_wordlength = NormalizeWordLength()
    data = [
        (
            dict(
                text=dict(
                    original = """wwwww hiiiii !!!!!!!!    blahhhhh.""",
                    current = [dict(pos=(0, 34), name=None, text="""wwwww hiiiii !!!!!!!!    blahhhhh.""")]
                )
            ),
            dict(
                text=dict(
                    original = """wwwww hiiiii !!!!!!!!    blahhhhh.""",
                    current = [dict(pos=(0, 26), name=None, text="""wwwww hiiiii !!! blahhhhh.""")],
                )
            )
        )
    ]
    for doc, expected in data:
        # pdb.set_trace()
        print "ORIG:", doc
        print "\tEXPECTED:", expected
        res = normalize_wordlength(doc)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_normalize_wordlength passed!', '\n'


def test():
    test_normalize_wordlength()


if __name__ == '__main__':
    test()



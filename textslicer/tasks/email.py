

from .abc import Tokenizer
from ..base.email import match_email
from ..base.tokenize import update_segments


class GetEmail(Tokenizer):
    @staticmethod
    def tokenizer_matcher(text):
        return match_email(text)



def test_get_email():
    get_email = GetEmail()
    data = [
        (
            dict(
                text = dict(
                    original = 'send mail to me@example.com or you@example.org',
                    current = [dict(pos=(0, 46), name=None, text='send mail to me@example.com or you@example.org')],
                )
            ),
            dict(
                text = dict(
                    original = 'send mail to me@example.com or you@example.org',
                    current = [
                        dict(pos=(0, 13), name=None, text='send mail to '),
                        dict(pos=(13, 27), name='email', text='me@example.com'),
                        dict(pos=(27, 31), name=None, text=' or '),
                        dict(pos=(31, 46), name='email', text='you@example.org')
                    ],
                )
            ),
        )
    ]
    failures = 0
    for doc, expected in data:
        # pdb.set_trace()
        print "ORIG:", doc
        print "\tEXPECTED:", expected
        res = get_email(doc)
        print '\tRESULT:', res
        try:
            assert res == expected
        except Exception as e:
            failures += 1
            print "Failed!"
        print
    if not failures:
        print 'test_get_email passed!'


def test():
    test_get_email()


if __name__ == "__main__":
    test()



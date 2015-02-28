
import re
import pdb
import logging
from pprint import pformat

#   Custom
from .regex_ import match_all, REGEX_FLAGS


#:  Match email addresses
def get_email_pattern():
    digit = r'[0-9]'
    alpha = r'[A-Za-z]'
    asym = r'[!#\$%&\'*+-/=?^_`{|}~]'
    atext = r'(?: {alpha} | {digit} | {asym} )'.format(alpha=alpha, digit=digit, asym=asym)
    #   Negative lookahead to prevent exponential backtracking when encountering ellipses.
    dot_atom = r'{atext}+ (?: \. (?!\.) (?: {atext})+)*'.format(atext=atext)
    domain_literal = r'\[ (?:[\x21-\x5a\x5e-\x7e])* \]'
    local_part = dot_atom
    domain = r'{dot_atom} | {domain_literal}'.format(dot_atom=dot_atom, domain_literal=domain_literal)
    address = r'(?P<email> {local_part} \@ {domain})'.format(local_part=local_part, domain=domain)
    return address

EMAIL_PATTERN = get_email_pattern()
EMAIL_REGEX = re.compile(EMAIL_PATTERN, flags=REGEX_FLAGS)
EMAIL_SHORTCUT_REGEX = re.compile(u'\@')


def match_email(text):
    """
    >>> match_email('send mail to me@example.com or you@example.org')
        {'email_0': ('me@example.com', (13, 27)), 'email_1': ('you@example.org', (31, 46))}

    problem:
        _quetel: j'ai une astuce pour ne pas perdre de la batterie iphone..................................................................

        - Causes exponential backtracking
            - Add negative lookahead check \. (?!\.)
    """
    #   =============
    # logging.info(u"Matching email: {0}".format(text))
    #   =============
    if EMAIL_SHORTCUT_REGEX.search(text):
        res = match_all(text, ((EMAIL_REGEX, None),), ('email',))
    else:
        res = []
    return res


def test_match_email():
    data = [
        (
            'send mail to me@example.com or you@example.org',
            [
                {'name': 'email', 'text': 'you@example.org', 'pos': (31, 46)},
                {'name': 'email', 'text': 'me@example.com', 'pos': (13, 27)}
            ],
        ),
        (
            "_quetel: j'ai une astuce pour ne pas perdre de la batterie iphone......................",
            [
                {'name': 'email', 'text': 'you@example.org', 'pos': (31, 46)},
                {'name': 'email', 'text': 'me@example.com', 'pos': (13, 27)}
            ],
        ),
        (
            "_quetel: j'ai une astuce pour ne pas perdre de la batterie iphone..................................................................",
            [
                {'name': 'email', 'text': 'you@example.org', 'pos': (31, 46)},
                {'name': 'email', 'text': 'me@example.com', 'pos': (13, 27)}
            ],
        )
    ]
    passed = True
    for text, expected in data:
        res = match_email(text)
        print text
        print '\tRESULT:', pformat(res)
        if res != expected:
            passed = False
    if passed:
        print 'test_match_email passed!'


def test():
    test_match_email()


if __name__ == "__main__":
    test()



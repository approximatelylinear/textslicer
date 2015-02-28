
import re
import pdb

import unicode_utils
from .constants import REGEX_FLAGS


ALPHA_RE = re.compile('[a-z,A-Z]')

UNICHAR_BY_CAT = unicode_utils.UNICHAR_BY_CAT
PUNC = unicode_utils.PUNC
ZS = set(UNICHAR_BY_CAT['Zs'])

#: Only spaces (i.e. no newlines, tabs, etc.)
ZS_SRT = sorted(list(ZS))
WHITESPACE_PATTERN = ur'[{0}]'.format(ur''.join([ch for ch in ZS_SRT]))

#:  Simple list of ASCII boundary characters.
#   NB: No ^, $, '\b' regex patterns.
BOUNDARY_CHARS_ASCII = [
    '.', ',', ';', ':',
    '!', '?', '~', '|',
    r'\-', r'\\', '/', '`',
    '\'', '"',
    '(', ')', '\[', '\]', '{', '}',
]
_BOUNDARY_PATTERN_ASCII = ur'{0}'.format(ur''.join(BOUNDARY_CHARS_ASCII))
BOUNDARY_PATTERN_ASCII = ur'(?:[\s{0}])'.format(_BOUNDARY_PATTERN_ASCII)


#:  Simple list of ASCII non-punc special characters.
SPECIAL_CHARS_ASCII = [
    '^', '$', '&', '%',
    '*', '#', '@', '+',
    '=', '>', '<',
]
_SPCHAR_PATTERN_ASCII = ur'{0}'.format(ur''.join(SPECIAL_CHARS_ASCII))
SPCHAR_BDRY_CHARS_ASCII = sorted(
    list(set(BOUNDARY_CHARS_ASCII) | set(SPECIAL_CHARS_ASCII))
)
SPCHAR_BDRY_PATTERN_ASCII = ur'(?:[\s{0}])'.format(
    ur'{0}'.format(ur''.join(SPCHAR_BDRY_CHARS_ASCII))
)


#: All unicode punctuation
#   Sort by character
PUNC_SRT = sorted(list(PUNC))
PUNC_PATTERN = ur'[{0}]'.format(
    ur''.join([ur'\{0}'.format(ch) for ch in PUNC_SRT])
)
#: 0-2 spaces
WHITESPACE_MAYBE_PATTERN = ur'{0}{{,2}}'.format(WHITESPACE_PATTERN)

#: Punctuation, string start, string end, whitespace
BOUNDARY_CHARS = set(BOUNDARY_CHARS_ASCII) | set(SPECIAL_CHARS_ASCII) | PUNC
BOUNDARY_CHARS.remove('-')
BOUNDARY_CHARS.remove('\\')

# BOUNDARY_CHARS = set(BOUNDARY_CHARS_ASCII) | set(SPECIAL_CHARS_ASCII)
BOUNDARY_SRT = sorted(list(BOUNDARY_CHARS))

BOUNDARY_PATTERN = ur'(?:[\s{0}])'.format(
    ur''.join([ur'\{0}'.format(ch) for ch in BOUNDARY_SRT])
    # ur''.join([ur'{0}'.format(ch) for ch in BOUNDARY_SRT])
)
BOUNDARY_PATTERN_L = ur'(?:^|\b|(?:{0}+))'.format(BOUNDARY_PATTERN)
BOUNDARY_PATTERN_R = ur'(?:$|\b|(?:{0}+))'.format(BOUNDARY_PATTERN)


#:  Regex pattern used in the nltk.tokenize.WordPunctTokenizer module
WORD_PUNCT_PATTERN = ur'(?:\w+|[^\w\s]+)'
WORD_PUNCT_REGEX = re.compile(WORD_PUNCT_PATTERN, flags=REGEX_FLAGS)


#: Currency
CURRENCY_CHARS = [
    #   Dollar sign
    u'$', u'\uFE69', u'\uFF04',
    #   Cent
    u'\xa2', u'\uFFE0',
    #   Pound
    u'\xa3', u'\uFFE1',
    #   yen
    u'\xa5', u'\uFFE5',
    #   currency
    u'\xa4',
    #   won
    u'\u20A9', u'\uFFE6',
    #   euro
    u'\u20AC', u'\u20A1',
    #   euro currency
    u'\u20A0',
    #   franc
    u'\u20A3',
    #   lira
    u'\u20A4',
    #   peso
    u'\u20B1',
]
CURRENCY_PATTERN = ur'[{0}]'.format(ur''.join([ch for ch in CURRENCY_CHARS]))

CURRENCY_CHARS_ALL = set(UNICHAR_BY_CAT['Sc'])
CURRENCY_ALL_PATTERN = ur'[{0}]'.format(
    ur''.join([ch for ch in CURRENCY_CHARS_ALL])
)

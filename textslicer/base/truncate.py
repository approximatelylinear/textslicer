
#   Stdlib
import string
import pdb

#   Custom
from .constants import *
from .regex_patterns import PUNC_SRT, BOUNDARY_CHARS_ASCII

BOUNDARY_CHARS = ur''.join([ur'\{0}'.format(ch) for ch in PUNC_SRT])
#BOUNDARY_CHARS = ur''.join([ur'\{0}'.format(ch) for ch in BOUNDARY_CHARS_ASCII])

LETTER_SET = frozenset(
    string.ascii_lowercase +
    string.ascii_uppercase +
    string.digits +
    #   Keep white space.
    string.whitespace +
    #   Keep boundary chars.
    BOUNDARY_CHARS
)

REGEX_WHITESPACE = re.compile(
    ur'[\s%s]+' % (string.whitespace), flags=REGEX_FLAGS
)
TRUNCATE_CHARS_REGEXES = {}

def truncate_whitespace(text):
    """
    Truncates all whitespace sequences to a single space.
    """
    text = REGEX_WHITESPACE.sub(' ', text)
    return text


def truncate_boundaries(text, upper_bound=3):
    """
    Truncates all boundary sequences to a single item.
    """
    # boundaries = re.compile(r'[%s]+' % (PUNC), REGEX_FLAGS)
    # text = boundaries.sub(' ', text)
    text = truncate_chars(
        text,
        upper_bound=upper_bound,
        chars=BOUNDARY_CHARS
    )
    return text


def truncate_special_chars(text, upper_bound=3):
    """
    Truncates all sequences of special characters or punctuation to a length of
    two.
    """
    text = truncate_chars(
        text,
        upper_bound=upper_bound,
        chars=ESC_SPECIAL_CHARACTERS
    )
    return text


def truncate_chars(text, upper_bound=3, chars=ur'\S'):
    """
    Truncates all sequences of chars specified in the regex `chars` to a length
    of `upper_bound`.

    Default: Truncates all non-whitespace characters to a length of three.
    """
    ############
    # pdb.set_trace()
    ############
    key = chars + '_' + str(upper_bound)
    regex_ = TRUNCATE_CHARS_REGEXES.get(key)
    if not regex_:
    	upper_bound_str = '{%s,}' % upper_bound
    	regex_ = re.compile(
        	ur'([{c}])(\1){ub}'.format(c=chars, ub=upper_bound_str),
        	REGEX_FLAGS
    	)
    	TRUNCATE_CHARS_REGEXES[key] = regex_
    text = regex_.sub(ur'\1' * upper_bound, text)
    return text

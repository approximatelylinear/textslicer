
# -*- coding: utf-8 -*-

import sys
import os
import re
import json
import unicodedata
import itertools
import pdb
import traceback
from pprint import pformat
from collections import defaultdict, deque
try:
    import cPickle as pickle
except ImportError:
    import pickle

#   3rd party
from BeautifulSoup import UnicodeDammit
from termcolor import colored

#   Custom
from constants import *

PATH_DATA = os.path.join(THIS_DIR, 'data')
PATH_UCD = os.path.join(PATH_DATA, 'ucd')

def cache_ucd_blocks(source):
    ucd_blocks = defaultdict(dict)
    if isinstance(source, basestring):
        source = source.split('\n')
    for line in source:
        if (not line.strip()) or line.startswith('#'):
            continue
        codepoints, name = [i.strip() for i in line.split(';')]
        codepoints = codepoints.split('..')
        ucd_blocks['by_codepoint'][tuple(codepoints)] = name
        ucd_blocks['by_name'][name] = tuple(codepoints)
    return ucd_blocks


PATH_UCD_BLOCKS = os.path.join(PATH_UCD, 'Blocks.pkl')
PATH_UCD_BLOCKS_SRC = os.path.join(PATH_UCD, 'Blocks.txt')
if not os.path.exists(PATH_UCD_BLOCKS):
    with open(PATH_UCD_BLOCKS_SRC, 'rbU') as f:
        UCD_BLOCKS = cache_ucd_blocks(f)
    with open(PATH_UCD_BLOCKS, 'wb') as f:
        pickle.dump(UCD_BLOCKS, f)
else:
    with open(PATH_UCD_BLOCKS, 'rb') as f:
        UCD_BLOCKS = pickle.load(f)


UCD_BLOCKNAMES_SYMBOLS = [
    'Combining Diacritical Marks',
    'Combining Diacritical Marks Supplement',
    'General Punctuation',
    'Superscripts and Subscripts',
    'Currency Symbols',
    'Combining Diacritical Marks for Symbols',
    'Letterlike Symbols',
    'Number Forms',
    'Arrows',
    'Mathematical Operators',
    'Miscellaneous Technical',
    'Control Pictures',
    'Optical Character Recognition',
    'Enclosed Alphanumerics',
    'Box Drawing',
    'Block Elements',
    'Geometric Shapes',
    'Miscellaneous Symbols',
    'Dingbats',
    'Miscellaneous Mathematical Symbols-A',
    'Supplemental Arrows-A',
    'Braille Patterns',
    'Supplemental Arrows-B',
    'Miscellaneous Mathematical Symbols-B',
    'Supplemental Mathematical Operators',
    'Miscellaneous Symbols and Arrows',
    'Supplemental Punctuation',
]

#   Greek and Slavic
UCD_BLOCKNAMES_SLAVIC = [
    'Greek and Coptic',
    'Greek Extended',
    'Coptic',
    'Cyrillic',
    'Cyrillic Supplement',
    'Cyrillic Extended-A',
    'Cyrillic Extended-B',
    'Armenian',
    'Georgian',
    'Georgian Supplement',
    'Glagolitic',
]

UCD_BLOCKNAMES_SEMITIC = [
    'Hebrew',
    'Syriac',
    'Arabic',
    'Arabic Supplement',
    'Arabic Presentation Forms-A',
    'Arabic Presentation Forms-B',
    'Arabic Extended-A',
    'Tifinagh',
    'Thaana',
    'Samaritan',
    'Mandaic',
]

#   First nations
UCD_BLOCKNAMES_ABORIGINAL = [
    'Cherokee',
    'Unified Canadian Aboriginal Syllabics',
    'Unified Canadian Aboriginal Syllabics Extended',
]

#   Runic
UCD_BLOCKNAMES_RUNIC = [
    'Ogham',
    'Runic',
]

UCD_BLOCKNAMES_AFRICAN = [
    'NKo',
    'Ethiopic',
    'Ethiopic Supplement',
    'Ethiopic Extended',
    'Ethiopic Extended-A',
    'Sundanese',
    'Sundanese Supplement',
    'Vai',
    'Bamum',
]

UCD_BLOCKNAMES_ENG = [
    'Basic Latin',
    'Latin-1 Supplement',
    'Latin Extended-A',
    'Alphabetic Presentation Forms',
]

#   Pacific islands
UCD_BLOCKNAMES_PACIFIC = [
    'Tagalog',
    'Hanunoo',
    'Buhid',
    'Tagbanwa',
]

UCD_BLOCKNAMES_SOUTH_ASIAN = [
    'Sinhala',
    'Thai',
    'Lao',
    'Tibetan',
    'Myanmar',
    'Myanmar Extended-A',
    'Khmer',
    'Limbu',
    'Tai Le',
    'New Tai Lue',
    'Khmer Symbols',
    'Buginese',
    'Tai Tham',
    'Balinese',
    'Batak',
    'Lepcha',
    'Lisu',
    'Phags-pa',
    'Kayah Li',
    'Rejang',
    'Javanese',
    'Tai Viet',
    'Cham',
    'Latin Extended Additional',    #   Vietnamese
]

UCD_BLOCKNAMES_INDIAN = [
    'Devanagari',
    'Devanagari Extended',
    'Bengali',
    'Gurmukhi',
    'Gujarati',
    'Oriya',
    'Tamil',
    'Saurashtra',
    'Telugu',
    'Kannada',
    'Malayalam',
    'Ol Chiki',
    'Vedic Extensions',
    'Common Indic Number Forms',
    'Syloti Nagri',
    'Meetei Mayek',
    'Meetei Mayek Extensions',
]

UCD_BLOCKNAMES_JPN = [
    'Hiragana',
    'Katakana',
    'Katakana Phonetic Extensions',
    'Kanbun',
]

UCD_BLOCKNAMES_ZH = [
    'Bopomofo',
    'Bopomofo Extended',
    'Yi Syllables',
    'Yi Radicals',
    'Yijing Hexagram Symbols',
]

UCD_BLOCKNAMES_KOR = [
    'Hangul Jamo',
    'Hangul Compatibility Jamo',
    'Hangul Jamo Extended-A',
    'Hangul Jamo Extended-B',
    'Hangul Syllables',
]

UCD_BLOCKNAMES_CJK = [
    'CJK Radicals Supplement',
    'Kangxi Radicals',
    'Ideographic Description Characters',
    'CJK Symbols and Punctuation',
    'CJK Strokes',
    'Enclosed CJK Letters and Months',
    'CJK Compatibility',
    'CJK Unified Ideographs Extension A',
    'CJK Unified Ideographs',
    'CJK Compatibility Ideographs',
    'CJK Compatibility Forms',
] + UCD_BLOCKNAMES_JPN + UCD_BLOCKNAMES_KOR + UCD_BLOCKNAMES_ZH

UCD_BLOCKNAMES_NORTH_ASIAN = [
    'Mongolian'
]

UCD_BLOCKNAMES_ASIAN = (
        UCD_BLOCKNAMES_CJK
    +   UCD_BLOCKNAMES_INDIAN
    +   UCD_BLOCKNAMES_PACIFIC
    +   UCD_BLOCKNAMES_NORTH_ASIAN
)

#   Blocks of non-english characters
UCD_BLOCKNAMES_NONENG = (
        UCD_BLOCKNAMES_ASIAN
    +   UCD_BLOCKNAMES_AFRICAN
    +   UCD_BLOCKNAMES_RUNIC
    +   UCD_BLOCKNAMES_SEMITIC
    +   UCD_BLOCKNAMES_SLAVIC
)


def merge_codepoints(codepoints):
    codepoints = sorted(codepoints)
    codepoints = list(reversed(codepoints))
    codepoints_ = []
    #   Merge adjacent codepoints
    while codepoints:
        s, e = codepoints.pop()
        while codepoints:
            s2, e2 = codepoints.pop()
            if (e + 1) == s2:
                e = e2
            else:
                #   Add s2 and e2 back
                codepoints.append((s2, e2))
                break
        #   Add the last pair of codepoints
        codepoints_.append((s, e))
    return codepoints_


def get_codepoints_noneng(ucd_blocks):
    #   =============================

    #   =============================
    by_name = ucd_blocks['by_name']
    codepoints = ( by_name[name] for name in UCD_BLOCKNAMES_NONENG )
    codepoints = [ (int(s, 16), int(e, 16)) for s, e in codepoints ]
    codepoints = merge_codepoints(codepoints)
    return codepoints


PATH_CODEPOINTS_NONENG = os.path.join(PATH_DATA, 'cache', 'codepoints_noneng.pkl')
if not os.path.exists(PATH_CODEPOINTS_NONENG):
    CODEPOINTS_NONENG = get_codepoints_noneng(UCD_BLOCKS)
    with open(PATH_CODEPOINTS_NONENG, 'wb') as f:
        pickle.dump(CODEPOINTS_NONENG, f)
else:
    with open(PATH_CODEPOINTS_NONENG, 'rb') as f:
        CODEPOINTS_NONENG = pickle.load(f)
CHARS_NONENG = [ (unichr(s), unichr(e)) for s, e in CODEPOINTS_NONENG ]


def get_codepoints_by_lang(ucd_blocks):
    data = dict(
        # jpn       = UCD_BLOCKNAMES_JPN,
        # kor       = UCD_BLOCKNAMES_KOR,
        # zh        = UCD_BLOCKNAMES_ZH,
        cjk       = UCD_BLOCKNAMES_CJK,
        indian    = UCD_BLOCKNAMES_INDIAN,
        s_asian   = UCD_BLOCKNAMES_SOUTH_ASIAN,
        pacific   = UCD_BLOCKNAMES_PACIFIC,
        slavic    = UCD_BLOCKNAMES_SLAVIC,
        eng       = UCD_BLOCKNAMES_ENG,
        semitic   = UCD_BLOCKNAMES_SEMITIC,
        african   = UCD_BLOCKNAMES_AFRICAN,
    )
    by_name = ucd_blocks['by_name']
    for name in data:
        blockname = data[name]
        codepoints = ( by_name[name] for name in blockname )
        codepoints = [ (int(s, 16), int(e, 16)) for s, e in codepoints ]
        codepoints = merge_codepoints(codepoints)
        data[name] = codepoints
    return data


PATH_CODEPOINTS_BY_LANG = os.path.join(PATH_DATA, 'cache', 'codepoints_by_lang.pkl')
if not os.path.exists(PATH_CODEPOINTS_BY_LANG):
    CODEPOINTS_BY_LANG = get_codepoints_by_lang(UCD_BLOCKS)
    with open(PATH_CODEPOINTS_BY_LANG, 'wb') as f:
        pickle.dump(CODEPOINTS_BY_LANG, f)
else:
    with open(PATH_CODEPOINTS_BY_LANG, 'rb') as f:
        CODEPOINTS_BY_LANG = pickle.load(f)

################
# pdb.set_trace()
################
LANG_BY_CHARS = (
    ((s, lang), (e + 1, 'other'))
        for lang, cps in CODEPOINTS_BY_LANG.iteritems()
            for s, e in cps
)
################
# pdb.set_trace()
################
LANG_BY_CHARS = itertools.chain.from_iterable(LANG_BY_CHARS)
LANG_BY_CHARS = sorted(LANG_BY_CHARS, key=lambda x: x[0])

result = []
LANG_BY_CHARS = list(reversed(LANG_BY_CHARS))
while LANG_BY_CHARS:
    cp, name = LANG_BY_CHARS.pop()
    # print cp, name
    try:
        cp2, name2 = LANG_BY_CHARS.pop()
    except IndexError:
        result.append((cp, name))
        break
    # print cp2, name2
    # pdb.set_trace()
    if cp == cp2:
        if name != 'other':
            result.append((cp, name))
        else:
            result.append((cp2, name2))
    else:
        result.append((cp, name))
        LANG_BY_CHARS.append((cp2, name2))
LANG_BY_CHARS = result
LANG_BY_CHARS_CP, LANG_BY_CHARS_NAME = zip(*LANG_BY_CHARS)



def get_all_unichars(s, e):
    allpoints = range(*[int('0x{0}'.format(i), 16) for i in (s, e)])
    limit = 2 << 15
    unichars = set([ unichr(p) for p in allpoints if p < limit])
    return unichars


def cache_unichar_by_cat():
    unicode_category = defaultdict(set)
    for c in map(unichr, range(sys.maxunicode + 1)):
        unicode_category[unicodedata.category(c)].add(c)
    return unicode_category


PATH_UNICHAR_BY_CAT = os.path.join(PATH_DATA, 'cache', 'unichar_by_cat.pkl')
if not os.path.exists(PATH_UNICHAR_BY_CAT):
    UNICHAR_BY_CAT = cache_unichar_by_cat()
    with open(PATH_UNICHAR_BY_CAT, 'wb') as f:
        pickle.dump(UNICHAR_BY_CAT, f)
else:
    with open(PATH_UNICHAR_BY_CAT, 'rbU') as f:
        UNICHAR_BY_CAT = pickle.load(f)

try:
    import regex
    REGEX_FLAGS_ = regex.IGNORECASE|regex.UNICODE|regex.X|regex.DOTALL|regex.MULTILINE
    REGEX_SYMBOLS = regex.compile(r'\p{S}+', flags=REGEX_FLAGS_)
    REGEX_PUNC = regex.compile(r'\p{P}+', flags=REGEX_FLAGS_)
    REGEX_COMBINING_MARKS = regex.compile('\p{Block=CombiningDiacriticalMarks}')
except ImportError:
    REGEX_SYMBOLS = None
    REGEX_PUNC = None
    REGEX_COMBINING_MARKS = None


SYMBOLS = set()
for cat in ['Sm', 'Sc', 'Sk', 'So']: SYMBOLS |= UNICHAR_BY_CAT[cat]

PUNC_ALL = set()
for cat in ['Pc', 'Pd', 'Ps', 'Pe', 'Pi', 'Pf', 'Po']:
    PUNC_ALL |= UNICHAR_BY_CAT[cat]


#   Only keep commonly used punctuation.
RANGES_PUNC = [
    (u'\x00', u'\u06d4'),
    (u'\u0964', u'\u0970'),
    (u'\u0f0b', u'\u0f11'),
    (u'\u104a', u'\u104b'),
    (u'\u10fb', u'\u1368'),
    (u'\u166d', u'\u166d'),
    (u'\u17d4', u'\u17d6'),
    (u'\u1800', u'\u180a'),
    (u'\u2010', u'\u29fd'),
    (u'\u2e00', u'\u2e13'),
    (u'\u2e17', u'\u2e18'),
    (u'\u2e1a', u'\u2e30'),
    (u'\u3001', u'\u30fb'),
    (u'\ufd3e', u'\uff65'),
]
PUNC = set()
for c in PUNC_ALL:
    for s, e in RANGES_PUNC:
        if s <= c <= e:
            PUNC.add(c)
            break


WHITESPACE = set()
for cat in ['Zs', 'Zl', 'Zp']: WHITESPACE |= UNICHAR_BY_CAT[cat]

COMBINING_MARKS = set()
COMBINING_MARKS_BLOCKS = [
    'Combining Diacritical Marks',
    'Combining Diacritical Marks Supplement',
    'Combining Diacritical Marks for Symbols'
]
for block in COMBINING_MARKS_BLOCKS:
    COMBINING_MARKS |= get_all_unichars(*UCD_BLOCKS['by_name'][block])


UNICODE_SYMBOL_EQUIVALENTS = {
    # double quote
    u'\u00AB': u'"',    #   «
    u'\u00BB': u'"',    #   »
    u'\u201C': u'"',
    u'\u201D': u'"',
    u'\u201E': u'"',    #   „
    u'\u201F': u'"',    #   ‟
    u'\u2033': u'"',    #   ″
    u'\u2036': u'"',    #   ‶
    u'\u275D': u'"',    #   ❝
    u'\u275E': u'"',    #   ❞
    u'\u301D': u'"',    #   〝
    u'\u3003': u'"',    #   〃
    u'\uFF02': u'"',    #   ＂

    # single quote
    u'\u0060': u'\'',
    u'\u00b4': u'\'',
    u'\u2018': u'\'',
    u'\u2019': u'\'',
    u'\u201b': u'\'',   #   ‛
    u'\u2032': u'\'',   #   ′
    u'\u2035': u'\'',   #   ‵
    u'\u2039': u'\'',   #   ‹
    u'\u203A': u'\'',   #   ›
    u'\u275B': u'\'',   #   ❛
    u'\u275C': u'\'',   #   ❜
    u'\u2308': u'\'',   #   ⌈
    u'\u230A': u'\'',   #   ⌊
    u'\u2E02': u'\'',   #   ⸂
    u'\u2E03': u'\'',   #   ⸃
    u'\u2E0C': u'\'',   #   ⸌
    u'\u2E0D': u'\'',   #   ⸍
    u'\u2E1C': u'\'',   #   ⸜
    u'\u2E1D': u'\'',   #   ⸝
    u'\uFE10': u'\'',   #   ︐
    u'\uFE11': u'\'',   #   ︑
    u'\uFF07': u'\'',   #   ＇

    # ellipsis
    u'\u2026': u'...',
    u'\u22EF': u'...',  #   ⋯

    # hyphen/dash
    u'\u2014': u'-',
    u'\u2013': u'-',
    u'\u2043': u'-',    #   ⁃
    u'\u23BA': u'-',    #   ⎺
    u'\u23BB': u'-',    #   ⎻
    u'\u23BC': u'-',    #   ⎼
    u'\u23BD': u'-',    #   ⎽
    u'\u2500': u'-',    #   ─
    u'\u2501': u'-',    #   ━
    u'\u2504': u'-',    #   ┄
    u'\u2505': u'-',    #   ┅
    u'\u2508': u'-',    #   ┈
    u'\u2509': u'-',    #   ┉
    u'\u254C': u'-',    #   ╌
    u'\u254D': u'-',    #   ╍

    # Trademark
    u'\u2122': u'TM',
    # Registered
    u'\u00ae': u'(R)',
    # copyright
    u'\u00a9': u'(C)',
    # times operator
    u'\u00d7': u' x ',
}



def to_unicode(text, is_html=False, html=None):
    """
    Converts text to unicode by leveraging BeautifulSoup's superior encoding
    detection.

    From http://lxml.de/elementsoup.html .
    """
    if html is not None: is_html = html
    if text is None: text = u''
    if not isinstance(text, unicode):
        try:
            #   Try to convert it with the utf-8 codec
            text = unicode(text, 'utf-8')
        except UnicodeDecodeError:
            #   Didn't work...Try to detect the encoding with heuristics
            unicode_kwargs = {}
            if is_html:
                unicode_kwargs['isHTML'] = True
                unicode_kwargs['smartQuotesTo'] = 'html'
            else:
                unicode_kwargs['isHTML'] = False
                unicode_kwargs['smartQuotesTo'] = None
            converted = UnicodeDammit(text, **unicode_kwargs)
            text = converted.unicode or u''
    return text


def dict_to_unicode(doc):
    docs = deque([(0, doc)])
    #idx = 0
    while docs:
        #if idx > 10000:
        #    break
        #idx += 1
        depth, doc_ = docs.popleft()
        if isinstance(doc_, dict):
            for k in doc_:
                if isinstance(doc_[k], str):
                    doc_[k] = to_unicode(doc_[k])
                elif hasattr(doc_[k], '__iter__'):
                    #   Sequence
                    docs.append((depth + 1, doc_[k]))
        elif hasattr(doc_, '__iter__'):
            for d in doc_:
                docs.append((depth + 1, d))
    return doc



def replace_unicode(text):
    """
    Normalizes the unicode in :text.

            #. Replaces any non-ascii characters we want to preserve with an ascii translation (e.g. u'\u00ae' ==> '(R)').
            #. Decomposes each unicode character into its constituents, preserving whatever has a direct ascii translation, and discarding the rest.

        Note: This will clobber any non-English posts.
    """
    text = english_symbols_to_ascii(text)
    text = unicode_to_ascii(text)
    return text


def normalize_unicode(text):
    if not isinstance(text, unicode):
        text = unicode(text, encoding='utf-8')
    try:
        # Normalize with NFKD and throw out all combining marks
        text = unicodedata.normalize('NFKD', text)
    except Exception as e:
        print e
        print colored(traceback.format_exc(), 'red')
        # pdb.set_trace()
    if REGEX_COMBINING_MARKS:
        text = REGEX_COMBINING_MARKS.sub(u'', text)
    else:
        text = u''.join( ch for ch in text if ch not in COMBINING_MARKS )
    return text


def normalize_unicode_lang_det(text):
    #   Preserve (and combine) combining marks for language detection
    return unicodedata.normalize('NFKC', text)


def unicode_to_ascii(text):
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    return text


def english_symbols_to_ascii(text):
    """
    Replaces common unicode patterns with ascii equivalents in a more-or-less
    straightforward but occasionally ad-hoc manner.
    """
    for orig, repl in UNICODE_SYMBOL_EQUIVALENTS.iteritems(): text = text.replace(orig, repl)
    return text


def remove_symbols(text):
    if REGEX_SYMBOLS:
        text = REGEX_SYMBOLS.sub('', text)
    else:
        text = ''.join( c for c in text if c not in SYMBOLS )
    return text


def remove_punc(text):
    if REGEX_PUNC:
        text = REGEX_PUNC.sub('', text)
    else:
        text = ''.join( c for c in text if c not in PUNC )
    return text


def get_symbols(text):
    return ( dict(pos=(idx, idx + len(c)), text=c, name='symbol') for idx, c in enumerate(text) if c in SYMBOLS )


def get_punc(text):
    return ( dict(pos=(idx, idx + len(c)), text=c, name='punc') for idx, c in enumerate(text) if c in PUNC )



def test_get_symbols():
    data = [
        (u'abcdefg', []),
        (u'abcdefg \u00AE', [dict(pos=(8, 9), text=u'\u00AE', name='symbol')]),
        (
            u'abc\u00A9defg \u00AE',
            [
                dict(pos=(3, 4), text=u'\u00A9', name='symbol'),
                dict(pos=(9, 10), text=u'\u00AE', name='symbol')
            ]
        )
    ]
    for text, expected in data:
        # pdb.set_trace()
        res = list(get_symbols(text))
        print text.encode('utf-8'), res
        assert res == expected
    print 'test_get_symbols passed!', '\n'


def test_get_punc():
    data = [
        (u'abcdefg', []),
        (u'abcdefg .', [dict(pos=(8, 9), text=u'.', name='punc')]),
        (
            u'abc!defg .',
            [
                dict(pos=(3, 4), text=u'!', name='punc'),
                dict(pos=(9, 10), text=u'.', name='punc')
            ]
        ),
    ]
    for text, expected in data:
        # pdb.set_trace()
        res = list(get_punc(text))
        print text.encode('utf-8'), res
        assert res == expected
    print 'test_get_punc passed!', '\n'


def test():
    test_get_symbols()
    test_get_punc()


if __name__ == "__main__":
    test()

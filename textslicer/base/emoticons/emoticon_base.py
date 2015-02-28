
#   stdlib
import re
import pdb
import logging

#   Custom
from ..regex_ import REGEX_FLAGS, match_all
from ..regex_patterns import WHITESPACE_MAYBE_PATTERN, PUNC_PATTERN, BOUNDARY_PATTERN
from .constants_emoji import EMOJI


BOUNDARY_PATTERN = ur'(?:^|(?:{0}+)|$)'.format(BOUNDARY_PATTERN)


def get_emoji_regexes(emoji):
    #   ==========================================
    def get_regex(chars):
        pat = ur'(?P<emo>[{0}])'.format(ur''.join([ch for ch in chars]))
        return re.compile(pat, flags=REGEX_FLAGS)
    #   ==========================================
    result = {}
    for k, chars in emoji.iteritems():
        ################
        # logging.info(u"{0} {1}".format(k, chars))
        # pdb.set_trace()
        ############
        if chars:
            result[k] = get_regex(chars)
    return result
EMOJI_REGEXES = get_emoji_regexes(EMOJI)


#   Emoticon patterns adapted from Brendan O'Connour's `emoticons.py` script.
#   Eyes
EYES_NORMAL = ur'[:=]'       #   :, =
EYES_COLON = ur':'       #   :, =
EYES_WINK = ur'[;]'          #   ;

#   Nose
NOSE = ur"""
(?:
    {ws}    #   Optional whitespace
    [o\-\^]  #   o, -, ^
    {ws}
)
""".format(
    ws=WHITESPACE_MAYBE_PATTERN
)

NOSE_DASH = ur"""
(?:
    {ws}    #   Optional whitespace
    \-      #   o, -
    {ws}
)
""".format(
    ws=WHITESPACE_MAYBE_PATTERN
)

#   Mouth
MOUTHS_HAPPY = ur'[D\)\]\>\}]'         #   D, ), ]
MOUTHS_SAD = ur'[\(\[\<\{\@]'            #   (, [

MOUTHS_TONGUE = ur'[pP]'             #   p, P
OTHER_MOUTHS = ur'[doO\/\\]'         #   d, o, O, /, \
MOUTHS_SURPRISE = ur'[doO]'          #   d, o, O
MOUTHS_WRY = ur'[\/\\\|]'            #   /, \, |


#   Combinations
HAPPY_EMOTICON =  ur"""
(?:
    # \^_\^
    # |
    (?:
        (?:
            {eyes}|{wink}
        )
        {nose}*{happy}
    )
)
""".format(
    eyes=EYES_NORMAL,
    wink=EYES_WINK,
    nose=NOSE,
    happy=MOUTHS_HAPPY,
)


HAPPY_EMOTICON_REV =  ur"""
(?:
    # \^_\^
    # |
    (?:
        {sad}{nose}*
        (?:
            {eyes}|{wink}
        )
    )
)
""".format(
    eyes=EYES_NORMAL,
    wink=EYES_WINK,
    nose=NOSE,
    sad=MOUTHS_SAD
)

SAD_EMOTICON =  ur"""
(?:
    (?:
        {eyes}|{wink}
    )
    {nose}*{sad}
)
""".format(
    eyes=EYES_NORMAL,
    wink=EYES_WINK,
    nose=NOSE,
    sad=MOUTHS_SAD,
)
SAD_EMOTICON_REV =  ur"""
(?:
    {happy}{nose}*
    (?:
        {eyes}|{wink}
    )
)
""".format(
    eyes=EYES_NORMAL,
    wink=EYES_WINK,
    nose=NOSE,
    happy=MOUTHS_HAPPY,
)

EYES_NORMAL_WINK = ur"""
    (?:
        {eyes}|{wink}
    )
""".format(
    eyes=EYES_NORMAL,
    wink=EYES_WINK,
)

EYES_COLON_WINK = ur"""
    (?:
        {eyes}|{wink}
    )
""".format(
    eyes=EYES_COLON,
    wink=EYES_WINK,
)


TONGUE_EMOTICON = EYES_NORMAL_WINK + NOSE_DASH + MOUTHS_TONGUE
WRY_EMOTICON = EYES_NORMAL_WINK + NOSE + ur'*' + MOUTHS_WRY
WRY_EMOTICON_REV = MOUTHS_WRY + NOSE + ur'*' + EYES_NORMAL_WINK
SURPRISE_EMOTICON = EYES_COLON_WINK + NOSE_DASH + MOUTHS_SURPRISE
SURPRISE_EMOTICON_REV = MOUTHS_SURPRISE + NOSE_DASH + EYES_COLON_WINK
LOVE_EMOTICON = ur'(?:(?:<3)|<{2,}|>{2,})'


EMOTICON = ur"""
(?:
    (?:
        [\^\-T][_o]{{,3}}[\^\-T]        #   e.g. '^o^', '-__-', 'T_T'
                                        #   NB: Extra curly braces used to make literal for string formatter.
    )
    |
    {love}                             #   <3 or >>... or <<...
    |
    (?:
        {eyes}|{wink}                   #   Eyes
    )
        {nose}*                         #   Optional Nose
    (?:
        {tongue}|{surprise}|{wry}|{sad}|{happy}  #   Mouths
    )
)
""".format(
    love=LOVE_EMOTICON,
    eyes=EYES_NORMAL,
    wink=EYES_WINK,
    nose=NOSE,
    surprise=MOUTHS_SURPRISE,
    wry=MOUTHS_WRY,
    tongue=MOUTHS_TONGUE,
    sad=MOUTHS_SAD,
    happy=MOUTHS_HAPPY
)
EMOTICON_PATTERN = EMOTICON


"""
    emoticon = "(?:{bdry}{pat}{bdry})".format(bdry=BOUNDARY_PATTERN, pat=pat)
"""

def make_regex(pat):
    emoticon = ur"""
    (?:
        {bdry}
        (?P<emo>{pat})
        {bdry}
    )
    """.format(
        bdry=BOUNDARY_PATTERN,
        pat=pat
    )
    _regex = re.compile(emoticon, flags=REGEX_FLAGS)
    return _regex


HAPPY_REGEX = make_regex(HAPPY_EMOTICON)
HAPPY_REGEX_REV = make_regex(HAPPY_EMOTICON_REV)
SAD_REGEX = make_regex(SAD_EMOTICON)
SAD_REGEX_REV = make_regex(SAD_EMOTICON_REV)
TONGUE_REGEX = make_regex(TONGUE_EMOTICON)
WRY_REGEX = make_regex(WRY_EMOTICON)
WRY_REGEX_REV = make_regex(WRY_EMOTICON_REV)
SURPRISE_REGEX = make_regex(SURPRISE_EMOTICON)
SURPRISE_REGEX_REV = make_regex(SURPRISE_EMOTICON_REV)
EMOTICON_REGEX = make_regex(EMOTICON_PATTERN)
LOVE_REGEX = make_regex(LOVE_EMOTICON)


def match_emoticon_happy(text):
    res = match_all(
        text,
        ((HAPPY_REGEX, 'emo_happy'), (HAPPY_REGEX_REV, 'emo_happy'),),# (EMOJI_REGEXES['happy'], 'happy')),
        ('emo',),
        shortcircuit=False
    )
    return res

def match_emoticon_sad(text):
    res = match_all(
        text,
        ((SAD_REGEX, 'emo_sad'), (SAD_REGEX_REV, 'emo_sad'),),# (EMOJI_REGEXES['sad'], 'sad')),
        ('emo',),
        shortcircuit=False
    )
    return res

def match_emoticon_love(text):
    res = match_all(
        text,
        ((LOVE_REGEX, 'emo_love'),),# (EMOJI_REGEXES['love'], 'love')),
        ('emo',),
        shortcircuit=False
    )
    return res

def match_emoticon_silly(text):
    res = match_all(
        text,
        ((TONGUE_REGEX, 'emo_silly'),), #(EMOJI_REGEXES.get('silly', ''), 'silly')),
        ('emo',),
        shortcircuit=False
    )
    return res

def match_emoticon_wry(text):
    res = match_all(
        text,
        ((WRY_REGEX, 'emo_wry'), (WRY_REGEX_REV, 'emo_wry')), #(EMOJI_REGEXES['wry'], 'wry')),
        ('emo',),
        shortcircuit=False
    )
    return res

def match_emoticon_surprise(text):
    res = match_all(
        text,
        ((SURPRISE_REGEX, 'emo_surprise'), (SURPRISE_REGEX_REV, 'emo_surprise'),), #(EMOJI_REGEXES['surprise'], 'surprise')),
        ('emo',),
        shortcircuit=False
    )
    return res

def match_emoticons(text):
    result = []
    matchers = [
        match_emoticon_happy,
        match_emoticon_sad,
        match_emoticon_love,
        match_emoticon_silly,
        match_emoticon_wry,
        match_emoticon_surprise
    ]
    for matcher in matchers:
        ##############
        # pdb.set_trace()
        ##############
        res = matcher(text)
        if res: result.extend(res)
    result = sorted(result, key=lambda d: d['pos'])
    return result



def match_emoticon_OLD(s, regexes, name):
    res = {}
    count = 0
    for regex_ in regexes:
        idx_start = 0
        # pdb.set_trace()
        while idx_start < len(s):
            #print idx_start
            k = '{0}_{1}'.format(('emo_{0}'.format(name) if name else 'emo'), count)
            m = regex_.search(s, idx_start)
            if m:
                g_emo = m.group('emo')
                idxs_emo = m.span('emo')
                idx_start = idxs_emo[1]
                res[k] = (g_emo, idxs_emo)
                count += 1
            else:
                g_emo, idxs_emo = None, None
                idx_start = len(s)
    return res


def test_happy():
    data = [
        ':)', '(:',
        '=]', '[=',
        ';]', '[;',
        ':-)', '(-:',
        ':o)', '(o:',
        ';->', '<-:',
    ]
    seqs = [(data, match_emoticon_happy)]
    _test(seqs, 'happy')


def _test(seqs, name):
    boundaries = ' .'#\n\r\t.,;:!?-\/[]()'
    for seq, func in seqs:
        for pat in seq:
            test_seqs = [
                (
                    bdry,
                    (
                        "blah blah{b}{p} blah{b}{p} blah".format(p=pat, b=bdry),
                        [
                            {'text': pat, 'pos': (16 + len(pat), 16 + (len(pat) * 2)), 'name': '{0}_emo'.format(name)},
                            {'text': pat, 'pos': (10, 10 + len(pat)), 'name': '{0}_emo'.format(name)},
                        ]
                    ),
                    (
                        "blah blah {p}{b}blah {p}{b}blah".format(p=pat, b=bdry),
                        [
                            {'text': pat, 'pos': (16 + len(pat), 16 + (len(pat) * 2)), 'name': '{0}_emo'.format(name)},
                            {'text': pat, 'pos': (10, 10 + len(pat)), 'name': '{0}_emo'.format(name)},
                        ]
                    )
                )
                    for bdry in boundaries
            ]
            for bdry, (before, expected_before), (after, expected_after) in test_seqs:
                print 'INPUT:', before
                actual_before = func(before)
                print 'ACTUAL:', actual_before
                try:
                    assert actual_before == expected_before
                except Exception as e:
                    print 'ERROR: expected {0} but got {1}'.format(expected_before, actual_before)
                print
                print 'INPUT:',after
                actual_after = func(after)
                print 'ACTUAL:', actual_after
                try:
                    assert actual_after == expected_after
                except Exception as e:
                    print 'ERROR: expected {0} but got {1}'.format(expected_after, actual_after)
                print


def test():
    test_happy()


def test_OLD():
    """
    from python_utilities.text_processing import emoticons
    emoticons.test()
    """
    happy = [
        ':)', '(:',
        '=]', '[=',
        ';]', '[;',
        ':-)', '(-:',
        ':o)', '(o:',
        ';->', '<-:',
    ]
    sad = [
        ':(', '):',
        '=[', ']=',
        ';[', '];',
        ':-(', ')-:',
        ':o(', ')o:',
        ';-<', '>-:',
    ]
    tongue = [
        ':-P',
        '=-P',
        ';-p',
        ':-P',
    ]
    surprise = [
        ':-o', 'O-:',
        ';-O', 'o-;',
    ]
    wry = [
        ':|', '|:',
        ':-|', '|-:',
        ';|', '|;',
        ';-|', '|-;',
        '=|', '|=',
        '=-|', '|-=',
        ':\\', '\:',
        ':-\\', '\-:',
        ';\\', '\;',
        ';-\\', '\-;',
        '=\\', '\=',
        '=-\\', '\-=',
        ':/', '/:',
        ':-/', '/-:',
        ';/', '/;',
        ';-/', '/-;',
        '=/', '/=',
        '=-/', '/-=',
    ]
    love = [
        '<3',
        '<<<<',
        '>>>',
    ]
    seqs = [
        # (happy, parse_emoticon_happy, '<emo:SMILE>'),
        # (sad, parse_emoticon_sad, '<emo:FROWN>'),
        # (tongue, parse_emoticon_tongue, '<emo:SILLY>'),
        # (surprise, parse_emoticon_surprise, '<emo:SURPRISE>'),
        # (wry, parse_emoticon_wry, '<emo:WRY>'),
        # (love, parse_emoticon_love, '<emo:LOVE>'),
        ##########
        (happy, match_emoticon_happy, '<emo:SMILE>'),
        (sad, match_emoticon_sad, '<emo:FROWN>'),
        (tongue, match_emoticon_silly, '<emo:SILLY>'),
        (surprise, match_emoticon_surprise, '<emo:SURPRISE>'),
        (wry, match_emoticon_wry, '<emo:WRY>'),
        (love, match_emoticon_love, '<emo:LOVE>'),
    ]
    # boundaries = ur' \n\r\t\.\,\;\:\!\?\-\\\/\[\]\(\)'
    boundaries = ' \n\r\t.,;:!?-\/[]()'
    for seq, func, expected in seqs:
        for pat in seq:
            test_seqs = [
                (
                    bdry,
                    (
                        "blah blah{b}{p} blah{b}{p} blah".format(p=pat, b=bdry),
                        "blah blah{b}{p} blah{b}{p} blah".format(p=expected, b=bdry)
                    ),
                    (
                        "blah blah {p}{b}blah {p}{b}blah".format(p=pat, b=bdry),
                        "blah blah {p}{b}blah {p}{b}blah".format(p=expected, b=bdry),
                    )
                )
                    for bdry in boundaries
            ]
            for bdry, (before, expected_before), (after, expected_after) in test_seqs:
                print 'INPUT:', before
                actual_before = func(before)
                print 'ACTUAL:', actual_before
                if not actual_before == expected_before:
                    print 'ERROR: expected {0} but got {1}'.format(expected_before, actual_before)
                print
                print 'INPUT:',after
                actual_after = func(after)
                print 'ACTUAL:', actual_after
                if not actual_after == expected_after:
                    print 'ERROR: expected {0} but got {1}'.format(expected_after, actual_after)
                print


"""
    from python_utilities.text_processing import emoticons
    emoticon_tests = [
        #   Pass
        ':)',     #   Eyes, Mouth
        '=[',
        ';]',
        ':-)',    #   Eyes, Nose, MoUth
        ';-P',
        ':OO',
        '=oO',
        '^_^',
        '^o^',
        #   Fail
        '---',
        '-)',
        ':-',
        ';--',
        ':-P['  #   Currently matches ':-P' and passes.
    ]
    for s in emoticon_tests: print s, str(emoticons.EMOTICON_REGEX.findall(s))
"""

if __name__ == "__main__":
    test()

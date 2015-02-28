# -*- coding: utf-8 -*-

import re
import pdb

from .regex_ import REGEX_FLAGS
from .regex_patterns import SPCHAR_BDRY_PATTERN_ASCII

#############
DEBUG = False
#############

#: Heuristics for identifying English contraction expressions.
#: (NB: These assume that hashtags and mentions have been filtered out, since
#  those should be treated as literal expressions wrt contractions.)
CONTRACTIONS_PATTERNS_FULL_REPL = [
    # Mispellings
    (ur"(?: cannot|cant)"                                , ur'can not'),
    (ur"(?: (got|beat|join) \s* (?: '?em))"              , ur'\1 them'),
    (ur"(?: (bet|get|got|let|want|what?)cha)"            , ur'\1 you'),
    (ur"(?: (could|might|must|should|would)\s+of)"       , ur'\1 have'),
    (ur"(?: (could|might|must|should|would) a)"          , ur'\1 have'),
    (ur"(?: (kind|lots|sort) a)"                         , ur'\1 of'),
    (ur"(?: (out|lot) ta)"                               , ur'\1 of'),
    (ur"(?: d\'?(?: ye|ya))"                             , ur'do you'),
    (ur"(?: gimme)"                                      , ur'give me'),
    (ur"(?: lemme)"                                      , ur'let me'),
    (ur"(?: gonna)"                                      , ur'going to'),
    (ur"(?: wanna)"                                      , ur'want to'),
    (ur"(?: gotta)"                                      , ur'got to'),
    (ur"(?: (?: hav|haf) ta)"                            , ur'have to'),
    (ur"(?: c\'?m (on|in|out))"                          , ur'come \1'),
    (ur"(?: whad{,3}[jy]a)"                              , ur'what do you'),
    (ur"(?: howd{,3}[jy]a)"                              , ur'how do you'),
    (ur"(?:imma)"                                        , ur'i am going to'),
    (ur"(?: dunno )"                                     , ur'do not know'),
    (ur"(o\')\s+"                                        , ur'of '),
    #   Auxilliaries
    #       Literals
    (ur"(?: (is|are|was|were|have) nt)"                  , ur"\1 not"),
    #       Patterns
    (ur"(?: (\w+)\ ?'ll )"                               , ur'\1 will'),
    (ur"(?: (\w+)\ ?'re )"                               , ur'\1 are'),
    (ur"(?: (\w+)\ ?'ve )"                               , ur'\1 have'),
    (ur"(?: ca\ ?n't )"                                  , ur'can not'),
    (ur"(?: wo\ ?n't )"                                  , ur'will not'),
    (ur"(?: (\w+)\ ?n't )"                               , ur'\1 not'),
    (ur"(?: (\w+)\ ?'s )"                                , ur"\1 s"),
    (ur"(?: i\ ?'m )"                                    , ur"I am"),
    (ur"(?: (\w+)\ ?'d )"                                , ur"\1 'd"),
    (ur"(?: mor\ ?'n )"                                  , ur"more than"),
    (ur"(?: (\w+)\ ?'n )"                                , ur"\1 'n"),
    (ur"(?: 'em)"                                        , ur"them"),
]

#   TBD
#   Is it more efficient to search for individual literal in a dictionary
#   than use a regex?
CONTRACTIONS_LITERALS = dict()


#:  Patterns where we only split out the auxiliaries, rather than guessing the
#:  replacement.
CONTRACTIONS_PATTERNS_SPLIT = [
    # Mispellings
    (ur"(?: cannot)"                                     , ur"can not"),
    (ur"(?: (?P<em>got|beat|join) \s* (?: \'?em))"       , ur"\1 em"),
    (ur"(?: (bet|get|got|let|want|what)cha)"             , ur"\1 you"),
    (ur"(?: (be|ge|go|le|wan|wha)cha)"                   , ur"\1t you"),
    (ur"(?: (could|might|must|should|would)\s+of)"       , ur"\1 have"),
    (ur"(?: (could|might|must|should|would) (?:ve|a))"   , ur"\1 have"),
    (ur"(?: (kind|lots|sort) a)"                         , ur"\1 of"),
    (ur"(?: (out|lot) ta)"                               , ur"\1 of"),
    (ur"(?: d\'?(?: ye|ya))"                             , ur'do you'),
    (ur"(?: gimme)"                                      , ur'give me'),
    (ur"(?: lemme)"                                      , ur'let me'),
    (ur"(?: gonna)"                                      , ur'going to'),
    (ur"(?: wanna)"                                      , ur'want to'),
    (ur"(?: gotta)"                                      , ur'got to'),
    (ur"(?: (?: hav|haf) ta)"                            , ur'have to'),
    (ur"(?: c\'?m (on|in|out))"                          , ur'come \1'),
    (ur"(?: whad{,3}[jy]a)"                              , ur'what do you'),
    (ur"(?: howd{,3}[jy]a)"                              , ur'how do you'),
    (ur"(?:i'?mm?a)"                                     , ur'i am going to'),
    (ur"(?: dunno )"                                     , ur'do not know'),
    (ur"(o\')\s+"                                        , ur'of '),
    #   Auxilliaries
    (ur"(?: (is|are|was|were|have|do)n'?t)"             , ur"\1 not"),
    (ur"(?: ain'?t )"                                   , ur"am not"),
    (ur"(?: can'?t )"                                   , ur"can not"),
    (ur"(?: won'?t )"                                   , ur"will not"),
    (ur"(?: i'm )"                                      , ur"i am"),
    (ur"(?: mor'n )"                                    , ur"more n"),
    (ur"(?: (\w+)'ll )"                                 , ur"\1 will"),
    (ur"(?: (\w+)'re )"                                 , ur"\1 are"),
    (ur"(?: (\w+)'ve )"                                 , ur"\1 have"),
    (ur"(?: (\w+)n't )"                                 , ur"\1 not"),
    (ur"(?: (\w+)'s )"                                  , ur"\1 s"),
    (ur"(?: (\w+)'d )"                                  , ur"\1 d"),
    (ur"(?: (\w+)'n )"                                  , ur"\1 n"),
    (ur"(?: (\w+)'em )"                                 , ur"\1 em"),
]


#: Fully replace contractions.
CONTRACTIONS_PATTERNS = CONTRACTIONS_PATTERNS_FULL_REPL
#: Leave the contracted portion as is (in most cases).
CONTRACTIONS_PATTERNS = CONTRACTIONS_PATTERNS_SPLIT
#: Test for the presence of contractions
CONTRACTIONS_PATTERN_TEST = ur"""
    '|em|cha|mm|nn|tt|wha|how|ould|ight|ust|nt|hav|haf|dye|dya|kind|log|sort
"""

CONTRACTIONS_REGEX_TEST = re.compile(
    CONTRACTIONS_PATTERN_TEST, flags=REGEX_FLAGS
)

#   Regexes designed to operate on the word level
CONTRACTIONS_PATTERNS_WORD = CONTRACTIONS_PATTERNS + [
    (ur"(?: '?t (is|was))"                              , ur"it \1"),
    (ur"(?: (\w+?)in')"                                 , ur"\1ing"),
]

CONTRACTIONS_REGEXES_WORD = [
    (re.compile(pat, flags=REGEX_FLAGS), repl)
        for pat, repl in CONTRACTIONS_PATTERNS_WORD
]

CONTRACTIONS_PATTERNS_SPC_BDRY = [
    #   Space at ends of replacement is intentional.
    #   (Pattern consumes boundaries.)
    (
        ur"(?: (?:^|{0}+?) (?: '?t (is|was)) \b)".format(
            SPCHAR_BDRY_PATTERN_ASCII
        ),
        ur' it \1 '
    ),
    (
        ur"(?: \b(?: (\w+?)in')(?:{0}+|$))".format(
            SPCHAR_BDRY_PATTERN_ASCII
        ),
        ur" \1ing "
    ),
]

CONTRACTIONS_REGEXES_BDRY = [
    (re.compile(ur"\b{0}\b".format(pat), flags=REGEX_FLAGS), repl)
        for pat, repl in CONTRACTIONS_PATTERNS
]
CONTRACTIONS_REGEXES_SPC_BDRY = [
    (re.compile(pat, flags=REGEX_FLAGS), repl)
        for pat, repl in CONTRACTIONS_PATTERNS_SPC_BDRY
]
CONTRACTIONS_REGEXES = CONTRACTIONS_REGEXES_BDRY + CONTRACTIONS_REGEXES_SPC_BDRY


def maybe_has_contraction(text):
    return bool(CONTRACTIONS_REGEX_TEST.search(text))


def replace_contractions_sentence(text):
    for regexp, repl in CONTRACTIONS_REGEXES:
        # print repl
        matches = regexp.findall(text)
        if matches:
            if DEBUG:
                #   ----------------------------------------------------
                print '\t', regexp.pattern, '|', str(matches), '|', repl
                #   ----------------------------------------------------
            text = regexp.sub(repl, text)
    #   Contract spaces
    text = re.sub(' +', ' ', text)
    text = text.strip()
    return text


def replace_contractions_word(text):
    for regexp, repl in CONTRACTIONS_REGEXES_WORD:
        # print repl
        matches = regexp.findall(text)
        if matches:
            if DEBUG:
                #   ----------------------------------------------------
                print '\t', regexp.pattern, '|', str(matches), '|', repl
                #   ----------------------------------------------------
            text = regexp.sub(repl, text)
            #   Take first match, since were operating on a single word.
            break
    #   Contract spaces
    text = re.sub(' +', ' ', text)
    text = text.strip()
    return text


tests = [
    "o' the morning", "beat 'em",
    "could of", "should of", "might of", "must of", "would of",
    "coulda", "shoulda", "mighta", "musta", "woulda",
    "lotsa", "kinda", "sorta",
    "d'ye", "c'mon", "'tis", "'twas", "betcha", "gotcha",
    "gimme", "gonna", "gotta", "lemme",
    "wanna", "imma", "dunno",
    "ain't", "won't", "can't", "cant",
    "goin'", "fittin'", "waitin'",
    "I'll", "you'll", "she'll",
    "I'd", "you'd", "she'd",
    "it's", "life's",
    "you're", "they're", "we're",
    "I've", "you've", "they've",
    "mor'n",
]

expected = [
    "of the morning", "beat them",
    "could have", "should have", "might have", "must have", "would have",
    "could have", "should have", "might have", "must have", "would have",
    "lots of", "kind of", "sort of",
    "do you", "come on", "it is", "it was", "bet you", "got you",
    "give me", "going to", "got to", "let me",
    "want to", "i am going to", "do not know",
    "am n't", "will n't", "can n't", "can n't",
    "going", "fitting", "waiting",
    "I 'll", "you 'll", "she 'll",
    "I 'd", "you 'd", "she 'd",
    "it 's", "life 's",
    "you 're", "they 're", "we 're",
    "I 've", "you 've", "they 've",
    "more 'n",
]

tests2 = [
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

expected2 = [
    "of the morning aaaa beat them",
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


tests = zip(tests, expected)
tests2 = zip(tests2, expected2)

def test():
    print 'TESTS 1:'
    for t, e in tests:
        print 'SENTENCE-LEVEL:'
        print 'TEST match?', bool(CONTRACTIONS_REGEX_TEST.search(t))
        t_sub = replace_contractions_sentence(t)
        print 'test:', t
        print '\t', 'expected:', e
        print '\t', 'actual:', t_sub
        print '\t', 'passed:', t_sub == e
        print
        print 'WORD-LEVEL:'
        print '\tTEST match?', [
            bool(CONTRACTIONS_REGEX_TEST.search(w)) for w in t.split(' ')
        ]
        t_sub = [ replace_contractions_word(w) for w in t.split(' ') ]
        t_sub = ' '.join(t_sub)
        print 'test:', t
        print '\t', 'expected:', e
        print '\t', 'actual:', t_sub
        print '\t', 'passed:', t_sub == e
        print
        print
    print 'TESTS 2:'
    for t, e in tests2:
        print 'SENTENCE-LEVEL:'
        print '\tTEST match?', bool(CONTRACTIONS_REGEX_TEST.search(t))
        t_sub = replace_contractions_sentence(t)
        print 'test:', t
        print '\t', 'expected:', e
        print '\t', 'actual:', t_sub
        print '\t', 'passed:', t_sub == e
        print
        print 'WORD-LEVEL:'
        print '\tTEST match?', [
            bool(CONTRACTIONS_REGEX_TEST.search(w)) for w in t.split(' ')
        ]
        t_sub = [ replace_contractions_word(w) for w in t.split(' ') ]
        t_sub = ' '.join(t_sub)
        print 'test:', t
        print '\t', 'expected:', e
        print '\t', 'actual:', t_sub
        print '\t', 'passed:', t_sub == e
        print
        print

if __name__ == '__main__':
    test()

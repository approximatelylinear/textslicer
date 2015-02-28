

#   Stdlib
import logging
import itertools
import re
import string
import os
import operator
import copy
import random
from pprint import pformat
import pdb

#   3rd party
import nltk
from nltk.tokenize import RegexpTokenizer
try:
    import enchant
except ImportError:
    pass
import unicode_utils

#   Custom
from .constants import *
from .regex_patterns import WORD_PUNCT_PATTERN



def update_segments(segments, matcher, **kwargs):
    process_types = kwargs.get('process_types') or set([None])
    targets_ = []
    segments_ = []
    for segment in segments:
        #   Format:
        #       (start, end), token type, text
        # (s_seg, e_seg), _type, text = segment
        (s_seg, e_seg), _type, text = segment['pos'], segment['name'], segment['text']
        if _type not in process_types:
            segments_.append(segment)
            continue
        tokens_target = matcher(text)
        #   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        #   Precondition: Tokens should be in sorted order.
        tokens_target_srt = sorted(tokens_target, key=lambda d: d['pos'])
        try:
            assert tokens_target == tokens_target_srt
        except AssertionError:
            logging.error("Tokens are not sorted!")
            pdb.set_trace()
            tokens_target = tokens_target_srt
        #   !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        s_seg_curr = 0
        ###############
        # print segments
        # pdb.set_trace()
        ###############
        for token in tokens_target:
            #   Original position is relative to the current segment.
            s_tok, e_tok = token['pos']
            #   Update the position so that it's relative to the original text.
            s_tok_orig, e_tok_orig = s_tok + s_seg, e_tok + s_seg
            token['pos'] = s_tok_orig, e_tok_orig
            #   Further split the current segment according to the tokens.
            segments_curr = [
                dict(
                    pos=(s_seg + s_seg_curr, s_tok_orig),
                    name=_type,
                    text=text[s_seg_curr : s_tok]
                ),
                dict(
                    pos=(s_tok_orig, e_tok_orig),
                    name=token['name'],
                    text=token['text'],
                ),
            ]
            #########
            # print segments_curr
            #########
            segments_curr = [
                seg for seg in segments_curr
                    #   Text is non-empty or it's a utility token
                    #   (e.g. indicates boundaries.)
                    if seg['text'] or (seg['name'] and seg['name'].startswith('!'))
            ]
            segments_.extend(segments_curr)
            s_seg_curr = e_tok
        if s_seg_curr < len(text):
            segments_.append(
                dict(
                    pos=(s_seg + s_seg_curr, s_seg + len(text)),
                    name=_type,
                    text=text[s_seg_curr:]
                )
            )
        targets_.extend(tokens_target)
        ###############
        # print pformat(segments_)
        # print pformat(targets_)
        # pdb.set_trace()
        # print
        ###############
    return segments_, targets_


from bisect import bisect_left
def update_gaps(result, gaps):
    """
    >>> update_gaps([('a', 1), ('b', 2), ('c', 10)], [2, 3, 6, 7, 8])
    [1, 4, 12]
    >>> update_gaps([('a', 1), ('b', 2), ('c', 10)], [])
    [1, 2, 10]
    >>> update_gaps([('a', 1), ('b', 2), ('c', 3)], [4, 5, 6])
    [1, 2, 3]
    """
    offsets_new = []
    result = sorted(result, key=lambda x: x[0])
    offset = 0
    for idx, c in result:
        idx += offset
        idx_ins = bisect_left(gaps, idx)
        idx_stop = 0
        while (idx_ins < len(gaps)) and (idx == gaps[idx_ins]):
            if idx_stop > len(gaps):
                break
            idx_stop += 1
            idx += 1
            offset += 1
            idx_ins = bisect_left(gaps,idx)
        offsets_new.append((idx, c))
    return offsets_new


##  ==========================PIPELINES==============================


class TokenizeToWords(object):
    def __init__(
            self,
            tokenizer=None,
            sent_tokenizer=None,
            word_tokenizer=None,
            *args,
            **kwargs
        ):
        super(TokenizeToWords, self).__init__()
        if tokenizer is None: tokenizer = TextTokenizer(
            sent_tokenizer=sent_tokenizer,
            word_tokenizer=word_tokenizer
        )
        self.tokenizer = tokenizer

    def process_item(self, text, **kwargs):
        tokens = self.tokenizer.tokenize_to_words(text)
        ############
        # print tokens
        # pdb.set_trace()
        ############
        return tokens

    def __call__(self, text, **kwargs):
        return self.process_item(text, **kwargs)



class TokenizeToSents(object):
    def __init__(
            self,
            tokenizer=None,
            sent_tokenizer=None,
            word_tokenizer=None,
            *args,
            **kwargs
        ):
        super(TokenizeToSents, self).__init__()
        if tokenizer is None: tokenizer = TextTokenizer(
            sent_tokenizer=sent_tokenizer,
            word_tokenizer=word_tokenizer
        )
        self.tokenizer = tokenizer

    def process_item(self, text, **kwargs):
        tokens = self.tokenizer.tokenize_to_sentences(text)
        return tokens

    def __call__(self, text, **kwargs):
        return self.process_item(text, **kwargs)



class WordSegmenterobject(object):
    pass




class TextTokenizer(object):
    """
    A class that provides methods for tokenizing a piece of text.
    """
    def __init__(self, sent_tokenizer=None, word_tokenizer=None):
        if sent_tokenizer: self.sent_tokenizer = sent_tokenizer
        if word_tokenizer: self.word_tokenizer = word_tokenizer

    @property
    def sent_tokenizer(self):
        """
        Initializes self.__sent_tokenizer if one is not supplied to the __init__
        method with the NLTK-supplied 'tokenizers/punkt/english.pickle'.
        """
        try:
            self.__sent_tokenizer
        except AttributeError:
            self.__sent_tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
        return self.__sent_tokenizer

    @sent_tokenizer.setter
    def sent_tokenizer(self, value):
        self.__sent_tokenizer = value

    @property
    def word_tokenizer(self):
        """Initializes self._word tokenizer if one is not supplied to the
        :py:meth:`__init__` method. This default tokenizer adds patterns for
        detecting urls to the standard NLTK Word Punct tokenizer.
        """
        try:
            self.__word_tokenizer
        except AttributeError:
            #   Tokenize urls, products then everything else.
            self.__word_tokenizer = RegexpTokenizer(
                r'|'.join(
                    # [pat for name, pat in IGNORE_SPECIAL_CHAR_PATTERNS] +
                    [WORD_PUNCT_PATTERN]
                ),
                flags = REGEX_FLAGS
            )
        return self.__word_tokenizer

    @word_tokenizer.setter
    def word_tokenizer(self, value):
        self.__word_tokenizer = value

    def get_word_count(self, text):
        """Gets the word count for a text by tokenizing it and returning the length
        of the resulting sequence.

        *Note*: This is an expensive operation that should not be called if we
        already have a tokenized version of the text.
        """
        text = unicode_utils.to_unicode(text)
        words = self.tokenize_to_words(text)
        return len(list(words))

    def tokenize_to_words(self, text):
        """Get a sequence of lowercase strings corresponding to the words in a
        text. Sentence-boundaries are only implicitly preserved (e.g.
        through punctuation).
        """
        text = unicode_utils.to_unicode(text)
        words = self.word_tokenizer.tokenize(text)
        return words

    def tokenize_to_sentences(self, text):
        """Returns a sequence containing each sentence in a text. Each sentence is
        converted to lowercase stripped of whitespace at the beginning and end.
        """
        text = unicode_utils.to_unicode(text)
        word_tokenized_sents = self.tokenize_text(text)
        lowercase_sents = (
            ( word.lower().strip() for word in words )
                for words in word_tokenized_sents
        )
        return lowercase_sents

    def tokenize_text(self, text):
        """Returns a sequence of sequences containing each sentence in a text,
        and then each word.
        """
        text = unicode_utils.to_unicode(text)
        sents = self.sent_tokenizer.tokenize(text)
        word_tokenized_sents = (
            self.word_tokenizer.tokenize(sent) for sent in sents
        )
        return word_tokenized_sents

#:  Default text tokenizer, globally available to all methods
TEXT_TOKENIZER = TextTokenizer()



##  ==========================WORD SEGMENTATION ================================
class WordSegmenter(object):

    @staticmethod
    def test(check_spelling=False):
        text = """
        Return a random floating point number N such that low <= N <= high and with the
        specified mode between those bounds. The low and high bounds default to zero and
        one. The mode argument defaults to the midpoint between the bounds, giving a
        symmetric distribution.
        """
        text = textwrap.dedent(text)
        text_fragments = [text[:e] for e in xrange(0, len(text), 50)]
        text_fragments = [''.join(t.split()) for t in text_fragments]
        best_segmentations = [(t, WordSegmenter.segment_text(
                                t,
                                check_spelling=check_spelling))
                                    for t in text_fragments]
        for t, s in best_segmentations:
            print t, '\t==>\t', s, '\n'

    @staticmethod
    def segment_text_with_annealing(text, break_prob=.25, iterations=5, check_spelling=False):
        if check_spelling:
            spell_checker = WordSegmenter.get_spell_checker()
        else:
            spell_checker = None
        total_segs = [''.join('1' if random.random() < break_prob else '0'
            for c in text) for idx in xrange(iterations)]
        trials = [  WordSegmenter.segment_with_annealing(
                        text,
                        curr_segs,
                        spell_checker=spell_checker
                    )
                    for curr_segs in total_segs ]
        sorted_trials = sorted(trials, key=operator.itemgetter(1), reverse=True)
        best_segmentations = [WordSegmenter.segment(text, segs) for segs, score
            in sorted_trials[:10]]
        best = best_segmentations[0]
        #########
        print best
        #########
        return best

    @staticmethod
    def segment_text(text, **kwargs):
        segmentation = WordSegmenter.segment(text)
        return segmentation

    @staticmethod
    def segment(text, **kwargs):
        spell_checker = WordSegmenter.get_spell_checker()
        start = 0
        words = []
#         prev_word = False
#         count = 0
        while text:
#             count += 1
            text = text[start:]
            for stop in reversed(xrange(len(text) + 1)):
                word = text[:stop]
                if stop == 0:
                    words.append(word)
                    text = ''
                    break
                elif word and spell_checker.check(word):
                    words.append(word)
                    if stop == len(text):
                        text = ''
                    else:
                        text = text[stop:]
                    break
        return words

    @staticmethod
    def segment_with_annealing( text,
                                segs,
                                iterations=500,
                                cooling_rate=1.2,
                                spell_checker=None ):
        """
        Uses simulated annealing to converge on the segmentation that best
        matches the objective function given in `WordSegmenter.evaluate`.
        The lower the score, the better.
        """
        temperature = float(len(segs))
        best = None
        while temperature > 0.5:
            #   Score the current segmentation
            best_segs, best = segs, WordSegmenter.evaluate( text,
                                                            segs,
                                                            spell_checker )
            for i in xrange(iterations):
                #   Randomly perturb the segmentation
                guess = WordSegmenter.flip_n_bits(segs, int(round(temperature)))
                score = WordSegmenter.evaluate(text, guess, spell_checker)
                if score < best:
                    best, best_segs = score, guess
            score, segs = best, best_segs
            temperature = temperature / cooling_rate
        return (segs, best)

    @staticmethod
    def get_spell_checker():
        enchant_broker = enchant.Broker()
        enchant_broker.set_ordering('en_US', 'aspell,myspell')
        d = enchant_broker.request_dict("en_US")
        return d

    @staticmethod
    def evaluate(text, segs, spell_checker=None):
        segments = WordSegmenter._segment(text, segs)
        #   Penalize large numbers of segments
        text_size = len(segments)
        #   Unknown words
        if spell_checker:
            #   Enchant complains when it encounters an empty string.
            segments = ( s for s in segments if s )
            #   Ignore known words in determining the lexicon size.
            segments = [s for s in segments if not spell_checker.check(s)]
        #   Length of unique words + boundaries
        #   Penalize large numbers of distinct words
        lexicon_size = len(' '.join(list(set(segments))))
        return text_size + lexicon_size

    @staticmethod
    def _segment(text, segs):
        l = (   [0] +
                [idx + 1 for idx in xrange(len(segs)) if segs[idx] == '1'] +
                [len(segs) + 1] )
        start_end_pairs = [(l[idx], l[idx + 1]) for idx in xrange(len(l) - 1)]
        segments = [text[s:e] for s, e in start_end_pairs]
        return segments

    @staticmethod
    def flip_n_bits(segs, n):
        for i in xrange(n):
            segs = WordSegmenter.flip_bit(
                segs,
                random.randint(0, len(segs) - 1)
            )
        return segs

    @staticmethod
    def flip_bit(segs, pos):
        return segs[:pos] + str(1 - int(segs[pos])) + segs[pos + 1:]



class RegexReplacer(object):
    """
    A class for building a sequence of regular expressions and using them to
    successively replace patterns in a text.
    """
    def __init__(self, patterns=''):
        self.patterns = patterns

    @property
    def compiled_patterns(self):
        try:
            self.__compiled_patterns
        except AttributeError:
            joined_patterns = (
                self.join_regex_list(match_repl_pair)
                    for match_repl_pair in self.patterns
            )
            self.__compiled_patterns = (
                (re.compile(regex, REGEX_FLAGS), repl)
                    for regex, repl in joined_patterns
            )
        return self.__compiled_patterns

    def join_regex_list(self, match_repl_pair):
        """
        Combines each item in a sequence with '|' and then returns the result.

        :param match_repl_pair: The sequence of items to combine.
        """
        new_match_repl_pair = []
        for item in match_repl_pair:
            if isinstance(item, list): item = r'|'.join(item)
            new_match_repl_pair.append(item)
        return new_match_repl_pair

    def replace(self, text):
        """
        Replaces all matches for the patterns in :py:attr:`compiled_patterns`
        with their corresponding replacements in :py:attr:`compiled_patterns`.

        :param text: The text that will be scanned for replacements.
        """
        text = unicode_utils.to_unicode(text)
        for pattern, repl in self.compiled_patterns: text = re.sub(pattern, repl, text)
        return text



from collections import Counter


def get_single_occurrences(words):
    """
    Gets all words that occur only once within a sequence.
    """
    words_ctr = Counter(words)
    words = set( word for word in words if words_ctr[word] == 1 )
    return words


def remove_single_occurrences(words):
    """
    Removes all words that occur only once within a sequence.
    """
    words_ctr = Counter(words)
    words = ( word for word in words if words_ctr[word] > 1 )
    return words

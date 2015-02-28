
#   Stdlib
import re
import urlparse
import string
from pprint import pformat
import pdb

#   Custom
from .match_base import SCHEME_REGEX, URL_REGEX, URL_REGEX_2

##  ==========================URL PARSING======================================

def normalize_url(url, protocol='http'):
    """
    Normalizes a URL

    #. Removes whitespace and punctuation from the beginning and end.
    #. Adds a web protocol if one is absent.

    """
    if url.strip():
        ##  Strip off leading and training whitespace and punctuation
        legal_punc = '-._~/#?'
        illegal_punc = set(string.punctuation) - set(legal_punc)
        illegal_punc = ''.join(illegal_punc)
        illegal_chars = string.whitespace + illegal_punc
        #   Remove illegal characters from the beginning and end.
        url = url.strip(illegal_chars)
        #   Make sure urls start with a common scheme.
        if not SCHEME_REGEX.match(url):
            url = protocol + '://' + url
    return url

def test_normalize_url():
    urls = [
        ('http://www.google.com', 'http://www.google.com'),
        ('www.google.com/', 'http://www.google.com/'),
        (' www.google.com/!^ ', 'http://www.google.com/'),
        ('', ''),
    ]
    for url, expected in urls:
        res = normalize_url(url)
        print url, res
        assert res == expected
    print 'test_normalize_url passed!'


def split_url(url):
    """Extracts the path portion of a URL.

        :param string url: Url to parse

    >>> u1 = 'www.google.com'
    >>> u2 = 'www.google.com/blah'
    >>> u3 = 't.co.wev/aslkdfjads'
    >>> u4 = 'http://t.co.wev/aslkdfjads/'
    >>> for u in [u1, u2, u3, u4]:
            print split_url(u)
    """
    url = normalize_url(url)
    parse_result = urlparse.urlparse(url)
    domain, path = parse_result.netloc.strip('/'), parse_result.path.strip('/')
    return domain, path


def test_split():
    urls = [
        ('www.google.com', ('www.google.com', '')),
        ('www.google.com/blah', ('www.google.com', 'blah')),
        ('t.co.wev/aslkdfjads', ('t.co.wev', "aslkdfjads")),
        ('http://t.co.wev/aslkdfjads/', ('t.co.wev', 'aslkdfjads'))
    ]
    for url, expected in urls:
        assert split_url(url) == expected
    print 'test_split passed!'


def extract_urls(text):
    """Removes all URLs from the text in a post.

        :param dict text: The text to process

    """
    urls = URL_REGEX.findall(text)
    if urls:
        urls = [ url[0] for url in urls if url ]
        text_new = URL_REGEX.sub('', text)
    if not urls:
        urls = URL_REGEX_2.findall(text)
        text_new = URL_REGEX_2.sub('', text)
    urls_split = [ split_url(url) for url in urls ]
    text_new = text_new.strip()
    result = {
        'text' :    dict(orig=text, clean=text_new),
        'urls' :    dict(orig=urls, split=urls_split)
    }
    return result


def test_extract():
    urls = [
        ('aaaaaaaaaa www.google.com aaaaaaaaaa', dict(text=dict(orig='aaaaaaaaaa www.google.com aaaaaaaaaa', clean='aaaaaaaaaa  aaaaaaaaaa'), urls=dict(orig=['www.google.com'], split=[('www.google.com', '')]))),
        ('aaaaaaaaaa www.google.com/blah aaaaaaaaaa', dict(text=(dict(orig='aaaaaaaaaa www.google.com/blah aaaaaaaaaa', clean='aaaaaaaaaa  aaaaaaaaaa')), urls=dict(orig=['www.google.com/blah'], split=[('www.google.com', 'blah')]))),
        ('aaaaaaaaaa t.co.wev/aslkdfjads aaaaaaaaaa', dict(text=(dict(orig='aaaaaaaaaa t.co.wev/aslkdfjads aaaaaaaaaa', clean='aaaaaaaaaa  aaaaaaaaaa')), urls=dict(orig=['t.co.wev/aslkdfjads'], split=[('t.co.wev', "aslkdfjads")]))),
        ('aaaaaaaaaa http://t.co.wev/aslkdfjads/ aaaaaaaaaa', dict(text=(dict(orig='aaaaaaaaaa http://t.co.wev/aslkdfjads/ aaaaaaaaaa', clean='aaaaaaaaaa  aaaaaaaaaa')), urls=dict(orig=['http://t.co.wev/aslkdfjads/'], split=[('t.co.wev', 'aslkdfjads')]))),
    ]
    for url, expected in urls:
        res = extract_urls(url)
        print url
        print '\t RESULT:', pformat(res)
        print
        print '\t EXPECTED:', pformat(expected)
        assert res == expected
    print 'test_extract passed!'


def test():
    test_normalize_url()
    test_split()
    test_extract()

# TEXT_TOKENIZER = tokenize.TEXT_TOKENIZER
# def segment_urls(text):
#     """Splits a string containing multiple urls into segments."""
#     #   Create an intermediate tokenization
#     text_container = TEXT_TOKENIZER.tokenize_to_words(text)
#     text_container = itertools.chain.from_iterable(
#         segment_url(text) for text in text_container
#     )
#     return ' '.join(text_container)


# def segment_url(text):
#     """Splits a url into segments."""
#     #   Does it start with a scheme?
#     if SCHEME_REGEX.match(text):
#         url_segments = text.split('/')[2:]
#         url_segments = sum([s.split('.') for s in url_segments], [])
#         url_segments = ( s for s in url_segments if s and s != 'www' )
#         segments = sum(
#             [tokenize.WordSegmenter.segment_text(s) for s in url_segments],
#             []
#         )
#     else:
#         segments = [text]
#     return segments

if __name__ == '__main__':
    test()

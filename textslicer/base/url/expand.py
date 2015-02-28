
#   Stdlib
import re
import logging
import urllib
from urlparse import urlparse, urljoin
import random
import pdb
from pprint import pformat
from collections import deque, Counter

#   3rd party
import requests
from requests.exceptions import HTTPError
from lrucache import LRUCache

#   Custom
from .constants_url import THIS_DIR, DEBUG
from .domain_base import get_domain, SHORTENER_DOMAINS
from .clean_base import normalize_url


CACHE_FINAL = LRUCache()
CACHE_TEMP = LRUCache()


def expand(url, max_depth=5, force=False):
    domain = get_domain(url)
    # print domain
    if force or (len(domain) < 7) or (domain in SHORTENER_DOMAINS):
        print url
        res = _expand(url, max_depth)
    else:
        res = [url]
    return res


def _expand(url, max_depth=5, cache_final=CACHE_FINAL, cache_temp=CACHE_TEMP):
    if cache_final is not None and random.randint(0, 1000) == 0:
        logging.info(
            'Ratio id hits/misses: {0:.3f}'.format(
                cache_final.get_ratio()
            )
        )
    url_orig = url
    path = [url]
    idx = 0
    ############
    # print url
    # pdb.set_trace()
    #############
    while idx < max_depth:
        idx += 1
        cached = cache_final.get(url) if cache_final is not None else None
        if cached:
            #   Final result.
            path.append(cached)
            break
        else:
            cached = cache_temp.get(url) if cache_temp is not None else None
            if cached:
                #   Intermediate result.
                if cached == url:
                    #   No further expansions.
                    break
                else:
                    path.append(cached)
                    continue
            result = resolve(url)
            if result:
                #   Expansion differs from previous url
                #   Format:
                #       {
                #           'url': dict(orig=url, source=url_source),
                #       }
                if 'url' in result:
                    expanded = result['url']['source']
                    result['url'] = expanded
                    path.append(result)
                    if cache_temp is not None:
                        cache_temp[url] = expanded
                    url = expanded
                elif 'status' in result:
                    #   Replace last segment of path.
                    result['url'] = url
                    path[-1] = result
                    #   Error, or exansion the same as previous url
                    if cache_temp is not None:
                        cache_temp[url] = url
                    if cache_final is not None:
                        cache_final[url_orig] = url
                    break
            else:
                #   Error, or exansion the same as previous url
                if cache_temp is not None:
                    cache_temp[url] = url
                if cache_final is not None:
                    cache_final[url_orig] = url
                break
    ###################
    print url_orig, pformat(path), '\n'
    pdb.set_trace()
    ###################
    return path


def resolve(url):
    result = None
    try:
        #   Request the url, but give up after 1 seconds.
        # logging.info('Requesting {0}...'.format(url))
        response = requests.head(url, allow_redirects=False, timeout=1)
        response.raise_for_status()
    except HTTPError as e_http:
        response = {
            'status': response.status_code
        }
    except Exception as e_oth:
        logging.warning('\t...Timed out.')
        result = {
            'status': 'timeout'
        }
    else:
        if 'location' in response.headers:
            url_next = response.headers['location']
            # (Pinched from requests)
            # Handle redirection without scheme (see: RFC 1808 Section 4)
            if url_next.startswith('//'):
                parsed_rurl = urlparse(response.url)
                url_next = '{0}:{1}'.format(parsed_rurl.scheme, url_next)
            # Facilitate non-RFC2616-compliant 'location' headers
            # (e.g. '/path/to/resource' instead of 'http://domain.tld/path/to/resource')
            if not urlparse(url_next).netloc:
                url_next = urljoin(response.url, url_next)
            if url_next != url:
                result = {
                    'url'   : dict(orig=url, source=url_next),
                }
        else:
            result = {
                'status'    : 'final',
            }
    #############
    # print pformat(result)
    # pdb.set_trace()
    #############
    return result


def resolve_short_url(url, force=False, depth=1):
    """
    Given a short URL, returns its real URL. By default, it will only resolve a
    whitelist of known URL shorteners, but this can be overridden with the `force`
    argument.

    Source: https://gist.github.com/bfirsh/2003517
    """
    domain = urlparse(url).netloc
    # If the domain is long and not a known url shortener, don't bother resolving
    if not force and len(domain) >= 7 and domain not in SHORTENER_DOMAINS:
        return url
    count = 0
    while count < depth:
        count += 1
        try:
            #   Request the url, but give up after 1 seconds.
            # logging.info('Requesting {0}...'.format(url))
            response = requests.head(url, allow_redirects=False, timeout=1)
        except Exception as e:
            logging.warning('\t...Timed out.')
            break
        if 'location' not in response.headers:
            break
        url = response.headers['location']
        # (Pinched from requests)
        # Handle redirection without scheme (see: RFC 1808 Section 4)
        if url.startswith('//'):
            parsed_rurl = urlparse(response.url)
            url = '{0}:{1}'.format(parsed_rurl.scheme, url)
        # Facilitate non-RFC2616-compliant 'location' headers
        # (e.g. '/path/to/resource' instead of 'http://domain.tld/path/to/resource')
        if not urlparse(url).netloc:
            url = urljoin(response.url, url)
    return url



class ExpandBitly(object):
    def __init__(self):
        self.urls = []
        self.rate = 30

    @staticmethod
    def expand(urls):
        url_base = "https://api-ssl.bitly.com"
        url_srv = "/v3/expand"
        params = [
            (access_token, "c2d17b3d66492ffb8ce164aba43cb92888bee396"),
        ]
        if not hasattr(urls, '__iter__'): urls = [urls]
        shorturls = [('shortUrl', url) for url in urls]
        params = params + shorturls
        params_str = urllib.urlencode(params)
        url = url_base + url_srv + '?' + params_str
        resp = requests.get(url)
        return resp

    def finalize(self):
        return self.expand(self.urls)

    def __call__(self, url, **kwargs):
        self.urls.append(url)
        if len(self.urls) >= 30:
            resp = self.expand(self.urls)
            self.urls = []
        else:
            resp = None
        return resp


bitly_expander = ExpandBitly()

def expand_short_url(url):
    #########
    # print url
    # pdb.set_trace()
    #########
    domain_orig = get_domain(url)
    if domain_orig == 'bit.ly':
        result = ExpandBitly(url)
    elif domain_orig in SHORTENER_DOMAINS:
        #   TBD:    Utilize apis when available (e.g. goo.gl, bit.ly, etc.)
        url_source, domain_source = request_url(url)
    else:
        url_source, domain_source = None, None
    result = {
        'url'       : dict(orig=url, source=url_source),
        'domain'    : dict(orig=domain_orig, source=domain_source)
    }
    return result



def expand_googl():
    pass




#   DEPRECATED
def request_url(url):
    try:
        #   Request the url, but give up after 1 seconds.
        logging.info('Requesting {0}...'.format(url))
        # response = requests.get(url, timeout=1)
        response = requests.head(url, timeout=1)
    except Exception as e:
        logging.warning('\t...Timed out.')
        url_source = None
        domain_source = None
        ###################
        logging.info(response.history)
        pdb.set_trace()
        ###################
    else:
        url_source = normalize_url(response.url)
        domain_source = get_domain(url_source)
    return url_source, domain_source



def test():
    urls = [
        "https://t.co/of5Aess8cc",
        "http://t.co/vUHxnDuF7A",
        "http://t.co/b7NwjjQ2r3"
    ]
    for url in urls:
        r = expand_short_url(url)
        print pformat(r)


if __name__ == '__main__':
    test()

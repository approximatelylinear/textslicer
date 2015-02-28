
import os
import random
import logging
import time
try:
    import cPickle as pickle
except ImportError:
    import pickle
from collections import deque, Counter
from pprint import pformat
import pdb

from .abc import Tokenizer
from .constants_tasks import THIS_DIR
from ..base.tokenize import update_segments
from ..base.url import match, domain, expand



class GetUrls(Tokenizer):
    tokenizer_key = ''
    tokenizer_name = 'url'

    def __init__(self, *args, **params):
        super(GetUrls, self).__init__(*args, **params)

    def add_embedded_info(self, doc, segments_, **params):
        embedded_by_orig = dict(
            (url_info['original'], url_info)
                for url_info in doc['urls']['embedded']
        )
        for segment in segments_:
            if segment['name'] == self.tokenizer_name:
                url_info = embedded_by_orig.get(segment['text'])
                if url_info:
                    expanded = url_info.get('expanded')
                    if expanded:
                        segment['norm'] = expanded
                    subdomain = url_info.get('subdomain')
                    if subdomain:
                        segment['subdomain'] = subdomain
        #   Re-sort the segments.
        # segments_ = sorted(segments_, key=lambda d: d['pos'])
        return segments_

    def process(self, doc, **params):
        #   !!!!!!!!!!!!!!!!!!!!!!!!
        assert 'text' in doc
        #   !!!!!!!!!!!!!!!!!!!!!!!!
        field_in = params.get('field_in')  or 'current'
        field_out = params.get('field_out')  or 'current'
        tokens = doc['text'].setdefault('tokens', {})
        segments = doc['text'][field_in]
        segments_, targets_ = update_segments(segments, match_base.match_url)
        if (doc.get('urls') or {}).get('embedded'):
            segments_ = self.add_embedded_info(doc, segments_, **params)
        doc['text'][field_out] = segments_
        return doc




def test_get_urls():
    get_urls = GetUrls()
    docs = [
        (
            {   'text' : {
                    'original': 'aaaaaaaaaa www.google.com aaaaaaaaaa',
                    'current': [
                        dict(
                            pos=(0, 36),
                            name=None,
                            text='aaaaaaaaaa www.google.com aaaaaaaaaa'
                        )
                    ],
                }
            },
            {   'text' : {
                    'original': 'aaaaaaaaaa www.google.com aaaaaaaaaa',
                    'current': [
                        dict(pos=(0, 11), name=None, text='aaaaaaaaaa '),
                        dict(pos=(11, 25), name='url', text='www.google.com'),
                        dict(pos=(25, 36), name=None, text=' aaaaaaaaaa'),
                    ],
                    'tokens' : {}
                }
            }
        ),
        (
            {   'text' : {
                    'original': u'RT @Thegooglefactz: The iPhone is the second best selling product of all time, the 1st is the Rubik\u2019s Cube.',
                    'current': [
                        dict(
                            pos=(0, 107),
                            name=None,
                            text=u'RT @Thegooglefactz: The iPhone is the second best selling product of all time, the 1st is the Rubik\u2019s Cube.'
                        )
                    ],
                }
            },
            {   'text' : {
                    'original': 'aaaaaaaaaa www.google.com aaaaaaaaaa',
                    'current': [
                        dict(pos=(0, 11), name=None, text='aaaaaaaaaa '),
                        dict(pos=(11, 25), name='url', text='www.google.com'),
                        dict(pos=(25, 36), name=None, text=' aaaaaaaaaa'),
                    ],
                    'tokens' : {}
                }
            }
        ),
    ]
    failures = 0
    for doc, expected in docs:
        print 'ORIG:', doc
        res = get_urls(doc)
        print 'EXPECTED:', pformat(expected)
        print 'RESULT:', pformat(res)
        try:
            assert res == expected
        except Exception as e:
            failures += 1
            print "Failed!"
        print
    if not failures:
        print 'test_get_urls passed!'




class RemoveURLs(object):
    def __init__(self, *args, **kwargs):
        pass

    def process_item(self, text, **kwargs):
        text = remove_urls(text, **kwargs)
        return text

    def __call__(self, doc, **kwargs):
        text = doc['text']['original']
        doc['text']['no_url'] = self.process_item(text, **kwargs)
        return doc

#   TBD
remove_urls = lambda x: x


class ExpandShortUrls(object):
    # fname_cache = 'short_urls_cache.pkl'
    # path_cache = os.path.join(THIS_DIR, '..', 'data', fname_cache)

    def __init__(self, *args, **kwargs):
        super(ExpandShortUrls, self).__init__()
        # #   TBD:    Change cache to LRU
        # if os.path.exists(self.path_cache):
        #     with open(self.path_cache, 'rb') as f:
        #         self.cache = pickle.load(f)
        # else:
        #     self.cache = {}

    def expand(self, url, max_depth=5):
        path = expand_base.expand(url, max_depth)
        return path

    def __call__(self, doc, **kwargs):
        #   NB: The multiple fieldnames are there to handle naming
        #   inconsistencies among versions.
        # pdb.set_trace()
        urls = doc['urls'].get('embedded') or []
        if isinstance(urls, dict):
            # urls = urls.values()[0]x if urls.values() else []
            urls = urls.values()
        # urls = (
        #         (doc['urls'].get('embedded') or [])
        #     +   (doc['urls'].get('embedded_url') or [])
        # )
        urls_ = []
        while urls:
            status = None
            url_info = urls.pop()
            if isinstance(url_info, dict):
                expanded = url_info.get('expanded') or ''
                original = url_info.get('original') or ''
                if url_info.get('status'):
                    urls_.append(url_info)
                    continue
            else:
                #   Hack to fix normalization issue...
                original, expanded = url_info[0], url_info[1]
                url_info = {}
            #   Check every url
            to_expand = expanded or original
            path = self.expand(to_expand, max_depth=5)
            #   `expanded` and `original` will be the same if no expansion is required.
            url_last = path[-1]
            #   Record the status
            status = url_last.get('status') or 200
            expanded = url_last.get('url') or ''
            url_info['status'] = status
            ###############
            # if expanded != original:
            #     print 'Expanded:', expanded
            ###############
            url_info['original'], url_info['expanded'] = original, expanded
            urls_.append(url_info)
        doc['urls']['embedded'] = urls_
        ####################
        # if urls_:
        #     print pformat(urls_)
        #     # time.sleep(.5)
        #     pdb.set_trace()
        ####################
        return doc



def test_expand_short_urls():
    expand_short_urls = ExpandShortUrls()
    docs = [
        (
            {   'urls' : {
                    'embedded': [
                        dict(expanded="", original="https://t.co/of5Aess8cc"),
                    ]
                }
            },
            {   'urls' : {
                    'embedded': [
                        dict(expanded=u'https://www.youtube.com/watch?v=WIbnT0M3EOs', original="https://t.co/of5Aess8cc",
                            status="final",
                        ),
                    ]
                }
            },
        ),
        (
            {   'urls' : {
                    'embedded': [
                        dict(expanded="", original="https://t.co/vUHxnDuF7A"),
                    ]
                }
            },
            {   'urls' : {
                    'embedded': [
                        dict(expanded=u'http://whatstrending.com/funny/10182-josh-homme-and-nick-swardson-are-disappointing-g', original="https://t.co/vUHxnDuF7A", status="final",),
                    ]
                }
            },
        ),
        (
            {   'urls' : {
                    'embedded': [
                        dict(expanded="", original="https://t.co/b7NwjjQ2r3"),
                    ]
                }
            },
            {   'urls' : {
                    'embedded': [
                        dict(expanded=u'http://whatstrending.com/funny/10140-kids-have-never-seen-a-cassette-player-before', original="https://t.co/b7NwjjQ2r3", status="final",),
                    ]
                }
            },
        ),
    ]
    for doc, expected in docs:
        print 'ORIG:', doc
        res = expand_short_urls(doc)
        print 'EXPECTED:', expected
        print 'RESULT:', res
        assert res == expected
        print
    print 'test_expand_urls passed!'



class GetDomains(Tokenizer):
    def __init__(self, *args, **kwargs):
        super(GetDomains, self).__init__(*args, **kwargs)

    @staticmethod
    def get_tld(s):
        domain_str = domain_base.get_domain(s)
        d = domain_base.parse_domain(domain_str)
        return d

    @staticmethod
    def get_domain_type(domain_info):
        #   Is it a blog domain?
        domain_info = domain_base.parse_domain_blog(domain_info)
        #   =====================
        # print pformat(domain_info)
        #   =====================
        if domain_info['match_domain_blog']['tld']:
            domain_type = 'blog'
        else:
            #   Is it a photo domain?
            domain_info = domain_base.parse_domain_photo(domain_info)
            if domain_info['match_domain_photo']['tld']:
                domain_type = 'photo'
            else:
                domain_type = 'unknown'
        return domain_type

    def get_domains(self, urls, **params):
        while urls:
            url_info = urls.pop()
            if isinstance(url_info, dict):
                #   Already processed?
                if url_info.get('subdomain'):
                    yield url_info
                    continue
                url = (
                        url_info.get('expanded')
                    or  url_info.get('expanded_url')
                    or  ""
                )
            else:
                #   Hack to fix normalization issue...
                url = url_info[1] or url_info[0] or  ""
                url_info = {}
            domain_info = self.get_tld(url)
            domain_type = self.get_domain_type(domain_info)
            tld_info = domain_info['tld']
            if tld_info:
                url_info['root_domain'], _ = tld_info
            else:
                url_info['root_domain'] = None
            subdomain_info = domain_info['subdomain']
            if subdomain_info:
                url_info['subdomain'], _ = subdomain_info
            else:
                url_info['subdomain'] = None
            url_info['domain_type'] = domain_type
            yield url_info

    def process(self, doc, **params):
        urls = doc['urls'].get('embedded') or []
        if isinstance(urls, dict):
            urls = urls.values()[0] if urls.values() else []
        urls_ = list(self.get_domains(urls, **params))
        doc['urls']['embedded'] = urls_
        return doc




class GetDomains_OLD(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, doc, **kwargs):
        urls = doc['urls'].get('embedded') or []
        if isinstance(urls, dict):
            urls = urls.values()[0] if urls.values() else []
        # urls = (
        #         (doc['urls'].get('embedded') or [])
        #     +   (doc['urls'].get('embedded_url') or [])
        # )
        urls_ = []
        while urls:
            url_info = urls.pop()
            if isinstance(url_info, dict):
                #   Already processed?
                if url_info.get('subdomain'):
                    urls_.append(url_info)
                    continue
                url = (
                        url_info.get('expanded')
                    or  url_info.get('expanded_url')
                    or  ""
                )
            else:
                #   Hack to fix normalization issue...
                url = url_info[1] or url_info[0] or  ""
                url_info = {}
            domain_info = self.get_tld(url)
            domain_type = self.get_domain_type(domain_info)
            tld_info = domain_info['tld']
            if tld_info:
                url_info['root_domain'], _ = tld_info
            else:
                url_info['root_domain'] = None
            subdomain_info = domain_info['subdomain']
            if subdomain_info:
                url_info['subdomain'], _ = subdomain_info
            else:
                url_info['subdomain'] = None
            url_info['domain_type'] = domain_type
            urls_.append(url_info)
        doc['urls']['embedded'] = urls_
        return doc

    @staticmethod
    def get_tld(s):
        domain_str = domain_base.get_domain(s)
        d = domain_base.parse_domain(domain_str)
        return d

    @staticmethod
    def get_domain_type(domain_info):
        #   Is it a blog domain?
        domain_info = domain_base.parse_domain_blog(domain_info)
        #   =====================
        # print pformat(domain_info)
        #   =====================
        if domain_info['match_domain_blog']['tld']:
            domain_type = 'blog'
        else:
            #   Is it a photo domain?
            domain_info = domain_base.parse_domain_photo(domain_info)
            if domain_info['match_domain_photo']['tld']:
                domain_type = 'photo'
            else:
                domain_type = 'unknown'
        return domain_type


def test_get_domains():
    get_domains = GetDomains()
    data = [
        ('http://a.b.c.d.e.f.g.co', {'root_domain': 'co', 'subdomain': 'a.b.c.d.e.f.g', 'domain_type': 'unknown'}),
        ('https://t.info.ru/abcd', {'subdomain': 't', 'root_domain': 'info.ru', 'domain_type': 'unknown'}),
        ('http://blah.wordpress.com', {'domain_type': 'blog', 'root_domain': 'com', 'subdomain': 'blah.wordpress'}),
        ('http://blah.adweek.blogs.com/abcd', {'domain_type': 'blog', 'root_domain': 'com', 'subdomain': 'blah.adweek.blogs'}),
        ('http://blah.imgur.com/abcd', {'domain_type': 'photo', 'root_domain': 'com', 'subdomain': 'blah.imgur'}),
        ('https://blah.meh.smugmug.com/abcd', {'domain_type': 'photo', 'root_domain': 'com', 'subdomain': 'blah.meh.smugmug'})
    ]
    docs = [
        (
            dict(urls=dict(embedded=[dict(expanded=url, original="")])),
            dict(
                urls=dict(
                    embedded=[
                        dict(
                            expanded=url,
                            original="",
                            root_domain=expected['root_domain'],
                            subdomain=expected['subdomain'],
                            domain_type=expected['domain_type'],
                        )
                    ]
                )
            )
        )
            for url, expected in data
    ]
    for doc, expected in docs:
        print 'ORIG:', doc
        res = get_domains(doc)
        print 'EXPECTED:', expected
        print 'RESULT:', res
        assert res == expected
        print
    print 'test_get_domains passed!'



class GetUrlTypes(Tokenizer):
    def __init__(self, *args, **kwargs):
        super(GetUrlTypes, self).__init__(*args, **kwargs)

    def get_types(self, urls, **params):
        while urls:
            url_info = urls.pop()
            #   TBD:    Check media urls.
            if isinstance(url_info, dict):
                url = (
                        url_info.get('expanded')
                    or  url_info.get('expanded_url')
                    or  ""
                )
            else:
                #   Hack to fix normalization issue...
                url = url_info[1] or url_info[0] or  ""
                url_info = {}
            url_info['url_type'] = get_url_type(url)
            yield url_info

    def process(self, doc, **params):
        urls = (
                (doc['urls'].get('embedded') or [])
            +   (doc['urls'].get('embedded_url') or [])
        )
        urls_ = list(self.get_types(urls, **params))
        doc['urls']['embedded'] = urls_
        return doc




class GetUrlTypes_OLD(object):
    def __init__(self, *args, **kwargs):
        pass

    def __call__(self, doc, **kwargs):
        urls = (
                (doc['urls'].get('embedded') or [])
            +   (doc['urls'].get('embedded_url') or [])
        )
        urls_ = []
        while urls:
            url_info = urls.pop()
            #   TBD:    Check media urls.
            if isinstance(url_info, dict):
                url = (
                        url_info.get('expanded')
                    or  url_info.get('expanded_url')
                    or  ""
                )
            else:
                #   Hack to fix normalization issue...
                url = url_info[1] or url_info[0] or  ""
                url_info = {}
            url_info['url_type'] = get_url_type(url)
            urls_.append(url_info)
        doc['urls']['embedded'] = urls_
        return doc

get_url_type = lambda x: ''



def test():
    test_get_urls()
    test_expand_short_urls()
    test_get_domains()


if __name__ == '__main__':
    test()

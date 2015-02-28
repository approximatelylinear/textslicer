
import os
import re
import urlparse
import pdb
import traceback

from termcolor import colored

from .constants_url import THIS_DIR, DEBUG
from ..regex_ import match_all, REGEX_FLAGS
from .clean import normalize_url



def make_domain_regex(domains):
    _domain_pattern = r'|'.join(
        # '(?:\.{0})'.format(d) for d in domains
        '{0}'.format(d) for d in domains
    )
    domain_pattern = r"(?:(?P<subdomain>.+)\.)*(?P<tld>{0})$".format(_domain_pattern)
    domain_regex = re.compile(domain_pattern, REGEX_FLAGS)
    return domain_regex


#:  Second-level domains
with open(os.path.join(THIS_DIR, 'data', 'domains_second_level.txt'), 'rbU') as f:
    SECOND_LEVEL_DOMAINS = set([i.strip().strip('\n') for i in f])
ROOT_DOMAIN_REGEX = make_domain_regex(SECOND_LEVEL_DOMAINS)

#:  Photo sharing sites
with open(os.path.join(THIS_DIR, 'data', 'domains_photo.txt'), 'rbU') as f:
    PHOTO_DOMAINS = set([i.strip().strip('\n') for i in f])
PHOTO_DOMAIN_REGEX = make_domain_regex(PHOTO_DOMAINS)

#:  Video sharing sites
with open(os.path.join(THIS_DIR, 'data', 'domains_video.txt'), 'rbU') as f:
    VIDEO_DOMAINS = set([i.strip().strip('\n') for i in f])
VIDEO_DOMAIN_REGEX = make_domain_regex(VIDEO_DOMAINS)

#:  Blogs
with open(os.path.join(THIS_DIR, 'data', 'domains_blog.txt'), 'rbU') as f:
    BLOG_DOMAINS = set([i.strip().strip('\n') for i in f])
BLOG_DOMAIN_REGEX = make_domain_regex(BLOG_DOMAINS)

#:  Url shorteners
with open(os.path.join(THIS_DIR, 'data', 'domains_shorten.txt'), 'rbU') as f:
    SHORTENER_DOMAINS = set([i.strip().strip('\n') for i in f])
SHORTENER_DOMAIN_REGEX = make_domain_regex(SHORTENER_DOMAINS)


def match_domain(s, regex_):
    res = {}
    m = regex_.match(s)
    if m:
        g_domain = m.group('subdomain')
        idxs_domain = m.span('subdomain')
        g_tld = m.group('tld')
        idxs_tld = m.span('tld')
    else:
        g_domain, idxs_domain = None, None
        g_tld, idxs_tld = None, None
    res['subdomain'] = (g_domain, idxs_domain)
    res['tld'] = (g_tld, idxs_tld)
    return res


def sub_domain_tld(s): return ROOT_DOMAIN_REGEX.sub(r'\g<1>|\g<2>', s)
def match_domain_tld(s):
    return match_domain(s, ROOT_DOMAIN_REGEX)


def sub_domain_blog(s):
    return BLOG_DOMAIN_REGEX.sub(r'\g<1>|\g<2>', s)
def match_domain_blog(s):
    return match_domain(s, BLOG_DOMAIN_REGEX)


def sub_domain_photo(s): return PHOTO_DOMAIN_REGEX.sub(r'\g<1>|\g<2>', s)
def match_domain_photo(s):
    return match_domain(s, PHOTO_DOMAIN_REGEX)


def sub_domain_shortener(s): return SHORTENER_DOMAIN_REGEX.sub(r'\g<1>|\g<2>', s)
def match_domain_shortener(s):
    return match_domain(s, SHORTENER_DOMAIN_REGEX)


def get_domain(text):
    text = normalize_url(text)
    domain = urlparse.urlparse(text).netloc
    return domain


def test_get_domain():
    data = [
        ('http://a.b.c.d.e.f.g.co/Lho5BFR7Sx', 'a.b.c.d.e.f.g.co'),
        ('http://t.u.f.y.co/yTEdfTaqWm', 't.u.f.y.co'),
        ('http://t.info.ru/yTEdfTaqWm', 't.info.ru'),
        ('http://t.co.uk/mjMMV2d7Q', 't.co.uk'),
    ]
    for text, expected in data:
        res = get_domain(text)
        print text
        print '\t', res
        assert res == expected
    print 'test_get_domain passed!'



def get_tld(text):
    """Gets the root domain of a url."""
    #   Patch up the url as necessary
    domain = get_domain(text)
    parse_dict = parse_domain(domain)
    root_domain = parse_dict['tld']
    return root_domain


def parse_domain(domain, idxs_domain=None, func=None, max_depth=20):

    # pdb.set_trace()

    if idxs_domain is None:
        idxs_domain = (0, len(domain) - 1)
    if func is None:
        func = match_domain_tld
    root = None
    tlds = []
    if '.' not in domain:
        domain = '.' + domain
    domain_curr, idxs_domain_curr = domain, idxs_domain
    idx = 0
    while True:
        #   Cases:
        #       +subdomain, +tld    Recurse into subdomain
        #       -subdomain, +tld    Stop, output current (empty) subdomain and current (populated) tld
        #       -subdomain, -tld    Stop, output previous (populated) subdomain and current (empty) tld
        #   Note:
        #       +subdomain, -tld    shouldn't happen
        if idx > max_depth:
            break
        idx += 1
        res = func(domain_curr)
        domain_next, idxs_domain_next = res['subdomain']
        tld, idxs_tld = res['tld']
        ##########
        if DEBUG:
            print ' ' * idx, idx
            print ' ' * (idx + 1), 'res:', res
            print ' ' * (idx + 1), 'domain_curr:', domain_curr
            print ' ' * (idx + 1), 'domain_next:', domain_next
            print ' ' * (idx + 1), 'tld:', tld
            print ' ' * (idx + 1), 'tlds so far:', tlds
            print
        ###########
        if tld:
            tld = tld.strip().strip('.')
            tlds.append((tld, idxs_tld))
            domain_curr, idxs_domain_curr = domain_next, idxs_domain_next
            if not domain_curr:
                #   Case:   -subdomain, +tld    Stop, output current (empty) subdomain and current (populated) tld
                subdomain, idxs_subdomain = domain_curr, idxs_domain_curr
                break
            #   Case:   +subdomain, +tld    Continue, recurse into subdomain
        else:
            #   Case:   -subdomain, -tld    Stop, output previous (populated) subdomain and current (empty) tld
            subdomain, idxs_subdomain = domain_curr, idxs_domain_curr
            break
    if tlds:
        tlds = list(reversed(tlds))
        names_tld, idxs_tld = zip(*tlds)
        tld = ('.'.join(names_tld), (idxs_tld[0][0], idxs_tld[-1][-1]))
    """
    pat = ur"\s*(www\d?\.)?(?P<sd>.+)\s*"
    parse = lambda sd: re.sub(pat, ur"\g<sd>", sd)
    parse('abc.com')
    parse('www.abc.com')
    parse('www2.abc.com')
    parse(' www.abc.com ')
    parse(' www2.abc.com ')
    """
    pat_www = ur"\s*(www\d?\.)?(?P<sd>.+)\s*"
    try:
        subdomain = re.sub(pat_www, ur"\g<sd>", subdomain)
    except Exception as e:
        print e
        print colored(traceback.format_exc(), 'red')
        # pdb.set_trace()
    if subdomain: subdomain = subdomain.strip().strip('.')
    result = {
        'orig_domain'   : domain.strip().strip('.'),
        'tld'           : tld,
        'tlds'          : tlds,     #    Redundant, but may be useful.
        'subdomain'     : (subdomain, idxs_subdomain),
    }
    return result


def test_parse_domain():
    data = [
        ('a.b.c.d.e.f.g.co', {'orig_domain': 'a.b.c.d.e.f.g.co', 'tlds': [('co', (14, 16))], 'subdomain': ('a.b.c.d.e.f.g', (0, 13)), 'tld': ('co', (14, 16))}),
        ('t.u.f.y.co', {'orig_domain': 't.u.f.y.co', 'tlds': [('co', (8, 10))], 'subdomain': ('t.u.f.y', (0, 7)), 'tld': ('co', (8, 10))}),
        ('t.info.ru', {'orig_domain': 't.info.ru', 'tlds': [('info', (2, 6)), ('ru', (7, 9))], 'subdomain': ('t', (0, 1)), 'tld': ('info.ru', (2, 9))}),
        ('t.co.uk', {'orig_domain': 't.co.uk', 'tlds': [('co', (2, 4)), ('uk', (5, 7))], 'subdomain': ('t', (0, 1)), 'tld': ('co.uk', (2, 7))})
    ]
    for text, expected in data:
        res = parse_domain(text)
        print text
        print '\t', res
        assert res == expected
    print 'test_parse_domain passed!'



def parse_domain_special(domain, func=None):
    # Ignore the top domain
    if isinstance(domain, basestring):
        parse_dict = parse_domain(domain)
    elif isinstance(domain, dict):
        parse_dict = domain
    else:
        raise RuntimeError("Must pass a dictionary of domain names to `parse_domain_special`.")
    domain = parse_dict['subdomain']
    parse_dict_sub = parse_domain(domain[0], idxs_domain=domain[1], func=func)
    parse_dict[func.func_name] = parse_dict_sub
    # parse_dict['subdomain'] = parse_dict_sub['subdomain']
    # The 'subtld' field will contain the special domain if there's a match.
    return parse_dict


def parse_domain_blog(domain):
    return parse_domain_special(domain, match_domain_blog)


def test_parse_domain_blog():
    data = [
        ('blah.wordpress.com', {
            'match_domain_blog': {
                'orig_domain': 'blah.wordpress', 'tlds': [('wordpress', (5, 14))], 'subdomain': ('blah', (0, 4)), 'tld': ('wordpress', (5, 14))
            },
            'orig_domain': 'blah.wordpress.com', 'tlds': [('com', (15, 18))], 'subdomain': ('blah.wordpress', (0, 14)), 'tld': ('com', (15, 18))
        }),
        ('blah.livejournal.com', {
            'match_domain_blog': {
                'orig_domain': 'blah.livejournal', 'tlds': [('livejournal', (5, 16))], 'subdomain': ('blah', (0, 4)), 'tld': ('livejournal', (5, 16))
            },
            'orig_domain': 'blah.livejournal.com', 'tlds': [('com', (17, 20))], 'subdomain': ('blah.livejournal', (0, 16)), 'tld': ('com', (17, 20))
        }),
        ('blah.blogspot.com', {
            'match_domain_blog': {
                'orig_domain': 'blah.blogspot', 'tlds': [('blogspot', (5, 13))], 'subdomain': ('blah', (0, 4)), 'tld': ('blogspot', (5, 13))
            },
            'orig_domain': 'blah.blogspot.com', 'tlds': [('com', (14, 17))], 'subdomain': ('blah.blogspot', (0, 13)), 'tld': ('com', (14, 17))
        }),
        ('blah.yuku.com', {
            'match_domain_blog': {
                'orig_domain': 'blah.yuku', 'tlds': [('yuku', (5, 9))], 'subdomain': ('blah', (0, 4)), 'tld': ('yuku', (5, 9))
            },
            'orig_domain': 'blah.yuku.com', 'tlds': [('com', (10, 13))], 'subdomain': ('blah.yuku', (0, 9)), 'tld': ('com', (10, 13))
        }),
        ('blah.adweek.blogs.com', {
            'match_domain_blog': {
                'orig_domain': 'blah.adweek.blogs', 'tlds': [('adweek.blogs', (5, 17))], 'subdomain': ('blah', (0, 4)), 'tld': ('adweek.blogs', (5, 17))
            },
            'orig_domain': 'blah.adweek.blogs.com', 'tlds': [('com', (18, 21))], 'subdomain': ('blah.adweek.blogs', (0, 17)), 'tld': ('com', (18, 21))
        }),
        ('blah.adweek.meh.blogs.com', {
            'match_domain_blog': {
                'orig_domain': 'blah.adweek.meh.blogs', 'tlds': [], 'subdomain': ('blah.adweek.meh.blogs', (0, 21)), 'tld': None
            },
            'orig_domain': 'blah.adweek.meh.blogs.com', 'tlds': [('com', (22, 25))], 'subdomain': ('blah.adweek.meh.blogs', (0, 21)), 'tld': ('com', (22, 25))
        }),
    ]
    for text, expected in data:
        res = parse_domain_blog(text)
        print text
        print '\t', res
        assert res == expected
    print 'test_parse_domain_blog passed!'


def parse_domain_photo(domain):
    return parse_domain_special(domain, match_domain_photo)




def test_parse_domain_photo():
    data = [
        ('blah.imgur.com', {
            'match_domain_photo': {
                'orig_domain': 'blah.imgur', 'tlds': [('imgur', (5, 10))], 'subdomain': ('blah', (0, 4)), 'tld': ('imgur', (5, 10))
            },
            'orig_domain': 'blah.imgur.com', 'tlds': [('com', (11, 14))], 'subdomain': ('blah.imgur', (0, 10)), 'tld': ('com', (11, 14))
        }),
        ('blah.shutterfly.com', {
            'match_domain_photo': {'orig_domain': 'blah.shutterfly', 'tlds': [('shutterfly', (5, 15))], 'subdomain': ('blah', (0, 4)), 'tld': ('shutterfly', (5, 15))},
            'orig_domain': 'blah.shutterfly.com', 'tlds': [('com', (16, 19))], 'subdomain': ('blah.shutterfly', (0, 15)), 'tld': ('com', (16, 19))
        }),
        ('blah.instagram.com', {
            'match_domain_photo': {'orig_domain': 'blah.instagram', 'tlds': [('instagram', (5, 14))], 'subdomain': ('blah', (0, 4)), 'tld': ('instagram', (5, 14))},
            'orig_domain': 'blah.instagram.com', 'tlds': [('com', (15, 18))], 'subdomain': ('blah.instagram', (0, 14)), 'tld': ('com', (15, 18))
        }),
        ('blah.photobucket.com', {
            'match_domain_photo': {'orig_domain': 'blah.photobucket', 'tlds': [('photobucket', (5, 16))], 'subdomain': ('blah', (0, 4)), 'tld': ('photobucket', (5, 16))},
            'orig_domain': 'blah.photobucket.com', 'tlds': [('com', (17, 20))], 'subdomain': ('blah.photobucket', (0, 16)), 'tld': ('com', (17, 20))
        }),
        ('blah.meh.smugmug.com', {
            'match_domain_photo': {'orig_domain': 'blah.meh.smugmug', 'tlds': [('smugmug', (9, 16))], 'subdomain': ('blah.meh', (0, 8)), 'tld': ('smugmug', (9, 16))},
            'orig_domain': 'blah.meh.smugmug.com', 'tlds': [('com', (17, 20))], 'subdomain': ('blah.meh.smugmug', (0, 16)), 'tld': ('com', (17, 20))
        }),
    ]
    for text, expected in data:
        res = parse_domain_photo(text)
        print text
        print '\t', res
        assert res == expected
    print 'test_parse_domain_photo passed!'



def get_query_dict(url):
    """Returns a query dict with only one entry per key."""
    parse = urlparse.urlparse(url)
    query_dict = urlparse.parse_qs(parse.query) if parse.query else {}
    query_dict = dict (
        (k, v.pop()) if v else (k, v) for k, v in query_dict.iteritems()
    )
    return query_dict



def test():
    test_get_domain()
    test_parse_domain()
    test_parse_domain_blog()
    test_parse_domain_photo()


if __name__ == '__main__':
    test()

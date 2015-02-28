
import pdb
from pprint import pformat
import itertools


def get_all_ngrams(words, max_num=5, key=None, process_types=None):
    """
    Fetches all n-grams from 2 to `max_num`.
    """
    if isinstance(words, basestring):
        raise TypeError("`get_all_ngrams` requires a sequence.")
    for idx in xrange(2, max_num + 1):
        ngrams = get_ngrams(
            words, idx, to_list=True, process_types=process_types
        )
        if ngrams:
            if key is not None:
                #   Add extra info (e.g. count, market, orig text) as the key.
                ngrams = [ dict(zip(key, ng)) for ng in ngrams ]
            # ------------------------
            #for ng in ngrams: print ng
            # ------------------------
            yield idx, ngrams


def get_ngrams(words, num=2, to_list=False, process_types=None):
    """
        Format:
            [ dict(pos=(start, end), name=type, text=text), ... ]

    """
    if isinstance(words, basestring):
        raise TypeError("`get_ngrams` requires a sequence.")
    if process_types is None:
        process_types = set(['w', 'num'])  #   Only process words and numbers by default.
    #   ==========================================================
    def get_segs(words, num):
        #   Moving window for capturing successive word sequences.
        windows = ( (start, start + num) for start in range(len(words)) )
        for start, end in windows:
            seg = words[start:end]
            right_type = True
            #   Filter out sequences that aren't of the right type.
            for seg_ in seg:
                type_ = seg_['name']
                if type_ not in process_types:
                    #   Some member of the sequence doesn't have the right type.
                    right_type = False
                    break
            if right_type and len(seg) == num:
                yield seg

    def join_segs(segs):
        #   Format: dict(pos=(s, e), name=type_, text=text, children=children), dict(pos=(s, e), name=type_, text=text, children=children))
        #   Update (start, end) with (min, max) of the segment
        #   NB: segs must be in sorted order for this to work
        s = segs[0]['pos'][0]   #   'start' position
        e = segs[-1]['pos'][1]  #   'end' position
        text_list = []
        types = []
        children = []
        for seg in iter(segs):
            pstn, type_, text = seg['pos'], seg['name'], seg['text']
            children.append(dict(pos=pstn, name=type_, text=text))
            types.append(type_)
            text_list.append(text)
        text = '_'.join(text_list)
        types = ['ngram'] + types
        type_ = '_'.join(types)
        res = dict(pos=(s, e), name=type_, text=text, children=children)
        return res
    #   ==========================================================
    segments = get_segs(words, num)
    segments = ( join_segs(segs) for segs in segments )
    if to_list: segments = list(segments)
    return segments



def test_get_ngrams():
    data = [
        (
            [],
            [],
        ),
        (
            [((0, 2), 'w', 'ab'), ((2, 4), 'w', 'cd'), ((4, 6), 'w', 'ef')],
            [((0, 4), 'w_w', 'ab_cd'), ((2, 6), 'w_w', 'cd_ef')],
        ),
    ]
    for text, expected in data:
        print "ORIG:", text
        print "\tEXPECTED:", pformat(expected)
        res = get_ngrams(text, num=2, to_list=True)
        print '\tRESULT:', pformat(res)
        assert res == expected
        print
    print 'test_get_ngrams passed!', '\n'


def test_get_all_ngrams():
    data = [
        (
            [],
            [], # [(2, []), (3, [])]
        ),
        (
            [((0, 2), 'w', 'ab'), ((2, 4), 'w', 'cd'), ((4, 6), 'w', 'ef')],
            [
                (2, [((0, 4), 'w_w', 'ab_cd'), ((2, 6), 'w_w', 'cd_ef')]),
                (3, [((0, 6), 'w_w_w', 'ab_cd_ef')]),
            ],
        ),
    ]
    for words, expected in data:
        print "ORIG:", words
        print "\tEXPECTED:", pformat(expected)
        res = list(get_all_ngrams(words, max_num=3))
        print '\tRESULT:', pformat(res)
        assert res == expected
        print
    print 'test_get_all_ngrams passed!', '\n'



def vectorize_ngrams(words, n=2):
    windows = ( (start, start + n) for start in xrange(len(words)) )
    segments = ( words[start:end] for start, end in windows )
    segments = ( s for s in segments if len(s) == n )
    #   Combine the ngrams.
    segments = ( '_'.join(s) for s in segments )
    segments = list(segments)
    segments = segments + words
    return segments



def get_top_ngrams(df, k=100):
    #   Remove items with a count of 1
    df = df[df['count'] > 1]
    #   Get quantiles for each ngram
    groups = df.groupby('length', group_keys=False)
    #   ===========================================
    def get_top(group):
        #   Keep only the top `k` items
        curr_k = int(k / (group['length'][0]))
        return group.sort_index(by='count')[-curr_k:][::-1]
    #   ===========================================
    top_ngrams_df = groups.apply(get_top)
    top_ngrams_df = top_ngrams_df.set_index('ngram')
    return top_ngrams_df


def code_ngrams(top_ngrams_df, fname, base_dir, brand='', origin=''):
    """
    Utility for interactive coding of ngrams by category.
    """
    avail_codes = set(['b', 'p', 'o'])
    codes = []
    #   Make sure it's sorted and then assign the ranks.
    top_ngrams_df = top_ngrams_df.sort_index(by='count', ascending=False)
    top_ngrams_df['rank'] = xrange(1, len(top_ngrams_df) + 1)
    ngrams = list(top_ngrams_df.index.values)
    print '\n---------------------------------------'
    print 'Coding for {0} ngrams'.format(len(ngrams))
    skip_flag = 0
    while ngrams:
        ngram = ngrams[-1]
        print ngram
        print 'Enter code (b = brand), (p = product), (o = other)'
        code = raw_input()
        if (code in avail_codes) or (skip_flag == 1):
            #   -------------------
            print '\tUsing:', code
            #   -------------------
            if skip_flag == 1: code = 'o'
            codes.append(code)
            ngrams.pop()
            #   ---------
            print '\t{0} ngrams left'.format(len(ngrams))
            #   ---------
            skip_flag = 0
        else:
            #   -------------------
            print "\tCouldn't understand {0}. Try again using one of ({1}) or hit <enter> to select 'other'".format(
                repr(code), ', '.join(avail_codes)
            )
            skip_flag = 1
            #   -------------------
    top_ngrams_df['codes'] = list(reversed(codes))
    if brand: top_ngrams_df['brand'] = brand
    if origin: top_ngrams_df['origin'] = origin
    return top_ngrams_df



def test_get_ngrams_OLD():
    tests = [
        ('ive got one ... ace ..', 'ive got one ... ace ..', ['i\ve got', 'got one', 'one ace']),
        (
            'Morning Maria, these pics will be uploaded over on our mobile page at www.facebook.com/samsungmobileuk ~Ravi',
            'morning maria, these pics will be uploaded over on our mobile page at www.facebook.com/samsungmobileuk ravi',
            [
                'morning maria', 'maria pics', 'pics uploaded',
                'uploaded mobile', 'mobile page',
                'page www.facebook.com/samsungmobileuk',
                'www.facebook.com/samsungmobileuk ravi'
            ]
        ),
        (
            'bought galaxy ace ....won bd-d8500m bluray player..cool..love samsung',
            'bought galaxy ace ....won bd-d8500m bluray player..cool..love samsung',
            [
                'bought galaxy', 'galaxy ace', 'ace won', 'won bd-8500m', 'bd-8500m bluray',
                'bluray player', 'player cool', 'cool love', 'love samsung'
            ]
        ),
        (
            'I\'m glad it has Jelly Bean 4.1 onboard, but your "Nature UI" is hideous...',
            'I am glad it has Jelly Bean 4.1 onboard, but your "Nature UI" is hideous...',
            [
                'glad jelly', 'jelly bean', 'bean 4.1', '4.1 onboard', 'onboard nature',
                'nature ui', 'ui hideous',
            ]
        ),
        (
            'Rylan isn\'t in the competition anymore yaaay!! I want James to win xx <3',
            'Rylan is not in the competition anymore yaaay!! I want James to win xx <3',
            [
                'rylan competition', 'competition anymore', 'anymore yaaay', 'yaaay want',
                'want james', 'james win', 'win xx', 'xx <3'
            ]
        ),
        (
            'my iphone 3g still works',
            'my iphone 3g still works',
            ['iphone 3g', '3g still', 'still works']
        ),
        (
            'I can actually use stock for a while 4.1.2 on SGS3',
            'I can actually use stock for a while 4.1.2 on SGS3',
            ['actually use', 'use stock', 'stock 4.1.2', '4.1.2 sgs3']
        ),
        (
            'Hi Sharron, we\'re here to help - don\'t panic! :)',
            'Hi Sharron, we are here to help - do not panic! :)',
            ['hi sharron', 'sharron help', 'help panic', 'panic :)']
        ),
        (
            'some phrase with a date 9/1/2012 and another date 10-2-99',
            'some phrase with a date 9/1/2012 and another date 10-2-99',
            [
                'some phrase', 'phrase date', 'date 9/1/2012', '9/1/2012 another',
                'another date', 'date 10-2-99'
            ]
        ),
        (
            'phrase with emoticons :). ^_^, ^o^',
            'phrase with emoticons ^_^, ^o^',
            ['phrase emoticons', 'emoticons ^_^', '^_^ ^o^']
        ),
        (
            'phrase with url www.facebook.com/samsungmobileuk, www.foo.com and https://bar.org',
            'phrase with url www.facebook.com/samsungmobileuk, www.foo.com and https://bar.org',
            [
                'phrase url', 'url www.facebook.com/samsungmobileuk',
                'www.facebook.com/samsungmobileuk www.foo.com',
                'www.foo.com https://bar.org'
            ]
        ),
        (
            'phrase with times 6:00 AM 10:20 2:45pm',
            'phrase with times 6:00 AM 10:20 2:45pm',
            ['phrase times', 'times 6:00', '6:00 AM', 'AM 10:20', '10:20 2:45pm']
        ),
        (
            'phrase with product codes 4.1, 4.1.2. SGS3 and bd-d8500m',
            'phrase with product codes 4.1, 4.1.2. SGS3 and bd-d8500m',
            [
                'phrase product', 'product codes', 'codes 4.1',
                '4.1 4.1.2', '4.1.2 sgs3', 'sgs3 bd-d8500m'
            ]
        ),
        (
            'phrase with comma-sep numbers and decimals 103,000, 50,000, 60.00, 100,000,000.53, .100',
            'phrase with comma-sep numbers and decimals 103,000, 50,000, 60.00, 100,000,000.53, .100',
            [
                'phrase comma', 'comma sep', 'sep numbers', 'numbers decimals',
                'decimals 103,000', '103,000, 50,000', '50,000 60.00', '60.00 100,000,000.53',
                '100,000,000.53 .100'
            ]
        )
    ]
    for orig, clean, expected in tests:
        print 'Orig:', orig
        #   TBD:    Add expected results for ngram sizes other than 2.
        print 'Expected:', expected
        orig = orig.split()
        #actual = get_ngrams(orig, 2, to_list=True)
        print 'Actual:'
        all_ngrams = get_all_ngrams(orig, 5)
        for num, actual in all_ngrams.iteritems():
            print '\t', str(num), str(actual)
            print


def test():
    test_get_ngrams()
    test_get_all_ngrams()


if __name__ == '__main__':
    test()



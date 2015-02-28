
EMOJI = dict(
    happy   = set([
        u'\u2323',
        # u'\U0001f600',
        # u'\U0001f601',
        # u'\U0001f602',
        # u'\U0001f603',
        # u'\U0001f604',
        # u'\U0001f605',
        # u'\U0001f606',
        # u'\U0001f607',
        # u'\U0001f608',
        # u'\U0001f609',
        # u'\U0001f60A',
        # u'\U0001f60B',
        # u'\U0001f60C',
        # u'\U0001f60E',
        # u'\U0001f60F',
        # u'\U0001f639',
        # u'\U0001f63A',
        # u'\U0001f63B',
        # u'\U0001f64C',
        # u'\U0001f44f',  #   'CLAPPING HANDS SIGN'
    ]),
    blank   = set([
        # u'\U0001f610',
        # u'\U0001f614',
        # u'\U0001f636',
    ]),
    wry     = set([
        # u'\U0001f611',
        # u'\U0001f612',
        # u'\U0001f615',
        # u'\U0001f63C',
    ]),
    sad     = set([
        u'\u2322',
        # u'\U0001f613',
        # u'\U0001f616',
        # u'\U0001f61E',
        # u'\U0001f61F',
        # u'\U0001f622',
        # u'\U0001f623',
        # u'\U0001f625',
        # u'\U0001f628',
        # u'\U0001f629',
        # u'\U0001f62A',
        # u'\U0001f62B',
        # u'\U0001f62D',
        # u'\U0001f63F',
        # u'\U0001f4a9',  #   'PILE OF POO',
        # u'\U0001F494',  #   'BROKEN HEART',
    ]),
    angry   = set([
        # u'\U0001f620',
        # u'\U0001f621',
        # u'\U0001f624',
        # u'\U0001f626',
        # u'\U0001f627',
        # u'\U0001f62C',
        # u'\U0001f63E',
        # u'\U0001f63D',
    ]),
    love    = set([
        u'\u2764',      #   'HEAVY BLACK HEART'
        u'\u2763',      #   'HEAVY HEART EXCLAMATION MARK ORNAMENT'
        u'\u2665',      #   'BLACK HEART SUIT'
        u'\u2661',      #   'WHITE HEART SUIT'
        u'\u2766',      #   'FLORAL SUIT'
        u'\u2619',      #   'REVERSED ROTATED FLORAL SUIT'
        u'\u2767',      #   'ROTATED FLORAL HEART BULLET'
        # u'\U0001F493',      #   'BEATING HEART'
        # u'\U0001F495',      #   'TWO HEARTS'
        # u'\U0001F496',      #   'SPARKLING HEART'
        # u'\U0001F497',      #   'GROWING HEART'
        # u'\U0001F498',      #   'HEART WITH ARROW'
        # u'\U0001F499',      #   'BLUE HEART'
        # u'\U0001F49A',      #   'GREEN HEART'
        # u'\U0001F49B',      #   'YELLOW HEART'
        # u'\U0001F49C',      #   'PURPLE HEART'
        # u'\U0001F49D',      #   'HEART WITH RIBBON'
        # u'\U0001F49E',      #   'REVOLVING HEARTS'
        # u'\U0001F49F',      #   'HEART DECORATION'
        # u'\U0001f60D',
        # u'\U0001f617',
        # u'\U0001f618',
        # u'\U0001f619',
    ]),
    money   = set([
        # u'\U0001F4B0',  #'MONEY BAG'
        # u'\U0001F4B1',  #'CURRENCY EXCHANGE'
        # u'\U0001F4B2',  #'HEAVY DOLLAR SIGN'
        # u'\U0001F4B3',  #'CREDIT CARD'
        # u'\U0001F4B4',  #'BANKNOTE WITH YEN SIGN'
        # u'\U0001F4B5',  #'BANKNOTE WITH DOLLAR SIGN'
        # u'\U0001F4B6',  #'BANKNOTE WITH EURO SIGN'
        # u'\U0001F4B7',  #'BANKNOTE WITH POUND SIGN'
        # u'\U0001F4B8',  #'MONEY WITH WINGS'
        # u'\U0001F4B9',  #'CHART WITH UPWARDS TREND AND YEN SIGN'
    ]),
    silly   = set([
        # u'\U0001f61B',
        # u'\U0001f61C',
        # u'\U0001f61D',
    ]),
    surprise    = set([
        # u'\U0001f62E',
        # u'\U0001f62F',
        # u'\U0001f630',
        # u'\U0001f631',
        # u'\U0001f632',
        # u'\U0001f633',
    ])
)


#:  An attempt at condensing the above characters to character ranges. Not much benefit...
EMOJI_RANGES = dict(
    happy = [
        u'\u2323',
        (u'\U0001f600', u'\U0001f60F'),
        (u'\U0001f63A', u'\U0001f63B'),
        u'\U0001f44f',  #   'CLAPPING HANDS SIGN'
        u'\U0001f64C',
    ],
    blank   = [
        u'\U0001f610',
        u'\U0001f614',
        u'\U0001f636',
    ],
    wry     = [
        (u'\U0001f611', u'\U0001f612'),
        u'\U0001f615',
        u'\U0001f63C',
    ],
    sad     = [
        u'\u2322',
        u'\U0001f613',
        u'\U0001f616',
        (u'\U0001f61E', u'\U0001f61F'),
        (u'\U0001f622', u'\U0001f623'),
        u'\U0001f625',
        (u'\U0001f628', u'\U0001f62B'),
        u'\U0001f62D',
        u'\U0001f63F',
        u'\U0001F494',  #   'BROKEN HEART',
        u'\U0001f4a9',  #   'PILE OF POO',
    ],
    angry   = [
        (u'\U0001f620', u'\U0001f621'),
        u'\U0001f624',
        (u'\U0001f626', u'\U0001f627'),
        (u'\U0001f62C', u'\U0001f63E'),
    ],
    love    = [
        #   Heart Suits
        u'\u2619'
        u'\u2661'
        u'\u2665'
        u'\u2763'
        u'\u2764'
        u'\u2766'
        u'\u2767'
        #   Misc Heart icons
        u'\U0001F493',
        (u'\U0001F495', u'\U0001F49F'),
        u'\U0001f60D',
        (u'\U0001f617', u'\U0001f619'),
    ],
    money   = [
        (u'\U0001F4B0', u'\U0001F4B9'),
    ],
    silly   = [
        (u'\U0001f61B', u'\U0001f61D')
    ],
    surprise    = [
        (u'\U0001f62E', u'\U0001f633'),
    ]
)

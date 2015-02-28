
import os
# import pdb
import htmlentitydefs
# from pprint import pformat
try:
    import cPickle as pickle
except ImportError:
    import pickle

from .constants import THIS_DIR

STOPWORDS_URL = """www
www2 http https
ftp sftp ftps
arp tcp pop3 imap
icmp dhcp smtp
rtmp rtmpt afp
whois mms mailto
ae aero af
ao aq arpa az
bh biz bl bn bq
bt bv bw bz ci ck
cl cm cn co com coop
cr cx cy cz dk dz edu
fj fk fm fr gd
gf gg gh gl gn gov
gq gs gu gw gy hm
hn hu io ir je jm
jp kg kh km kn kw
kz lc lr ls mg
mh mil mk ml mn
mobi mq mw mx mz nf
nl nr org pf pk pn
py rs rw sg
sk sl sm sr sv sx
sz tc td tj tk tl
tn tw tz ua uy
uz vg vn vu wf ws""".split('\n')

#   Stopwords
def get_stopwords():
    from nltk.corpus import stopwords as nltk_stopwords
    stopwords_url = set(sum([l.split() for l in STOPWORDS_URL], []))
    stopwords = (
            stopwords_url
        |   set(nltk_stopwords.words('english'))
        |   set(['&{0};'.format(s) for s in htmlentitydefs.entitydefs.keys()])
        |   set(['&{0};'.format(s.lower()) for s in htmlentitydefs.entitydefs.keys()])
        |   set(['rt', '...'])
        |   set(r'\.\,\;\:\!\?\-\\\/\[\]\(\)')
    )
    return stopwords

PATH_DATA = os.path.join(THIS_DIR, '..', 'data')
PATH_STOPWORDS = os.path.join(PATH_DATA, 'stopwords.pkl')
try:
    with open(PATH_STOPWORDS, 'rb') as f:
        STOPWORDS = pickle.load(f)
except Exception as e:
    STOPWORDS = get_stopwords()
    with open(PATH_STOPWORDS, 'wb') as f:
        pickle.dump(STOPWORDS, f)

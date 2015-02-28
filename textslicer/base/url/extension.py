
#   Stdlib
import os

#   Custom
from .constants_url import THIS_DIR


def make_ext_regex(fname):
    with open(os.path.join(THIS_DIR, 'data', fname), 'rbU') as f:
        exts = set(list(f))
    return exts, _make_ext_regex(exts)

def _make_ext_regex(exts):
    _ext_pattern = r'|'.join( '{0}'.format(d) for d in exts )
    ext_pattern = r"(?P<path>.*?)\.(?P<ext>{0})$".format(_ext_pattern)
    ext_regex = re.compile(ext_pattern, REGEX_FLAGS)
    return ext_regex

def match_ext(s, regex_):
    res = {}
    m = regex_.match(s)
    if m:
        g_path = m.group('path')
        idxs_path = m.span('path')
        g_ext = m.group('ext')
        idxs_ext = m.span('ext')
    else:
        g_path, idxs_path = None, None
        g_ext, idxs_ext = None, None
    res['path'] = (g_path, idxs_path)
    res['ext'] = (g_ext, idxs_ext)
    return res


#:  Image extensions
IMAGE_EXTS, IMAGE_EXT_REGEX = make_ext_regex('ext_image.txt')
def match_image_ext(item):
    return match_ext(item, IMAGE_EXT_REGEX)


#:  Video extensions
VIDEO_EXTS, VIDEO_EXT_REGEX = make_ext_regex('ext_video.txt')
def match_video_ext(item):
    return match_ext(item, VIDEO_EXT_REGEX)


#:  Document extensions
DOCUMENT_EXTS, DOCUMENT_EXT_REGEX = make_ext_regex('ext_document.txt')
def match_document_ext(item):
    return match_ext(item, DOCUMENT_EXT_REGEX)


#:  Audio extensions
AUDIO_EXTS, AUDIO_EXT_REGEX = make_ext_regex('ext_audio.txt')
def match_audio_ext(item):
    return match_ext(item, AUDIO_EXT_REGEX)

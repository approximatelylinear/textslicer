
import re
import pdb
import htmlentitydefs
import itertools
import traceback

#   3rd party
try:
    from lxml import etree
    import lxml.html
    from lxml.html.clean import Cleaner as LXMLCleaner
except ImportError:
    pass
try:
    import enchant
except ImportError:
    pass
from BeautifulSoup import BeautifulSoup, Comment, UnicodeDammit



def remove_html_tags(text, clean_kwargs=None, tree_kwargs=None, **ignore):
    if clean_kwargs is None: clean_kwargs = {}
    if tree_kwargs is None: tree_kwargs = {}
    if text:
        try:
            text = remove_html_tags_with_lxml(text, clean_kwargs, tree_kwargs)
        except Exception as e:
            # print e
            # print traceback.format_exc()
            # pdb.set_trace()
            text = remove_html_tags_with_beautifulsoup(text, clean_kwargs, tree_kwargs)
    return text


def test_remove_html_tags():
    data = [
        (
            """<table border=0><tr><td><table border=0><tr><td><img src="s.gif" height=1 width=0></td><td valign=top><center><a id=up_7592488 href="vote?for=7592488&amp;dir=up&amp;whence=%69%74%65%6d%3f%69%64%3d%37%35%39%30%36%34%34"><div class="votearrow" title="upvote"></div></a><span id=down_7592488></span></center></td><td class="default"><div style="margin-top:2px; margin-bottom:-10px; "><span class="comhead"><a href="user?id=dmix">dmix</a> 3 hours ago  | <a href="item?id=7592488">link</a></span></div><br>
<span class="comment"><font color=#000000>One important and often overlooked feature of Tails is when you shut it down it wipes your system memory&#x2F;RAM using sdmem.<p>Your encrypted data and sensitive files are often accessible via memory forensics even if you shut your computer down. Including the websites you visited. Your encryption keys can be in your computers memory for weeks and is easily accessible via a memory dump.<p>This is why people say that with physical access your computer can always be owned. Even if it&#x27;s encrypted. Tails is the only one I know that handles this attack vector by default.<p><a href="https://tails.boum.org/contribute/design/memory_erasure/" rel="nofollow">https:&#x2F;&#x2F;tails.boum.org&#x2F;contribute&#x2F;design&#x2F;memory_erasure&#x2F;</a></font></span><p><font size=1><u><a href="reply?id=7592488&amp;whence=%69%74%65%6d%3f%69%64%3d%37%35%39%30%36%34%34">reply</a></u></font></td></tr></table></td></tr>
            """,
            """
            dmix link  Your encrypted data and sensitive files are often accessible via memory forensics even if you shut your computer down. Including the websites you visited. Your encryption keys can be in your computers memory for weeks and is easily accessible via a memory dump. This is why people say that with physical access your computer can always be owned. Even if it's encrypted. Tails is the only one I know that handles this attack vector by default. https://tails.boum.org/contribute/design/memory_erasure/ reply
            """.strip()
        )
    ]
    for doc, expected in data:
        # pdb.set_trace()
        print "ORIG:", doc
        print "\tEXPECTED:", expected
        res = remove_html_tags(doc)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_remove_html_tags passed!', '\n'


def remove_html_tags_with_lxml(text, clean_kwargs=None, tree_kwargs=None):
    """
    Uses LXML's text rendering engine to:

        #. Clean the text.
        #. Parse the text.
        #. Mark links in the parsed structure.
        #. Convert the parsed structure back to text.
    """
    XPATH_LEAF_NODES = etree.XPath("//*[not(*)]")
    if clean_kwargs is None: clean_kwargs = {}
    if tree_kwargs is None: tree_kwargs = {}
    ###############
    # pdb.set_trace()
    ###############
    #   Clean text
    try:
        #   Parse the html and build an lxml tree.
        doc = lxml.html.fromstring(text, **tree_kwargs)
        cleaner = LXMLCleaner(**clean_kwargs)
        #   Run the cleaning routines on the doc
        cleaner(doc)
        leaf_nodes = XPATH_LEAF_NODES.evaluate(doc)
        text = u' '.join([ n.text_content() for n in leaf_nodes ]).strip()
    except UnicodeDecodeError:
        text = u''
    return text


def clean_text_with_lxml(text, **kwargs):
    """
    Uses the default lxml cleaner and removes
    scripts, javascript, comments, style, links, meta
    page_structure, processing_instructions, embedded,
    frames, forms, annoying_tags, unknown_tags, and
    unsafe_attrs.
    """
    ###############
#     pdb.set_trace()
    ###############
    cleaner = LXMLCleaner(**kwargs)
    text = cleaner.clean_html(text)
    return text


def remove_html_tags_with_beautifulsoup(text, clean_kwargs=None, tree_kwargs=None):
    if clean_kwargs is None: clean_kwargs = {}
    if tree_kwargs is None: tree_kwargs = {}
    try:
        text_soup = BeautifulSoup(text)
        #   Remove comments
        comments = text_soup.findAll(text=(lambda text: isinstance(text, Comment)))
        for cmmt in comments: cmmt.extract()
        #   Remove script and style tags
        scripts = text_soup.findAll('script')
        noscripts = text_soup.findAll('noscript')
        styles = text_soup.findAll('style')
        for scrpt in itertools.chain(scripts, noscripts, styles): scrpt.extract()
        text = get_text_with_beautifulsoup(text_soup)
    except UnicodeDecodeError:
        text = u''
    # Use a regex to wipe out any remaining tags
    tag_regex = re.compile(ur'<.*?>')
    text = tag_regex.sub(u' ', text)
    return text


def get_text_with_beautifulsoup(soup):
    text = ''.join(soup.findAll(text=True)).strip()
    return text


def unescape_html(text):
    """
    Converts html entities to their unicode equivalents.
    """
    text = re.sub(ur'&([^;]{,10});', convert_entity_to_char, text)
    return text


def convert_entity_to_char(match_obj):
    """
    Converts entities in the html text to their unicode
    equivalents.

    #. Non-numeric characters get translated to their equivalent in the stdlib 'htmlentitydefs' dictionary or to a question-mark.
    #. Numeric characters get translated directly.

    """
    try:
        entity = match_obj.group(1)
        if entity.startswith(u'#'):
            #   Numeric sequence
            entity = u'0' + entity[1:]
            if entity.startswith('x'):
                entity = entity[1:]
                base = 16
            else:
                base = 10
            char = unichr(int(entity, base))
        else:
            #   Text label.
            #   (Unknown labels get replaced with u''.)
            char = unichr(htmlentitydefs.name2codepoint.get(entity, 0))
    except Exception as e:
        #   Default to u''
        char = u''
    return char


def convert_entity_to_codepoint(match_obj):
    """
    Gets the codepoint for an html entity, and returns it as a unicode string.
    """
    entity = match_obj.group(1)
    codepoint = htmlentitydefs.name2codepoint.get(entity, 0)
    return u'{codepoint}'.format(codepoint=codepoint)


def convert_codepoint_to_char(match_obj):
    """
    Converts a unicode codepoint to a unicode character.
    """
    codepoint = match_obj.group(1)
    return unichr(int(codepoint))


def test():
    test_remove_html_tags()


if __name__ == '__main__':
    test()

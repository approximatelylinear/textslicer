

from .abc import CharFilter
from ..base.html import remove_html_tags, unescape_html


class RemoveHTML(CharFilter):
    def process_item(self, text, **kwargs):
        text = remove_html_tags(text, **kwargs)
        text = unescape_html(text)
        return text



def test_remove_html():
    remove_html = RemoveHTML()
    data = [
        (
            dict(
                text=dict(
                    original = """<table border=0><tr><td><table border=0><tr><td><img src="s.gif" height=1 width=0></td><td valign=top><center><a id=up_7592488 href="vote?for=7592488&amp;dir=up&amp;whence=%69%74%65%6d%3f%69%64%3d%37%35%39%30%36%34%34"><div class="votearrow" title="upvote"></div></a><span id=down_7592488></span></center></td><td class="default"><div style="margin-top:2px; margin-bottom:-10px; "><span class="comhead"><a href="user?id=dmix">dmix</a> 3 hours ago  | <a href="item?id=7592488">link</a></span></div><br><span class="comment"><font color=#000000>One important and often overlooked feature of Tails is when you shut it down it wipes your system memory&#x2F;RAM using sdmem.<p>Your encrypted data and sensitive files are often accessible via memory forensics even if you shut your computer down. Including the websites you visited. Your encryption keys can be in your computers memory for weeks and is easily accessible via a memory dump.<p>This is why people say that with physical access your computer can always be owned. Even if it&#x27;s encrypted. Tails is the only one I know that handles this attack vector by default.<p><a href="https://tails.boum.org/contribute/design/memory_erasure/" rel="nofollow">https:&#x2F;&#x2F;tails.boum.org&#x2F;contribute&#x2F;design&#x2F;memory_erasure&#x2F;</a></font></span><p><font size=1><u><a href="reply?id=7592488&amp;whence=%69%74%65%6d%3f%69%64%3d%37%35%39%30%36%34%34">reply</a></u></font></td></tr></table></td></tr>""",
                    current = [((0, 1462), None, """<table border=0><tr><td><table border=0><tr><td><img src="s.gif" height=1 width=0></td><td valign=top><center><a id=up_7592488 href="vote?for=7592488&amp;dir=up&amp;whence=%69%74%65%6d%3f%69%64%3d%37%35%39%30%36%34%34"><div class="votearrow" title="upvote"></div></a><span id=down_7592488></span></center></td><td class="default"><div style="margin-top:2px; margin-bottom:-10px; "><span class="comhead"><a href="user?id=dmix">dmix</a> 3 hours ago  | <a href="item?id=7592488">link</a></span></div><br><span class="comment"><font color=#000000>One important and often overlooked feature of Tails is when you shut it down it wipes your system memory&#x2F;RAM using sdmem.<p>Your encrypted data and sensitive files are often accessible via memory forensics even if you shut your computer down. Including the websites you visited. Your encryption keys can be in your computers memory for weeks and is easily accessible via a memory dump.<p>This is why people say that with physical access your computer can always be owned. Even if it&#x27;s encrypted. Tails is the only one I know that handles this attack vector by default.<p><a href="https://tails.boum.org/contribute/design/memory_erasure/" rel="nofollow">https:&#x2F;&#x2F;tails.boum.org&#x2F;contribute&#x2F;design&#x2F;memory_erasure&#x2F;</a></font></span><p><font size=1><u><a href="reply?id=7592488&amp;whence=%69%74%65%6d%3f%69%64%3d%37%35%39%30%36%34%34">reply</a></u></font></td></tr></table></td></tr>""")]
                )
            ),
            dict(
                text=dict(
                    original = """<table border=0><tr><td><table border=0><tr><td><img src="s.gif" height=1 width=0></td><td valign=top><center><a id=up_7592488 href="vote?for=7592488&amp;dir=up&amp;whence=%69%74%65%6d%3f%69%64%3d%37%35%39%30%36%34%34"><div class="votearrow" title="upvote"></div></a><span id=down_7592488></span></center></td><td class="default"><div style="margin-top:2px; margin-bottom:-10px; "><span class="comhead"><a href="user?id=dmix">dmix</a> 3 hours ago  | <a href="item?id=7592488">link</a></span></div><br><span class="comment"><font color=#000000>One important and often overlooked feature of Tails is when you shut it down it wipes your system memory&#x2F;RAM using sdmem.<p>Your encrypted data and sensitive files are often accessible via memory forensics even if you shut your computer down. Including the websites you visited. Your encryption keys can be in your computers memory for weeks and is easily accessible via a memory dump.<p>This is why people say that with physical access your computer can always be owned. Even if it&#x27;s encrypted. Tails is the only one I know that handles this attack vector by default.<p><a href="https://tails.boum.org/contribute/design/memory_erasure/" rel="nofollow">https:&#x2F;&#x2F;tails.boum.org&#x2F;contribute&#x2F;design&#x2F;memory_erasure&#x2F;</a></font></span><p><font size=1><u><a href="reply?id=7592488&amp;whence=%69%74%65%6d%3f%69%64%3d%37%35%39%30%36%34%34">reply</a></u></font></td></tr></table></td></tr>""",
                    current = [((0, 516), None, """dmix link  Your encrypted data and sensitive files are often accessible via memory forensics even if you shut your computer down. Including the websites you visited. Your encryption keys can be in your computers memory for weeks and is easily accessible via a memory dump. This is why people say that with physical access your computer can always be owned. Even if it's encrypted. Tails is the only one I know that handles this attack vector by default. https://tails.boum.org/contribute/design/memory_erasure/ reply""")],
                )
            )
        )
    ]
    for doc, expected in data:
        # pdb.set_trace()
        print "ORIG:", doc
        print "\tEXPECTED:", expected
        res = remove_html(doc)
        print '\tRESULT:', res
        assert res == expected
        print
    print 'test_remove_html passed!', '\n'


def test():
    test_remove_html()


if __name__ == '__main__':
    test()



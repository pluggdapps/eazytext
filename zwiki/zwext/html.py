# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2010 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : none
# Notes  : none
# Todo   : none
#   1. Unit test case for this extension.

from   zwiki.zwext    import ZWExtension
from   zwiki          import split_style, lhtml

wikidoc = """
=== Html
: Description :: Raw html text.
"""

tmpl = 'div class="zwext-html" style="%s"> %s </div>'

class Html( ZWExtension ) :
    """Implements Html() wikix"""

    def __init__( self, props, nowiki, *args ) :
        self.nowiki  = nowiki
        
        d_style, s_style = split_style( props.pop( 'style', {} ))
        self.style  = s_style
        self.css = {}
        self.css.update( d_style )
        self.css.update( props )

    def tohtml( self ) :
        fn = lambda (k, v) : '%s : %s' % (k,v)
        style = '; '.join(map( fn, self.css.items() ))
        if self.style :
            style += '; ' + self.style + '; '

        try :
            boxnode = lhtml.fromstring( self.nowiki )
        except :
            html = tmpl % (style, '')
        else :
            html = tmpl % (style, lhtml.tostring(boxnode) )
        return html


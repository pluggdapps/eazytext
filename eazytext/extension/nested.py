# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2009 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

# Gotcha : none
# Notes  : none
# Todo   : none
#   1. Unit test case for this extension.

from   zope.component       import getGlobalSiteManager

from   eazytext.extension   import Extension, nowiki2prop
from   eazytext.interfaces  import IEazyTextExtension

gsm = getGlobalSiteManager()

doc = """
=== Nested

: Description ::
    Nest another EazyText document / text within the current
    document. Property key-value pairs accepts CSS styling attributes.
"""

class Nested( Extension ) :
    tmpl = '<div class="etext-nested" style="%s"> %s </div>'
    pluginname = 'Nested'
    
    def __init__( self, *args ):
        self.config = {
            'nested' : True,
            'include_skin' : False,
        }

    def __call__( self, argtext ):  # Does not take any argument.
        return eval( 'Nested()' )

    def html( self, node, igen, *args, **kwargs ):
        from   eazytext        import Translate
        style, text = nowiki2prop( node.text )
        html = ''
        if text :
            try :
                t    = Translate( etxtext=text, etxconfig=self.config )
                html = self.tmpl % ( style, t( context={} ) )
            except :
                if node.parser.etparser.debug : raise
                html = self.tmpl % ('', '')
        return html


# Register this plugin
gsm.registerUtility( Nested(), IEazyTextExtension, Nested.pluginname )
Nested._doc = doc

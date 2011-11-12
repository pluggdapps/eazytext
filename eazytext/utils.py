# This file is subject to the terms and conditions defined in
# file 'LICENSE', which is part of this source code package.
#       Copyright (c) 2011 SKR Farms (P) LTD.

# -*- coding: utf-8 -*-

import re, sys

HTML_CHARS = [ '"', "'", '&', '<', '>' ]
ENDMARKER  = '<{<{}>}>'

class ConfigItem( dict ):
    """Convenience class encapsulating config value description, which is a
    dictionary of following keys,

    ``default``,
        Default value for this settings parameter.
    ``types``,
        Comma separated value of valid types. Allowed types are str, unicode,
        basestring, int, long, bool, 'csv'. 'csv' is a custom defined.
    ``help``,
        Help string describing the purpose and scope of settings parameter.
    ``webconfig``,
        Boolean, specifying whether the settings parameter is configurable via
        web.
    """
    typestr = {
        str   : 'str', unicode : 'unicode', list : 'list', tuple : 'tuple',
        'csv' : 'csv', dict    : 'dict',    bool : 'bool',
    }
    def _options( self ):
        opts = self.get( 'options', '' )
        return opts() if callable(opts) else opts

    # Compulsory fields
    default = property( lambda self : self['default'] )
    types   = property(
                lambda s : ', '.join([ s.typestr[k] for k in s['types'] ])
              )
    # Optional fields, mostly for rendering on user-agent.
    help = property( lambda self : self.get('help', '') )
    webconfig = property( lambda self : self.get('webconfig', True) )
    options = property( _options )


class ConfigDict( dict ):
    """Configuration class to implement settings.py module providing the
    package-default options. Along with the default options, it is possible to
    add help-text for each config-key, as a dictionary.

    The setting-value description will be aggregated as a dictionary under,
        self._spec
    """
    def __init__( self, *args, **kwargs ):
        self._spec = {}
        dict.__init__( self, *args, **kwargs )

    def __setitem__( self, name, value ):
        self._spec[name] = ConfigItem( value )
        return dict.__setitem__( self, name, value['default'] )

    def specifications( self ):
        return self._spec


def escape_htmlchars( text ) :
    """If the text is not supposed to have html characters, escape them"""
    text = re.compile( r'&', re.MULTILINE | re.UNICODE ).sub( '&amp;', text )
    text = re.compile( r'"', re.MULTILINE | re.UNICODE ).sub( '&quot;', text )
    text = re.compile( r'<', re.MULTILINE | re.UNICODE ).sub( '&lt;', text )
    text = re.compile( r'>', re.MULTILINE | re.UNICODE ).sub( '&gt;', text )
    return text


def split_style( style ) :
    """`style` can be a CSS style dictionary or string. If dictionary, it can
    have one non-CSS key 'style'. This key can contain the CSS property as a
    string or as another dictionary, in which case the dictionary can once
    again be treated as `style`"""
    style   = style or {}
    s_style = ''
    if isinstance( style, dict ) :
        inner_style = style.pop( 'style', {} )
    elif isinstance( style, (str, unicode) ) :
        inner_style = style
        style       = {}
    if isinstance( inner_style, dict ) and inner_style :
        d_style, s_style = split_style( inner_style )
        style.update( d_style )
    elif isinstance( inner_style, ( str, unicode )) :
        s_style = inner_style
    return style, s_style

def constructstyle( kwargs, defcss={}, styles='' ) :
    """Construct styles for macros and extensions based on the style passed as
    function arguments, extension properties and defaults style dictionary"""
    d_style, s_style = split_style( kwargs.pop( 'style', {} ))
    css    = {}             # A new dictionary instance
    css.update( defcss )
    css.update( d_style )
    css.update( kwargs )

    style = '; '.join([ "%s: %s" % (k,v) for k,v in css.items() ])
    style = '; '.join(filter(None, [style, s_style, styles ]))
    return style

def obfuscatemail( text ) :
    """Obfuscate email id"""
    return '@'.join([ n[:-3] + '...' for n in text.split( '@', 1 ) ])

def is_matchinghtml( text ) :
    """Check whether html special characters are present in the document."""
    return [ ch for ch in HTML_CHARS if ch in text ]

def wiki_properties( text ) :
    """Parse wiki properties, in the begining of the text,
        @ .....
        @ .....
    Should be a python consumable dictionary.
    Return property, remaining-text.
    """
    props = []
    # Strip off leading newlines
    textlines = text.lstrip( '\n\r' ).split('\n')
    for i in range(len( textlines )) :
        l = textlines[i].lstrip(' \t')
        if len(l) and l[0] == '@' :
            props.append( l[1:] )
            continue
        break;
    text = '\n'.join( textlines[i:] )
    try :
        props = eval( ''.join( props ) ) if props else {}
    except :
        log.error( sys.exc_info() )
        props = {}
    return props, text

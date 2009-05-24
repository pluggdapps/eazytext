import unittest
import os
import difflib              as diff
from   random               import choice, randint, shuffle

from   nose.tools           import assert_equal
import cElementTree         as et

from   zwiki.zwlexer        import ZWLexer
from   zwiki.zwparser       import ZWParser
from   zwiki.test.testlib   import ZWMARKUP, ZWMARKUP_RE, UNICODE, \
                                   gen_psep, gen_ordmark, gen_unordmark, \
                                   gen_bqmark, gen_defnmark, gen_btableline, \
                                   gen_headtext, gen_texts, gen_row, \
                                   gen_wordlist, gen_words, gen_linkwords, gen_links,\
                                   gen_macrowords, gen_macros, \
                                   gen_htmlwords, gen_htmls, gen_xwikinames

stdfiles_dir    = os.path.join( os.path.split( __file__ )[0], 'stdfiles' )
rndfiles_dir    = os.path.join( os.path.split( __file__ )[0], 'rndfiles' )
samplefiles_dir = os.path.join( os.path.split( __file__ )[0], 'samplefiles' )
words           = None
links           = None
macros          = None
htmls           = None
xwikinames      = None

crooked_nowiki  ="""
{{{}}}
{{{ }}}
{{{
  }}}
{{{
    hello world
    {{{
          {{{
            }}}
{{{
    hi world"""

crooked_table  ="""
|=|=|=

|||=
|=||=

|
|

|
"""
crooked_btable = """
||{ { "style" : "color:green; background-color:#ffffcc;", "cellpadding" : "20", \
      "cellspacing" : "0", "border" : "5px",  \
      "caption" : "fruits and icecreams" }
||={ "color" : "black" } | Fruits 

||-{ "color" : "black" } | Fruits 

|| { "color" : "black" } | Fruits 

||={ "color" : "black" } | Fruits 

||{{ "color" : "black" } | Fruits 

||}
"""

def setUpModule() :
    global words, links, macros, htmls, xwikinames
    print "Initialising wiki ..."
    wordlist     = gen_wordlist( maxlen=20, count=200 )
    words        = gen_words( wordlist, count=200, huri_c=10, wuri_c=10 )
    print "Initialising links ..."
    linkwords    = gen_linkwords( maxlen=50, count=200 )
    links        = gen_links( linkwords, 100 )
    print "Initialising macros ..."
    macrowords   = gen_macrowords( maxlen=50, count=200 )
    macros       = gen_macros( macrowords, 100 )
    print "Initialising htmls ..."
    htmlwords    = gen_htmlwords( maxlen=50, count=200 )
    htmls        = gen_htmls( htmlwords, 100 )
    print "Initialising wiki extension names ..."
    xwikinames   = gen_xwikinames( 100 )
    
def tearDownModule() :
    pass

class TestDumpsValid( object ) :
    """Test cases to validate ZWiki parser."""

    def _test_execute( self, type, testcontent, count, ref='' ) :
        # Initialising the parser
        zwparser     = ZWParser( lex_optimize=True, yacc_optimize=False )
        # Prepare the reference.
        ref        = ref or testcontent
        ref        = zwparser.wiki_preprocess( ref )
        props, ref = zwparser._wiki_properties( ref )

        # Characterize the generated testcontent set the wikiproperties
        wikiprops   = {}
        testcontent = ( "@ %s " % wikiprops ) + '\n' + testcontent

        # Test by comparing the dumps
        try :
            tu      = zwparser.parse( testcontent, debuglevel=0 )
            result  = tu.dump()[:-1]
        except :
            tu     = zwparser.parse( testcontent, debuglevel=2 )
            result = tu.dump()[:-1]
        if result != ref :
            # open( 'result', 'w' ).write( result )
            # open( 'ref', 'w' ).write( ref )
            print ''.join(diff.ndiff( result.splitlines(1), ref.splitlines(1) ))
        assert result == ref, type+'... testcount %s'%count

        # Test by translating to html
        #tu   = zwparser.parse( testcontent, debuglevel=0 )
        #html = tu.tohtml()
        #et.fromstring( html ) 

    def test_0_file( self ) :
        """If file `ref` is available pick it and test it"""
        testlist  = []
        ref       = os.path.isfile( 'ref' ) and open( 'ref' ).read()
        ref and testlist.append( ref )
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'ref', t, testcount
            testcount += 1

    def test_1_heading( self ) :
        """Testing heading markup"""
        print "Testing heading markup"
        headmarkup= [ '=' , '==', '===', '====', '=====' ]
        testlist  = [ choice(headmarkup) + gen_headtext( words ) +
                      choice( headmarkup + [ '' ] ) + gen_psep(3)
                        for i in range(50) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'heading', t, testcount
            testcount += 1

    def test_2_hrule( self ) :
        """Testing horizontal rule markup"""
        print "\nTesting horizontal rule markup"
        self._test_execute( 'horizontalrule', '----', 1 )

    def test_3_wikix( self ) :
        """Testing wiki extension markup""" 
        print "\nTesting wiki extension markup"
        wikix_cont = '\n'.join([ choice(words) for i in range(randint(1,20)) ])
        testlist   = [ '{{{' + choice(xwikinames) + '\n' + wikix_cont + \
                       '\n}}}\n' + gen_psep(randint(0,3))
                       for i in range(1000) ]
        testcount  = 1
        for t in testlist :
            yield self._test_execute, 'wikix', t, testcount
            testcount += 1

    def test_4_escapenewline( self ) :
        """Testing wiki text containing `~~\\n`"""
        print "\nTesting wiki text containing `~~\\n`"
        testlist = [ ('hello ~~\nworld', 'hello \nworld') ]
        testcount = 1
        for t, r in testlist :
            yield self._test_execute, 'escapenewline', t, testcount, r
            testcount += 1

    def test_5_lastcharesc( self ) :
        """Testing wiki text with last char as `~`"""
        print "\nTesting wiki text with last char as `~`"
        testlist = [ ('hello world~', 'hello world')  ]
        testcount = 1
        for t,r in testlist :
            yield self._test_execute, 'lastcharesc', t, testcount, r
            testcount += 1

    def test_6_textlines( self ) :
        """Testing textlines"""
        print "\nTesting textlines"
        testlist  = [ '\n'.join([ gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=1,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ]  +\
                    [ '\n'.join([ gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=0,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      choice(ZWMARKUP) + ' ' +
                      '\n'.join([ gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=0,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      choice(ZWMARKUP) + ' ' 
                      '\n'.join([ gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=0,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ])
                      for i in range(10) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'textlines', t, testcount
            testcount += 1

    def test_7_bigtable( self ) :
        """Testing big tables"""
        print "\nTesting big tables"
        testlist = [ '\n'.join([ gen_btableline( words, links, macros, htmls )
                                 for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'bigtable', t, testcount

    def test_8_table( self ) :
        """Testing tables"""
        print "\nTesting tables"
        testlist  = [ '\n'.join([ gen_row( words, links, macros, htmls )
                                  for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ] 
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'table', t, testcount
            testcount += 1

    def test_9_ordlists( self ) :
        """\nTesting ordered list"""
        print "\nTesting ordered list"
        testlist  = [ '\n'.join([ gen_ordmark() + \
                                  gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=1,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'ordlists', t, testcount
            testcount += 1

    def test_A_unordlists( self ) :
        """Testing unordered list"""
        print "\nTesting unordered list"
        testlist  = [ '\n'.join([ gen_unordmark() + \
                                  gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=1,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'unordlists', t, testcount
            testcount += 1

    def test_B_blockquotes( self ) :
        """Testing blockquotes"""
        print "\nTesting blockquotes"
        testlist  = [ '\n'.join([ gen_bqmark() + \
                                  gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=1,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'blockquotes', t, testcount
            testcount += 1

    def test_C_definitions( self ) :
        """Testing definitions"""
        print "\nTesting definitions"
        testlist  = [ '\n'.join([ gen_defnmark() + \
                                  gen_texts(
                                    words, links, macros, htmls,
                                    tc=5, pc=1, ec=2, lc=1, mc=1, hc=1, fc=1,
                                    nopipe=True
                                  )
                                  for j in range(randint(0,10)) ]) +
                      gen_psep(randint(0,3)) for i in range(100) ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'definitions', t, testcount
            testcount += 1

    def test_D_unicode( self ) :
        """Testing unicoded test"""
        print "\nTesting unicoded text"
        testlist = [ '' ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'unordlists', t, testcount
            testcount += 1

    def test_E_crooked_wikix( self ) :
        """Testing crooked nowiki syntax"""
        print "\nTesting crooked nowiki syntax"
        testlist = [ crooked_nowiki, '{{{ \n hi world \n' ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'crooked_nowiki', t, testcount
            testcount += 1

    def test_F_crooked_table( self ) :
        """Testing crooked table syntax"""
        print "\nTesting crooked table syntax"
        testlist = [ crooked_table ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'crooked_table', t, testcount
            testcount += 1

    def test_G_crooked_btable( self ) :
        """Testing crooked big table syntax"""
        print "\nTesting crooked big table syntax"
        testlist = [ crooked_btable ]
        testcount = 1
        for t in testlist :
            yield self._test_execute, 'crooked_btable', t, testcount
            testcount += 1


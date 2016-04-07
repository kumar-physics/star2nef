#!/usr/bin/python -u

from __future__ import absolute_import

# suggested by one of the PEPs, probably doesn't work
#
if __name__ == "__main__" and __package__ is None :
    __package__ = "sans"


import sys
PY3 = (sys.version_info[0] == 3)


import unicodedata

from .lexer import STARLexer
from .handlers import ErrorHandler, ContentHandler, ContentHandler2
from .SansParser import parser, parser2
from .CifParser import parser as cifparser
from .DicParser import parser as dicparser

# NOTE: this should match the dictionary definition of framecode tags: varchar(127)
# otherwise you get "invalid framecode" error for no apparent reason
# if the length matches, at least the validator will say "value too long"...
#
LONG_VALUE = 128

DEFAULT_QUOTE = STARLexer.DVNSINGLE

#
# grrr
#
def isascii( s ) :

    try:
        s.encode('ascii')
        return True
    except (UnicodeDecodeError, UnicodeEncodeError):
        return False

#
#
#
def toascii( s ) :

    if isascii( s ) : return s

    if PY3:
        return unicodedata.normalize( "NFKD", s ).encode('ascii','ignore').decode()
    else:
        return unicodedata.normalize( "NFKD", s.decode( "utf-8" ) ).encode( "ascii", "ignore" )

#
#
#
def sanitize( s ) :
    if s is None : return None
    string = str( s ).strip()
    if len( string ) < 1 : return None
    if not isascii( string ) : string = toascii( string )
    return string

#
# Quote string for STAR.
#
def quote_style( value, verbose = False ) :

    import re

    global LONG_VALUE
    global DEFAULT_QUOTE

# must sanitize the same way as quote()
#
    string = sanitize( value )

    if string is None : return STARLexer.DVNNON
    if len( string ) > LONG_VALUE : 
        if verbose : sys.stdout.write( "Too long\n" )
        return STARLexer.DVNSEMICOLON
    if "\n" in string : 
        if verbose : sys.stdout.write( "Has newline\n" )
        return STARLexer.DVNSEMICOLON

    dq1 = re.compile( "(^\")|(\s+\")" )
    dq2 = re.compile( "\"\s+" )
    has_dq = False
    m = dq1.search( string )
    if m : has_dq = True
    else :
        m = dq2.search( string )
        if m : has_dq = True

    if verbose and has_dq : sys.stdout.write( "Has double quote\n" )

    sq1 = re.compile( "(^')|(\s+')" )
    sq2 = re.compile( "'\s+" )
    has_sq = False
    m = sq1.search( string )
    if m : has_sq = True
    else :
        m = sq2.search( string )
        if m : has_sq = True

    if verbose and has_sq : sys.stdout.write( "Has single quote\n" )

    if has_sq and has_dq : return STARLexer.DVNSEMICOLON

# whitespace is only preserved inside semicolons
    string = string.strip()
    if len( string ) < 1 : return STARLexer.DVNNON

    if has_sq : return STARLexer.DVNDOUBLE
    if has_dq : return STARLexer.DVNSINGLE

    m = STARLexer._re_osemi.search( string )
    if m : 
        if verbose : sys.stdout.write( "Found %s\n" % (STARLexer._re_osemi.pattern,) )
        return DEFAULT_QUOTE

    spc = re.compile( r"\s+" )
    m = spc.search( string )
    if m :
        if verbose : sys.stdout.write( "Has space\n" )
# technically not needed but most code out there can't handle the alternative
        if "'" in string : return STARLexer.DVNDOUBLE
        if '"' in string : return STARLexer.DVNSINGLE
        if verbose : sys.stdout.write( "Has space, no quotes\n" )
        return DEFAULT_QUOTE

    for i in ( STARLexer._re_comment, STARLexer._re_global, STARLexer._re_data,
               STARLexer._re_saveend, STARLexer._re_loop, STARLexer._re_stop, STARLexer._re_tag ) :
        m = i.search( string )
        if m : 
            if verbose : sys.stdout.write( "Has %s\n" % (i.pattern,) )
            return DEFAULT_QUOTE

    return STARLexer.DVNNON

def quote( value, style = None, verbose = False ) :

#    if PY3:
#        from io import StringIO
#    else:
#        from cStringIO import StringIO

# must sanitize the same way as quote_style()
#
    value = sanitize( value )
    if value is None : return "."

    if style is None : qs = quote_style( value, verbose = verbose )
    else : qs = style

    if qs == STARLexer.DVNNON :
        rc = str( value ).strip()
        if len( rc ) < 1 : return "."
        else : return rc

# cStringIO was slower than  "+" in my tests
#
#    buf = StringIO()
    buf = ""
    if qs == STARLexer.DVNSEMICOLON :
# expn: if the newline around ; was added by our pretty-printer, then it'll be adding an extra
# blank line every time the file is printed.
        if "\n" in value :
            if value.startswith( "\n" ) : buf += ";"
            else : buf += ";\n"
            if value.endswith( "\n" ) : buf += value
            else :
                buf += value
                buf += "\n"
            buf += ";"
        else :
            buf += ";\n"
            buf += value
            buf += "\n;"
    elif qs == STARLexer.DVNDOUBLE :
        buf += '"'
        buf += value
        buf += '"'
    elif qs == STARLexer.DVNSINGLE :
        buf += "'"
        buf += value
        buf += "'"
    else :
        raise( "This can never happen" )

#    rc = buf.getvalue()
#    buf.close()
    return buf

# both style and value in one function call
#
def check_quote( value, verbose = False ) :
    qs = quote_style( value, verbose = verbose )
    val = quote( value, style = qs, verbose = verbose )
    return (qs, val)


#
#
__all__ = ["PY3","LONG_VALUE", "quote_style", "quote", "check_quote", 
           "STARLexer", "ErrorHandler", "ContentHandler", "ContentHandler2",
           "parser", "parser2", "cifparser", "dicparser" ]
#
#

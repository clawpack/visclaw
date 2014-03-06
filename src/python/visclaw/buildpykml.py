import pykml
#import urllib2

# This is for when I was attempting to at least get something to work. Not sure where this url came from? I must have seen an example on pykml

#try:
#  print urllib2.urlopen('http://www.reefgeek.com/equipment/Controllers_&_Monitors/Neptune_Systems_AquaController/Apex_Controller_&_Accessories/').read()
#except urllib2.HTTPError, e:
#    print e.code
#    print e.msg
#    print e.headers
#    print e.fp.read()

from pykml import parser

from pykml.factory import write_python_script_for_kml_document

#url = 'http://code.google.com/apis/kml/documentation/kmlfiles/altitudemode_reference.kml'

#fileobject = urllib2.urlopen(url)

#'file.kml' is a sample file found on pykml website
fileobject = open('testfile.kml')

doc = parser.parse(fileobject).getroot()

script = write_python_script_for_kml_document(doc)

fileout=open('file.py','w')

fileout.write(script)

fileout.close()

#---------------------------------------------------------------
# This error occured when using a sample kml file to parse
#---------------------------------------------------------------

#~...src/python/visclaw %  python buildpykml.py
#Traceback (most recent call last):
#  File "buildpykml.py", line 21, in <module>
#    doc = parser.parse(fileobject).getroot()
#  File "/Users/spotter0/anaconda/lib/python2.7/site-packages/pykml/parser.py", line 55, in parse
#    return objectify.parse(fileobject)
#  File "lxml.objectify.pyx", line 1850, in lxml.objectify.parse (src/lxml/lxml.objectify.c:21435)
#  File "lxml.etree.pyx", line 3197, in lxml.etree.parse (src/lxml/lxml.etree.c:65042)
#  File "parser.pxi", line 1593, in lxml.etree._parseDocument (src/lxml/lxml.etree.c:93318)
#  File "parser.pxi", line 1624, in lxml.etree._parseFilelikeDocument (src/lxml/lxml.etree.c:93661)
#  File "parser.pxi", line 1506, in lxml.etree._parseDocFromFilelike (src/lxml/lxml.etree.c:92516)
#  File "parser.pxi", line 1069, in lxml.etree._BaseParser._parseDocFromFilelike (src/lxml/lxml.etree.c:89538)
#  File "parser.pxi", line 577, in lxml.etree._ParserContext._handleParseResultDoc (src/lxml/lxml.etree.c:84711)
#  File "parser.pxi", line 676, in lxml.etree._handleParseResult (src/lxml/lxml.etree.c:85816)
#  File "parser.pxi", line 616, in lxml.etree._raiseParseError (src/lxml/lxml.etree.c:85138)
#lxml.etree.XMLSyntaxError: Start tag expected, '<' not found, line 1, column 1

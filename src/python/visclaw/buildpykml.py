import pykml
from pykml import parser

from pykml.factory import write_python_script_for_kml_document

url = 'http://code.google.com/apis/kml/documentation/kmlfiles/altitudemode_reference.kml'

#fileobject = urllib2.urlopen(url)
fileobject = open('file.kml')

doc = parser.parse(fileobject).getroot()

script = write_python_script_for_kml_document(doc)

fileout=open('file.py','w')

fileout.write(script)

fileout.close()

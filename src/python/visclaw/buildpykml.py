from pykml.factory import write_python_script_for_kml_document

url = 'http://code.google.com/apis/kml/documentation/kmlfiles/altitudemode_reference.kml'

fileobject = urllib2.urlopen(url)

doc = parser.parse(fileobject).getroot()

script = write_python_script_for_kml_document(doc)

print script
from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import ATOM_ElementMaker as ATOM
from pykml.factory import GX_ElementMaker as GX

doc = KML.kml(
  etree.Comment(' required when using gx-prefixed elements '),
  KML.Placemark(
    KML.name('gx:altitudeMode Example'),
    KML.LookAt(
      KML.longitude('146.806'),
      KML.latitude('12.219'),
      KML.heading('-60'),
      KML.tilt('70'),
      KML.range('6300'),
      GX.altitudeMode('relativeToSeaFloor'),
    ),
    KML.LineString(
      KML.extrude('1'),
      GX.altitudeMode('relativeToSeaFloor'),
      KML.coordinates(
      '146.825,12.233,400'
      '146.820,12.222,400'
      '146.812,12.212,400'
      '146.796,12.209,400'
      '146.788,12.205,400'
      ),
    ),
  ),
)
print etree.tostring(etree.ElementTree(doc),pretty_print=True

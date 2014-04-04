from lxml import etree
from pykml.factory import KML_ElementMaker as KML
from pykml.factory import ATOM_ElementMaker as ATOM
from pykml.factory import GX_ElementMaker as GX

fileout = open('googleearth.kml','w')
fileout.write('<?xml version="1.0" encoding="UTF-8"?>\n')
framenos = 10

midnight = datetime.datetime.combine( datetime.date.today(), datetime.time() )
seconds = datetime.timedelta( seconds=234 )
time = midnight + seconds
time.strftime( '%H:%M:%S' )

doc = KML.kml(
KML.Document(
KML.Folder()))

for i in range(1,framenos+1):
    doc.Document.Folder.append(
        KML.GroundOverlay(
            KML.TimeSpan(
                KML.begin('2013-10-02T00:00:00Z', time),
                KML.end('2013-10-02T00:01:00Z', time),
            ),
            KML.drawOrder(i)
        )
    )

fileout.write(etree.tostring(etree.ElementTree(doc),pretty_print=True))
#print etree.tostring(etree.ElementTree(doc),pretty_print=True)
fileout.close()







#ML.GroundOverlay(
# KML.TimeSpan(
#   KML.begin('2013-10-02T00:00:00Z'),
#   KML.end('2013-10-02T00:01:00Z'),
# ),
# KML.drawOrder('1'),
# KML.altitude('0.0'),
# KML.altitudeMode('clampToGround'),
# KML.Icon(
#   KML.href('frame0000fig0.png'),
# ),
# KML.LatLonBox(
#   KML.north('0.0'),
#   KML.south('-60.0'),
#   KML.east('-60'),
#   KML.west('-120'),
#   KML.rotation('0.0'),
# ),
# id="ID",

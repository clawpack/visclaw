# This file will create .kml file in example/_plots
# The kml will then be created, containing all data (placemarks, metadata, 
# images, etc.) to be loaded into Google Earth

pm1 = KML.Placemark(
    KML.name("Hello World!"),
    KML.Point(
        KML.coordinates("-64.5253,18.4607")
        )
    )

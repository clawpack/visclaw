
from bg_image import fetch_img

extent = [-123, -122, 47, 48.2] # Puget Sound
fname = 'test_fetch_img.jpg'
fetch_img(extent, fname, source='QuadtreeTiles', scale=None, figsize=None)

extent = [-122.45, -122.15, 47.5, 47.7] # Seattle
fname = 'test_fetch_img_map.jpg'
fetch_img(extent, fname, source='OSM', scale=None, figsize=None)

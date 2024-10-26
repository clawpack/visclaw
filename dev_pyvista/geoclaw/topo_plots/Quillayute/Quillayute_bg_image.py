"""
Fetch a background image for a specified extent.
"""

import sys

sys.path.insert(0,'..')
from bg_image import fetch_img

extent = [-124.66, -124.57, 47.9, 47.93]
fname = 'Quillayute_img.jpg'
fetch_img(extent, fname, source='QuadtreeTiles', scale=None, figsize=None)

if 0:
    fname = 'Quillayute_img_map.jpg'
    fetch_img(extent, fname, source='OSM', scale=None, figsize=None)

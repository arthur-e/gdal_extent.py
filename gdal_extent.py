'''
A command-line utility for getting the extent (bounds) of any raster as
Well-Known Text (WKT), GeoJSON, or other vector formats. Can be called from
the command line with a raster in a GDAL-supported format to produce a GeoJSON
Polygon string:

python gdal_extent.py path/to/some/raster.tiff
'''

import json
import sys
from osgeo import gdal, ogr

def get_min_max_extent(rast, as_string=False):
    '''
    Returns the minimum and maximum coordinate values in the sequence expected
    by, e.g., the `-te` switch in various GDAL utiltiies:
    (xmin, ymin, xmax, ymax).
    '''
    gt = rast.GetGeoTransform()
    xsize = rast.RasterXSize # Size in the x-direction
    ysize = rast.RasterYSize # Size in the y-direction
    xr = abs(gt[1]) # Resolution in the x-direction
    yr = abs(gt[-1]) # Resolution in the y-direction
    ext = [gt[0], gt[3] - (ysize * yr), gt[0] + (xsize * xr), gt[3]]

    if as_string:
        return ' '.join(map(str, ext))

    return ext


def get_rect_extent_as_sequence(rast):
    '''
    Returns the rectangular extent of the input raster as a sequence with
    four coordinate pairs, one for each corner starting with the upper-left
    and moving clockwise.
    '''
    gt = rast.GetGeoTransform()
    c = get_min_max_extent(rast)
    # Top-left, top-right, bottom-right, bottom-left
    return [(c[0], c[3]), (c[2], c[3]), (c[2], c[1]), (c[0], c[1])]


if __name__ == '__main__':
    ds = gdal.Open(sys.argv[1])
    ext = get_rect_extent_as_sequence(ds)

    # Repeat the last coordinate (for closure)
    ext.append(ext[0])

    result = {
        'coordinates': [ext],
        'type': 'Polygon'
    }

    print(json.dumps(result, sort_keys=False, indent=2))
    ds = None

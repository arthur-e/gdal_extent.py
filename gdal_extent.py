'''
A command-line utility for getting the extent (bounds) of any raster as
Well-Known Text (WKT), GeoJSON, or other vector formats.
'''

import json
import sys
from osgeo import gdal, ogr

def get_rect_extent_as_sequence(rast):
    '''
    Returns the rectangular extent of the input raster as a sequence with
    four coordinate pairs, one for each corner starting with the upper-left
    and moving clockwise.
    '''
    gt = rast.GetGeoTransform()
    xsize = ds.RasterXSize # Size in the x-direction
    ysize = ds.RasterYSize # Size in the y-direction
    xr = abs(gt[1]) # Resolution in the x-direction
    yr = abs(gt[-1]) # Resolution in the y-direction
    ext = [(gt[0], gt[3])] # Get the top-left corner coordinates
    ext.append((gt[0] + (xsize * xr), gt[3])) # Top-right
    ext.append((gt[0] + (xsize * xr), gt[3] - (ysize * yr))) # Bottom-right
    ext.append((gt[0], gt[3] - (ysize * yr))) # Bottom-left
    return ext

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

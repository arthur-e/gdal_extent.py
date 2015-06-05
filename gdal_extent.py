#!/usr/bin/env python

# A command-line utility for getting the extent (bounds) of any raster as
# Well-Known Text (WKT), GeoJSON, or other vector formats.

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


def get_rect_extent_as_geojson(rast):
    '''
    Returns the rectangular extent as GeoJSON Polygon string.
    '''
    ext = get_rect_extent_as_sequence(rast)

    # Repeat the last coordinate (for closure)
    ext.append(ext[0])

    result = {
        'coordinates': [ext],
        'type': 'Polygon'
    }

    return json.dumps(result, sort_keys=False, indent=2)


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


def get_width_height(rast, as_string=False):
    '''
    Returns the width and height of the raster, optionally as a string.
    '''
    if as_string:
        return ' '.join(map(str, (rast.RasterXSize, rast.RasterYSize)))

    return (rast.RasterXSize, rast.RasterYSize)


def display_usage():
    print('Usage: gdal_extent.py [-geojson|-size] input_files')
    print('')


def main(argv=None):
    if argv is None:
        argv = sys.argv

    argv = gdal.GeneralCmdLineProcessor(argv)
    names = [] # Filenames found
    func = get_min_max_extent # Function to call

    if argv is None:
        sys.exit(0)

    # Parse command line arguments.
    i = 1
    while i < len(argv):

        if argv[i] == '-geojson':
            func = get_rect_extent_as_geojson

        if argv[i] == '-size':
            func = get_width_height

        else:
            names.append(argv[i])

        i = i + 1

    if len(names) == 0:
        sys.stdout.write('No input files selected.')
        display_usage()
        sys.exit(1)

    # Execute the function for each filename
    for name in names:
        ds = gdal.Open(name)
        sys.stdout.write(func(ds, as_string=True))
        sys.stdout.write('\n')
        ds = None

    return 0


if __name__ == '__main__':
    sys.exit(main())

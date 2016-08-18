#!/usr/bin/env python

# A command-line utility for getting the extent (bounds) of any raster as
# Well-Known Text (WKT), GeoJSON, or other vector formats.

import argparse
import json
import sys
from osgeo import gdal, ogr

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # Default with no options/ switches: Report min/max bounds
        if message.find('unrecognized arguments') >= 0:
            main(sys.argv[1:], get_min_max_bounds)
            sys.exit(2)

        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)


def get_min_max_bounds(rast):
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
    return [gt[0], gt[3] - (ysize * yr), gt[0] + (xsize * xr), gt[3]]


def get_rect_extent(rast):
    '''
    Returns the rectangular extent as GeoJSON Polygon string.
    '''
    ext = get_rect_extent_as_sequence(rast)

    # Repeat the last coordinate (for closure)
    ext.append(ext[0])

    return {
        'coordinates': [ext],
        'type': 'Polygon'
    }


def get_rect_extent_as_sequence(rast):
    '''
    Returns the rectangular extent of the input raster as a sequence with
    four coordinate pairs, one for each corner starting with the upper-left
    and moving clockwise.
    '''
    gt = rast.GetGeoTransform()
    c = get_min_max_bounds(rast)
    # Top-left, top-right, bottom-right, bottom-left
    return [(c[0], c[3]), (c[2], c[3]), (c[2], c[1]), (c[0], c[1])]


def get_width_height(rast):
    '''
    Returns the width and height of the raster.
    '''
    return (rast.RasterXSize, rast.RasterYSize)


def stringify(sequence, sep=' '):
    return ' '.join(map(str, sequence))


def main(args, handler, as_json=False, indent=None):
    # Execute the function for each filename
    for name in args:
        ds = gdal.Open(name)

        # Write results to standard output
        if as_json:
            sys.stdout.write(json.dumps(handler(ds), sort_keys=False,
                indent=indent))

        else:
            sys.stdout.write(stringify(handler(ds)))

        sys.stdout.write('\n')
        ds = None


if __name__ == '__main__':
    parser = CustomArgumentParser(description='''
        A command-line tool for reporting the extent of GDAL datasets:
        [-b --bounds] returns the min-max bounds (xmin, ymin, xmax, ymax);
        [-e --extent] returns the rectangular extent as a GeoJSON polygon;
        [-s --size]   returns the width and height.
    ''')

    # Commands
    commands_group = parser.add_mutually_exclusive_group()
    commands_group.add_argument('-b', '--bounds', metavar='PATH',
        nargs='*', help='')
    commands_group.add_argument('-e', '--extent', metavar='PATH',
        nargs='*', help='')
    commands_group.add_argument('-s', '--size', metavar='PATH',
        nargs='*', help='')

    # Options
    parser.add_argument('-j', '--as-json', action='store_true',
        help='output GeoJSON')
    parser.add_argument('-i', '--indent', metavar='WIDTH', default=None,
        help='indentation for output GeoJSON', type=int)

    # If no arguments are supplied...
    if len(sys.argv) == 1:
        parser.print_usage()
        sys.exit(1)

    args = parser.parse_args()
    kwargs = {
        'as_json': args.as_json,
        'indent': args.indent
    }

    if args.bounds:
        main(args.bounds, get_min_max_bounds, **kwargs)

    elif args.extent:
        kwargs['as_json'] = True # Force JSON output
        main(args.extent, get_rect_extent, **kwargs)

    elif args.size:
        main(args.size, get_width_height, **kwargs)

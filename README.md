# gdal_extent.py

A command-line utility for getting the extent (bounds) of any raster as Well-Known Text (WKT), GeoJSON, or other vector formats.
It is intended to compliment the [library of GDAL utilities already available](gdal.org/gdal_utilities.html).

## Utilities

Default behavior at CLI; to get the rectangular extent of a raster in the format expected by other [GDAL utiltiies](http://www.gdal.org/gdal_utilities.html), e.g., the `-te` switch with `gdal_rasterize`:

```sh
$ ./gdal_extent.py Wayne_county.tiff
289965.0 4655115.0 346215.0 4701645.0
```

To get the width/height of a raster:

```sh
$ ./gdal_extent.py --size Wayne_county.tiff
1875 1551
```

To get a GeoJSON Polygon for the rectangular extent as a string, with 2 spaces for indentation:

```sh
$ ./gdal_extent.py --extent --as-json -i 2 Wayne_county.tiff
{
  "coordinates": [
    [
      [
        289965.0,
        4701645.0
      ],
      [
        346215.0,
        4701645.0
      ],
      [
        346215.0,
        4655115.0
      ],
      [
        289965.0,
        4655115.0
      ],
      [
        289965.0,
        4701645.0
      ]
    ]
  ],
  "type": "Polygon"
}
```

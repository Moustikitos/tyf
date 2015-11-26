http://bruno.thoorens.free.fr/img/tyf.png

# `Tyf`
[![pypi](https://img.shields.io/pypi/l/Tyf.svg?style=flat-square)](http://bruno.thoorens.free.fr/licences/Tyf.html)

[![pypi](https://img.shields.io/pypi/pyversions/Tyf.svg?style=flat-square)](https://pypi.python.org/pypi/Tyf)

[![pypi](https://img.shields.io/pypi/v/Tyf.svg?style=flat-square)](https://pypi.python.org/pypi/Tyf)
[![pypi](https://img.shields.io/pypi/dm/Tyf.svg?style=flat-square)](https://pypi.python.org/pypi/Tyf)
[![pypi](https://img.shields.io/badge/wheel-yes-brightgreen.svg?style=flat-square)](https://pypi.python.org/pypi/Tyf)

## Why this package ?
Tyf package provides pythonic way to view and edit Exif data from TIFF and JPEG files.

```python
>>> import Tyf
>>> jpg = Tyf.open(r".\IMG_20150730_210115.jpg")
>>> tif = Tyf.open(r".\CEA.tif")
>>> geotiff = Tyf.gkd.Gkd(tif[0])
>>> print(tif[0]["ImageWidth"])
514
>>> print(tif[0]["ShutterSpeedValue"])
7.0
>>> print(geotiff["GeographicTypeGeoKey"])
4267
```

## Contributing


## TODO

+ ``save`` method for JpegFile and TiffFile ``class``
+ overcast of __add__ and __radd__ operator of TiffFile ``class``
+ command line utility script

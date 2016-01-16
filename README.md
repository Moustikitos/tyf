# `Tyf`
[![pypi](https://img.shields.io/pypi/l/Tyf.svg?style=flat-square)](http://bruno.thoorens.free.fr/licences/tyf.html)

[![pypi](https://img.shields.io/pypi/pyversions/Tyf.svg?style=flat-square)](https://pypi.python.org/pypi/Tyf)

[![pypi](https://img.shields.io/pypi/v/Tyf.svg?style=flat-square)](https://pypi.python.org/pypi/Tyf)
[![pypi](https://img.shields.io/pypi/dm/Tyf.svg?style=flat-square)](https://pypi.python.org/pypi/Tyf)
[![pypi](https://img.shields.io/badge/wheel-yes-brightgreen.svg?style=flat-square)](https://pypi.python.org/pypi/Tyf)

[<img src="https://assets.gratipay.com/gratipay.svg?etag=3tGiSB5Uw_0-oWiLLxAqpQ~~" />](https://gratipay.com/Tyf)

## Why this package ?
Tyf package provides pythonic way to view Exif data from TIFF and JPEG files.

```python
>>> import Tyf
>>> jpg = Tyf.open(r".\IMG_20150730_210115.jpg")
>>> tif = Tyf.open(r".\CEA.tif")
>>> geotiff = Tyf.gkd.Gkd(tif[0])
>>> print(tif[0]["ImageWidth"])
514
>>> print(jpg["GPSLatitude"])
(51.2095416, 0.0, 0.0)
>>> print(geotiff["GeographicTypeGeoKey"])
4267
```

## Contributing
### Bug report & feedback
Use project issues.

### Add / modify / fix code
Guidance words: keep it simple and solid!

1. open a issue to propose your contribution
2. once issue is granted
  + fork this repository
  + edit your contribution
  + start a pull request

## TODO
+ command line utility script
+ API documentation

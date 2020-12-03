# `Tyf`

[![pypi](https://img.shields.io/pypi/l/Tyf.svg?style=flat-square)](http://bruno.thoorens.free.fr/licences/tyf.html)

[![pypi](https://img.shields.io/pypi/pyversions/Tyf.svg?style=flat-square)](https://pypi.python.org/pypi/Tyf)
[![pypi](https://img.shields.io/pypi/v/Tyf.svg?style=flat-square)](https://pypi.python.org/pypi/Tyf)
[![pypi](https://img.shields.io/badge/wheel-yes-brightgreen.svg?style=flat-square)](https://pypi.python.org/pypi/Tyf)

## Support this project

  * [X] Send &#1126; to `AUahWfkfr5J4tYakugRbfow7RWVTK35GPW`
  * [X] Vote `arky` on [Ark blockchain](https://explorer.ark.io) and [earn &#1126; weekly](http://arky-delegate.info/arky)

## Why this package ?
Tyf package provides pythonic way to work with embeded data in TIFF and JPEG images.

### Read / write EXIF and IFD data
 + read / edit EXIF data from JPEG images
 + read / edit IFD data from TIFF images
 + read / edit GEOTIFF data from IFD
 + read / edit XMP data from IFD
 + work directly with python numbers, string and datetime
 + interpolate coordinates using GEOTIFF ModelTransformation

### Do more with JPEG and TIFF files
 + split exif data from JPEG into different files
 + extract TIFF or JPEG thumbnails from JPEG files
 + strip EXIF data from JPEG File
 + dump location thumbnail using [mapbox API](https://docs.mapbox.com/api)

## Quick start
```python
>>> import Tyf
```

Tyf provide high level functions using EXIF data from JPEG images.

```python
>>> jpg = Tyf.open("test/IMG_20150730_210115.jpg")
>>> jpg.__class__
<class 'Tyf.JpegFile'>
>>> jpg.save_thumbnail("test_thumb") # extension automatically added
```

![EXIF thumbnail](https://raw.githubusercontent.com/Moustikitos/tyf/master/test/test_thumb.jpg)

There are 2 attributes to access data within ``Tif.JpegFile`` :
 + ``ifd0`` containing picture IFD, EXIF and eventually GPS data 
 + ``ifd1`` containing thubnail IFD data

``ifd0`` and ``ifd1`` are shortcut to the first and second
IFD in ``ifd`` attribute that is itself a ``Tyf.TiffFile``.

```python
>>> jpg.ifd[0] == jpg.ifd0
True
>>> jpg.ifd[1] == jpg.ifd1
True
>>> jpg.ifd.__class__
<class 'Tyf.TiffFile'>
>>> jpg.ifd0[256]
<IFD tag ImageWidth:2560>
>>> jpg.ifd0["ImageWidth"]
<IFD tag ImageWidth:2560>
>>> jpg.ifd0[256].value, jpg.ifd0[256].comment
(2560, 'Number of columns in the image, ie, the number of pixels per row')
>>> jpg.ifd0["GPSLongitude"].value
5.1872093
```

### ``Tyf.ifd.Ifd`` class

```python
>>> jpg.ifd0.__class__
<class 'Tyf.ifd.Ifd'>
>>> for tag in jpg.ifd0.tags(): print(tag)
...
<IFD tag ImageWidth:2560>
<IFD tag ImageLength:1920>
<IFD tag Make:'Google'>
<IFD tag Model:'Nexus S'>
<IFD tag Orientation:1>
<IFD tag Software:'KVT49L'>
<IFD tag DateTime:datetime.datetime(2015, 7, 30, 21, 1, 16)>
<IFD tag Artist:'THOORENS Bruno'>
<IFD tag YCbCrPositioning:1>
<IFD tag Copyright:'THOORENS Bruno'>
<IFD tag Exif IFD:2286>
<IFD tag GPS IFD:4754>
<IFD tag XPTitle:'Beautifull Rainbow'>
<IFD tag XPComment:'For testing purpose only !'>
<IFD tag XPAuthor:'THOORENS Bruno'>
<IFD tag XPKeywords:'Rainbow;Belgium'>
<IFD tag ExposureTime:0.008333333333333333>
<IFD tag FNumber:2.6>
<IFD tag ExposureProgram:3>
<IFD tag ISOSpeedRatings:50>
<IFD tag ExifVersion:b'0220'>
<IFD tag DateTimeOriginal:datetime.datetime(2015, 7, 30, 21, 1, 16)>
<IFD tag DateTimeDigitized:datetime.datetime(2015, 7, 30, 21, 1, 16)>
<IFD tag ShutterSpeedValue:7.0>
<IFD tag ApertureValue:3.0>
<IFD tag BrightnessValue:6.0>
<IFD tag ExposureBiasValue:0.0>
<IFD tag MaxApertureValue:3.0>
<IFD tag MeteringMode:2>
<IFD tag Flash:0>
<IFD tag FocalLength:3.43>
<IFD tag ColorSpace:1>
<IFD tag PixelXDimension:2560>
<IFD tag PixelYDimension:1920>
<IFD tag ExposureMode:0>
<IFD tag WhiteBalance:0>
<IFD tag SceneCaptureType:0>
<IFD tag GPSVersionID:(2, 2, 0, 0)>
<IFD tag GPSLatitudeRef:True>
<IFD tag GPSLatitude:51.2095416>
<IFD tag GPSLongitudeRef:True>
<IFD tag GPSLongitude:5.1872093>
<IFD tag GPSAltitudeRef:False>
<IFD tag GPSAltitude:0.0>
<IFD tag GPSTimeStamp:(19.0, 1.0, 7.0)>
<IFD tag GPSImgDirectionRef:'M'>
<IFD tag GPSImgDirection:33.0>
<IFD tag GPSProcessingMethod:b'ASCII\x00\x00\x00NETWORK'>
<IFD tag GPSDateStamp:'2015:07:30'>
>>> jpg.ifd0.get_location()
(5.1872093, 51.2095416, -0.0)
>>> jpg.ifd0.dump_location("test_location")
```

![5.1872093, 51.2095416](https://raw.githubusercontent.com/Moustikitos/tyf/master/test/test_location.png)

```python
>>> jpg.ifd0.set_location(4.362859, 48.958472, 0)
>>> jpg.ifd0.dump_location("test_location2")
```

![4.362859, 48.958472](https://raw.githubusercontent.com/Moustikitos/tyf/master/test/test_location2.png)

## Contribute
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
+ API documentation

## Changes

### 1.4.1
+ ``Ifd`` class rewrited
+ bugfix issue #7
+ bugfix issue #14
+ removed XMP support

### 1.3.2
+ ``JpegFile`` API change
+ ``JpegFile`` keeps XMP metadata as ``xml.etree.ElementTree.Element`` object
+ ``Ifd`` class manage to translate tags
+ added ``find`` and ``place`` method to ``Ifd`` class
+ encoders / decoders improvements

### 1.3.1
+ encoders / decoders bugfix
+ added ``__iter__`` to ``Ifd`` class

### 1.3.0
+ bugfix issue #10
+ sub ifd API change (sub ifd recursivity added)

### 1.2.5
+ bugfix issue #5
+ bugfix issue #6

### 1.2.4
+ added ``set_location`` and ``get_location`` to ``Ifd`` class

### 1.2.3
+ bugfix for ``Tyf.Image.save`` method
+ added ``__PY3__`` variable for verion testing

### 1.2.2
+ bugfix for ``Tyf.gkd.Gkd.to_ifd`` method

### 1.2.1
+ bugfix for issue #1

### 1.2.0
+ ``PIL`` (``pillow``) integration for JPEG images

### 1.1.3
+ added ``load_location`` & ``dump_location`` to ``Ifd`` class
+ added ``dump_exif`` & ``load_exif`` to ``JpegFile`` class

### 1.1.2
+ ``JpegFile`` class now handle JPEG and TIFF thumbnail
+ added ``save_thumbnail`` method for ``JpegFile`` class
+ ``TiffFile`` raster data loaded only if needed or on demand
+ added ``load_raster`` method for ``TiffFile`` class
+ ``_2`` encoder fix (ascii encoder)
+ code tweaks

### 1.1.1
+ added hability to read custom sub IFD
+ ``_5`` encoder fix (rational encoder)
+ ``__repr__`` format update
+ removed ``thumbnail`` property for ``JpegFile`` class

### 1.1b0
+ added encoders / decoders
+ added ``ifd1`` property to ``JpegFile`` class
+ added ``exif_ifd`` property to ``Ifd`` class
+ added ``gps_ifd`` property to ``Ifd`` class

### 1.0b1
+ fixed bug with Exif data modified by windows explorer
+ added XP tags

### 1.0b0
+ added ``gkd`` property for ``TiffFile`` class
+ added ``exif`` property for ``JpegFile`` class
+ read/write ifd and exif data
+ ``TiffFile`` concatenation using ``+`` operator (i.e. multi image ``TIFF`` file)

### 0.9a1
+ multiple IFD management with ``TiffFile`` class
+ added ``save`` method for ``JpegFile`` and ``TiffFile`` classes
+ full ``JPEG`` Exif read (IFD0 and IFD1 for ``0xffe1`` marker)
+ added ``thumbnail`` property for ``JpegFile`` class

### 0.8a4
+ first consistant release

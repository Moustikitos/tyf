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
 + work directly with python numbers, string and datetime

### Do more with JPEG and TIFF files
 + split exif data from JPEG into different files
 + extract TIFF or JPEG thumbnails from JPEG files
 + strip EXIF data from JPEG File
 + dump location thumbnail using google API
 + interpolate coordinates using GEOTIFF ModelTransformation

## Quick start
```python
>>> import Tyf
```

Tyf provide high level functions using EXIF data from JPEG images.

```python
>>> jpg = Tyf.open("IMG_20150730_210115.jpg")
>>> jpg.__class__
<class 'Tyf.JpegFile'>
>>> jpg.save_thumbnail("test_thumb") # .jpg or .tif extension automatically added
```

[EXIF thumbnail](https://raw.githubusercontent.com/Moustikitos/tyf/master/test/test_thumb.jpg)

There are 2 attributes to access data within ``Tif.JpegFile`` :
 + ``ifd0`` containing picture IFD and EXIF data 
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
```

### ``Tyf.ifd.Ifd`` class

```python
>>> jpg.ifd0.__class__
<class 'Tyf.ifd.Ifd'>
```

An Image File Directory (IFD) contains a serie of values identified by integers.

```python
>>> jpg.ifd0.get_location()
(5.1872093, 51.2095416, -0.0)
>>> jpg.ifd0.dump_location("test_location")
```

[5.1872093, 51.2095416](https://raw.githubusercontent.com/Moustikitos/tyf/master/test/test_location.png)

```python
>>> jpg.ifd0.set_location(4.362859, 48.958472, 0)
>>> jpg.ifd0.dump_location("test_location2")
```

![4.362859, 48.958472](https://raw.githubusercontent.com/Moustikitos/tyf/master/test/test_location2.png)

Nice !

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

### 1.3.2
+ ``JpegFile`` API change
+ ``JpegFile`` keeps XMP metadata as ``xml.etree.ElementTree.Element`` object
+ ``Ifd`` class manage to translate tags
+ added ``find`` and ``place`` method to ``Ifd`` class
+ encoders / decoders improvements

### 1.3.1
+ encoders / decoders bugfix
+ added ``__iter__`` to ``Ifd`` class
```python
>>> jpg = Tyf.open("test.jpg")
>>> for v in jpg.ifd0: print(v)
...
('ImageWidth', 2560)
('ImageLength', 1920)
[...]
('GPSProcessingMethod', b'NETWORK')
('GPSDateStamp', datetime.datetime(2015, 12, 29, 0, 0))
```

### 1.3.0
+ bugfix issue #10
+ sub ifd API change (sub ifd recursivity added)
```python
>>> jpg.ifd0
{256: <Tiff tag 0x100: ImageWidth = (2560,)>, 257: <Tiff tag 0x101: ImageLength = (1920,)>, 34853: <Tiff tag 0x8825: GPS IFD = (968,)>, 34665: <Tiff tag 0x8769: Exif IFD = (495,)>, 306: <Tiff tag 0x132: DateTime = b'2015:07:30 21:01:16\x00'>, 271: <Tiff tag 0x10f: Make = b'Google\x00'>, 272: <Tiff tag 0x110: Model = b'Nexus S\x00'>, 305: <Tiff tag 0x131: Software = b'KVT49L\x00'>, 274: <Tiff tag 0x112: Orientation = (1,)> :: Normal, 531: <Tiff tag 0x213: YCbCrPositioning = (1,)> :: Centered, 33432: <Tiff tag 0x8298: Copyright = b'Bruno THOORENS\x00'>, 40092: <Tiff tag 0x9c9c: XPComment = (83, 0, 105, 0, 109, 0, 112, 0, 108, 0, 101, 0, 32, 0, 99, 0, 111, 0, 109, 0, 109, 0, 101, 0, 110, 0, 116, 0, 97, 0, 105, 0, 114, 0, 101, 0, 32, 0, 101, 0, 110, 0, 32, 0, 97, 0, 115, 0, 99, 0, 105, 0, 105, 
0, 32, 0, 112, 0, 111, 0, 117, 0, 114, 0, 32, 0, 88, 0, 80, 0)>}
>>> jpg.ifd0.exif
{36864: <Exif tag 0x9000: ExifVersion = b'0220'>, 37377: <Exif tag 0x9201: ShutterSpeedValue = (70, 10)>, 37378: <Exif tag 0x9202: ApertureValue = (30, 10)>, 36867: <Exif tag 0x9003: DateTimeOriginal = b'2015:12:29 08:00:00\x00'>, 36868: <Exif tag 0x9004: DateTimeDigitized = b'2015:07:30 21:01:16\x00'>, 37381: <Exif tag 0x9205: MaxApertureValue = (30, 10)>, 37510: <Exif tag 0x9286: UserComment = b'ASCII\x00\x00\x00Simple commentaire en ascii'>, 37383: <Exif tag 0x9207: MeteringMode = (2,)> :: Center Weighted Average, 37385: <Exif tag 0x9209: Flash = (0,)> :: Flash did not fire, 37386: <Exif tag 0x920a: FocalLength = (343, 100)>, 41986: <Exif tag 0xa402: ExposureMode = (0,)> :: Auto exposure, 40963: <Exif tag 0xa003: PixelYDimension = (1920,)>, 37380: <Exif tag 0x9204: ExposureBiasValue = (0
, 0)>, 33434: <Exif tag 0x829a: ExposureTime = (1, 120)>, 33437: <Exif tag 0x829d: FNumber = (26, 10)>, 34850: <Exif tag 0x8822: ExposureProgram = (3,)> :: Aperture priority, 40961: <Exif tag 0xa001: ColorSpace = (1,)> :: RGB, 41990: <Exif tag 0xa406: SceneCaptureType = (0,)> :: Standard, 34855: <Exif tag 0x8827: ISOSpeedRatings = (50,)>, 41987: <Exif tag 0xa403: WhiteBalance = (0,)> :: Auto white balance, 37379: <Exif tag 0x9203: BrightnessValue = (60, 10)>, 40962: <Exif tag 0xa002: PixelXDimension = (2560,)>}
>>> jpg.ifd0.gps
{0: <GPS tag 0x0: GPSVersionID = (2, 2, 0, 0)>, 1: <GPS tag 0x1: GPSLatitudeRef = b'N\x00'> :: North latitude, 2: <GPS tag 0x2: GPSLatitude = (43, 1, 30, 1, 0, 1)>, 3: <GPS tag 0x3: GPSLongitudeRef = b'E\x00'> :: East longitude, 4: <GPS tag 0x4: GPSLongitude = (3, 1, 30, 1, 0, 1)>, 5: <GPS tag 0x5: GPSAltitudeRef = (1,)> :: Below sea level, 6: <GPS tag 0x6: GPSAltitude = (20, 1)>, 7: <GPS tag 0x7: GPSTimeStamp = (8, 1, 0, 1, 0, 1)>, 16: <GPS tag 0x10: GPSImgDirectionRef = b'M\x00'> :: Magnetic direction, 17: <GPS tag 0x11: GPSImgDirection = (33, 1)>, 27: <GPS tag 0x1b: GPSProcessingMethod = b'ASCII\x00\x00\x00NETWORK'>, 29: <GPS tag 0x1d: GPSDateStamp = b'2015:12:29\x00'>}
```

### 1.2.5
+ bugfix issue #5
+ bugfix issue #6

### 1.2.4
+ added ``set_location`` and ``get_location`` to ``Ifd`` class
```python
>>> from Tyf.ifd import Ifd
>>> ifd = Ifd()
>>> ifd.set_location(-4.362746, 48.958474, -152.2356)
>>> for tag in ifd.tags(): print(tag)
...
<GPS tag 0x1: GPSLatitudeRef = b'N\x00'> :: 'North latitude'
<GPS tag 0x2: GPSLatitude = (48, 1, 57, 1, 38133, 1250)>
<GPS tag 0x3: GPSLongitudeRef = b'W\x00'> :: 'West longitude'
<GPS tag 0x4: GPSLongitude = (4, 1, 21, 1, 57357, 1250)>
<GPS tag 0x5: GPSAltitudeRef = (1,)> :: 'Below sea level'
<GPS tag 0x6: GPSAltitude = (380589, 2500)>
>>> ifd.get_location()
(-4.362746, 48.958474, -152.2356)
```

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

Support this project
====================

.. image:: http://bruno.thoorens.free.fr/img/gratipay.png
   :target: https://gratipay.com/tyf

or

.. image:: http://bruno.thoorens.free.fr/img/bitcoin.png

3Jgib9SQiDLYML7QKBYtJUkHq2nyG6Z63D

Quick start
===========

>>> import Tyf

Tyf provide high level functions using EXIF data from JPEG images.

>>> jpg = Tyf.open("IMG_20150730_210115.jpg")
>>> jpg.__class__
<class 'Tyf.JpegFile'>
>>> jpg.save_thumbnail("test_thumb") # .jpg or .tif extension automatically added

.. image:: https://raw.githubusercontent.com/Moustikitos/tyf/master/test/test_thumb.jpg

``Tif.JpegFile`` class provides data access trough 3 major attributes :
 + ``ifd0`` containing picture IFD and EXIF data 
 + ``ifd1`` containing thubnail IFD data
 + ``xmp`` containing picture XMP data

``ifd0`` and ``ifd1`` are contained in ``ifd`` attributes that is itself a ``Tyf.TiffFile``

>>> jpg.ifd.__class__
<class 'Tyf.TiffFile'>
>>> jpg.ifd0.get_location()
(5.1872093, 51.2095416, -0.0)
>>> jpg.ifd0.dump_location("pypi_test_location", format="jpg", size="512x256")

.. image:: https://raw.githubusercontent.com/Moustikitos/tyf/master/test/pypi_test_location.jpg

``ifd0`` and ``ifd1`` handles data with two different ways :
 + pythonic way using ``__getitem__`` and ``__setitem__`` syntax
 + using ``Tyf.ifd.Tag`` class via ``get`` and ``append`` method

>>> jpg.ifd0.__class__
<class 'Tyf.ifd.Ifd'>
>>> jpg.ifd0[0x110]
'Nexus S'
>>> jpg.ifd0.get(0x110)
Tiff tag 0x110: Model = b'Nexus S\x00'
>>> tag = jpg.ifd0.get("Model") # same as jpg.ifd0.get(0x110)
>>> tag.digest("Kazaam Trooper")
>>> tag
Tiff tag 0x110: Model = b'Kazaam Trooper\x00'
>>> jpg.ifd0.append(tag)
>>> jpg.ifd0["Model"] # same as jpg.ifd0[0x110]
'Kazaam Trooper'
>>> jpg.ifd0["Model"] = "Kazaam Trooper L450"
>>> jpg.ifd0["Model"]
'Kazaam Trooper L450'

Let's save our modification and check it :

>>> jpg.save("test.jpg")
>>> jpg = Tyf.open("test.jpg")
>>> jpg.ifd0["Model"]
'Kazaam Trooper L450'

Nice ! Now have a look to ``ifd0`` in details :

>>> jpg.ifd0.gps
{16: GPS tag 0x10: GPSImgDirectionRef = b'M\x00' :: Magnetic direction, 1: GPS t
ag 0x1: GPSLatitudeRef = b'N\x00' :: North latitude, 2: GPS tag 0x2: GPSLatitude
 = (512095416, 10000000, 0, 1, 0, 1), 3: GPS tag 0x3: GPSLongitudeRef = b'E\x00'
 :: East longitude, 4: GPS tag 0x4: GPSLongitude = (51872093, 10000000, 0, 1, 0,
 1), 5: GPS tag 0x5: GPSAltitudeRef = (0,) :: Above sea level, 6: GPS tag 0x6: G
PSAltitude = (0, 100), 7: GPS tag 0x7: GPSTimeStamp = (19, 1, 1, 1, 7, 1), 17: G
PS tag 0x11: GPSImgDirection = (33, 1), 27: GPS tag 0x1b: GPSProcessingMethod = 
b'ASCII\x00\x00\x00NETWORK', 29: GPS tag 0x1d: GPSDateStamp = b'2015:07:30\x00'}
>>> jpg.ifd0.exif
{36864: Exif tag 0x9000: ExifVersion = b'0220', 37377: Exif tag 0x9201: ShutterS
peedValue = (70.0, 10.0), 37378: Exif tag 0x9202: ApertureValue = (30, 10), 3686
7: Exif tag 0x9003: DateTimeOriginal = b'2015:07:30 21:01:16\x00', 36868: Exif t
ag 0x9004: DateTimeDigitized = b'2015:07:30 21:01:16\x00', 37381: Exif tag 0x920
5: MaxApertureValue = (30, 10), 41990: Exif tag 0xa406: SceneCaptureType = (0,) 
:: Standard, 40961: Exif tag 0xa001: ColorSpace = (1,) :: RGB, 37385: Exif tag 0
x9209: Flash = (0,) :: Flash did not fire, 37386: Exif tag 0x920a: FocalLength =
 (343, 100), 41986: Exif tag 0xa402: ExposureMode = (0,) :: Auto exposure, 40963
: Exif tag 0xa003: PixelYDimension = (1920,), 37380: Exif tag 0x9204: ExposureBi
asValue = (0.0, 0.0), 33434: Exif tag 0x829a: ExposureTime = (1, 120), 59932: Ex
if tag 0xea1c: Padding = b'\x1c\xea\x00\x00\x00\x08\x00\x00\x00\x00\x00\x00\x1c\
xea\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
[...]
x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
x00\x00', 33437: Exif tag 0x829d: FNumber = (26, 10), 34850: Exif tag 0x8822: Ex
posureProgram = (3,) :: Aperture priority, 34855: Exif tag 0x8827: ISOSpeedRatin
gs = (50,), 41987: Exif tag 0xa403: WhiteBalance = (0,) :: Auto white balance, 3
7383: Exif tag 0x9207: MeteringMode = (2,) :: Center Weighted Average, 37379: Ex
if tag 0x9203: BrightnessValue = (60, 10), 40962: Exif tag 0xa002: PixelXDimensi
on = (2560,)}

``Tyf`` package provides simple way to view and edit Exif data from 
``TIFF`` and ``JPEG`` files.

Changes
=======

1.3.2

+ ``JpegFile`` API change
+ ``JpegFile`` keeps XMP metadata as ``xml.etree.ElementTree.Element`` object
+ ``Ifd`` class manage to translate tags
+ added ``find`` and ``place`` method to ``Ifd`` class
+ encoders / decoders improvements

1.3.1

+ encoders / decoders bugfix
+ added ``__iter__`` to ``Ifd`` class

>>> jpg = Tyf.open("test.jpg")
>>> for v in jpg.ifd0: print(v)
...
('ImageWidth', 2560)
('ImageLength', 1920)
[...]
('GPSProcessingMethod', b'NETWORK')
('GPSDateStamp', datetime.datetime(2015, 12, 29, 0, 0))

1.3.0

+ bugfix issue #10
+ sub ifd API change (sub ifd recursivity added)

>>> jpg.ifd0
{256: <Tiff tag 0x100: ImageWidth = (2560,)>, 257: <Tiff tag 0x101: ImageLength = (1920,)
>, 34853: <Tiff tag 0x8825: GPS IFD = (968,)>, 34665: <Tiff tag 0x8769: Exif IFD = (495,)
>, 306: <Tiff tag 0x132: DateTime = b'2015:07:30 21:01:16\x00'>, 271: <Tiff tag 0x10f: Ma
ke = b'Google\x00'>, 272: <Tiff tag 0x110: Model = b'Nexus S\x00'>, 305: <Tiff tag 0x131:
 Software = b'KVT49L\x00'>, 274: <Tiff tag 0x112: Orientation = (1,)> :: Normal, 531: <Ti
ff tag 0x213: YCbCrPositioning = (1,)> :: Centered, 33432: <Tiff tag 0x8298: Copyright = 
b'Bruno THOORENS\x00'>, 40092: <Tiff tag 0x9c9c: XPComment = (83, 0, 105, 0, 109, 0, 112,
 0, 108, 0, 101, 0, 32, 0, 99, 0, 111, 0, 109, 0, 109, 0, 101, 0, 110, 0, 116, 0, 97, 0, 
105, 0, 114, 0, 101, 0, 32, 0, 101, 0, 110, 0, 32, 0, 97, 0, 115, 0, 99, 0, 105, 0, 105, 
0, 32, 0, 112, 0, 111, 0, 117, 0, 114, 0, 32, 0, 88, 0, 80, 0)>}
>>> jpg.ifd0.exif
{36864: <Exif tag 0x9000: ExifVersion = b'0220'>, 37377: <Exif tag 0x9201: ShutterSpeedVa
lue = (70, 10)>, 37378: <Exif tag 0x9202: ApertureValue = (30, 10)>, 36867: <Exif tag 0x9
003: DateTimeOriginal = b'2015:12:29 08:00:00\x00'>, 36868: <Exif tag 0x9004: DateTimeDig
itized = b'2015:07:30 21:01:16\x00'>, 37381: <Exif tag 0x9205: MaxApertureValue = (30, 10
)>, 37510: <Exif tag 0x9286: UserComment = b'ASCII\x00\x00\x00Simple commentaire en ascii
'>, 37383: <Exif tag 0x9207: MeteringMode = (2,)> :: Center Weighted Average, 37385: <Exi
f tag 0x9209: Flash = (0,)> :: Flash did not fire, 37386: <Exif tag 0x920a: FocalLength =
 (343, 100)>, 41986: <Exif tag 0xa402: ExposureMode = (0,)> :: Auto exposure, 40963: <Exi
f tag 0xa003: PixelYDimension = (1920,)>, 37380: <Exif tag 0x9204: ExposureBiasValue = (0
, 0)>, 33434: <Exif tag 0x829a: ExposureTime = (1, 120)>, 33437: <Exif tag 0x829d: FNumbe
r = (26, 10)>, 34850: <Exif tag 0x8822: ExposureProgram = (3,)> :: Aperture priority, 409
61: <Exif tag 0xa001: ColorSpace = (1,)> :: RGB, 41990: <Exif tag 0xa406: SceneCaptureTyp
e = (0,)> :: Standard, 34855: <Exif tag 0x8827: ISOSpeedRatings = (50,)>, 41987: <Exif ta
g 0xa403: WhiteBalance = (0,)> :: Auto white balance, 37379: <Exif tag 0x9203: Brightness
Value = (60, 10)>, 40962: <Exif tag 0xa002: PixelXDimension = (2560,)>}
>>> jpg.ifd0.gps
{0: <GPS tag 0x0: GPSVersionID = (2, 2, 0, 0)>, 1: <GPS tag 0x1: GPSLatitudeRef = b'N\x00
'> :: North latitude, 2: <GPS tag 0x2: GPSLatitude = (43, 1, 30, 1, 0, 1)>, 3: <GPS tag 0
x3: GPSLongitudeRef = b'E\x00'> :: East longitude, 4: <GPS tag 0x4: GPSLongitude = (3, 1,
 30, 1, 0, 1)>, 5: <GPS tag 0x5: GPSAltitudeRef = (1,)> :: Below sea level, 6: <GPS tag 0
x6: GPSAltitude = (20, 1)>, 7: <GPS tag 0x7: GPSTimeStamp = (8, 1, 0, 1, 0, 1)>, 16: <GPS
 tag 0x10: GPSImgDirectionRef = b'M\x00'> :: Magnetic direction, 17: <GPS tag 0x11: GPSIm
gDirection = (33, 1)>, 27: <GPS tag 0x1b: GPSProcessingMethod = b'ASCII\x00\x00\x00NETWOR
K'>, 29: <GPS tag 0x1d: GPSDateStamp = b'2015:12:29\x00'>}

1.2.5

+ bugfix issue #5
+ bugfix issue #6

1.2.4

+ added ``set_location`` and ``get_location`` to ``Ifd`` class

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

1.2.3

+ bugfix for ``Tyf.Image.save`` method
+ added ``__PY3__`` variable for verion testing

1.2.2

+ bugfix for ``Tyf.gkd.Gkd.to_ifd`` method

1.2.1

+ bugfix for issue #1

1.2.0

+ ``PIL`` (``pillow``) integration for JPEG images

1.1.3

+ added ``load_location`` & ``dump_location`` to ``Ifd`` class
+ added ``dump_exif`` & ``load_exif`` to ``JpegFile`` class

1.1.2

+ ``JpegFile`` class now handle JPEG and TIFF thumbnail
+ added ``save_thumbnail`` method for ``JpegFile`` class
+ ``TiffFile`` raster data loaded only if needed or on demand
+ added ``load_raster`` method for ``TiffFile`` class
+ ``_2`` encoder fix (ascii encoder)
+ code tweaks

1.1.1

+ added hability to read custom sub IFD
+ ``_5`` encoder fix (rational encoder)
+ ``__repr__`` format update
+ removed ``thumbnail`` property for ``JpegFile`` class

1.1b0

+ added encoders / decoders
+ added ``ifd1`` property to ``JpegFile`` class
+ added ``exif_ifd`` property to ``Ifd`` class
+ added ``gps_ifd`` property to ``Ifd`` class

1.0b1

+ fixed bug with Exif data modified by windows explorer
+ added XP tags

1.0b0

+ added ``gkd`` property for ``TiffFile`` class
+ added ``exif`` property for ``JpegFile`` class
+ read/write ifd and exif data
+ ``TiffFile`` concatenation using ``+`` operator (i.e. multi image ``TIFF`` file)

0.9a1

+ multiple IFD management with ``TiffFile`` class
+ added ``save`` method for ``JpegFile`` and ``TiffFile`` classes
+ full ``JPEG`` Exif read (IFD0 and IFD1 for ``0xffe1`` marker)
+ added ``thumbnail`` property for ``JpegFile`` class

0.8a4

+ first consistant release

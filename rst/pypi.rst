``Tyf`` package provides simple way to view and edit Exif data from 
``TIFF`` and ``JPEG`` files.

Support this project
====================

.. image:: http://bruno.thoorens.free.fr/img/gratipay.png
   :target: https://gratipay.com/tyf

---

.. image:: http://bruno.thoorens.free.fr/img/bitcoin.png

1WJfDP1F2QTgqQhCT53KmhRwQSUkKRHgh

.. image:: http://bruno.thoorens.free.fr/img/wallet.png

Quick view
==========

>>> import Tyf

``TiffTag``
-----------

>>> tifftag = Tyf.ifd.TiffTag("GPSLongitude", value=3.5)
>>> tifftag
<Tiff tag 0x4: GPSLongitude = (3, 1, 30, 1, 0, 1)>
>>> tifftag.tag
4
>>> tifftag.type
5
>>> tifftag.count
3
>>> tifftag.value
(3, 1, 30, 1, 0, 1)
>>> tifftag._decode()
3.5

``Ifd``
-------

>>> from Tyf import tags
>>> ifd = Tyf.ifd.Ifd(sub_ifd={34853:[tags.gpsT,"GPS tag"],34665:[tags.exfT,"Exif tag"]})
>>> ifd["UserComment"] = "Simple commentaire"
>>> ifd["GPSLongitude"] = 3.5
>>> ifd["Copyright"] = "Bruno THOORENS"
>>> ifd
{33432: <Tiff tag 0x8298: Copyright = b'Bruno THOORENS\x00'>}
>>> ifd.gps_ifd
{4: <GPS tag 0x4: GPSLongitude = (3, 1, 30, 1, 0, 1)>}
>>> ifd.exif_ifd
{37510: <Exif tag 0x9286: UserComment = b'ASCII\x00\x00\x00Simple commentaire'>}

Thumbnail location can be dumped from google ``staticmap`` API if all latitude and longitude tags exists.

>>> ifd["GPSLatitude"] = ifd["GPSLatitudeRef"] = 48.958474
>>> ifd["GPSLongitude"] = ifd["GPSLongitudeRef"] = 4.362743
>>> ifd.dump_location("./pypi_test_location", format="jpg")

.. image:: https://raw.githubusercontent.com/Moustikitos/tyf/master/test/pypi_test_location.jpg

``to_buffer``
-------------

>>> from io import BytesIO as StringIO
>>> s = StringIO()
>>> Tyf.to_buffer(ifd, s, offset=0)
173
>>> s.getvalue()
b'\x03\x00\x98\x82\x02\x00\x0f\x00\x00\x00*\x00\x00\x00%\x88\x04\x00\x01\x00\x00\x00U\x00
\x00\x00\x86\x92\x07\x00\x1a\x00\x00\x009\x00\x00\x00\x00\x00\x00\x00Bruno THOORENS\x00AS
CII\x00\x00\x00Simple commentaire\x00\x00\x04\x00\x01\x00\x02\x00\x02\x00\x00\x00N\x00\x0
0\x00\x02\x00\x05\x00\x03\x00\x00\x00\x8b\x00\x00\x00\x03\x00\x02\x00\x02\x00\x00\x00E\x0
0\x00\x00\x04\x00\x05\x00\x03\x00\x00\x00\xa3\x00\x00\x00\x00\x00\x00\x000\x00\x00\x00\x0
1\x00\x00\x009\x00\x00\x00\x01\x00\x00\x00\xf5\x94\x00\x00\xe2\x04\x00\x00\x04\x00\x00\x0
0\x01\x00\x00\x00\x15\x00\x00\x00\x01\x00\x00\x00\xff\xbf\x01\x00\xc4\t\x00\x00'
>>> ifd # tags have been automaticaly added to localize SubIFD in main IFD data
{33432: <Tiff tag 0x8298: Copyright = b'Bruno THOORENS\x00'>, 34853: <Tiff tag 0x8825: GP
S IFD = (85,)>, 37510: <Tiff tag 0x9286: UserComment = b'ASCII\x00\x00\x00Simple commenta
ire'>}

``from_buffer``
---------------

>>> s.seek(0)
>>> ifd1 = Tyf.ifd.Ifd()
>>> Tyf.from_buffer(ifd1, s, offset=0)
0
>>> ifd1
{33432: <Tiff tag 0x8298: Copyright = b'Bruno THOORENS\x00'>, 34853: <Tiff tag 0x8825: GP
S IFD = (85,)>, 37510: <Tiff tag 0x9286: UserComment = b'ASCII\x00\x00\x00Simple commenta
ire'>}
>>> ifd1.gps_ifd
{1: <GPS tag 0x1: GPSLatitudeRef = b'N\x00'> := 'North latitude', 2: <GPS tag 0x2: GPSLat
itude = (48, 1, 57, 1, 38133, 1250)>, 3: <GPS tag 0x3: GPSLongitudeRef = b'E\x00'> := 'Ea
st longitude', 4: <GPS tag 0x4: GPSLongitude = (4, 1, 21, 1, 114687, 2500)>}
>>> ifd1.exif_ifd
{37510: <Exif tag 0x9286: UserComment = b'ASCII\x00\x00\x00Simple commentaire'>}
>>> ifd1["GPSLongitude"]
4.362743
>>> ifd1.get(0x4)
<GPS tag 0x4: GPSLongitude = (4, 1, 21, 1, 114687, 2500)>

``open``
--------

``Tyf`` package exports ``open`` function. It returns ``JpegFile`` or 
``TiffFile`` class that enables metadata reading and writing.

>>> import Tyf
>>> jpg = Tyf.open(r".\IMG_20150730_210115.jpg")
>>> tif = Tyf.open(r".\CEA.tif")
>>> isinstance(jpg, dict)
True
>>> isinstance(tif, list)
True

``JpegFile``
------------

``JpegFile`` class is an ordered dictionary mapping all marker found in ``JPEG`` file.
Values are stored as binary data except ``0xffe1`` one stored as a ``TiffFile``
instance. It contains two image file directories (IFD), one for the image and 
another one for the thumbnail.

>>> type(jpg[0xffe1])
<class 'Tyf.TiffFile'>
>>> len(jpg[0xffe1])
2
>>> jpg.exif # shortcut to jpg[0xffe1][0]
{256: <Tiff tag 0x100: ImageWidth = (2560,)>, 305: <Tiff tag 0x131: Software = b'KVT49L\x
00'>, 274: <Tiff tag 0x112: Orientation = (1,)> := 'Normal', 531: <Tiff tag 0x213: YCbCrP
ositioning = (1,)> := 'Centered', 34853: <Tiff tag 0x8825: GPS IFD = (572,)>, 257: <Tiff 
tag 0x101: ImageLength = (1920,)>, 34665: <Tiff tag 0x8769: Exif IFD = (176,)>, 306: <Tif
f tag 0x132: DateTime = b'2015:07:30 21:01:16\x00'>, 272: <Tiff tag 0x110: Model = b'Nexu
s S\x00'>, 271: <Tiff tag 0x10f: Make = b'Google\x00'>}
>>> jpg.ifd1 # shortcut to jpg[0xffe1][1]
{256: <Tiff tag 0x100: ImageWidth = (320,)>, 257: <Tiff tag 0x101: ImageLength = (240,)>,
 274: <Tiff tag 0x112: Orientation = (1,)> := 'Normal', 259: <Tiff tag 0x103: Compression
 = (6,)> := 'JPEG', 513: <Tiff tag 0x201: JPEGInterchangeFormat = (966,)>, 296: <Tiff tag
 0x128: ResolutionUnit = (2,)> := 'Inch', 282: <Tiff tag 0x11a: XResolution = (72, 1)>, 2
83: <Tiff tag 0x11b: YResolution = (72, 1)>, 514: <Tiff tag 0x202: JPEGInterchangeFormatL
ength = (9624,)>}

All information, including GPS and Exif IFD are available using ``.tags()`` 
method of its first item

>>> for tag in jpg.exif.tags(): print(tag)
...
<Tiff tag 0x100: ImageWidth = (2560,)>
<Tiff tag 0x101: ImageLength = (1920,)>
[...]
<GPS tag 0x1b: GPSProcessingMethod = b'ASCII\x00\x00\x00NETWORK'>
<GPS tag 0x1d: GPSDateStamp = b'2015:07:30\x00'>

JPEG or TIFF thumbnail embeded in JPEG file can be extracted into a single file

>>> jpg.save_thumbnail(".\test_thumb") # file extension will be appended automaticaly

.. image:: https://raw.githubusercontent.com/Moustikitos/tyf/master/test/test_thumb.jpg

``TiffFile``
------------

``TiffFile`` class is a list of IFD found in ``TIFF`` file or ``JPEG`` marker 
``0xffe1``. Each IFD is a dictionary containing tag-value pair.

>>> for tag in tif[0].tags(): print(tag)
...
<Tiff tag 0x100: ImageWidth = (514,)>
<Tiff tag 0x101: ImageLength = (515,)>
[...]
<Tiff tag 0x87b0: GeoDoubleParamsTag = (-117.333333333333, 33.75, 0.0, 0.0)>
<Tiff tag 0x87b1: GeoAsciiParamsTag = b'unnamed|NAD27|\x00'>

If asked (or needed), any raster data found will be loaded.

>>> tif.has_raster
True
>>> tif.raster_loaded
False
>>> tif.load_raster()
>>> tif.raster_loaded
True

Geotiff data can also be extracted from IFD.

>>> geotiff = tif.gkd
>>> for tag in geotiff[0].tags(): print(tag) # geotiff from the first ifd
...
<Geotiff Tag 0x400: GTModelTypeGeoKey = (1,)> := 'Projection Coordinate System'
<Geotiff Tag 0x401: GTRasterTypeGeoKey = (1,)> := 'Raster pixel is area'
[...]
<Geotiff Tag 0xc0a: ProjFalseEastingGeoKey = (0.0,)>
<Geotiff Tag 0xc0b: ProjFalseNorthingGeoKey = (0.0,)>
>>> mt = geotiff[0].getModelTransformation()
>>> mt(50, 50) # compute pixel coordinates
(-25492.059935252837, 4252883.436953031, 0.0, 1.0)

Changes
=======

0.8a4

+ first consistant release

0.9a1

+ multiple IFD management with ``TiffFile`` class
+ added ``save`` method for ``JpegFile`` and ``TiffFile`` classes
+ full ``JPEG`` Exif read (IFD0 and IFD1 for ``0xffe1`` marker)
+ added ``thumbnail`` property for ``JpegFile`` class

1.0b0

+ added ``gkd`` property for ``TiffFile`` class
+ added ``exif`` property for ``JpegFile`` class
+ read/write ifd and exif data
+ ``TiffFile`` concatenation using ``+`` operator (i.e. multi image ``TIFF`` file)

1.0b1

+ fixed bug with Exif data modified by windows explorer
+ added XP tags

1.1b0

+ added encoders / decoders
+ added ``ifd1`` to ``JpegFile`` class
+ added ``exif_ifd`` to ``Ifd`` class
+ added ``gps_ifd`` to ``Ifd`` class

1.1.1

+ added hability to read custom sub IFD
+ rational encoder fix
+ ``__repr__`` format update
+ removed ``thumbnail`` property for ``JpegFile`` class

1.1.2

+ ``JpegFile`` class now handle JPEG and TIFF thumbnail
+ added ``save_thumbnail`` method for ``JpegFile`` class
+ ``TiffFile`` raster data loaded only if needed or on demand
+ added ``load_raster`` method for ``TiffFile`` class
+ ``_2`` encoder fix
+ code tweaks

Todo
====

+ command line scripts
+ API documentation

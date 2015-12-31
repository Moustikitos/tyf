``Tyf`` package provides simple way to view and edit (beta) Exif data from 
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

``Tyf`` package exports ``open`` function. It returns ``JpegFile`` or 
``TiffFile`` class that enables metadata reading and writing(soon).

>>> import Tyf
>>> jpg = Tyf.open(r".\IMG_20150730_210115.jpg")

https://raw.githubusercontent.com/Moustikitos/tyf/master/test/IMG_20150730_210115.jpg

>>> tif = Tyf.open(r".\CEA.tif")

https://github.com/Moustikitos/tyf/blob/master/test/CEA.tif?raw=true

>>> type(jpg)
<class 'Tyf.JpegFile'>
>>> isinstance(jpg, dict)
True
>>> type(tif)
<class 'Tyf.TiffFile'>
>>> isinstance(tif, list)
True

``JpegFile`` class is an ordered dictionary mapping all marker found in ``JPEG`` file.
Values are stored as binary data except ``0xffe1`` one stored as a  ``TiffFile``
instance. It contains two image file directories (IFD), one for the image and 
another one for the thumbnail.

>>> type(jpg[0xffe1])
<class 'Tyf.TiffFile'>
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

``TiffFile`` class is a list of IFD found in ``TIFF`` file or ``JPEG`` marker 
``0xffe1``. Each IFD is a dictionary containing tag-value pair and raster data 
if any is found.

>>> for tag in tif[0].tags(): print(tag)
...
<Tiff tag 0x100: ImageWidth = (514,)>
<Tiff tag 0x101: ImageLength = (515,)>
[...]
<Tiff tag 0x87b0: GeoDoubleParamsTag = (-117.333333333333, 33.75, 0.0, 0.0)>
<Tiff tag 0x87b1: GeoAsciiParamsTag = b'unnamed|NAD27|\x00'>

Geotiff data can also be extracted from IFD.

>>> geotiff = tif.gkd[0] # geotiff from the first ifd
>>> for tag in geotiff.tags(): print(tag)
...
<Geotiff Tag 0x400: GTModelTypeGeoKey = (1,)> := 'Projection Coordinate System'
<Geotiff Tag 0x401: GTRasterTypeGeoKey = (1,)> := 'Raster pixel is area'
[...]
<Geotiff Tag 0xc0a: ProjFalseEastingGeoKey = (0.0,)>
<Geotiff Tag 0xc0b: ProjFalseNorthingGeoKey = (0.0,)>
>>> mt = geotiff.getModelTransformation()
>>> mt(50, 50) # compute pixel coordinates
(-25492.059935252837, 4252883.436953031, 0.0, 1.0)

Changes
=======

0.8a4

+ first consistant release

>>> tif[0]["ImageWidth"]
514
>>> tif[0, "ImageWidth"]
514
>>> geotiff["ProjNatOriginLongGeoKey"]
-117.333333333333
>>> jpg["GPSLatitudeRef"]
b'N'
>>> jpg["GPSLatitude"]
51.2095416

0.9a1

+ multiple IFD management with ``TiffFile`` class
+ added ``save`` method for ``JpegFile`` and ``TiffFile`` classes
+ full ``JPEG`` Exif read (IFD0 and IFD1 for ``0xffe1`` marker)
+ added ``thumbnail`` property for ``JpegFile`` class

>>> # simple way to extract JPEG thumbnail
>>> out = open(r".\test_thumb.jpg", "wb")
>>> out.write(jpg.thumbnail)
>>> out.close()

.. image:: https://raw.githubusercontent.com/Moustikitos/tyf/master/test/test_thumb.jpg
   :align: center

1.0b0

+ added ``gkd`` property for ``TiffFile`` class
+ added ``exif`` property for ``JpegFile`` class
+ read/write ifd and exif data

>>> tif[0]["Copyright"] = b"Simple commentaire en ascii"
>>> tif[0]["UserComment"] = b"ASCII\x00\x00\x00Simple commentaire en ascii"

+ ``TiffFile`` concatenation using ``+`` operator (i.e. multi image ``TIFF`` file)

>>> tif2 = Tyf.open(r".\SP27GTIF.tif")

https://github.com/Moustikitos/tyf/blob/master/test/SP27GTIF.TIF?raw=true

>>> tif += tif2
>>> tif.save(r".\test.tif")

https://github.com/Moustikitos/tyf/blob/master/test/test.tif?raw=true

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

Todo
====

+ command line utility script
+ API documentation

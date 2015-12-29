``Tyf`` package provides simple way to view and edit (beta) Exif data from ``TIFF``
and ``JPEG`` files.

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

``Tyf`` package exports ``open`` function. It returns ``JpegFile`` or ``TiffFile`` class that enables metadata reading and writing(soon).

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

``JpegFile`` class is an ordered dictionary mapping all marker found in ``JPEG`` file. Values are stored as binary data except ``0xffe1`` one stored as a ``TiffFile`` instance. It contains two image file directories (IFD), one for the image and another one for the thumbnail.

>>> type(jpg[0xffe1])
<class 'Tyf.TiffFile'>
>>> jpg.exif # shortcut to jpg[0xffe1][0]
{256: <Tiff tag : ImageWidth (0x100) = 2560>, 257: <Tiff tag : ImageLength (0x101) = 192
0>, 34853: <Tiff tag : GPS IFD (0x8825) = 572>, 34665: <Tiff tag : Exif IFD (0x8769) = 1
76>, 306: <Tiff tag : DateTime (0x132) = 2015:07:30 21:01:16>, 271: <Tiff tag : Make (0x
10f) = Google>, 272: <Tiff tag : Model (0x110) = Nexus S>, 305: <Tiff tag : Software (0x
131) = KVT49L>, 274: <Tiff tag : Orientation (0x112) = 1> :: "Normal", 531: <Tiff tag : 
YCbCrPositioning (0x213) = 1> :: "Centered"}
>>> jpg.ifd1 # shortcut to jpg[0xffe1][1]
{256: <Tiff tag : ImageWidth (0x100) = 320>, 257: <Tiff tag : ImageLength (0x101) = 240>,
 514: <Tiff tag : JPEGInterchangeFormatLength (0x202) = 9624>, 259: <Tiff tag : Compressi
on (0x103) = 6> :: "JPEG", 513: <Tiff tag : JPEGInterchangeFormat (0x201) = 966>, 296: <T
iff tag : ResolutionUnit (0x128) = 2> :: "Inch", 274: <Tiff tag : Orientation (0x112) = 1
> :: "Normal", 282: <Tiff tag : XResolution (0x11a) = 72.0>, 283: <Tiff tag : YResolution
 (0x11b) = 72.0>}

All information, including GPS and Exif IFD are available using ``.tags()`` method of its first item

>>> for tag in jpg.exif.tags(): print(tag)
...
<Tiff tag : ImageWidth (0x100) = 2560>
<Tiff tag : ImageLength (0x101) = 1920>
<Tiff tag : Make (0x10f) = Google>
<Tiff tag : Model (0x110) = Nexus S>
<Tiff tag : Orientation (0x112) = 1> :: "Normal"
[...]
<GPS tag : GPSTimeStamp (0x7) = (19.0, 1.0, 7.0)>
<GPS tag : GPSImgDirectionRef (0x10) = M> :: "Magnetic direction"
<GPS tag : GPSImgDirection (0x11) = 33.0>
<GPS tag : GPSProcessingMethod (0x1b) = NETWORK>
<GPS tag : GPSDateStamp (0x1d) = 2015:07:30>

``TiffFile`` class is a list of IFD found in ``TIFF`` file or ``JPEG`` marker ``0xffe1``.
Each IFD is a dictionary containing tag-value pair and raster data if any is found.

>>> for tag in tif[0].tags(): print(tag)
...
<Tiff tag : ImageWidth (0x100) = 514>
<Tiff tag : ImageLength (0x101) = 515>
<Tiff tag : BitsPerSample (0x102) = 8>
<Tiff tag : Compression (0x103) = 1> :: "Uncompressed"
<Tiff tag : PhotometricInterpretation (0x106) = 1> :: "BlackIsZero"
[...]
<Tiff tag : ModelPixelScaleTag (0x830e) = (60.02213698319374, 60.02213698319374, 0.0)>
<Tiff tag : ModelTiepointTag (0x8482) = (0.0, 0.0, 0.0, -28493.166784412522, 4255884.5438
021915, 0.0)>
<Tiff tag : GeoKeyDirectoryTag (0x87af) = (1, 1, 0, 14, 1024, 0, 1, 1, 1025, 0, 1, 1, 102
6, 34737, 8, 0, 2048, 0, 1, 4267, 2049, 34737, 6, 8, 2054, 0, 1, 9102, 3072, 0, 1, 32767,
 3074, 0, 1, 32767, 3075, 0, 1, 28, 3076, 0, 1, 9001, 3078, 34736, 1, 1, 3080, 34736, 1, 
0, 3082, 34736, 1, 2, 3083, 34736, 1, 3)>
<Tiff tag : GeoDoubleParamsTag (0x87b0) = (-117.333333333333, 33.75, 0.0, 0.0)>
<Tiff tag : GeoAsciiParamsTag (0x87b1) = b'unnamed|NAD27|'>

Geotiff data can also be extracted from IFD.

>>> geotiff = tif.gkd[0] # geotiff from the first ifd
>>> for tag in geotiff.tags(): print(tag)
...
<GeoTiff Tag : GTModelTypeGeoKey (0x400) = 1> :: "Projection Coordinate System"
<GeoTiff Tag : GTRasterTypeGeoKey (0x401) = 1> :: "Raster pixel is area"
<GeoTiff Tag : GTCitationGeoKey (0x402) = b'unnamed'>
<GeoTiff Tag : GeographicTypeGeoKey (0x800) = 4267> :: "GCS_NAD27"
<GeoTiff Tag : GeogCitationGeoKey (0x801) = b'NAD27'>
<GeoTiff Tag : GeogAngularUnitsGeoKey (0x806) = 9102> :: "Degree"
<GeoTiff Tag : ProjectedCSTypeGeoKey (0xc00) = 32767> :: "User-defined"
<GeoTiff Tag : ProjectionGeoKey (0xc02) = 32767> :: "User-defined"
<GeoTiff Tag : ProjCoordTransGeoKey (0xc03) = 28> :: "User-defined"
<GeoTiff Tag : ProjLinearUnitsGeoKey (0xc04) = 9001> :: "Linear_Meter"
<GeoTiff Tag : ProjStdParallel1GeoKey (0xc06) = 33.75>
<GeoTiff Tag : ProjNatOriginLongGeoKey (0xc08) = -117.333333333333>
<GeoTiff Tag : ProjFalseEastingGeoKey (0xc0a) = 0.0>
<GeoTiff Tag : ProjFalseNorthingGeoKey (0xc0b) = 0.0>
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

Todo
====

+ command line utility script
+ API documentation
Support this project
====================

.. image:: http://bruno.thoorens.free.fr/img/gratipay.png
   :target: https://gratipay.com/tyf

---

.. image:: http://bruno.thoorens.free.fr/img/bitcoin.png

3Jgib9SQiDLYML7QKBYtJUkHq2nyG6Z63D

Quick view
==========

>>> import Tyf

``Tag``
-------

>>> import Tyf
>>> t = Tyf.ifd.Tag("GPSLongitude")
>>> t.digest(4.362743)
>>> t
<Orphan tag 0x4: GPSLongitude = (4, 1, 21, 1, 114687, 2500)>
>>> t = Tyf.ifd.Tag("GPSLongitude", value=4.362743)
>>> t
<Orphan tag 0x4: GPSLongitude = (4, 1, 21, 1, 114687, 2500)>
>>> t.type
5
>>> t.count
3
>>> t.value
(4, 1, 21, 1, 114687, 2500)
>>> t.decode()
4.362743
>>> t = Tyf.ifd.Tag("KeyTest")
<Orphan tag 0x0: Undefined = ''>

``Ifd``
-------

>>> from Tyf import tags
>>> ifd = Tyf.ifd.Ifd(tag_family=[tags.bTT, tags.xTT, tags.pTT])
>>> ifd["Copyright"] = "Bruno THOORENS"
>>> ifd
>>> ifd
{33432: <Tiff tag 0x8298: Copyright = b'Bruno THOORENS\x00'>}
>>> gps_ifd = ifd["GPS IFD"] # create "GPS IFD" sub ifd in ifd
>>> gps_ifd.append(t)
>>> gps_ifd # t is no more orphan
{4: <GPS tag 0x4: GPSLongitude = (4, 1, 21, 1, 114687, 2500)>}
>>> gps_ifd["GPSLongitudeRef"] = gps_ifd["GPSLongitude"]
>>> gps_ifd["GPSLatitude"] = gps_ifd["GPSLatitudeRef"] = 48.958474
>>> gps_ifd
{1: <GPS tag 0x1: GPSLatitudeRef = b'N\x00'> :: North latitude, 2: <GPS tag 0x2: GPSLatit
ude = (48, 1, 57, 1, 38133, 1250)>, 3: <GPS tag 0x3: GPSLongitudeRef = b'E\x00'> :: East 
longitude, 4: <GPS tag 0x4: GPSLongitude = (4, 1, 21, 1, 114687, 2500)>}
>>> ifd.dump_location("./pypi_test_location", format="jpg", size="512x256")

.. image:: https://raw.githubusercontent.com/Moustikitos/tyf/master/test/pypi_test_location.jpg

Thumbnail location can be dumped from google ``staticmap`` API if all latitude and longitude tags exist.

>>> for tag in ifd.tags(): print(tag)
...
<Tiff tag 0x8298: Copyright = b'Bruno THOORENS\x00'>
<Tiff tag 0x8825: GPS IFD = (0,)>
<GPS tag 0x1: GPSLatitudeRef = b'N\x00'> :: North latitude
<GPS tag 0x2: GPSLatitude = (48, 1, 57, 1, 38133, 1250)>
<GPS tag 0x3: GPSLongitudeRef = b'E\x00'> :: East longitude
<GPS tag 0x4: GPSLongitude = (4, 1, 21, 1, 114687, 2500)>

``to_buffer``
-------------

>>> from io import BytesIO as StringIO
>>> s = StringIO()
>>> Tyf.to_buffer(ifd, s, offset=0)
195
>>> s.getvalue()
b'\x02\x00\x98\x82\x02\x00\x0f\x00\x00\x00\x1e\x00\x00\x00%\x88\x04\x00\x01\x00\x00\x00-\
x00\x00\x00\x00\x00\x00\x00Bruno THOORENS\x00\x04\x00\x01\x00\x02\x00\x02\x00\x00\x00N\x0
0\x00\x00\x02\x00\x05\x00\x03\x00\x00\x00c\x00\x00\x00\x03\x00\x02\x00\x02\x00\x00\x00E\x
00\x00\x00\x04\x00\x05\x00\x03\x00\x00\x00{\x00\x00\x00\x00\x00\x00\x000\x00\x00\x00\x01\
x00\x00\x009\x00\x00\x00\x01\x00\x00\x00\xf5\x94\x00\x00\xe2\x04\x00\x00\x04\x00\x00\x00\
x01\x00\x00\x00\x15\x00\x00\x00\x01\x00\x00\x00\xff\xbf\x01\x00\xc4\t\x00\x00'

``from_buffer``
---------------

>>> s.seek(0)
0
>>> ifd1 = Tyf.ifd.Ifd(tag_family=[tags.bTT, tags.xTT, tags.pTT])
>>> Tyf.from_buffer(ifd1, s, offset=0)
0
>>> ifd1
{33432: <Tiff tag 0x8298: Copyright = b'Bruno THOORENS\x00'>, 34853: <Tiff tag 0x8825: GP
S IFD = (45,)>}
>>> ifd1.gps_ifd
{1: <GPS tag 0x1: GPSLatitudeRef = b'N\x00'> :: 'North latitude', 2: <GPS tag 0x2: GPSLat
itude = (48, 1, 57, 1, 38133, 1250)>, 3: <GPS tag 0x3: GPSLongitudeRef = b'E\x00'> :: 'Ea
st longitude', 4: <GPS tag 0x4: GPSLongitude = (4, 1, 21, 1, 114687, 2500)>}
>>> for tag in ifd1.tags(): print(tag)
...
<Tiff tag 0x8298: Copyright = b'Bruno THOORENS\x00'>
<Tiff tag 0x8825: GPS IFD = (45,)>
<GPS tag 0x1: GPSLatitudeRef = b'N\x00'> :: North latitude
<GPS tag 0x2: GPSLatitude = (48, 1, 57, 1, 38133, 1250)>
<GPS tag 0x3: GPSLongitudeRef = b'E\x00'> :: East longitude
<GPS tag 0x4: GPSLongitude = (4, 1, 21, 1, 114687, 2500)>
>>> ifd1["GPS IFD"]["GPSLongitude"]
4.362743

``open``
--------

``Tyf`` package exports ``open`` function. It returns ``JpegFile`` or 
``TiffFile`` class that enables metadata reading and writing.

>>> import Tyf
>>> jpg = Tyf.open(r".\IMG_20150730_210115.jpg")
>>> tif = Tyf.open(r".\CEA.tif")
>>> isinstance(jpg, list)
True
>>> isinstance(tif, list)
True

``JpegFile``
------------

``JpegFile`` class is an list mapping all marker found in ``JPEG`` file.
Values are stored as binary data except ``0xffe1`` one stored as a ``TiffFile``
instance or a ``xml.etree.ElementTree.Element`` object (XMP data).

>>> type(jpg.ifd)
<class 'Tyf.TiffFile'>
>>> len(jpg.ifd)
2
>>> jpg.ifd0 # shortcut to jpg.ifd[0]
{256: <Tiff tag 0x100: ImageWidth = (2560,)>, 305: <Tiff tag 0x131: Software = b'KVT49L\x
00'>, 274: <Tiff tag 0x112: Orientation = (1,)> :: Normal, 531: <Tiff tag 0x213: YCbCrPos
itioning = (1,)> :: Centered, 34853: <Tiff tag 0x8825: GPS IFD = (572,)>, 257: <Tiff tag 
0x101: ImageLength = (1920,)>, 34665: <Tiff tag 0x8769: Exif IFD = (176,)>, 306: <Tiff ta
g 0x132: DateTime = b'2015:07:30 21:01:16\x00'>, 272: <Tiff tag 0x110: Model = b'Nexus S\
x00'>, 271: <Tiff tag 0x10f: Make = b'Google\x00'>}
>>> jpg.ifd1 # shortcut to jpg.ifd[1]
{256: <Tiff tag 0x100: ImageWidth = (320,)>, 257: <Tiff tag 0x101: ImageLength = (240,)>,
 274: <Tiff tag 0x112: Orientation = (1,)> :: Normal, 259: <Tiff tag 0x103: Compression =
 (6,)> :: JPEG, 513: <Tiff tag 0x201: JPEGInterchangeFormat = (966,)>, 296: <Tiff tag 0x1
28: ResolutionUnit = (2,)> :: Inch, 282: <Tiff tag 0x11a: XResolution = (72, 1)>, 283: <T
iff tag 0x11b: YResolution = (72, 1)>, 514: <Tiff tag 0x202: JPEGInterchangeFormatLength 
= (9624,)>}
>>>jpg.xmp
<Element '{adobe:ns:meta/}xmpmeta' at 0x3307a90>

All information, including GPS and Exif IFD are available using ``.tags()`` 
method of its first item

>>> for tag in jpg.ifd0.tags(): print(tag)
...
<Tiff tag 0x100: ImageWidth = (2560,)>
<Tiff tag 0x101: ImageLength = (1920,)>
[...]
<GPS tag 0x1b: GPSProcessingMethod = b'ASCII\x00\x00\x00NETWORK'>
<GPS tag 0x1d: GPSDateStamp = b'2015:07:30\x00'>

JPEG or TIFF thumbnail embeded in JPEG file can be extracted into a single file

>>> jpg.save_thumbnail(".\test_thumb") # file extension will be appended automaticaly

.. image:: https://raw.githubusercontent.com/Moustikitos/tyf/master/test/test_thumb.jpg

And because ``JpegFile.ifd0`` is actually a shortcut to a ``Tyf.ifd.Ifd`` instance :

>>> jpg.ifd0.dump_location("./pypi_test_location1", format="jpg")

.. image:: https://raw.githubusercontent.com/Moustikitos/tyf/master/test/pypi_test_location1.jpg

``TiffFile``
------------

``TiffFile`` class is a list of IFD found in ``TIFF`` file. Each IFD is a dictionary
containing tag-value pair.

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
<Geotiff Tag 0x400: GTModelTypeGeoKey = (1,)> :: Projection Coordinate System
<Geotiff Tag 0x401: GTRasterTypeGeoKey = (1,)> :: Raster pixel is area
<Geotiff Tag 0x402: GTCitationGeoKey = b'unnamed'>
<Geotiff Tag 0x800: GeographicTypeGeoKey = (4267,)> :: NAD27
[...]
<Geotiff Tag 0xc0a: ProjFalseEastingGeoKey = (0.0,)>
<Geotiff Tag 0xc0b: ProjFalseNorthingGeoKey = (0.0,)>
>>> mt = geotiff[0].getModelTransformation()
>>> mt(50, 50) # compute pixel coordinates
(-25492.059935252837, 4252883.436953031, 0.0, 1.0)

``PIL`` integration
-------------------

>>> from Tyf import Image
>>> img = Tyf.Image.open(r".\IMG_20150730_210115.jpg")
>>> img
<PIL.JpegImagePlugin.JpegImageFile image mode=RGB size=2560x1920 at 0x32B26B0>
>>> exf = img._getexif()
>>> exf
[{256: <Tiff tag 0x100: ImageWidth = (2560,)>, 305: <Tiff tag 0x131: Software = b'KVT49L\
x00'>, 274: <Tiff tag 0x112: Orientation = (1,)> :: Normal, 531: <Tiff tag 0x213: YCbCrPo
sitioning = (1,)> :: Centered, 34853: <Tiff tag 0x8825: GPS IFD = (572,)>, 257: <Tiff tag
 0x101: ImageLength = (1920,)>, 34665: <Tiff tag 0x8769: Exif IFD = (176,)>, 306: <Tiff t
ag 0x132: DateTime = b'2015:07:30 21:01:16\x00'>, 272: <Tiff tag 0x110: Model = b'Nexus S
\x00'>, 271: <Tiff tag 0x10f: Make = b'Google\x00'>}, {256: <Tiff tag 0x100: ImageWidth =
 (320,)>, 257: <Tiff tag 0x101: ImageLength = (240,)>, 274: <Tiff tag 0x112: Orientation 
= (1,)> :: Normal, 259: <Tiff tag 0x103: Compression = (6,)> :: JPEG, 513: <Tiff tag 0x20
1: JPEGInterchangeFormat = (966,)>, 296: <Tiff tag 0x128: ResolutionUnit = (2,)> :: Inch,
 282: <Tiff tag 0x11a: XResolution = (72, 1)>, 283: <Tiff tag 0x11b: YResolution = (72, 1
)>, 514: <Tiff tag 0x202: JPEGInterchangeFormatLength = (9624,)>}]
>>> exf.__class__
<class 'Tyf.TiffFile'>
>>> exf[0]["UserComment"] = "Simple commentaire"
>>> exf[0]["Copyright"] = "Bruno THOORENS"
>>> img.save(r".\test.jpg", ifd=exf) # write JPEG image with exif

Quick start
===========

>>> import Tyf

Tyf provide high level functions using EXIF data from JPEG images.

>>> jpg = Tyf.open("IMG_20150730_210115.jpg")
>>> jpg.__class__
<class 'Tyf.JpegFile'>
>>> jpg.save_thumbnail("test_thumb") # .jpg or .tif extension automatically added

.. image:: https://raw.githubusercontent.com/Moustikitos/tyf/master/test/test_thumb.jpg

There are 3 attributes to access data within ``Tif.JpegFile`` :
 + ``ifd0`` containing picture IFD and EXIF data 
 + ``ifd1`` containing thubnail IFD data
 + ``xmp`` containing picture XMP data

``ifd0`` and ``ifd1`` are shortcut to the first and second
IFD in ``ifd`` attribute that is itself a ``Tyf.TiffFile``.

>>> jpg.ifd[0] == jpg.ifd0
True
>>> jpg.ifd[1] == jpg.ifd1
True
>>> jpg.ifd.__class__
<class 'Tyf.TiffFile'>

``xmp`` is a ``xml.etree.ElementTree.Element`` object parsed from XMP data found in
JPEG file.

>>> jpg.xmp.__class__
<class 'xml.etree.ElementTree.Element'>

``Tyf.ifd.Ifd`` class
---------------------

>>> jpg.ifd0.__class__
<class 'Tyf.ifd.Ifd'>

An Image File Directory (IFD) contains a serie of values identified by integers.

>>> jpg.ifd0.get_location()
(5.1872093, 51.2095416, -0.0)
>>> jpg.ifd0.dump_location("pypi_test_location", format="jpg", size="512x256")

.. image:: https://raw.githubusercontent.com/Moustikitos/tyf/master/test/pypi_test_location.jpg

>>> jpg.ifd0.set_location(4.362859, 48.958472, 0)
>>> jpg.ifd0.dump_location("pypi_test_location2", format="jpg", size="512x256")

.. image:: https://raw.githubusercontent.com/Moustikitos/tyf/master/test/pypi_test_location2.jpg

``ifd0`` and ``ifd1`` handle data with two different ways :
 + pythonic way using ``__getitem__`` and ``__setitem__`` syntax
 + using ``Tyf.ifd.Tag`` class via ``get`` and ``append`` method

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
>>> jpg.ifd0.get_location()
(4.362859, 48.958472, -0.0)
>>> jpg.ifd0["Model"]
'Kazaam Trooper L450'

Nice !

Support this project
====================

.. image:: http://bruno.thoorens.free.fr/img/gratipay.png
   :target: https://gratipay.com/tyf

or

.. image:: http://bruno.thoorens.free.fr/img/bitcoin.png

3Jgib9SQiDLYML7QKBYtJUkHq2nyG6Z63D


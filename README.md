# `Tyf`
## Copyright
[![pypi](https://img.shields.io/pypi/l/Tyf.svg)](https://htmlpreview.github.io/?https://github.com/Moustikitos/tyf/blob/master/tyf.html)

## Distribution
[![pypi](https://img.shields.io/pypi/pyversions/Tyf.svg)](https://pypi.python.org/pypi/Tyf)
[![pypi](https://img.shields.io/pypi/v/Tyf.svg)](https://pypi.python.org/pypi/Tyf)
[![pypi](https://img.shields.io/badge/wheel-yes-brightgreen.svg)](https://pypi.python.org/pypi/Tyf)
[![Downloads](https://pepy.tech/badge/Tyf/week)](https://pepy.tech/project/tyf)

## Support this project
[![Liberapay receiving](https://img.shields.io/liberapay/goal/Toons?logo=liberapay)](https://liberapay.com/Toons/donate)

[Buy &#1126;](https://bittrex.com/Account/Register?referralCode=NW5-DQO-QMT) and:

 + [X] Send &#1126; to `AUahWfkfr5J4tYakugRbfow7RWVTK35GPW`
 + [X] Vote `arky` on [Ark blockchain](https://explorer.ark.io) and [earn &#1126; weekly](http://dpos.arky-delegate.info/arky)

## Why this package ?
Tyf package provides pythonic way to work with embeded data in TIFF and JPEG images.

## Documentation
[The Tyf Project [WIP]](https://moustikitos.github.io/tyf/)

### Read / write EXIF and IFD data
 + read / edit EXIF data from JPEG images
 + read / edit IFD data from TIFF images
 + read / edit GEOTIFF data from IFD
 + read / edit XMP data from IFD and JPEG images
 + work directly with python numbers, string and datetime
 + interpolate map coordinates using GEOTIFF ModelTransformation

### Do more with JPEG and TIFF files
 + extract TIFF or JPEG thumbnails from JPEG files
 + dump EXIF data from JPEG into file
 + dump location thumbnail using any map provider API

## Quick view
```python
>>> import Tyf
>>> jpg = Tyf.open("test/IMG_20150730_210115.jpg")
>>> jpg.__class__
<class 'Tyf.JpegFile'>
>>> print(Tyf.xmp.tostring(jpg.xmp).decode()) 
<ns0:xmpmeta
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:ns0="adobe:ns:meta/" xmlns:ns3="http://ns.adobe.com/xap/1.0/"
 xmlns:ns4="http://ns.microsoft.com/photo/1.0/"
 xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"><rdf:RDF>
<rdf:Description rdf:about="uuid:faf5bdd5-ba3d-11da-ad31-d33d75182f1b">
<dc:title><rdf:Alt><rdf:li xml:lang="x-default">Beautifull Rainbow</rdf:li>
</rdf:Alt></dc:title><dc:description><rdf:Alt>
<rdf:li xml:lang="x-default">Beautifull Rainbow</rdf:li></rdf:Alt>
</dc:description><dc:creator><rdf:Seq><rdf:li>THOORENS Bruno</rdf:li>
</rdf:Seq></dc:creator><dc:rights><rdf:Alt>
<rdf:li xml:lang="x-default">THOORENS Bruno</rdf:li></rdf:Alt></dc:rights>
</rdf:Description>
<rdf:Description rdf:about="uuid:faf5bdd5-ba3d-11da-ad31-d33d75182f1b" />
<rdf:Description rdf:about="uuid:faf5bdd5-ba3d-11da-ad31-d33d75182f1b">
<ns3:Rating>4</ns3:Rating></rdf:Description>
<rdf:Description rdf:about="uuid:faf5bdd5-ba3d-11da-ad31-d33d75182f1b">
<ns4:Rating>75</ns4:Rating><ns4:LastKeywordXMP><rdf:Bag>
<rdf:li>Rainbow</rdf:li><rdf:li>Belgium</rdf:li></rdf:Bag>
</ns4:LastKeywordXMP></rdf:Description>
<rdf:Description rdf:about="uuid:faf5bdd5-ba3d-11da-ad31-d33d75182f1b">
<dc:subject><rdf:Bag><rdf:li>Rainbow</rdf:li><rdf:li>Belgium</rdf:li></rdf:Bag>
</dc:subject></rdf:Description>
</rdf:RDF></ns0:xmpmeta>
>>> jpg.save_thumbnail("test/test_thumb") # extension automatically added
```

![EXIF thumbnail](https://raw.githubusercontent.com/Moustikitos/tyf/master/test/test_thumb.jpg)

There are 3 attributes to access data within `Tyf.JpegFile` :

+ ``ifd0`` containing picture IFD, EXIF and eventually GPS data 
+ ``ifd1`` containing thubnail data
+ ``xmp`` containing XMP data

`ifd0` and `ifd1` are shortcut to the first and second IFD in `ifd` attribute which is itself a `Tyf.TiffFile`.

```python
>>> jpg.ifd[0] == jpg.ifd0
True
>>> jpg.ifd[1] == jpg.ifd1
True
>>> jpg.ifd.__class__
<class 'Tyf.TiffFile'>
>>> jpg.ifd0[256]
2560
>>> jpg.ifd0["ImageWidth"]
2560
>>> jpg.ifd0[256], jpg.ifd0.get("ImageWidth").comment
(2560, 'Number of columns in the image, ie, the number of pixels per row')
>>> jpg.ifd0["GPSLongitude"]
5.1872093
```

### `Tyf.ifd.Ifd` class

```python
>>> jpg.ifd0.__class__
<class 'Tyf.ifd.Ifd'>
>>> for tag in jpg.ifd0.tags(): print(tag)
...
<IFD tag ImageWidth:2560>
<IFD tag ImageLength:1920>
<IFD tag Make:'Google'>
<IFD tag Model:'Nexus S'>
<IFD tag Orientation:1 - Normal>
<IFD tag Software:'KVT49L'>
<IFD tag DateTime:datetime.datetime(2015, 7, 30, 21, 1, 16)>
<IFD tag Artist:'THOORENS Bruno'>
<IFD tag YCbCrPositioning:1 - Centered>
<IFD tag Copyright:'THOORENS Bruno'>
<IFD tag Exif IFD:2286>
<IFD tag GPS IFD:4754>
<IFD tag XPTitle:'Beautifull Rainbow'>
<IFD tag XPComment:'For testing purpose only !'>
<IFD tag XPAuthor:'THOORENS Bruno'>
<IFD tag XPKeywords:'Rainbow;Belgium'>
<IFD tag ExposureTime:0.008333333333333333>
<IFD tag FNumber:2.6>
<IFD tag ExposureProgram:3 - Aperture priority>
<IFD tag ISOSpeedRatings:50>
<IFD tag ExifVersion:b'0220'>
<IFD tag DateTimeOriginal:datetime.datetime(2015, 7, 30, 21, 1, 16)>
<IFD tag DateTimeDigitized:datetime.datetime(2015, 7, 30, 21, 1, 16)>
<IFD tag ShutterSpeedValue:7.0>
<IFD tag ApertureValue:3.0>
<IFD tag BrightnessValue:6.0>
<IFD tag ExposureBiasValue:0.0>
<IFD tag MaxApertureValue:3.0>
<IFD tag MeteringMode:2 - Center Weighted Average>
<IFD tag Flash:0 - Flash did not fire>
<IFD tag FocalLength:3.43>
<IFD tag ColorSpace:1 - RGB>
<IFD tag PixelXDimension:2560>
<IFD tag PixelYDimension:1920>
<IFD tag ExposureMode:0 - Auto exposure>
<IFD tag WhiteBalance:0 - Auto white balance>
<IFD tag SceneCaptureType:0 - Standard>
<IFD tag GPSVersionID:(2, 2, 0, 0)>
<IFD tag GPSLatitudeRef:'N'>
<IFD tag GPSLatitude:51.2095416>
<IFD tag GPSLongitudeRef:'E'>
<IFD tag GPSLongitude:5.1872093>
<IFD tag GPSAltitudeRef:0 - Above sea level>
<IFD tag GPSAltitude:0.0>
<IFD tag GPSTimeStamp:datetime.time(19, 1, 7)>
<IFD tag GPSImgDirectionRef:'M'>
<IFD tag GPSImgDirection:33.0>
<IFD tag GPSProcessingMethod:b'ASCII\x00\x00\x00NETWORK'>
<IFD tag GPSDateStamp:datetime.date(2015, 7, 30)>
>>> jpg.ifd0.get("Orientation").info
'Normal'
>>> jpg.ifd0.get_location()
(5.1872093, 51.2095416, -0.0)
>>> from Tyf import ifd
>>> ifd.dump_mapbox_location(jpg.ifd0, "test/test_location.png")
```

![5.1872093, 51.2095416](https://raw.githubusercontent.com/Moustikitos/tyf/master/test/test_location.png)

```python
>>> jpg.ifd0.set_location(4.362859, 48.958472, 0)
>>> ifd.dump_mapbox_location(jpg.ifd0, "test/test_location2.png")
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

# `Tyf`

[![pypi](https://img.shields.io/pypi/l/Tyf.svg)](https://htmlpreview.github.io/?https://github.com/Moustikitos/tyf/blob/master/tyf.html)
[![pypi](https://img.shields.io/pypi/pyversions/Tyf.svg)](https://pypi.python.org/pypi/Tyf)
[![pypi](https://img.shields.io/pypi/v/Tyf.svg)](https://pypi.python.org/pypi/Tyf)
[![pypi](https://img.shields.io/badge/wheel-yes-brightgreen.svg)](https://pypi.python.org/pypi/Tyf)
[![Downloads](https://pepy.tech/badge/Tyf/week)](https://pepy.tech/project/tyf)

## Support this project

[![Liberapay receiving](https://img.shields.io/liberapay/goal/Toons?logo=liberapay)](https://liberapay.com/Toons/donate)

## Why this package ?

Tyf package provides pythonic way to work with embeded data in TIFF and JPEG images.

## Documentation

[The Tyf Project [WIP]](https://moustikitos.github.io/tyf/)

### Read / write EXIF and IFD data

+ read / edit EXIF and XMP data from JPEG images
+ read / edit IFD and XMP data from TIFF images
+ read / edit / use GEOTIFF data from IFD
+ work directly with python types

### Do more with JPEG and TIFF files

+ extract TIFF or JPEG thumbnails from JPEG files
+ dump EXIF data from JPEG into file
+ dump location thumbnail using any map provider API

## Quick view

```python
>>> import Tyf
>>> tif = Tyf.open("test/CEA.tif")
>>> tif.__class__
<class 'Tyf.TiffFile'>
>>> for key in tif.gkd[0]: print(key)
... 
<GKD tag GTModelTypeGeoKey:(1,) - Projection Coordinate System>
<GKD tag GTRasterTypeGeoKey:(1,) - Raster pixel is area>
<GKD tag GTCitationGeoKey:b'unnamed'>
<GKD tag GeographicTypeGeoKey:(4267,) - NAD27>
<GKD tag GeogCitationGeoKey:b'NAD27'>
<GKD tag GeogAngularUnitsGeoKey:(9102,) - degree>
<GKD tag ProjectedCSTypeGeoKey:(32767,) - User-defined>
<GKD tag ProjectionGeoKey:(32767,) - User-defined>
<GKD tag ProjCoordTransGeoKey:(28,) - User-defined>
<GKD tag ProjLinearUnitsGeoKey:(9001,) - metre>
<GKD tag ProjStdParallel1GeoKey:(33.75,)>
<GKD tag ProjNatOriginLongGeoKey:(-117.333333333333,)>
<GKD tag ProjFalseEastingGeoKey:(0.0,)>
<GKD tag ProjFalseNorthingGeoKey:(0.0,)>
>>> tr = tif[0].getModelTransformation()
>>> tr(tif[0]["ImageWidth"]/2, tif[0]["ImageLength"]/2) 
(-13067.47757973173, 4240428.8435290195, 0.0)
>>> jpg = Tyf.open("test/IMG_20150730_210115.jpg")
unknown tag 18246 type [7]: <IFD tag Undefined:4> ignored
unknown tag 18249 type [7]: <IFD tag Undefined:75> ignored
>>> jpg.__class__
<class 'Tyf.JpegFile'>
>>> jpg["XPComment"]
<IFD tag XPComment:'For testing purpose only !'>
>>> jpg.xmp
<Element '{adobe:ns:meta/}xmpmeta' at 0x000001D6A2404130>
>>> jpg.get_xmp("Rating", ns="ADOBE").text
'4'
>>> jpg.set_xmp("UserComment", "Simple comment") 
<Element '{http://ns.adobe.com/exif/1.0/}UserComment' at 0x000001D6A24062F0>
>>> jpg.get_xmp("UserComment").text 
'Simple comment'
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

``Tyf`` package provides simple way to view and edit (future) Exif data from ``TIFF``
and ``JPEG`` files.

Quick view
==========

``Tyf`` package exports ``open`` function. It returns ``JpegFile`` or ``TiffFile`` class that enables metadata reading and writing(soon).

>>> import Tyf
>>> jpg = Tyf.open(r".\IMG_20150730_210115.jpg")
>>> tif = Tyf.open(r".\CEA.tif")
>>> type(jpg)
<class 'Tyf.JpegFile'>
>>> isinstance(tif, dict)
True
>>> type(tif)
<class 'Tyf.TiffFile'>
>>> isinstance(tif, list)
True

``JPEG`` files
==============

``JpegFile`` class is a python ``dict`` object of all marker contained in the ``JPEG`` file. The exif marker (``0xffd1``) is decoded to a tiff-like image file directory and handleable through ``ifd`` attribute. ``JpegFile.__getitem__`` allows direct access to ``ifd`` attribute.

>>> jpg.ifd[0x9201]
7.0
>>> jpg.ifd["ShutterSpeedValue"]
7.0
>>> jpg["ShutterSpeedValue"]
7.0

See all tags contained in a single ``JPEG`` file :

>>> for tag in jpg.ifd.values(): print(tag)
... 
<GPS tag : GPSVersionID (0x0) = (0, 0, 0, 0)>
<GPS tag : GPSLatitudeRef (0x1) = b'N'> :: "North latitude"
<GPS tag : GPSLatitude (0x2) = (51.2095416, 0.0, 0.0)>
<GPS tag : GPSLongitudeRef (0x3) = b'E'> :: "East longitude"
<GPS tag : GPSLongitude (0x4) = (5.1872093, 0.0, 0.0)>
<GPS tag : GPSAltitudeRef (0x5) = 0> :: "Above sea level"
<GPS tag : GPSAltitude (0x6) = 0.0>
<GPS tag : GPSTimeStamp (0x7) = (19.0, 1.0, 7.0)>
<GPS tag : GPSImgDirectionRef (0x10) = b'M'> :: "Magnetic direction"
<GPS tag : GPSImgDirection (0x11) = 33.0>
<GPS tag : GPSProcessingMethod (0x1b) = b'ASCII\x00\x00\x00NETWORK'>
<GPS tag : GPSDateStamp (0x1d) = b'2015:07:30'>
<Tiff tag : ImageWidth (0x100) = 2560>
<Tiff tag : ImageLength (0x101) = 1920>
<Tiff tag : Make (0x10f) = b'Google'>
<Tiff tag : Model (0x110) = b'Nexus S'>
<Tiff tag : Orientation (0x112) = 1> :: "Normal"
<Tiff tag : Software (0x131) = b'KVT49L'>
<Tiff tag : DateTime (0x132) = b'2015:07:30 21:01:16'>
<Tiff tag : YCbCrPositioning (0x213) = 1> :: "Centered"
<Exif tag : ExposureTime (0x829a) = 0.008333333333333333>
<Exif tag : FNumber (0x829d) = 2.6>
<Tiff tag : Exif IFD (0x8769) = 176>
<Exif tag : ExposureProgram (0x8822) = 3> :: "Aperture priority"
<Tiff tag : GPS IFD (0x8825) = 572>
<Exif tag : ISOSpeedRatings (0x8827) = 50>
<Exif tag : ExifVersion (0x9000) = b'0220'>
<Exif tag : DateTimeOriginal (0x9003) = b'2015:07:30 21:01:16'>
<Exif tag : DateTimeDigitized (0x9004) = b'2015:07:30 21:01:16'>
<Exif tag : ShutterSpeedValue (0x9201) = 7.0>
<Exif tag : ApertureValue (0x9202) = 3.0>
<Exif tag : BrightnessValue (0x9203) = 6.0>
<Exif tag : ExposureBiasValue (0x9204) = 0.0>
<Exif tag : MaxApertureValue (0x9205) = 3.0>
<Exif tag : MeteringMode (0x9207) = 2> :: "Center Weighted Average"
<Exif tag : Flash (0x9209) = 0> :: "Flash did not fire"
<Exif tag : FocalLength (0x920a) = 3.43>
<Exif tag : UserComment (0x9286) = b'\x00\x00\x00IICSAUser comments\x00'>
<Exif tag : ColorSpace (0xa001) = 1>
<Exif tag : PixelXDimension (0xa002) = 2560>
<Exif tag : PixelYDimension (0xa003) = 1920>
<Exif tag : ExposureMode (0xa402) = 0> :: "Auto exposure"
<Exif tag : WhiteBalance (0xa403) = 0> :: "Auto white balance"
<Exif tag : SceneCaptureType (0xa406) = 0> :: "Standard"

``TIFF`` files
==============

``TiffTile`` class is a python ``list`` object of all image file directories contained in the ``TIFF`` file.

>>> tif[0][0x100]
514 
>>> tif[0]["ImageWidth"]
514
>>> tif[0,"ImageWidth"] # beautifull !
514
>>> type(tif)
<class 'Tyf.TiffFile'>
>>> isinstance(tif, list)
True

See all tags contained in the first image file directory of a ``TIFF`` file :

>>> for tag in sorted(tif[0].values(), key=lambda v:v.tag): print(tag)
<Tiff tag : ImageWidth (0x100) = 514>
<Tiff tag : ImageLength (0x101) = 515>
<Tiff tag : BitsPerSample (0x102) = 8>
<Tiff tag : Compression (0x103) = 1> :: "Uncompressed"
<Tiff tag : PhotometricInterpretation (0x106) = 1> :: "BlackIsZero"
<Tiff tag : StripOffsets (0x111) = (426, 8136, 15846, 23556, 31266, 38976, 46686, 54396, 62106, 69816, 77526, 85236, 92946, 100656, 108366, 116076, 123786, 131496, 139206, 146916, 154626, 162336, 170046, 177756, 185466, 193176, 200886, 208596, 216306, 224016, 231726, 239436, 247146, 254856, 262566)>
<Tiff tag : SamplesPerPixel (0x115) = 1>
<Tiff tag : RowsPerStrip (0x116) = 15>
<Tiff tag : StripByteCounts (0x117) = (7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710, 7710)>
<Tiff tag : PlanarConfiguration (0x11c) = 1> :: "Chunky"
<Tiff tag : SampleFormat (0x153) = 1> :: "Unsigned integer data"
<Tiff tag : ModelPixelScaleTag (0x830e) = (60.02213698319374, 60.02213698319374, 0.0)>
<Tiff tag : ModelTiepointTag (0x8482) = (0.0, 0.0, 0.0, -28493.166784412522, 4255884.5438021915, 0.0)>
<Tiff tag : GeoKeyDirectoryTag (0x87af) = (1, 1, 0, 14, 1024, 0, 1, 1, 1025, 0, 1, 1, 1026, 34737, 8, 0, 2048, 0, 1, 4267, 2049, 34737, 6, 8, 2054, 0, 1, 9102, 3072, 0, 1, 32767, 3074, 0, 1, 32767, 3075, 0, 1, 28, 3076, 0, 1, 9001, 3078, 34736, 1, 1, 3080, 34736, 1, 0, 3082, 34736, 1, 2, 3083, 34736, 1, 3)>
<Tiff tag : GeoDoubleParamsTag (0x87b0) = (-117.333333333333, 33.75, 0.0, 0.0)>
<Tiff tag : GeoAsciiParamsTag (0x87b1) = b'unnamed|NAD27|'>

You may extract geotiff data :

>>> geotiff = Tyf.gkd.Gkd(tif[0])
>>> mt = geotiff.getModelTransformation()
>>> mt(50, 50) # coordiantes of the 50th col - 50th row pixel
(-25492.059935252837, 4252883.436953031, 0.0, 1.0)
>>> for tag in geotiff.values(): print(tag)
...
<GeoTiff Tag : GTModelTypeGeoKey (0x400) = 1> :: "Projection Coordinate System"
<GeoTiff Tag : GTRasterTypeGeoKey (0x401) = 1> :: "Raster pixel is area"
<GeoTiff Tag : GTCitationGeoKey (0x402) = b'unnamed'>
<GeoTiff Tag : ProjCoordTransGeoKey (0xc03) = 28> :: "User-defined"
<GeoTiff Tag : ProjLinearUnitsGeoKey (0xc04) = 9001> :: "Linear_Meter"
<GeoTiff Tag : ProjStdParallel1GeoKey (0xc06) = 33.75>
<GeoTiff Tag : GeogAngularUnitsGeoKey (0x806) = 9102> :: "Degree"
<GeoTiff Tag : GeogCitationGeoKey (0x801) = b'NAD27'>
<GeoTiff Tag : ProjNatOriginLongGeoKey (0xc08) = -117.333333333333>
<GeoTiff Tag : ProjFalseEastingGeoKey (0xc0a) = 0.0>
<GeoTiff Tag : ProjectedCSTypeGeoKey (0xc00) = 32767> :: "User-defined"
<GeoTiff Tag : ProjectionGeoKey (0xc02) = 32767> :: "User-defined"
<GeoTiff Tag : ProjFalseNorthingGeoKey (0xc0b) = 0.0>
<GeoTiff Tag : GeographicTypeGeoKey (0x800) = 4267> :: "GCS_NAD27"
>>> geotiff[0x800]
4267
>>> geotiff["GeographicTypeGeoKey"]
4267

Changes
=======

0.8a4

+ first consistant release

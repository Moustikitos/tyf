<a id="Tyf"></a>

# Tyf

__Bibliography__

 + [Tiff 6.0 spec](https://www.itu.int/itudoc/itu-t/com16/tiff-fx/docs/tiff6.pdf)
 + [GeoTiFF 1.8.1 spec](https://htmlpreview.github.io/?https://github.com/OSGeo/libgeotiff/blob/master/geotiff/html/spec/geotiff2.6.html)
 + [JPEG FIF 1.02 spec](https://www.w3.org/Graphics/JPEG/jfif3.pdf)
 + [XMP spec](https://developer.adobe.com/xmp/docs/XMPSpecifications/)

Tyf package aims to provide pythonic way to interact with metadata in TIFF and
JPEG files.

```python
>>> import Tyf
```

<a id="Tyf.open"></a>

#### open

```python
def open(f)
```

Return `JpegFile` or `TiffFile` instance according to argument.

**Arguments**:

- `f` _buffer or string_ - a valid file path or a python file object.
  

**Returns**:

- `Tyf.JpegFile|Tyf.TiffFile` - JPEG or TIFF instance.

<a id="Tyf.TiffFile"></a>

## TiffFile Objects

```python
class TiffFile(list)
```

This class is is a list of all Image File Directories defining the TIFF
file.

**Arguments**:

- `fileobj` _buffer_ - a python file object.
  
```python
>>> tif = Tyf.open("test/CEA.tif")
>>> tif[0]["BitsPerSample"]
<IFD tag BitsPerSample:8>
>>> tif[0]["ModelTiepointTag"].value
(0.0, 0.0, 0.0, -28493.166784412522, 4255884.5438021915, 0.0)
>>> tr = tif[0].getModelTransformation()
>>> tr(0, 0)
(-28493.166784412522, 4255884.5438021915, 0.0, 1.0)
>>> tr(tif[0]["ImageWidth"], tif[0]["ImageLength"])
(2358.211624949061, 4224973.143255847, 0.0, 1.0)
```

<a id="Tyf.TiffFile.gkd"></a>

#### gkd

shortcut to geokey directories

<a id="Tyf.TiffFile.raster_loaded"></a>

#### raster\_loaded

`True` if raster data loaded

<a id="Tyf.TiffFile.save"></a>

#### save

```python
def save(f, byteorder="<", idx=None, ifd1=None)
```

Save object into a TIFF file.

**Arguments**:

- `f` _buffer|string_ - a valid file path or a python file object
- `byteorder` _string_ - `">"` if big-endian used else `"<"`
- `idx` _int_ - IFD index to save
- `ifd1` _Tyf.ifd.Ifd_ - IFD to be used as thumbnail (only needed with
  JPEG saving)

<a id="Tyf.JpegFile"></a>

## JpegFile Objects

```python
class JpegFile(list)
```

List of JPEG segment tuple (marker, segment) defining the JPEG file. Tyf
manage to extract xmp data as python `ElementTree` object and EXIF data
as IFD. `ifd0` is a shortcut to JPEF Exif, `ifd1` is a shortcut to JPEG
Thumbnail and `xmp` is a shortcut to XMP data.

**Arguments**:

- `fileobj` _buffer_ - a python file object.
  
```python
>>> jpg = Tyf.open("test/IMG_20150730_210115.jpg")
>>> jpg.ifd0["GPS IFD"]
<IFD tag GPS IFD:794>
>>> jpg.ifd0.get_location()
(5.1872093, 51.2095416, 0.0)
>>> jpg.xmp
<Element '{adobe:ns:meta/}xmpmeta' at 0x000001CA40C7C4A0>
```

<a id="Tyf.JpegFile.ifd0"></a>

#### ifd0

shortcut to JPEG EXIF data

<a id="Tyf.JpegFile.ifd1"></a>

#### ifd1

shortcut to JPEG thumbnail

<a id="Tyf.JpegFile.xmp"></a>

#### xmp

```python
@property
def xmp(obj)
```

readonly XMP attribute

<a id="Tyf.JpegFile.__getitem__"></a>

#### \_\_getitem\_\_

```python
def __getitem__(item)
```

Return item from `ifd0`.

```python
>>> jpg["GPSLongitude"]
<IFD tag GPSLongitude:5.1872093>
```

<a id="Tyf.JpegFile.get"></a>

#### get

```python
def get(item, default=None)
```

Return item from `ifd1`.

```python
>>> jpg.get("ImageWidth")
<IFD tag ImageWidth:320>
```

<a id="Tyf.JpegFile.set_xmp"></a>

#### set\_xmp

```python
def set_xmp(tag, value, **attributes)
```

Set xmp tag value. Custom namespace can be used.

**Arguments**:

- `tag` _str_ - tag.
- `value` _str_ - tag value.
- `**attributes` - all elements to be set using `attributes` arg on
  `xml.etree.ElementTree.Element` creation.
  

**Returns**:

- `xml.etree.ElementTree.Element` - tag element.

<a id="Tyf.JpegFile.get_xmp"></a>

#### get\_xmp

```python
def get_xmp(tag, ns="http://ns.adobe.com/exif/1.0/")
```

Get xmp tag value. Custom namespace can be used.

**Arguments**:

- `tag` _str_ - tag name.
- `ns` _url_ - xml namespace url (default to
  http://ns.adobe.com/exif/1.0/).
  

**Returns**:

- `xml.etree.ElementTree.Element` - tag element.

<a id="Tyf.JpegFile.save"></a>

#### save

```python
def save(f)
```

Save object as a JPEG file. All segmet are writed in current order,
only `ifd0`, `ifd1` and `xmp` are recomputed.

**Arguments**:

- `f` _buffer or string_ - a valid file path or a python file object

<a id="Tyf.JpegFile.save_thumbnail"></a>

#### save\_thumbnail

```python
def save_thumbnail(f)
```

Save JPEG thumbnail in a separated TIFF or JPEG file, file extention
automatically appended.

**Arguments**:

- `f` _buffer or string_ - a valid file path or a python file object

<a id="Tyf.JpegFile.dump_exif"></a>

#### dump\_exif

```python
def dump_exif(f)
```

Save EXIF data in a separated file. If `f` is a file object, it is
not closed.

**Arguments**:

- `f` _buffer or string_ - a valid file path or a python file object


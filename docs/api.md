<a name="Tyf"></a>
# Tyf

Tyf package aims to provide pythoniv way to interact with metadata in TIFF
and JPEG files.

```python
>>> import Tyf
```

<a name="Tyf.open"></a>
#### open

```python
open(f)
```

Return JpegFile or TiffFile according to ``f``. If it is a file object,
it is not closed.

**Arguments**:

- `f` _buffer_ - a valid file path or a python file object

<a name="Tyf.TiffFile"></a>
## TiffFile Objects

```python
class TiffFile(list)
```

List of IFD found in TIFF file.

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

<a name="Tyf.TiffFile.gkd"></a>
#### gkd

shortcut to geokey directories

<a name="Tyf.TiffFile.raster_loaded"></a>
#### raster\_loaded

``True`` if raster data loaded

<a name="Tyf.TiffFile.save"></a>
#### save

```python
 | save(f, byteorder="<", idx=None, ifd1=None)
```

Save object as a TIFF file. If ``f`` is a file object, it is not
closed.

**Arguments**:

- `f` _buffer_ - a valid file path or a python file object
- `byteorder` _string_ - `">"` if little endian used else `"<"`
- `idx` _int_ - IFD index to save
- `ifd1` _Tyf.ifd.Ifd_ - IFD to be sused as thumbnail (only used for
  JPEG saving)

<a name="Tyf.JpegFile"></a>
## JpegFile Objects

```python
class JpegFile(list)
```

List of JPEG segment tuple (marker, segment) defining the JPEG file. Tyf
manage to extract xmd data as python ``ElementTree`` object and EXIF data
as IFD. ``ifd0`` is a shortcut to JPEF Exif, ``ifd1`` is a shortcut to JPEG
Thumbnail and ``xmp`` is a shortcut to XMP data.

```python
>>> jpg = Tyf.open("test/IMG_20150730_210115.jpg")
>>> jpg.ifd0["GPS IFD"]
<IFD tag GPS IFD:794>
>>> jpg.ifd0.get_location()
(5.1872093, 51.2095416, 0.0)
>>> jpg.xmp
<Element '{adobe:ns:meta/}xmpmeta' at 0x000001CA40C7C4A0>
```

<a name="Tyf.JpegFile.ifd0"></a>
#### ifd0

shortcut to JPEG EXIF data

<a name="Tyf.JpegFile.ifd1"></a>
#### ifd1

shortcut to JPEG thumbnail data

<a name="Tyf.JpegFile.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(fileobj)
```

**Arguments**:

- `fileobj` - a python file object

<a name="Tyf.JpegFile.__getitem__"></a>
#### \_\_getitem\_\_

```python
 | __getitem__(item)
```

Return item from ifd0.

```python
>>> jpg["GPSLongitude"]
<IFD tag GPSLongitude:5.1872093>
```

<a name="Tyf.JpegFile.get"></a>
#### get

```python
 | get(item, default=None)
```

Return item from ifd1.

```python
>>> jpg.get("ImageWidth")
<IFD tag ImageWidth:320>
```

<a name="Tyf.JpegFile.save"></a>
#### save

```python
 | save(f)
```

Save object as a JPEG file. All segmet are writed in current order,
only ``ifd0``, ``ifd1`` and ``xmp`` are recomputed. If ``f`` is a file
object, it is not closed.

**Arguments**:

- `f` _buffer_ - a valid file path or a python file object

<a name="Tyf.JpegFile.save_thumbnail"></a>
#### save\_thumbnail

```python
 | save_thumbnail(f)
```

Save JPEG thumbnail in a separated TIFF or JPEG file, file extention
automatically appended. If ``f`` is a file object, it is not closed.

**Arguments**:

- `f` _buffer_ - a valid file path or a python file object

<a name="Tyf.JpegFile.dump_exif"></a>
#### dump\_exif

```python
 | dump_exif(f)
```

Save EXIF data in a separated file. If ``f`` is a file object, it is
not closed.

**Arguments**:

- `f` _buffer_ - a valid file path or a python file object

<a name="Tyf.JpegFile.strip_exif"></a>
#### strip\_exif

```python
 | strip_exif()
```

Remove EXIF from JPEG, XMP data keeped.


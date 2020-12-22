<a name="Tyf.gkd"></a>
# Tyf.gkd

<a name="Tyf.ifd"></a>
# Tyf.ifd

<a name="Tyf.ifd.GeoKeyModel"></a>
#### GeoKeyModel

Mapping of named tuple to be used with geotiff `ModelPixelScaleTag`,
`ModelTiepointTag` and `ModelTransformationTag`.
```python
>>> import tyf
>>> from Tyf import ifd
>>> tif = Tyf.open("test/CEA.tif")
>>> ifd.GeoKeyModel["ModelTiepointTag"](*tif[0].tiepoints[0])
ModelTiepoint(I=0.0, J=0.0, K=0.0, X=-28493.1667844, Y=4255884.54380, Z=0.0)
>>> ifd.GeoKeyModel["ModelPixelScaleTag"](*tif[0]["ModelPixelScaleTag"])
ModelPixelScale(ScaleX=60.022136983193, ScaleY=60.022136983193, ScaleZ=0.0)
```

<a name="Tyf.ifd.Transform"></a>
#### Transform

```python
Transform(obj, x=0., y=0., z=0.)
```

Transformation between raster and model space using a model transformation
matrix applied to raster coordinates plus altitude.


```python
>>> mps = ifd.GeoKeyModel["ModelPixelScaleTag"]
>>> mtt = ifd.GeoKeyModel["ModelTiepointTag"]
>>> Sx, Sy, Sz = mps(*tif[0]["ModelPixelScaleTag"])
>>> I, J, K, X, Y, Z = mtt(*tif[0].tiepoints[0])
>>> matrix = ifd.GeoKeyModel["ModelTransformationTag"](
...     Sx, 0.,  0., X - I * Sx,
...     0., -Sy, 0., Y + J * Sy,
...     0., 0.,  Sz, Z - K * Sz,
...     0., 0.,  0., 1.
... )
>>> ifd.Transform(matrix, 10, 10)
(-27892.945414580587, 4255284.32243236, 0.0)
```

**Arguments**:

- `obj` _GeoKeyModel["ModelTransformationTag"]_ - transformation matrix
- `x` _float_ - pixel column index from left
- `y` _float_ - pixel row index from top
- `z` _float_ - altitude value

**Returns**:

  projeted coordinates X, Y, Z

<a name="Tyf.ifd.Tag"></a>
## Tag Objects

```python
class Tag(object)
```

<a name="Tyf.ifd.Tag.value"></a>
#### value

Encode and decode on the fly the `_v` attribute (see `Tyf.encoders` and
`Tyf.decoders` modules).
```python
>>> tag = ifd.Tag("GPSLongitude")
>>> tag.value = 5.62347
>>> tag._v
(5, 1, 37, 1, 6123, 250)  # 5/1 deg + 37/1 min + 6123/250 sec
>>> tag.value
5.62347
```

<a name="Tyf.ifd.Tag.info"></a>
#### info

Meaning of tag value if any (see `Tyf.values` module).
```python
>>> ifd.Tag("PhotometricInterpretation", value=3).info
'RGB Palette'
>>> ifd.Tag("Flash", value=0x000F).info
'Flash fired, compulsory flash mode, return light detected'
```

<a name="Tyf.ifd.Tag.__init__"></a>
#### \_\_init\_\_

```python
 | __init__(tag_or_key, value=None)
```

**Arguments**:

- `tag_or_key` _int or string_ - tag value or keyword
- `value` _any_ - value of the tag. If `None` is given, it is set to
  default value if anyone is defined else `_v` attribute
  is not created.

<a name="Tyf.ifd.Tag.read"></a>
#### read

```python
 | @staticmethod
 | read(fileobj, byteorder, db=None)
```

Extract an IFD tag from buffer current position. Buffer position is
adjusted to the end of IFD entry before returning the value.

**Arguments**:

- `fileobj` _buffer_ - a python file object
- `byteorder` _string_ - `">"` if big-endian used else `"<"`
- `db` _dict_ - authorized tag database

**Returns**:

  `Tyf.ifd.Tag`

<a name="Tyf.ifd.Tag.calcsize"></a>
#### calcsize

```python
 | calcsize()
```

Return tag value size in `bytes` when packed.

<a name="Tyf.ifd.Tag.pack"></a>
#### pack

```python
 | pack(byteorder)
```

Return a tuple containing packed IFD base entry [tag, type, count],
packed value and the info if value have to be written in IFD entry or
data.


```python
>>> ttc, val, ofs = ifd.Tag("GPSLongitude", value=5.62347).pack(">")
>>> ttc.hex()
'0004000500000003'
>>> val.hex()
'00000005000000010000002500000001000017eb000000fa'
>>> #   5,      1,     37,      1,   6123,    250
>>> # 5/1 deg   + 37/1 min         + 6123/250 sec
>>> ofs
True
```

**Arguments**:

- `byteorder` _string_ - `">"` if big-endian used else `"<"`

**Returns**:

  (packed ifd entry - packed value - is offset boolean)

<a name="Tyf.ifd.getModelTiePoints"></a>
#### getModelTiePoints

```python
getModelTiePoints(cls)
```

Return tiepoint list found in `ModelTiepointTag` tags. This function sets
a list of all points in private attribute `_model_tiepoints` on first
call.


```
ModelTiepointTag = (I1, J1, K1, X1, Y1, Z1, ...In, Jn, Kn, Xn, Yn, Zn)
_model_tiepoints = [(I1, J1, K1, X1, Y1, Z1), ...(In, Jn, Kn, Xn, Yn, Zn)]
```

**Arguments**:

- `cls` _dict or Tyf.ifd.Ifd_ - image file directory

**Returns**:

  Tiepoint `list`

**Raises**:

  KeyError if no `ModelTiepointTag` defined

<a name="Tyf.ifd.Ifd"></a>
## Ifd Objects

```python
class Ifd(dict)
```

Provide a very similar python `dict` interface to create and store IFD tags
with automatic sub IFD management. `exfT`, `gpsT` and `itrT` are
`Tyf.ifd.Ifd` attributes (sub IFD) for Exif, GPS and Interoperability tags.

```python
>>> i = ifd.Ifd()
>>> i["GPSLongitude"] = 5.62347  # --> GPS IFD
>>> i["FlashpixVersion"] = None  # None will set default value --> Exif IFD
>>> i
{}
>>> i.gpsT
{'GPSLongitude': <IFD tag GPSLongitude:5.62347>}
>>> i.exfT
{'FlashpixVersion': <IFD tag FlashpixVersion:b'0100'>}
>>> i.get("GPSLongitude")  # get method returns tag object
<IFD tag GPSLongitude:5.62347>
>>> i["GPSLongitude"]  # __getitem__ interface returns the python value
5.62347
>>> i.pop("FlashpixVersion")  # delete "FlashpixVersion" tag
<IFD tag FlashpixVersion:b'0100'>
>>> hasattr(i, "exfT")  # empty exfT sub IFD attribute removed
False
```

<a name="Tyf.ifd.Ifd.raster_loaded"></a>
#### raster\_loaded

`True` if raster is loaded

<a name="Tyf.ifd.Ifd.tiepoints"></a>
#### tiepoints

Geotiff tiepoint list

<a name="Tyf.ifd.Ifd.tags"></a>
#### tags

```python
 | tags()
```

Return iterator over all IFD values including sub IFD ones in the
order: `exfT` - `gpsT` - `itrT`.

<a name="Tyf.ifd.Ifd.set_location"></a>
#### set\_location

```python
 | set_location(lon, lat, alt=0.)
```

Set GPS IFD tags according to given longitude, latitude nd altitude.
If no GPS IFD exists, it is created according to version
`(2, 2, 0, 0)`.


```python
>>> i = ifd.Ifd()
>>> i.set_location(5.62347, 45.21345, 12)
>>> for t in i: print(t)
...
<IFD tag GPSVersionID:(2, 2, 0, 0)>
<IFD tag GPSLatitudeRef:'N'>
<IFD tag GPSLatitude:45.21345>
<IFD tag GPSLongitudeRef:'E'>
<IFD tag GPSLongitude:5.62347>
<IFD tag GPSAltitudeRef:0 - Above sea level>
<IFD tag GPSAltitude:12.0>
```

**Arguments**:

- `lon` _float_ - longitude in decimal degrees
- `lat` _float_ - latitude in decimal degrees
- `alt` _float_ - altitude in meters

<a name="Tyf.ifd.Ifd.get_location"></a>
#### get\_location

```python
 | get_location()
```


```python
>>> i = ifd.Ifd()
>>> i.get_location()
Traceback (most recent call last):
File "<stdin>", line 1, in <module>
File "X:/path/to/Tyf/ifd.py", line 568, in get_location
    raise Exception("No location data found")
Exception: No location data found
>>> i.set_location(5.62347, 45.21345, 12)
>>> i.get_location()
(5.62347, 45.21345, 12.0)
```

**Returns**:

  longitude - latitude - altitude tuple

**Raises**:

  Exception if no GPS IFD found


<a name="Tyf.gkd"></a>
# Tyf.gkd

<a name="Tyf.ifd"></a>
# Tyf.ifd

__Documentation__

 + [Tiff 6.0 spec](https://www.itu.int/itudoc/itu-t/com16/tiff-fx/docs/tiff6.pdf)
 + [GeoTiFF 1.8.1 spec](https://htmlpreview.github.io/?https://github.com/OSGeo/libgeotiff/blob/master/geotiff/html/spec/geotiff2.6.html)

<a name="Tyf.ifd.GeoKeyModel"></a>
#### GeoKeyModel

Mapping of named tuple to be used with geotiff `ModelPixelScaleTag`,
`ModelTiepointTag` and `ModelTransformationTag`.
```python
>>> import tyf
>>> from Tyf import ifd
>>> tif = Tyf.open("test/CEA.tif")
>>> ifd.GeoKeyModel["ModelTiepointTag"](*tif[0].tiepoints[0])
ModelTiepoint(I=0.0, J=0.0, K=0.0, X=-28493.166784412522, Y=4255884.5438021915, Z=0.0)
>>> ifd.GeoKeyModel["ModelPixelScaleTag"](*tif[0]["ModelPixelScaleTag"])
ModelPixelScale(ScaleX=60.02213698319374, ScaleY=60.02213698319374, ScaleZ=0.0)
```

<a name="Tyf.ifd.Transform"></a>
#### Transform

```python
Transform(obj, x=0., y=0., z=0.)
```

Transformation between raster and model space using a model transformation
matrix applied to raster coordinates plus altitude.


```python
>>> Sx, Sy, Sz = ifd.GeoKeyModel["ModelPixelScaleTag"](*tif[0]["ModelPixelScaleTag"])
>>> I, J, K, X, Y, Z = ifd.GeoKeyModel["ModelTiepointTag"](*tif[0].tiepoints[0])
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

  projeted coordinates (tuple): X, Y, Z

<a name="Tyf.ifd.Tag"></a>
## Tag Objects

```python
class Tag(object)
```

<a name="Tyf.ifd.Tag.value"></a>
#### value

Encode and decode on the fly the `_v` attribute.
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
- `value` _any_ - value of the tag

<a name="Tyf.ifd.Tag.read"></a>
#### read

```python
 | @staticmethod
 | read(fileobj, byteorder, db=None)
```

**Arguments**:

- `fileobj` _buffer_ - a python file object
- `byteorder` _string_ - `">"` if little endian used else `"<"`
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

Return a tuple containing the IFD base entry [tag, type, count], the
packed value and the info if value have to be written in IFD entry or
data.

**Arguments**:

- `byteorder` _string_ - `">"` if little endian used else `"<"`

**Returns**:

  tuple (`b"tag|type|count"`, `b"value"`, `True` if value is offset)

<a name="Tyf.ifd.getModelTiePoints"></a>
#### getModelTiePoints

```python
getModelTiePoints(cls)
```

Return tiepoint list found in `ModelTiepointTag` tags. This function sets
a list of all points in private attribute `_model_tie_points` on first
call.


```
ModelTiepointTag = (I1, J1, K1, X1, Y1, Z1, ..., In, Jn, Kn, Xn, Yn, Zn)
_model_tie_points = [(I1, J1, K1, X1, Y1, Z1), ..., (In, Jn, Kn, Xn, Yn, Zn)]
```

**Arguments**:

- `cls` _dict or `Tyf.ifd.Ifd`_ - image file directory

**Returns**:

  Tiepoint list

**Raises**:

  KeyError if no `ModelTiepointTag` defined

<a name="Tyf.ifd.Ifd"></a>
## Ifd Objects

```python
class Ifd(dict)
```

<a name="Tyf.ifd.Ifd.raster_loaded"></a>
#### raster\_loaded

`True` if raster is loaded

<a name="Tyf.ifd.Ifd.tiepoints"></a>
#### tiepoints

Tiepoint list


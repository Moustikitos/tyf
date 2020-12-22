# -*- encoding:utf-8 -*-
"""
# Documentation
 + [Tiff 6.0 spec](https://www.itu.int/itudoc/itu-t/com16/tiff-fx/docs/tiff6.pdf)
 + [GeoTiFF 1.8.1 spec](https://htmlpreview.github.io/?https://github.com/OSGeo/libgeotiff/blob/master/geotiff/html/spec/geotiff2.6.html)
"""

import io
import struct
import collections

from Tyf import TYPES, reduce
from Tyf import tags, encoders, decoders, values

try:
    from urllib.request import urlopen
    from io import BytesIO as StringIO
except ImportError:
    from urllib import urlopen
    from cStringIO import StringIO


#: Mapping of named tuple to be used with geotiff `ModelPixelScaleTag`,
#: `ModelTiepointTag` and `ModelTransformationTag`.
#: ```python
#: >>> import tyf
#: >>> from Tyf import ifd
#: >>> tif = Tyf.open("test/CEA.tif")
#: >>> ifd.GeoKeyModel["ModelTiepointTag"](*tif[0].tiepoints[0])
#: ModelTiepoint(I=0.0, J=0.0, K=0.0, X=-28493.1667844, Y=4255884.54380, Z=0.0)
#: >>> ifd.GeoKeyModel["ModelPixelScaleTag"](*tif[0]["ModelPixelScaleTag"])
#: ModelPixelScale(ScaleX=60.022136983193, ScaleY=60.022136983193, ScaleZ=0.0)
#: ```
GeoKeyModel = {
    "ModelPixelScaleTag": collections.namedtuple(
        "ModelPixelScale", "ScaleX, ScaleY, ScaleZ"
    ),
    "ModelTiepointTag": collections.namedtuple("ModelTiepoint", "I,J,K,X,Y,Z"),
    "ModelTransformationTag": collections.namedtuple(
            "ModelTransformation",
            "a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p"
        )
}


def Transform(obj, x=0., y=0., z=0.):
    """
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

    Arguments:
        obj (GeoKeyModel["ModelTransformationTag"]): transformation matrix
        x (float): pixel column index from left
        y (float): pixel row index from top
        z (float): altitude value
    Returns:
        projeted coordinates X, Y, Z
    """
    return (
        obj[0] * x + obj[1] * y + obj[2] * z + obj[3] * 1.,
        obj[4] * x + obj[5] * y + obj[6] * z + obj[7] * 1.,
        obj[8] * x + obj[9] * y + obj[10] * z + obj[11] * 1.
    )


class Tag(object):
    #: Encode and decode on the fly the `_v` attribute.
    #: ```python
    #: >>> tag = ifd.Tag("GPSLongitude")
    #: >>> tag.value = 5.62347
    #: >>> tag._v
    #: (5, 1, 37, 1, 6123, 250)  # 5/1 deg + 37/1 min + 6123/250 sec
    #: >>> tag.value
    #: 5.62347
    #: ```
    value = property(
        lambda cls: cls._getvalue(),
        lambda cls, v: cls._setvalue(v),
        None,
        ""
    )
    count = property(
        lambda cls:
            len(getattr(cls, "_v", (None, ))) //
            (2 if getattr(cls, "type", None) in [5, 10] else 1),
        None,
        None,
        ""
    )
    #: Meaning of tag value if any (see `Tyf.values` module).
    #: ```python
    #: >>> ifd.Tag("PhotometricInterpretation", value=3).info
    #: 'RGB Palette'
    #: >>> ifd.Tag("Flash", value=0x000F).info
    #: 'Flash fired, compulsory flash mode, return light detected'
    #: ```
    info = property(
        lambda cls: getattr(values, cls.key, {}).get(cls.value, None),
        None,
        None,
        ""
    )

    def _getvalue(self):
        if not hasattr(self, "_decode"):
            setattr(
                self, "_decode", getattr(
                    decoders, self.key, getattr(
                        decoders, "_%s" % self.type
                    )
                )
            )
        if hasattr(self, "_v"):
            return self._decode(self._v)
        return None

    def _setvalue(self, value):
        if not hasattr(self, "_encode"):
            setattr(
                self, "_encode", getattr(
                    encoders, self.key, getattr(
                        encoders, "_%s" % self.type
                    )
                )
            )
        self._v = self._encode(value)
        self._is_offset = self.count * struct.calcsize(
            "=" + TYPES[self.type][0]
        ) > 4

    def __init__(self, tag_or_key, value=None):
        """
        Arguments:
            tag_or_key (int or string): tag value or keyword
            value (any): value of the tag
        """
        self.tag, (self.key, self._types, default, self.comment) = \
            tags.get(tag_or_key)
        self.type = self._types[-1]
        if value or default:
            self.value = value or default

    def __repr__(self):
        if self.info:
            return "<IFD tag %s:%r - %s>" % (self.key, self.value, self.info)
        else:
            return "<IFD tag %s:%r>" % (self.key, self.value)

    @staticmethod
    def read(fileobj, byteorder, db=None):
        """
        Extract an IFD tag from buffer current position. Buffer position is
        adjusted to the end of IFD entry before returning the value.

        Arguments:
            fileobj (buffer): a python file object
            byteorder (string): `">"` if big-endian used else `"<"`
            db (dict): authorized tag database
        Returns:
            `Tyf.ifd.Tag`
        """
        # read tag, type and count
        fmt = byteorder + "HHL"
        tag, typ, cnt = struct.unpack(
            fmt, fileobj.read(struct.calcsize(fmt))
        )
        cls = Tag(tag)
        cls.key, cls._types, cls.default, cls.comment = tags.get(tag)[-1]
        cls.type = typ
        # extract value_or_offset
        value_or_offset = fileobj.read(struct.calcsize("=L"))
        if not isinstance(value_or_offset, bytes):
            value_or_offset = value_or_offset.encode("utf-8")
        # prepare structure value
        _typ = TYPES[typ][0]
        fmt = byteorder + ("%ds" % cnt if _typ == "s" else cnt * _typ)
        type_size = struct.calcsize("=" + _typ)
        data_size = cnt * type_size
        if data_size > 4:
            cls._is_offset = True
            # keep the end of tag definition position
            bckp = fileobj.tell()
            offset, = struct.unpack(byteorder+"L", value_or_offset)
            fileobj.seek(offset)
            value = struct.unpack(fmt, fileobj.read(struct.calcsize(fmt)))
            # go back to end of tag definition position
            fileobj.seek(bckp)
        else:
            cls._is_offset = False
            value = struct.unpack(fmt, value_or_offset[:data_size])
        # store raw value
        if typ in [2, 7]:
            # python 3.x
            if len(value) == 1:
                value = value[0]
            # python 2.x
            else:
                value = b"".join(value)
        cls._v = value
        return cls

    def calcsize(self):
        """
        Return tag value size in `bytes` when packed.
        """
        return struct.calcsize("=" + TYPES[self.type][0] * self.count)

    def pack(self, byteorder):
        """
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

        Arguments:
            byteorder (string): `">"` if big-endian used else `"<"`
        Returns:
            tuple (`|tag|type|count|`, `|value|`, `True` if value is offset)

        """
        tag, typ, cnt = self.tag, self.type, self.count
        info = struct.pack(byteorder + "HHL", tag, typ, cnt)
        typ_ = TYPES[typ][0]
        fmt = \
            byteorder + ("%ds" % cnt if typ_ == "s" else cnt * typ_)
        packed = \
            struct.pack(fmt, self._v) if typ_ == "s" else \
            struct.pack(fmt, *self._v)
        value_is_offset = getattr(self, "_is_offset", False)
        return (
            info,
            packed if value_is_offset else packed.ljust(4, b"\x00"),
            value_is_offset
        )


# for speed reason : load raster only if asked or if needed
def _load_raster(obj, fileobj):
    # striped raster data
    if "StripOffsets" in obj:
        setattr(obj, "stripes", tuple())
        offsets = obj["StripOffsets"]
        bytescounts = obj["StripByteCounts"]
        if isinstance(offsets, tuple):
            data = zip(offsets, bytescounts)
        else:
            data = ((offsets, bytescounts), )
        for offset, bytecount in data:
            fileobj.seek(offset)
            obj.stripes += (fileobj.read(bytecount), )
    # free raster data
    elif "FreeOffsets" in obj:
        setattr(obj, "free", tuple())
        offsets = obj["FreeOffsets"]
        bytescounts = obj["FreeByteCounts"]
        if isinstance(offsets, tuple):
            data = zip(offsets, bytescounts)
        else:
            data = ((offsets, bytescounts), )
        for offset, bytecount in data:
            fileobj.seek(offset)
            obj.free += (fileobj.read(bytecount), )
    # tiled raster data
    elif "TileOffsets" in obj:
        setattr(obj, "tiles", tuple())
        offsets = obj["TileOffsets"]
        bytescounts = obj["TileByteCounts"]
        if isinstance(offsets, tuple):
            data = zip(offsets, bytescounts)
        else:
            data = ((offsets, bytescounts), )
        for offset, bytecount in data:
            fileobj.seek(offset)
            obj.tiles += (fileobj.read(bytecount), )
    # get interExchange (thumbnail data for JPEG/EXIF data)
    if "JPEGInterchangeFormat" in obj:
        fileobj.seek(obj["JPEGInterchangeFormat"])
        obj.jpegIF = fileobj.read(obj["JPEGInterchangeFormatLength"])


def getModelTiePoints(cls):
    """
    Return tiepoint list found in `ModelTiepointTag` tags. This function sets
    a list of all points in private attribute `_model_tiepoints` on first
    call.

    ```
    ModelTiepointTag = (I1, J1, K1, X1, Y1, Z1, ...In, Jn, Kn, Xn, Yn, Zn)
    _model_tiepoints = [(I1, J1, K1, X1, Y1, Z1), ...(In, Jn, Kn, Xn, Yn, Zn)]
    ```

    Arguments:
        cls (dict or Tyf.ifd.Ifd): image file directory
    Returns:
        Tiepoint `list`
    Raises:
        KeyError if no `ModelTiepointTag` defined
    """
    if not hasattr(cls, "_model_tiepoints"):
        setattr(cls, "_model_tiepoints", [
            cls["ModelTiepointTag"][i:i+6]
            for i in range(0, len(cls["ModelTiepointTag"]), 6)
        ])
    return getattr(cls, "_model_tiepoints")


class Ifd(dict):
    """
    Provide a very similar python `dict` interface to create and store IFD tags
    with automatic sub IFD management. `exfT`, `gpsT` and `itrT` are
    `Tyf.ifd.Ifd` sub IFD storing Exif, GPS and Interoperability tags.

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
    ```
    """
    #: `True` if raster is loaded
    raster_loaded = property(
        lambda obj: any([
            len(getattr(obj, name, []))
            for name in ["stripes", "tiles", "free", "jpegIF"]
        ]),
        None, None, ""
    )
    #: Geotiff tiepoint list
    tiepoints = property(
        lambda cls: getModelTiePoints(cls),
        None, None, ""
    )

    def __init__(self, **kwargs):
        dict.__init__(self)
        self.tag_family = kwargs.pop(
            "tag_family", [tags.bTT, tags.xTT, tags.pTT]
        )

    def __delattr__(self, attr, value):
        if attr == "gpsT":
            dict.pop(self, "GPS IFD", False)
        elif attr == "exfT":
            dict.pop(self, "Exif IFD", False)
        elif attr == "itrT":
            dict.pop(self, "Interoperability IFD", False)
        dict.__delattr__(self, attr, value)

    def __setitem__(self, tag, value):
        try:
            self.get(tag).value = value
        except KeyError:
            self.append(Tag(tag, value))

    def __getitem__(self, tag):
        tag, (key, typ, default, comment) = tags.get(tag)
        if key in self:
            return dict.__getitem__(self, key).value
        for name in ["exfT", "gpsT", "itrT"]:
            if hasattr(self, name):
                dic = getattr(self, name)
                if key in dic:
                    return dict.__getitem__(dic, key).value
        raise KeyError("%s tag not found" % key)

    def __delitem__(self, tag):
        tag, (key, typ, default, comment) = tags.get(tag)
        if key in self:
            return dict.__delitem__(self, key)
        for name in ["exfT", "gpsT", "itrT"]:
            if hasattr(self, name):
                dic = getattr(self, name)
                if key in dic:
                    if len(dic) == 1:
                        delattr(self, name)
                    return dict.__delitem__(dic, key)
        raise KeyError("%s tag not found" % key)

    def set(self, tag, typ, value):
        tag = Tag(tag)
        tag.type = typ
        tag.value = value
        return dict.__setitem__(self, tag.key, tag)

    def get(self, tag, default=None):
        tag, (key, typ, default, comment) = tags.get(tag)
        if key in self:
            return dict.get(self, key, default)
        for name in ["exfT", "gpsT", "itrT"]:
            if hasattr(self, name):
                dic = getattr(self, name)
                if key in dic:
                    return dict.get(dic, key, default)
        raise KeyError("%s tag not found" % key)

    def pop(self, tag, default=None):
        tag, (key, typ, default, comment) = tags.get(tag)
        if key in self:
            return dict.pop(self, key)
        for name in ["exfT", "gpsT", "itrT"]:
            if hasattr(self, name):
                dic = getattr(self, name)
                if key in dic:
                    result = dict.pop(dic, key)
                    if len(dic) == 0:
                        delattr(self, name)
                    return result
        return default

    def set_location(self, longitude, latitude, altitude=0.):
        if not hasattr(self, "gpsT"):
            setattr(self, "gpsT", Ifd(tag_family=[tags.gpsT]))
        if "GPSVersionID" not in self:
            dict.__setitem__(self.gpsT, "GPSVersionID", Tag("GPSVersionID"))
        self["GPSLatitudeRef"] = "n" if latitude >= 0 else "s"
        self["GPSLatitude"] = latitude
        self["GPSLongitudeRef"] = "e" if longitude >= 0 else "w"
        self["GPSLongitude"] = longitude
        self["GPSAltitudeRef"] = altitude >= 0
        self["GPSAltitude"] = altitude

    def get_location(self):
        ifd = getattr(self, "gpsT", {})
        if set([
            "GPSLatitudeRef", "GPSLatitude",
            "GPSLongitudeRef", "GPSLongitude",
            "GPSAltitudeRef", "GPSAltitude"
        ]) <= set(ifd.keys()):
            return (
                (1 if ifd["GPSLongitudeRef"] == "E" else -1) *
                ifd["GPSLongitude"],
                (1 if ifd["GPSLatitudeRef"] == "N" else -1) *
                ifd["GPSLatitude"],
                (1 if ifd["GPSAltitudeRef"] else -1) *
                ifd["GPSAltitude"]
            )
        else:
            raise Exception("No location data found")

    def append(self, tag):
        for dic in self.tag_family:
            if tag.tag in dic:
                return dict.__setitem__(self, tag.key, tag)
        for name in ["exfT", "gpsT", "itrT"]:
            dic = getattr(tags, "_" + name, {})
            if tag.key in dic:
                if not hasattr(self, name):
                    setattr(self, name, Ifd(tag_family=[getattr(tags, name)]))
                return dict.__setitem__(getattr(self, name), tag.key, tag)

    def pack(self, byteorder="<"):
        result = {}

        for name in [n for n in ["exfT", "gpsT", "itrT"] if hasattr(self, n)]:
            result[name] = getattr(self, name).pack(byteorder)["root"]

        tags = [
            t.pack(byteorder) for t in
            sorted(self.values(), key=lambda e: e.tag)
        ]

        ifd_size = struct.calcsize("=H" + len(tags) * "HHLL" + "L")
        ifd_data = b"".join(t[1] for t in tags if t[-1])

        raster_length = set([
            "TileByteCounts", "StripByteCounts", "FreeByteCounts",
            "JPEGInterchangeFormatLength"
        ]) & set(self.keys())

        if len(raster_length):
            tag = list(raster_length)[0]
            raster_length = self[tag]
            ifd_raster_size = \
                reduce(int.__add__, raster_length) \
                if isinstance(raster_length, tuple) else raster_length
        else:
            ifd_raster_size = 0

        result.update(root={
            "size": ifd_size,
            "tags": tags,
            "data": ifd_data,
            "raster": ifd_raster_size
        })
        return result

    def url_load_location(self, url, **kwargs):
        longitude, latitude, alt = self.get_location()
        kwargs.update(lon=longitude, lat=latitude, alt=alt)
        try:
            opener = urlopen(url % kwargs)
        except Exception as error:
            print("%r" % error)
        else:
            return StringIO(opener.read())

    def dump_location(self, name, *args, **kwargs):
        fileobj = io.open(name, "wb")
        stringio = self.url_load_location(*args, **kwargs)
        fileobj.write(stringio.getvalue())
        fileobj.close()
        stringio.close()
        del fileobj, stringio

    def tags(self):
        for v in sorted(dict.values(self), key=lambda e: e.tag):
            yield v
        for name in ["exfT", "gpsT", "itrT"]:
            if hasattr(self, name):
                for v in getattr(self, name).tags():
                    yield v

    def getModelTransformation(self, tie_idx=0):
        if "ModelTransformationTag" in self:
            matrix = GeoKeyModel["ModelTransformationTag"](
               *self["ModelTransformationTag"]
            )
        elif "ModelTiepointTag" in self and "ModelPixelScaleTag" in self:
            Sx, Sy, Sz = self["ModelPixelScaleTag"]
            I, J, K, X, Y, Z = self["ModelTiepointTag"][
                6 * tie_idx:6 * tie_idx + 6
            ]
            matrix = GeoKeyModel["ModelTransformationTag"](
                Sx,  0., 0., X - I * Sx,
                0., -Sy, 0., Y + J * Sy,
                0., 0.,  Sz, Z - K * Sz,
                0., 0.,  0., 1.
            )
        else:
            matrix = GeoKeyModel["ModelTransformationTag"](
                1., 0.,  0., 0.,
                0., -1., 0., 0.,
                0., 0.,  1., 0.,
                0., 0.,  0., 1.
            )
        return lambda x, y, z=0., m=matrix: Transform(m, x, y, z)


def dump_mapbox_location(
    cls, name, zoom=15, width=400, height=300,
    token="pk.eyJ1IjoibW91c2lraXRvcyIsImEiOiJja2k2bGw2bnkzMXZ2MnJtcHlyejFrNXd4"
          "In0.JIyrV6sWjehsRHKVMBDFaw",
):
    return cls.dump_location(
        name,
        "https://api.mapbox.com/styles/v1/mapbox/outdoors-v11/static/"
        "pin-s+f74e4e(%(lon)s,%(lat)s)/%(lon)s,%(lat)s,%(zoom)s,0/"
        "%(width)sx%(height)s?access_token=%(token)s",
        zoom=15, width=400, height=300, token=token
    )

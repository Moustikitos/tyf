# -*- encoding:utf-8 -*-
"""
# Bibliography
 + [Tiff 6.0 spec](https://www.itu.int/itudoc/itu-t/com16/tiff-fx/docs/tiff6.pdf)
 + [GeoTiFF 1.8.1 spec](https://htmlpreview.github.io/?https://github.com/OSGeo/libgeotiff/blob/master/geotiff/html/spec/geotiff2.6.html)
 + [JPEG FIF 1.02 spec](https://www.w3.org/Graphics/JPEG/jfif3.pdf)
 + [XMP spec](https://developer.adobe.com/xmp/docs/XMPSpecifications/)

Tyf package aims to provide pythonic way to interact with metadata in TIFF and
JPEG files.

```python
>>> import Tyf
```
"""

__copyright__ = "Copyright © 2015-2023 - BSD Licence"
__author__ = "THOORENS Bruno"
__tiff__ = (6, 0)
__geotiff__ = (1, 8, 1)

import io
import os
import sys
import struct
import operator

import xml.etree.ElementTree as xmp

__PY3__ = sys.version_info[0] >= 3
__XMP__ = True

#: Adobe namespaces mapping related to TIFF and JPEG File
XmpNamespace = dict(
    RDF="http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    TIFF="http://ns.adobe.com/tiff/1.0/",
    ADOBE="http://ns.adobe.com/xap/1.0/",
    PHOTOSHOP="http://ns.adobe.com/photoshop/1.0/",
    EXIF="http://ns.adobe.com/exif/1.0/",
    MICROSOFT="http://ns.microsoft.com/photo/1.0",
    CAMERA_RAW_SETTINGS="http://ns.adobe.com/camera-raw-settings/1.0/",
    IPTC="http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/"
)


class InvalidFileError(Exception):
    """
    Raise when the input file is not valid, e.g. not a tiff or jpeg, or is a
    bigtiff.
    """
    pass


class XmpDataNotFound(Exception):
    "Raise when no xmp data found in JPEG file"
    pass


#: Type definition linking tag type value to python `struct` format
TYPES = {
    1:  ("B",  "UCHAR or USHORT"),
    2:  ("s",  "ASCII"),
    3:  ("H",  "UBYTE"),
    4:  ("L",  "ULONG"),
    5:  ("LL", "URATIONAL"),
    6:  ("b",  "CHAR or SHORT"),
    7:  ("s",  "UNDEFINED"),
    8:  ("h",  "BYTE"),
    9:  ("l",  "LONG"),
    10: ("ll", "RATIONAL"),
    11: ("f",  "FLOAT"),
    12: ("d",  "DOUBLE"),
}

# assure compatibility python 2 & 3
if __PY3__:
    from io import BytesIO as StringIO
    import functools
    reduce = functools.reduce
    long = int
else:
    TYPES[2] = ("c", "ASCII")
    TYPES[7] = ("c", "UDEFINED")
    from cStringIO import StringIO
    reduce = __builtins__["reduce"]

# here to avoid circular import
from Tyf import ifd, gkd


def unpack(fmt, fileobj):
    return struct.unpack(fmt, fileobj.read(struct.calcsize(fmt)))


def pack(fmt, fileobj, value):
    return fileobj.write(struct.pack(fmt, *value))


def _read_IFD(obj, fileobj, offset, byteorder="<"):
    "Read IFD from file object and return next IFD offset."
    # fileobj seek must be on the start offset
    fileobj.seek(offset)
    # get number of entry
    nb_entry, = unpack(byteorder+"H", fileobj)
    next_ifd_offset = offset + struct.calcsize("=H" + nb_entry*"HHLL")
    # for each entry
    for i in range(nb_entry):
        obj.append(ifd.Tag.read(fileobj, byteorder))
    # return next ifd offset, if =0 then end of TIFF
    return next_ifd_offset


def _from_buffer(obj, fileobj, offset, byteorder="<"):
    "Read IFD and sub IFD from file object and return next IFD offset."
    # read data from offset and get next ifd offset
    next_ifd_offset = _read_IFD(obj, fileobj, offset, byteorder)
    # read sub IFD if any
    for key in set(["GPS IFD", "Exif IFD", "Interoperability IFD"]) \
            & set(obj.keys()):
        _read_IFD(obj, fileobj, obj[key], byteorder)
    fileobj.seek(next_ifd_offset)
    next_ifd, = unpack(byteorder+"L", fileobj)
    return next_ifd


def _write_IFD(obj, fileobj, offset, byteorder="<", ifd1=None):
    "Write IFD in file object and return next ifd offset."
    # compute geotiff ifd if any found
    geokey = gkd.Gkd.from_ifd(obj)
    if len(geokey):
        geokey.compute()
        obj["GeoKeyDirectoryTag"] = geokey._34735
        obj["GeoDoubleParamsTag"] = geokey._34736
        obj["GeoAsciiParamsTag"] = geokey._34737

    # pack the ifd
    ifds = obj.pack(byteorder)
    if isinstance(ifd1, ifd.Ifd):
        ifds.update(ifd1=ifd1.pack(byteorder)["root"])

    # compute exif, gps and interoperability offsets
    ifd_size = ifds["root"]["size"]
    ifd_values = ifds["root"]["data"]
    # where to put ifd values
    ifd_offset_values = offset + ifd_size
    # where to put the sub ifds
    sub_ifd_offset = ifd_offset_values + len(ifd_values)

    # compute all possible sub ifd offsets
    for name in set(["exfT", "gpsT", "itrT"]) & set(ifds.keys()):
        i = ifds[name]
        obj[
            "Exif IFD" if name == "exfT" else
            "GPS IFD" if name == "gpsT" else
            "Interoperability IFD"
        ] = sub_ifd_offset
        # increment the next sub ifd offset
        sub_ifd_offset += i["size"] + len(i["data"])

    # if ifd1 given (thumbnail jor Jpeg), reserve needed space before raster
    # data
    if "ifd1" in ifds:
        raster_offset = \
            sub_ifd_offset + ifds["ifd1"]["size"] + \
            len(ifds["ifd1"]["data"]) + ifds["ifd1"]["raster"]
    # else raster data can follow the last sub ifd
    else:
        raster_offset = sub_ifd_offset

    # compute raster positions
    for tag in set(
        ["StripOffsets", "TileOffsets", "FreeOffsets", "JPEGInterchangeFormat"]
    ) & set(dict.keys(obj)):
        if "Offset" in tag:  # StripOffsets, TileOffsets or FreeOffsets
            raster_offsets = (raster_offset,)
            tagname = tag.replace("Offsets", "ByteCounts")
            bytecounts = obj[tagname]
            if isinstance(bytecounts, tuple):
                for bytecount in obj[tagname]:
                    raster_offsets += (raster_offsets[-1] + bytecount, )
            obj[tag] = raster_offsets
        else:  # JPEGInterchangeFormat
            obj[tag] = raster_offset

    # recompute all modified tags
    ifds = obj.pack(byteorder)
    if isinstance(ifd1, ifd.Ifd):
        ifds.update(ifd1=ifd1.pack(byteorder)["root"])
    # adjust raser offset with diff between first computation and second one
    raster_offset += len(ifds["root"]["data"]) - len(ifd_values)

    # write IFDs
    for key in set(["root", "exfT", "gpsT", "itrT"]) & set(ifds.keys()):
        packed = ifds[key]
        # go to according [SUB]IFD offset and determine associated data offset
        if key == "root":
            fileobj.seek(offset)
            data_offset = ifd_offset_values
        else:
            sub_ifd_offset = obj[
                "Exif IFD" if key == "exfT" else
                "GPS IFD" if key == "gpsT" else
                "Interoperability IFD"
            ]
            fileobj.seek(sub_ifd_offset)
            data_offset = sub_ifd_offset + packed["size"]

        tags = packed["tags"]
        # write number of entries
        pack(byteorder + "H", fileobj, (len(tags),))
        # write all ifd entries and data
        for entry, data, is_offset in tags:
            fileobj.write(entry)
            if not is_offset:
                fileobj.write(data)
            else:
                # put offset and shift it by len(data) for next offset value
                pack(byteorder + "L", fileobj, (data_offset, ))
                data_offset += len(data)

        if key == "root":
            next_ifd_offset = fileobj.tell()
        pack(byteorder + "L", fileobj, (0, ))
        fileobj.write(packed["data"])

    # write IFD1 (this should only be used with Jpeg exif thumbnail)
    if "ifd1" in ifds:
        ifd1_offset = fileobj.tell()
        fileobj.seek(next_ifd_offset)
        pack(byteorder + "L", fileobj, (ifd1_offset, ))
        _write_IFD(ifd1, fileobj, ifd1_offset, byteorder="<", ifd1=None)

    # write raster data
    if obj.raster_loaded:
        fileobj.seek(raster_offset)
        if hasattr(obj, "jpegIF"):
            fileobj.write(getattr(obj, "jpegIF"))
        else:
            for data in reduce(
                tuple.__add__, [
                    getattr(obj, name, tuple())
                    for name in ["stripes", "tiles", "free"]
                ]
            ):
                fileobj.write(data)

    return next_ifd_offset


def _fileobj(f, mode):
    #: returns fileobj from a path or a stringIO
    if hasattr(f, "close"):
        fileobj = f
        _close = False
    else:
        fileobj = io.open(f, mode)
        _close = True
    return fileobj, _close


def open(f):
    """
    Return `JpegFile` or `TiffFile` instance according to argument.

    Args:
        f (buffer or string): a valid file path or a python file object.

    Returns:
        Tyf.JpegFile|Tyf.TiffFile: JPEG or TIFF instance.
    """
    fileobj, _close = _fileobj(f, "rb")

    first, = unpack(">H", fileobj)
    fileobj.seek(0)

    if first == 0xffd8:
        obj = JpegFile(fileobj)
    elif first in [0x4d4d, 0x4949]:
        obj = TiffFile(fileobj)
    else:
        obj = None

    if _close:
        fileobj.close()

    if obj is None:
        raise InvalidFileError("file is not a valid JPEG nor TIFF image")
    else:
        return obj


class TiffFile(list):
    """
    This class is is a list of all Image File Directories defining the TIFF
    file.

    Args:
        fileobj (buffer): a python file object.

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
    """

    #: shortcut to geokey directories
    gkd = property(
        lambda obj: gkd.getGeokeyDirectories(obj),
        None, None, "Geotiff IFD"
    )

    #: `True` if raster data loaded
    raster_loaded = property(
        lambda obj: reduce(
            operator.__and__, [ifd.raster_loaded for ifd in obj]
        ),
        None, None, "True if all raster data loaded"
    )

    def __init__(self, fileobj):
        # determine byteorder
        first, = unpack(">H", fileobj)
        byteorder = "<" if first == 0x4949 else ">"
        # manage according to magic number found
        magic_number, = unpack(byteorder+"H", fileobj)
        if magic_number not in [0x732E, 0x2A]:  # 29486, 42
            fileobj.close()
            if magic_number == 0x2B:  # 43
                raise InvalidFileError("BigTIFF file not supported")
            else:
                raise InvalidFileError(
                    "Bad magic number. Not a valid TIFF file"
                )

        ifds = []
        next_ifd, = unpack(byteorder+"L", fileobj)
        while next_ifd != 0:
            i = ifd.Ifd(tag_family=["bTT", "pTT", "xTT"])
            next_ifd = _from_buffer(i, fileobj, next_ifd, byteorder)
            ifds.append(i)

        # keep filename source to load raster when needed
        if hasattr(fileobj, "name"):
            self._filename = fileobj.name
        # load raster if initializing from fileobj
        else:
            for i in ifds:
                ifd._load_raster(i, fileobj)

        list.__init__(self, ifds)

    def load_raster(self, idx=None):
        if hasattr(self, "_filename"):
            in_, c_ = _fileobj(self._filename, "rb")
            for item in iter(self) if idx is None else [self[idx]]:
                if not item.raster_loaded:
                    ifd._load_raster(item, in_)
            in_.close()

    def save(self, f, byteorder="<", idx=None, ifd1=None):
        """
        Save object into a TIFF file.

        Arguments:
            f (buffer|string): a valid file path or a python file object
            byteorder (string): `">"` if big-endian used else `"<"`
            idx (int): IFD index to save
            ifd1 (Tyf.ifd.Ifd): IFD to be used as thumbnail (only needed with
                JPEG saving)
        """
        self.load_raster()
        fileobj, _close = _fileobj(f, "wb")

        pack(
            byteorder+"HH", fileobj,
            (0x4949 if byteorder == "<" else 0x4d4d, 0x2A, )
        )
        next_ifd = 8

        for i in iter(self) if idx is None else [self[idx]]:
            pack(byteorder+"L", fileobj, (next_ifd,))
            next_ifd = _write_IFD(i, fileobj, next_ifd, byteorder, ifd1=ifd1)

        if _close:
            fileobj.close()
            del fileobj


class JpegFile(list):
    """
    List of JPEG segment tuple (marker, segment) defining the JPEG file. Tyf
    manage to extract xmp data as python `ElementTree` object and EXIF data
    as IFD. `ifd0` is a shortcut to JPEF Exif, `ifd1` is a shortcut to JPEG
    Thumbnail and `xmp` is a shortcut to XMP data.

    Args:
        fileobj (buffer): a python file object.

    ```python
    >>> jpg = Tyf.open("test/IMG_20150730_210115.jpg")
    >>> jpg.ifd0["GPS IFD"]
    <IFD tag GPS IFD:794>
    >>> jpg.ifd0.get_location()
    (5.1872093, 51.2095416, 0.0)
    >>> jpg.xmp
    <Element '{adobe:ns:meta/}xmpmeta' at 0x000001CA40C7C4A0>
    ```
    """

    #: shortcut to JPEG EXIF data
    ifd0 = property(
        lambda obj: getattr(obj, "ifd", [{}, {}])[0],
        None, None, "readonly image IFD attribute"
    )

    #: shortcut to JPEG thumbnail
    ifd1 = property(
        lambda obj: getattr(obj, "ifd", [{}, {}])[1],
        None, None, "readonly thumbnail IFD attribute"
    )

    @property
    def xmp(obj):
        "readonly XMP attribute"
        if not hasattr(obj, "_JpegFile__xmp_ns"):
            raise XmpDataNotFound("no XMP segment found")
        return list.__getitem__(obj, obj.__xmp_idx)[-1]

    def __init__(self, fileobj):
        sgmt = []

        fileobj.seek(0)
        marker, = unpack(">H", fileobj)
        if marker != 0xffd8:
            raise InvalidFileError("not a valid jpeg file")

        while marker != 0xffd9:  # EOI (End Of Image) Marker
            marker, count = unpack(">HH", fileobj)
            # if JPEG raw data
            if marker == 0xffda:
                fileobj.seek(-2, 1)
                sgmt.append((0xffda, fileobj.read()[:-2]))
                marker = 0xffd9
            elif marker == 0xffe1:
                data = fileobj.read(count-2)
                if data[:6] == b"Exif\x00\x00":
                    string = StringIO(data[6:])
                    self.ifd = TiffFile(string)
                    string.close()
                    sgmt.append((marker, self.ifd))
                elif b"ns.adobe.com" in data[:30]:
                    xmp_data_idx = data.find(b"\x00")
                    self.__xmp_idx = len(sgmt)
                    self.__xmp_ns = data[:xmp_data_idx]
                    sgmt.append(
                        (marker, xmp.fromstring(data[xmp_data_idx+1:]))
                    )
            else:
                sgmt.append((marker, fileobj.read(count-2)))

        list.__init__(self, sgmt)

    def __getitem__(self, item):
        """
        Return item from `ifd0`.

        ```python
        >>> jpg["GPSLongitude"]
        <IFD tag GPSLongitude:5.1872093>
        ```
        """
        return self.ifd0.get(item, None)

    def get(self, item, default=None):
        """
        Return item from `ifd1`.

        ```python
        >>> jpg.get("ImageWidth")
        <IFD tag ImageWidth:320>
        ```
        """
        return self.ifd1.get(item, default)

    def set_xmp(self, tag, value, **attributes):
        """
        Set xmp tag value. Custom namespace can be used.

        Args:
            tag (str): tag.
            value (str): tag value.
            **attributes: all elements to be set using `attributes` arg on
                `xml.etree.ElementTree.Element` creation.

        Returns:
            xml.etree.ElementTree.Element: tag element.
        """
        # create the xmp segment if no one found
        if not hasattr(self, "_JpegFile__xmp_ns"):
            self.__xmp_ns = b"http://ns.adobe.com/xap/1.0/"
            self.__xmp_idx = 2
            elem = xmp.Element("{adobe:ns:meta/}xmpmeta")
            xmp.SubElement(elem, "{%s}RDF" % XmpNamespace["RDF"])
            list.insert(self, self.__xmp_idx, (65505, elem))
        # get namespace
        ns = attributes.pop("ns", "http://ns.adobe.com/exif/1.0/")
        ns = XmpNamespace.get(ns, ns)
        # try to get a parent node containing at least one tag with the
        # according namespace
        parent = self.xmp.find(".//{%s}*/..." % ns)
        if parent is None:
            # create a 'Description' node in root element with rdf namespace
            parent = xmp.SubElement(
                self.xmp[0], "{%s}Description" % XmpNamespace["RDF"]
            )
        # add element with the appropriate namespace
        elem = xmp.SubElement(parent, "{%s}%s" % (ns, tag), **attributes)
        elem.text = "%s" % value
        parent.append(elem)
        return elem

    def get_xmp(self, tag, ns="http://ns.adobe.com/exif/1.0/"):
        """
        Get xmp tag value. Custom namespace can be used.

        Args:
            tag (str): tag name.
            ns (url): xml namespace url (default to
                http://ns.adobe.com/exif/1.0/).

        Returns:
            xml.etree.ElementTree.Element: tag element.
        """
        return self.xmp.find(".//{%s}%s" % (XmpNamespace.get(ns, ns), tag))

    def save(self, f):
        """
        Save object as a JPEG file. All segmet are writed in current order,
        only `ifd0`, `ifd1` and `xmp` are recomputed.

        Arguments:
            f (buffer or string): a valid file path or a python file object
        """
        fileobj, _close = _fileobj(f, "wb")
        pack(">H", fileobj, (0xffd8,))

        for marker, value in self:
            if marker == 0xffda:
                pack(">H", fileobj, (marker,))

            elif marker == 0xffe1:
                if isinstance(value, TiffFile):
                    string = StringIO()
                    if len(value) == 2:
                        value.save(string, idx=0, ifd1=value[-1])
                    else:
                        value.save(string)
                    data = string.getvalue()
                    value = b"Exif\x00\x00" + (
                        data if isinstance(data, bytes)
                        else data.encode("utf-8")
                    )
                    string.close()
                elif isinstance(value, xmp.Element):
                    data = xmp.tostring(self.xmp)
                    value = self.__xmp_ns + b"\x00" + (
                        data if isinstance(data, bytes)
                        else data.encode("utf-8")
                    )
                else:
                    value = b""
                pack(">HH", fileobj, (marker, len(value) + 2))

            else:
                pack(">HH", fileobj, (marker, len(value) + 2))

            fileobj.write(value)

        pack(">H", fileobj, (0xffd9,))

        if _close:
            fileobj.close()
            del fileobj

    def save_thumbnail(self, f):
        """
        Save JPEG thumbnail in a separated TIFF or JPEG file, file extention
        automatically appended.

        Arguments:
            f (buffer or string): a valid file path or a python file object
        """
        try:
            ifd = self.ifd1
        except Exception as error:
            print("%r" % error)
        else:
            compression = ifd[259]
            if hasattr(f, "close"):
                fileobj = f
                _close = False
            else:
                fileobj = io.open(
                    os.path.splitext(f)[0] +
                    (".jpg" if compression == 6 else ".tif"),
                    "wb"
                )
                _close = True

            if compression == 6:
                fileobj.write(ifd.jpegIF)
            elif compression == 1:
                self.ifd.save(fileobj, idx=1)

            if _close:
                fileobj.close()
                del fileobj

    def dump_exif(self, f):
        """
        Save EXIF data in a separated file. If `f` is a file object, it is
        not closed.

        Arguments:
            f (buffer or string): a valid file path or a python file object
        """
        fileobj, _close = _fileobj(f, "wb")
        self.ifd.save(fileobj)
        if _close:
            fileobj.close()
            del fileobj


# if PIL exists do some overridings
try:
    from PIL import Image as _Image
except ImportError:
    pass
else:

    def _getmeta(im):
        for _, data in im.applist:
            if data[:6] == b'Exif\x00\x00':
                fileobj = io.BytesIO(data[6:])
                setattr(im, "ifd", TiffFile(fileobj))
                fileobj.close()
            elif data[:29] == b'http://ns.adobe.com/xap/1.0/\x00':
                setattr(im, "xmp", xmp.fromstring(data[29:]))

    def _getexif(im):
        if not hasattr(im, "ifd"):
            try:
                data = im.info["exif"]
            except KeyError:
                return None
            # b'Exif\x00\x00' -> 6 bytes
            fileobj = io.BytesIO(data[6:])
            setattr(im, "ifd", TiffFile(fileobj))
            fileobj.close()
            del fileobj
        return im.ifd

    class Image(_Image.Image):
        """
        Pillow Image class override.
        """

        # keep a reference of original PIL Image object
        _image_ = _Image.Image

        @staticmethod
        def open(*args, **kwargs):
            img = _Image.open(*args, **kwargs)
            img._getmeta()
            return img

        def save(self, fp, format=None, **params):
            if (
                isinstance(fp, str) and
                os.path.splitext(fp)[-1].lower() in [".jpg", ".jpeg"]
                or
                isinstance(format, str) and
                format.lower() == "jpeg"
            ) and not params.pop("strip_exif", False):
                self._getexif()
                stringio = StringIO()
                self.ifd.save(stringio, idx=0, ifd1=self.ifd[1])
                data = stringio.getvalue()
                params["exif"] = b'Exif\x00\x00' + (
                    data if isinstance(data, bytes) else
                    data.encode("utf-8")
                )
                stringio.close()
                del stringio, data
            if hasattr(self, "xmp"):
                params["xmp"] = b'http://ns.adobe.com/xap/1.0/\x00' + \
                    xmp.tostring(self.xmp)
            return Image._image_.save(self, fp, format, **params)

    #: Pillow override
    _Image.Image = Image

    from PIL import JpegImagePlugin
    JpegImagePlugin._getexif = _getexif
    JpegImagePlugin.JpegImageFile._getmeta = _getmeta
    del _getexif, _getmeta

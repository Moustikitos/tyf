# -*- encoding:utf-8 -*-
__copyright__ = """Copyright © 2015-2020
http://bruno.thoorens.free.fr/licences/tyf.html"""
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

unpack = lambda fmt, fileobj: \
    struct.unpack(fmt, fileobj.read(struct.calcsize(fmt)))
pack = lambda fmt, fileobj, value: \
    fileobj.write(struct.pack(fmt, *value))

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
    # import urllib.request as urllib
else:
    TYPES[2] = ("c", "ASCII")
    TYPES[7] = ("c", "UDEFINED")
    from StringIO import StringIO
    # import urllib
    reduce = __builtins__["reduce"]

from Tyf import ifd, gkd, tags


def _read_IFD(obj, fileobj, offset, byteorder="<", db=None):
    # fileobj seek must be on the start offset
    fileobj.seek(offset)
    # get number of entry
    nb_entry, = unpack(byteorder+"H", fileobj)
    next_ifd_offset = offset + struct.calcsize("=H" + nb_entry*"HHLL")
    # for each entry
    for i in range(nb_entry):
        obj.append(ifd.Tag.read(fileobj, byteorder, db=db))
    return next_ifd_offset


def _from_buffer(obj, fileobj, offset, byteorder="<"):
    # read data from offset and get next ifd offset
    next_ifd_offset = _read_IFD(obj, fileobj, offset, byteorder)
    # read sub IFD if any
    sub_ifd_keys = \
        set(["GPS IFD", "Exif IFD", "Interoperability IFD"]) & set(obj.keys())
    for key in sub_ifd_keys:
        dic = getattr(
            tags,
            "gpsT" if "GPS" in key else
            "exfT" if "Exif" in key else
            "itrT"
        )
        _read_IFD(
            obj, fileobj, obj[key].value, byteorder,
            db=dict([(i[0], i[-1][0]) for i in dic.items()])
        )
    fileobj.seek(next_ifd_offset)
    next_ifd, = unpack(byteorder+"L", fileobj)
    return next_ifd


def _write_IFD(obj, fileobj, offset, byteorder="<", ifd1=None):

    geokey = gkd.Gkd.from_ifd(obj)
    if len(geokey):
        geokey.compute()
        obj["GeoKeyDirectoryTag"] = geokey._34735
        obj["GeoDoubleParamsTag"] = geokey._34736
        obj["GeoAsciiParamsTag"] = geokey._34737

    ifds = obj.pack()
    if isinstance(ifd1, ifd.Ifd):
        ifds.update(ifd1=ifd1.pack()["root"])

    # compute exif, gps and interoperability offsets
    ifd_size = ifds["root"]["size"]
    ifd_values = ifds["root"]["data"]

    # where to put ifd values
    ifd_offset_values = offset + ifd_size
    # where to put the next sub ifd
    sub_ifd_offset = ifd_offset_values + len(ifd_values)

    # compute all possible sub ifd offsets
    for name in [n for n in ["exfT", "gpsT", "itrT"] if n in ifds]:
        i = ifds[name]
        tag = \
            "Exif IFD" if name == "exfT" else \
            "GPS IFD" if name == "gpsT" else \
            "Interoperability IFD"
        obj[tag].value = sub_ifd_offset
        # increment the next sub ifd offset
        sub_ifd_offset += i["size"] + len(i["data"])

    # if ifd1 given (thumbnail), reserve needed space before raster data
    if "ifd1" in ifds:
        raster_offset = \
            sub_ifd_offset + ifds["ifd1"]["size"] + \
            len(ifds["ifd1"]["data"]) + ifds["ifd1"]["raster"]
    # else raster data can follow the last sub ifd
    else:
        raster_offset = sub_ifd_offset

    # compute raster positions
    for tag in [
        t for t in
        ["StripOffsets", "TileOffsets", "FreeOffsets", "JPEGInterchangeFormat"]
        if t in dict.keys(obj)
    ]:
        if "Offset" in tag:
            raster_offsets = (raster_offset,)
            tagname = tag.replace("Offsets", "ByteCounts")
            bytecounts = obj[tagname].value
            if isinstance(bytecounts, tuple):
                for bytecount in obj[tagname].value:
                    raster_offsets += (raster_offsets[-1] + bytecount, )
            obj[tag].value = raster_offsets
        else:  # JPEGInterchangeFormat
            obj[tag].value = raster_offset

    # recompute all modified tags
    ifds = obj.pack()
    if isinstance(ifd1, ifd.Ifd):
        ifds.update(ifd1=ifd1.pack()["root"])

    raster_offset += len(ifds["root"]["data"]) - len(ifd_values)

    for key in [
        k for k in ["root", "exfT", "gpsT", "itrT"]
        if k in ifds
    ]:
        packed = ifds[key]
        if key == "root":
            fileobj.seek(offset)
            data_offset = ifd_offset_values
        else:
            sub_ifd_offset = obj[
                "Exif IFD" if key == "exfT" else
                "GPS IFD" if key == "gpsT" else
                "Interoperability IFD"
            ].value
            fileobj.seek(sub_ifd_offset)
            data_offset = \
                sub_ifd_offset + packed["size"]

        tags = packed["tags"]
        # write number of entries
        pack(byteorder+"H", fileobj, (len(tags),))
        # write all ifd entries and data
        for entry, data, is_offset in tags:
            fileobj.write(entry)
            if not is_offset:
                fileobj.write(data)
            else:
                pack(byteorder+"L", fileobj, (data_offset, ))
                data_offset += len(data)

        if key == "root":
            next_ifd_offset = fileobj.tell()

        pack(byteorder+"L", fileobj, (0, ))
        fileobj.write(packed["data"])

    # write IFD1
    if "ifd1" in ifds:
        ifd1_offset = fileobj.tell()
        fileobj.seek(next_ifd_offset)
        pack(byteorder+"L", fileobj, (ifd1_offset, ))
        _write_IFD(ifd1, fileobj, ifd1_offset, byteorder="<", ifd1=None)

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
    if hasattr(f, "close"):
        fileobj = f
        _close = False
    else:
        fileobj = io.open(f, mode)
        _close = True
    return fileobj, _close


class TiffFile(list):

    gkd = property(
        lambda obj: [gkd.Gkd.from_ifd(ifd) for ifd in obj],
        None, None, "list of geotiff directory"
    )
    raster_loaded = property(
        lambda obj: reduce(
            operator.__and__, [ifd.raster_loaded for ifd in obj]
        ),
        None, None, ""
    )

    def __init__(self, fileobj):
        # determine byteorder
        first, = unpack(">H", fileobj)
        byteorder = "<" if first == 0x4949 else ">"

        magic_number, = unpack(byteorder+"H", fileobj)
        if magic_number not in [0x732E, 0x2A]:  # 29486, 42
            fileobj.close()
            if magic_number == 0x2B:  # 43
                raise IOError("BigTIFF file not supported")
            else:
                raise IOError("Bad magic number. Not a valid TIFF file")
        next_ifd, = unpack(byteorder+"L", fileobj)

        ifds = []
        while next_ifd != 0:
            i = ifd.Ifd(
                tag_name="Tiff tag", tag_family=[tags.bTT, tags.pTT, tags.xTT]
            )
            next_ifd = _from_buffer(i, fileobj, next_ifd, byteorder)
            ifds.append(i)

        if hasattr(fileobj, "name"):
            self._filename = fileobj.name
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

        if hasattr(fileobj, "close"):
            fileobj.close()
        del fileobj


class JpegFile(list):

    ifd0 = property(
        lambda obj: getattr(obj, "ifd")[0],
        None, None, "Image IFD"
    )
    ifd1 = property(
        lambda obj: getattr(obj, "ifd")[1],
        None, None, "Thumbnail IFD"
    )

    def __init__(self, fileobj):
        sgmt = []

        fileobj.seek(0)
        marker, = unpack(">H", fileobj)
        if marker != 0xffd8:
            raise Exception("not a valid jpeg file")

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
                    sgmt.append((0xffe1, self.ifd))
                elif b"ns.adobe.com" in data[:30]:
                    self.xmp = xmp.fromstring(data[data.find(b"\x00")+1:])
                    sgmt.append((0xffe1, self.xmp))
            else:
                sgmt.append((marker, fileobj.read(count-2)))

        list.__init__(self, sgmt)

    def save(self, f):
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
                    value = b"Exif\x00\x00" + string.getvalue()
                    string.close()
                elif isinstance(value, xmp.Element):
                    value = \
                        b'http://ns.adobe.com/xap/1.0/\x00' + \
                        xmp.tostring(self.xmp)
                pack(">HH", fileobj, (marker, len(value) + 2))

            else:
                pack(">HH", fileobj, (marker, len(value) + 2))

            fileobj.write(value)

        pack(">H", fileobj, (0xffd9,))

        if hasattr(fileobj, "close"):
            fileobj.close()
        del fileobj

    def save_thumbnail(self, f):
        try:
            ifd = self.ifd1
        except IndexError:
            pass
        else:
            compression = ifd[259].value
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

    def dump_exif(self, f):
        fileobj, _close = _fileobj(f, "wb")
        self.ifd.save(fileobj)
        if _close:
            fileobj.close()

    def strip_exif(self):
        ifd = self.ifd  # strip thumbnail(s?)
        ifd0 = self.ifd0
        while len(ifd) > 1:
            ifd.pop(-1)
        for key in list(k for k in dict.__iter__(ifd0) if k not in tags.bTT):
            ifd0.pop(key)


def open(f):
    fileobj, _close = _fileobj(f, "rb")

    first, = unpack(">H", fileobj)
    fileobj.seek(0)

    if first == 0xffd8:
        obj = JpegFile(fileobj)
    elif first in [0x4d4d, 0x4949]:
        obj = TiffFile(fileobj)

    if _close:
        fileobj.close()

    try:
        return obj
    except Exception:
        raise Exception("file is not a valid JPEG nor TIFF image")


# if PIL exists do some overridings
try:
    from PIL import Image as _Image
except ImportError:
    pass
else:
    def _getexif(im):
        try:
            data = im.info["exif"]
        except KeyError:
            return None
        # b'Exif\x00\x00' -> 6 bytes
        fileobj = io.BytesIO(data[6:])
        exif = TiffFile(fileobj)
        fileobj.close()
        del fileobj
        return exif

    class Image(_Image.Image):

        # keep a reference of original PIL Image object
        _image_ = _Image.Image

        @staticmethod
        def open(*args, **kwargs):
            return _Image.open(*args, **kwargs)

        def save(self, fp, format="JPEG", **params):
            params["exif"] = self.info["exif"]
            return Image._image_.save(self, fp, format="JPEG", **params)

    _Image.Image = Image

    from PIL import JpegImagePlugin
    JpegImagePlugin._getexif_ = JpegImagePlugin._getexif
    JpegImagePlugin._getexif = _getexif
    del _getexif

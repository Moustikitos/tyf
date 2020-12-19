# -*- encoding:utf-8 -*-
"""
``Tyf.decoders`` module defines simple definition to translate unpacked ifd tag
value to python one.
"""

import datetime


def _1(value):
    """
    Integer decoder.
    ```python
    >>> from Tyf import decoders
    >>> decoders._1((1, ))
    1
    >>> decoders._1((1.0, "6", 0b111))
    (1, 6, 7)
    ```
    """
    return int(value[0]) if len(value) == 1 else tuple(int(v) for v in value)


def _2(value):
    return value[:-1].decode("utf-8")


#: see Tyf.decoders._1
_3 = _1
#: see Tyf.decoders._1
_4 = _1


def _5(value):
    result = tuple(
        (float(n) / (1 if d == 0 else d))
        for n, d in zip(value[0::2], value[1::2])
    )
    return result[0] if len(result) == 1 else result


#: see Tyf.decoders._1
_6 = _1


def _7(value):
    return value


#: see Tyf.decoders._1
_8 = _1
#: see Tyf.decoders._1
_9 = _1
#: see Tyf.decoders._5
_10 = _5


def _11(value):
    return \
        float(value[0]) if len(value) == 1 else \
        tuple(float(v) for v in value)


#: see Tyf.decoders._11
_12 = _11


# PrivateTiffTag

def XPTitle(value):
    return "".join(chr(e) for e in value[0::2]).replace("\x00", "")


XPComment = XPAuthor = XPKeywords = XPSubject = XPTitle


def UserComment(value):
    return value[8:].decode("ascii", errors="ignore")


# ExifTag

def DateTime(value):
    return datetime.datetime.strptime(_2(value), "%Y:%m:%d %H:%M:%S")


DateTimeOriginal = DateTimeDigitized = DateTime


# GpsTag

def _deg(d, m, s):
    return d + (m + s / 60.) / 60.


def GPSLatitude(value):
    return _deg(*_5(value))


GPSLongitude = GPSLatitude


def GPSAltitudeRef(value):
    return _3(value)


def GPSAltitude(value):
    return _5(value)


def GPSTimeStamp(value):
    return datetime.time(*[int(e) for e in _5(value)])


def GPSDateStamp(value):
    dt = datetime.datetime.strptime(_2(value), "%Y:%m:%d")
    return datetime.date(dt.year, dt.month, dt.day)

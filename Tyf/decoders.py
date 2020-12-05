# -*- encoding:utf-8 -*-

import datetime


def _1(value):
    return int(value[0]) if len(value) == 1 else tuple(int(v) for v in value)


_3 = _4 = _6 = _8 = _9 = _1


def _2(value):
    return value[:-1].decode("utf-8")


def _5(value):
    result = tuple(
        (float(n) / (1 if d == 0 else d))
        for n, d in zip(value[0::2], value[1::2])
    )
    return result[0] if len(result) == 1 else result


def _7(value):
    return value


_10 = _5


def _11(value):
    return \
        float(value[0]) if len(value) == 1 else \
        tuple(float(v) for v in value)


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


def GPSLatitudeRef(value):
    return \
        True if value in [b"N\x00", b"N"] else \
        False if value in [b"S\x00", b"S"] else \
        None


def GPSLatitude(value):
    return _deg(*_5(value))


def GPSLongitudeRef(value):
    return \
        True if value in [b"E\x00", b"E"] else \
        False if value in [b"W\x00", b"W"] else \
        None


GPSLongitude = GPSLatitude


def GPSAltitudeRef(value):
    return bool(_3(value))


def GPSAltitude(value):
    return _5(value)


GPSTimeStamp = lambda value: datetime.time(*[int(e) for e in _5(value)])


def GPSDateStamp(value):
    dt = datetime.datetime.strptime(_2(value), "%Y:%m:%d")
    return datetime.date(dt.year, dt.month, dt.day)

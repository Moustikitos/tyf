# -*- encoding:utf-8 -*-
# Copyright © 2015-2016, THOORENS Bruno - http://bruno.thoorens.free.fr/licences/tyf.html

from Tyf import reduce

import math
import fractions


_m_u_short = 0
_M_u_short = 2**8
_m_u_byte = 0
_M_u_byte = 2**16
_m_u_long = 0
_M_u_long = 2**32

_m_s_short = -_M_u_short / 2
_M_s_short = _M_u_short / 2 - 1
_m_s_byte = -_M_u_byte / 2
_M_s_byte = _M_u_byte / 2 - 1
_m_s_long = -_M_u_long / 2
_M_s_long = _M_u_long / 2 - 1

_m_float = 1.17549e-38
_M_float = 3.40282e38
_m_double = 2.22507e-308
_M_double = 1.79769e308


class EncodingException(Exception):
    pass


def in_range(value, mini, maxi, cast=int):
    value = cast(value)
    if mini <= value < maxi:
        return value
    else:
        raise EncodingException(
            "%s not in range [%r:%r[" % (value, mini, maxi)
        )


def _1(value):
    if isinstance(value, tuple):
        return tuple(in_range(v, _m_u_short, _M_u_short) for v in value)
    else:
        return (in_range(value, _m_u_short, _M_u_short), )


def _2(value):
    if not isinstance(value, bytes):
        try:
            value = value.encode("utf-8")
        except Exception:
            raise EncodingException(
                "%s can not be encoded" % (value, )
            )
    if len(value) == 0:
        return b"\x00"
    else:
        return value + (b"\x00" if value[-1] != b"\x00" else "")


def _3(value):
    if isinstance(value, tuple):
        return tuple(in_range(v, _m_u_byte, _M_u_byte) for v in value)
    else:
        return (in_range(value, _m_u_byte, _M_u_byte), )


def _4(value):
    if isinstance(value, tuple):
        return tuple(in_range(v, _m_u_long, _M_u_long) for v in value)
    else:
        return (in_range(value, _m_u_long, _M_u_long), )


def _rational_yielder(*values):
    cnt = 0
    for v in values:
        if isinstance(v, int):
            cnt += 1
            yield (v, )
        else:
            if isinstance(v, float):
                v = str(v)
            f = fractions.Fraction(v).limit_denominator(10000000)
            cnt += 2
            yield (f.numerator, f.denominator)

    if cnt % 2:
        yield (1, )


def _5(value):
    if not isinstance(value, tuple):
        value = (value, )
    try:
        reduced = reduce(tuple.__add__, _rational_yielder(*value))
        return tuple(in_range(v, _m_u_long, _M_u_long) for v in reduced)
    except Exception:
        raise EncodingException(
            "%s can not be encoded as unsigned rational number(s)" % (value, )
        )


def _6(value):
    if isinstance(value, tuple):
        return tuple(in_range(v, _m_s_short, _M_s_short) for v in value)
    else:
        return (in_range(value, _m_s_short, _M_s_short), )


def _7(value):
    if not isinstance(value, bytes):
        value = value.encode("utf-8")
    return value


def _8(value):
    if isinstance(value, tuple):
        return tuple(in_range(v, _m_s_byte, _M_s_byte) for v in value)
    else:
        return (in_range(value, _m_s_byte, _M_s_byte), )


def _9(value):
    if isinstance(value, tuple):
        return tuple(in_range(v, _m_s_long, _M_s_long) for v in value)
    else:
        return (in_range(value, _m_s_long, _M_s_long), )


def _10(value):
    if not isinstance(value, tuple):
        value = (value, )
    try:
        reduced = reduce(tuple.__add__, _rational_yielder(*value))
        return tuple(in_range(v, _m_s_long, _M_s_long) for v in reduced)
    except Exception:
        raise EncodingException(
            "%s can not be encoded as unsigned rational number(s)" % (value, )
        )


def _11(value):
    if isinstance(value, tuple):
        return tuple(
            in_range(v, _m_float, _M_float, cast=float) for v in value
        )
    else:
        return (in_range(value, _m_float, _M_float, cast=float), )


def _12(value):
    if isinstance(value, tuple):
        return tuple(
            in_range(v, _m_double, _M_double, cast=float) for v in value
        )
    else:
        return (in_range(value, _m_double, _M_double, cast=float), )


# PrivateTiffTag:

def XPTitle(value):
    return reduce(tuple.__add__, [(ord(e), 0) for e in value]) + (0, 0)


XPComment = XPAuthor = XPKeywords = XPSubject = XPTitle


def UserComment(value):
    return b"ASCII\x00\x00\x00" + (
        value.encode("ascii", errors="replace")
        if not isinstance(value, bytes) else value
    )


# ExifTag:

def DateTime(value):
    try:
        return _2(value.strftime("%Y:%m:%d %H:%M:%S"))
    except Exception:
        raise EncodingException(
            "%s is not a valide datetime object" % (value, )
        )


DateTimeOriginal = DateTimeDigitized = DateTime


# class GpsTag:

def _dms(value, limit=180, epsilon=0.0001):
    value = abs(value) % limit

    degrees = float(math.floor(value))
    minutes = (value - degrees) * 60.0
    seconds = (minutes - math.floor(minutes)) * 60.0
    minutes = float(math.floor(minutes))

    if seconds >= (60. - epsilon):
        seconds, minutes = 0., minutes + 1.0
    if minutes >= (60. - epsilon):
        minutes, degrees = 0., degrees + 1.0

    return degrees, minutes, seconds


GPSProcessingMethod = UserComment


def GPSLatitudeRef(value):
    return b"N\x00" if bool(value) else b"S\x00"


def GPSLatitude(value):
    if isinstance(value, (int, float)):
        return _5(_dms(value, limit=90))


def GPSLongitudeRef(value):
    return b"E\x00" if bool(value) else b"W\x00"


def GPSLongitude(value):
    if isinstance(value, (int, float)):
        return _5(_dms(value, limit=180))


def GPSAltitudeRef(value):
    return _3(1 if bool(value) else 0)


def GPSAltitude(value):
    return _5(abs(value))


def GPSTimeStamp(value):
    try:
        return _5(tuple(
            float(e)
            for e in [value.hour, value.minute, value.second]
        ))
    except Exception:
        raise EncodingException(
            "%s is not a valide date object" % (value, )
        )


def GPSDateStamp(value):
    try:
        return _2(value.strftime("%Y:%m:%d"))
    except Exception:
        raise EncodingException(
            "%s is not a valide time object" % (value, )
        )

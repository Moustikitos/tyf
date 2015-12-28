# -*- encding:utf-8 -*-
# Copyright 2012-2015, THOORENS Bruno - http://bruno.thoorens.free.fr/licences/tyf.html
from . import reduce

_m_short = 0
_M_short = 2**8
def _1(value):
	value = int(value)
	return (_m_short, ) if value < _m_short else \
	       (_M_short, ) if value > _M_short else \
	       (value, )

def _2(value):
	if not isinstance(value, bytes):
		value = value.encode()
		value += b"\x00" if value[-1] != b"\x00" else ""
	return value

_m_byte = 0
_M_byte = 2**16
def _3(value):
	value = int(value)
	return (_m_byte, ) if value < _m_byte else \
	       (_M_byte, ) if value > _M_byte else \
	       (value, )

_m_long = 0
_M_long = 2**32
def _4(value):
	value = int(value)
	return (_m_long, ) if value < _m_long else \
	       (_M_long, ) if value > _M_long else \
	       (value, )

def _5(value):
	if not isinstance(value, tuple): value = (value, )
	return reduce(tuple.__add__, [(f.numerator, f.denominator) for f in [fractions.Fraction(str(v)) for v in value]])

_m_s_short = -_M_short/2
_M_s_short = _M_short/2-1
def _6(value):
	value = int(value)
	return (_m_s_short, ) if value < _m_s_short else \
	       (_M_s_short, ) if value > _M_s_short else \
	       (value, )

def _7(value):
	if not isinstance(value, bytes):
		value = value.encode()
	return value

_m_s_byte = -_M_byte/2
_M_s_byte = _M_byte/2-1
def _8(value):
	value = int(value)
	return (_m_s_byte, ) if value < _m_s_byte else \
	       (_M_s_byte, ) if value > _M_s_byte else \
	       (value, )

_m_s_long = -_M_long/2
_M_s_long = _M_long/2-1
def _9(value):
	value = int(value)
	return (_m_s_long, ) if value < _m_s_long else \
	       (_M_s_long, ) if value > _M_s_long else \
	       (value, )

_10 = _5

def _11(value):
	return (float(value), )

_12 = _11


_0x9c9b = _0x9c9c = _0x9c9d = lambda value : reduce(tuple.__add__, [(ord(e), 0) for e in value]) #"".join(chr(e) for e in value[0::2]).encode()

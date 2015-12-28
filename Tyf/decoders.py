# -*- encding:utf-8 -*-
# Copyright 2012-2015, THOORENS Bruno - http://bruno.thoorens.free.fr/licences/tyf.html

_1 = _3 = _4 = _6 = _8 = _9 = _11 = _12 = lambda value: value[0] if len(value) == 1 else value

_2 = lambda value: value[:-1]

def _5(value):
	result = tuple((float(n)/(1 if d==0 else d)) for n,d in zip(value[0::2], value[1::2]))
	return result[0] if len(result) == 1 else result

_7 = lambda value: value

_10 = _5

_0x9c9b = _0x9c9c = _0x9c9d = lambda value : "".join(chr(e) for e in value[0::2]).encode()[:-1]

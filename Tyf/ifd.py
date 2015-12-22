# -*- encoding: utf-8 -*-
# Copyright 2012-2015, THOORENS Bruno - http://bruno.thoorens.free.fr/licences/tyf.html

from . import tags, reduce, values, TYPES
import struct, fractions

_TAGS = {}
_TAGS.update(tags.bTT)
_TAGS.update(tags.xTT)
_TAGS.update(tags.pTT)
_TAGS.update(tags.exfT)
_TAGS.update(tags.gpsT)

_2TAG = dict((v[0], t) for t,v in _TAGS.items())
_2KEY = dict((v, k) for k,v in _2TAG.items())

# here are some functions to convert python value
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


class TiffTag(object):


	# defaults values
	comment = "Undefined tag"
	meaning = None
	key = "Unknown"
	tag = 0x0
	type = 0
	count = 0
	value = None
	name = "Tag"

	def __init__(self, tag=0x0, value=None, type=None, name="Tiff tag"):
		self.key, _typ, default, self.comment = _TAGS.get(tag, ("Unknown", [0], None, "Undefined tag 0x%x"%tag))
		self.type = _typ[-1] if type == None else type
		self.tag = tag
		self.name = name
		if value != None:
			self._fix(value)

	def _fix(self, value):
		exec("self.value = _%d(value)" % self.type)
		restricted = getattr(values, self.key, None)
		if restricted != None:
			self.meaning = restricted.get(value, "no description found [%r]" % (self.value,))
		self.count = len(self.value) // (1 if self.type not in [5,10] else 2)
		self._determine_if_offset()

	def _unfix(self):
		if self.type in [5, 10]:
			result = tuple((float(n)/(1 if d==0 else d)) for n,d in zip(self.value[0::2], self.value[1::2]))
			return result[0] if self.count == 1 else result
		elif self.type in [2]:
			return self.value[:-1]
		elif self.count == 1:
			return self.value[0]
		else:
			return self.value

	def __repr__(self):
		return "<%s : %s (0x%x) = %s>" % (self.name, self.key, self.tag, self._unfix()) + ("" if not self.meaning else ' :: "%s"'%self.meaning)

	def _determine_if_offset(self):
		if self.count == 1 and self.type in [1, 2, 3, 4, 6, 7, 8, 9]: setattr(self, "value_is_offset", False)
		elif self.count <= 3 and self.type in [2]: setattr(self, "value_is_offset", False)
		elif self.count <= 2 and self.type in [3, 8]: setattr(self, "value_is_offset", False)
		elif self.count <= 4 and self.type in [1, 6, 7]: setattr(self, "value_is_offset", False)
		else: setattr(self, "value_is_offset", True)

	def _fill(self):
		s = struct.calcsize(TYPES[self.type][0])
		voidspace = (struct.calcsize("L") - self.count*s)//s
		if self.type in [2, 7]: return self.value + b"\x00"*voidspace
		elif self.type in [1, 3, 6, 8]: return self.value + ((0,)*voidspace)
		return self.value

	def calcsize(self):
		return struct.calcsize(TYPES[self.type][0] * (self.count*(2 if self.type in [5,10] else 1))) if self.value_is_offset else 0


class Ifd(dict):
	tagname = "Tiff Tag"
	readonly = [259, 270, 271, 272, 301, 306, 318, 319, 529, 532, 33432]

	has_raster = property(lambda obj: bool(len(obj.stripes+obj.tiles+obj.free)), None, None, "")
	raster = property(lambda obj: reduce(bytes.__add__, obj.stripes+obj.tiles+obj.free), None, None, "")

	size = property(
		lambda obj: {
			"ifd": struct.calcsize("H" + (len(obj)*"HHLL") + "L"),
			"data": reduce(int.__add__, [t.calcsize() for t in dict.values(obj)])
		}, None, None, "")

	def __init__(self, *args, **kwargs):
		dict.__init__(self)
		setattr(self, "tagname", kwargs.get("tagname", "Tiff tag"))

		self.private_ifd = {}
		self.stripes = ()
		self.tiles = ()
		self.free = ()
		self.jpegIF = b""

	def __setitem__(self, tag, value):
		if isinstance(tag, str): tag = _2TAG[tag]
		if tag in tags.exfT:
			if not 34665 in self.private_ifd:
				self.addtag(TiffTag(34665, 0, name=self.tagname))
				self.private_ifd[34665] = Ifd(tagname="Exif tag")
			self.private_ifd[34665].addtag(TiffTag(tag, value))
		elif tag in tags.gpsT:
			if not 34853 in self.private_ifd:
				self.addtag(TiffTag(34853, 0, name=self.tagname))
				self.private_ifd[34853] = Ifd(tagname="GPS tag")
			self.private_ifd[34853].addtag(TiffTag(tag, value))
		else:
			dict.__setitem__(self, tag, TiffTag(tag, value, name=self.tagname))

	def __getitem__(self, tag):
		for i in self.private_ifd.values():
			try: return i[tag]
			except KeyError: pass
		if isinstance(tag, str): tag = _2TAG[tag]
		return dict.__getitem__(self, tag)._unfix()

	def set(self, tag, typ, count, value):
		tifftag = TiffTag(tag=tag, type=typ, name=self.tagname)
		tifftag.count = count
		tifftag.value = (value,) if count == 1 and typ not in [5, 10] else value
		tifftag._determine_if_offset()
		restricted = getattr(values, tifftag.key, None)
		if restricted != None:
			tifftag.meaning = restricted.get(value, "no description found  [%r]" % (tifftag.value,))
		dict.__setitem__(self, tag, tifftag)

	def addtag(self, tifftag):
		if isinstance(tifftag, TiffTag):
			restricted = getattr(values, tifftag.key, None)
			if restricted != None:
				tifftag.meaning = restricted.get(tifftag.value[0], "no description found [%r]" % (tifftag.value,))
			dict.__setitem__(self, tifftag.tag, tifftag)

	def tags(self):
		for v in sorted(dict.values(self), key=lambda e:e.tag):
			yield v
		for i in self.private_ifd.values():
			for v in sorted(dict.values(i), key=lambda e:e.tag):
				yield v

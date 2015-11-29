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

	def __init__(self, tag=0x0, value=None, name="Tiff tag"):
		self.key, typ_, default, self.comment = _TAGS.get(tag, ("Unknown", -1, None, "Undefined tag 0x%x"%tag))
		self.tag = tag
		self.name = name
		self._determine_if_offset()

	def _unfix(self):
		if self.type in [5,10]:
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


class Ifd(dict):
	readonly = [259, 270, 271, 272, 301, 306, 318, 319, 529, 532, 33432]

	size = property(
		lambda obj: {
			"ifd": struct.calcsize("H" + len(obj)*"HHLL" + "L"),
			"data": struct.calcsize("".join(TYPES[typ][0]*count for (typ,count) in [(t.type,t.count) for t in dict.values(obj) if t.value_is_offset]))
		}, None, None, "")

	def __init__(self, *args, **kwargs):
		dict.__init__(self)

		self.private_ifd = {}
		self.stripes = ()
		self.tiles = ()
		self.free = ()
		self.jpegIF = b""

	def __getitem__(self, tag):
		for i in self.private_ifd.values():
			try: return i[tag]
			except KeyError: pass
		if isinstance(tag, str): tag = _2TAG[tag]
		return dict.__getitem__(self, tag)._unfix()

	def set(self, tag, typ, count, value, name="Tiff tag"):
		tifftag = TiffTag(tag=tag, name=name)
		tifftag.type = typ
		tifftag.count = count
		tifftag.value = (value,) if count == 1 and typ not in [5, 10] else value
		tifftag._determine_if_offset()
		restricted = getattr(values, tifftag.key, None)
		if restricted: tifftag.meaning = restricted.get(value, "no description found")
		dict.__setitem__(self, tag, tifftag)
	
	def addtag(self, tifftag):
		if isinstance(tifftag, TiffTag):
			tifftag.key, typ_, default, tifftag.comment = _TAGS.get(tifftag.tag, ("Unknown", -1, None, "Undefined tag 0x%x"%tifftag.tag))
			restricted = getattr(values, tifftag.key, None)
			if restricted:
				tifftag.meaning = restricted.get(tifftag.value[0])
			dict.__setitem__(self, tifftag.tag, tifftag)

	def tags(self):
		for v in sorted(dict.values(self), key=lambda e:e.tag):
			yield v
		for i in self.private_ifd.values():
			for v in sorted(dict.values(i), key=lambda e:e.tag):
				yield v

# -*- encoding: utf-8 -*-
# Copyright 2012-2015, THOORENS Bruno - http://bruno.thoorens.free.fr/licences/tyf.html

from . import tags, encoders, decoders, reduce, values, TYPES
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

	def __init__(self, tag=0x0, type=None, value=None, name="Tiff tag"):
		self.key, _typ, default, self.comment = _TAGS.get(tag, ("Unknown", [0], None, "Undefined tag 0x%x"%tag))
		self.tag = tag
		self.name = name

		self.type = _typ[-1] if type == None else type
		if value != None: self._encoder(value)

	def __setattr__(self, attr, value):
		if attr == "type":
			try:
				object.__setattr__(self, "_encode", getattr(encoders, "_%s"%hex(self.tag)))
			except AttributeError:
				object.__setattr__(self, "_encode", getattr(encoders, "_%s"%value))
			try:
				object.__setattr__(self, "_decode", getattr(decoders, "_%s"%hex(self.tag)))
			except AttributeError:
				object.__setattr__(self, "_decode", getattr(decoders, "_%s"%value))
		elif attr == "value":
			restricted = getattr(values, self.key, None)
			if restricted != None:
				v = value[0] if isinstance(value, tuple) else value
				self.meaning = restricted.get(v, "no description found [%r]" % (v,))
			self.count = len(value) // (1 if self.type not in [5,10] else 2)
			self._determine_if_offset()
		object.__setattr__(self, attr, value)

	def _encoder(self, value):
		self.value = self._encode(value)

	def _decoder(self):
		return self._decode(self.value)

	def __repr__(self):
		return "<%s : %s (0x%x) = %s>" % (self.name, self.key, self.tag, self._decoder()) + ("" if not self.meaning else ' :: "%s"'%self.meaning)

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
				self.addtag(TiffTag(34665, 4, 0, name=self.tagname))
				self.private_ifd[34665] = Ifd(tagname="Exif tag")
			self.private_ifd[34665].addtag(TiffTag(tag, value=value))
		elif tag in tags.gpsT:
			if not 34853 in self.private_ifd:
				self.addtag(TiffTag(34853, 4, 0, name=self.tagname))
				self.private_ifd[34853] = Ifd(tagname="GPS tag")
			self.private_ifd[34853].addtag(TiffTag(tag, value=value))
		else:
			dict.__setitem__(self, tag, TiffTag(tag, value=value, name=self.tagname))

	def __getitem__(self, tag):
		for i in self.private_ifd.values():
			try: return i[tag]
			except KeyError: pass
		if isinstance(tag, str): tag = _2TAG[tag]
		return dict.__getitem__(self, tag)._decoder()

	def set(self, tag, typ, count, value):
		tifftag = TiffTag(tag=tag, type=typ, name=self.tagname)
		tifftag.count = count
		tifftag.value = (value,) if count == 1 and typ not in [5, 10] else value
		dict.__setitem__(self, tag, tifftag)

	def addtag(self, tifftag):
		if isinstance(tifftag, TiffTag):
			dict.__setitem__(self, tifftag.tag, tifftag)

	def tags(self):
		for v in sorted(dict.values(self), key=lambda e:e.tag):
			yield v
		for i in self.private_ifd.values():
			for v in sorted(dict.values(i), key=lambda e:e.tag):
				yield v

# -*- encoding: utf-8 -*-
# Copyright 2012-2015, THOORENS Bruno - http://bruno.thoorens.free.fr/licences/tyf.html

from . import tags, encoders, decoders, reduce, values, TYPES
import struct, fractions

_TAGS = tags._TAGS
_2TAG = tags._2TAG
_2KEY = tags._2KEY


class TiffTag(object):

	# IFD entries values
	tag = 0x0
	type = 0
	count = 0
	value = None

	# end user side values
	key = "Undefined"
	name = "Undefined tag"
	comment = "Nothing about this tag"
	meaning = None

	def __init__(self, tag, type=None, value=None, name="Tiff tag"):
		if tag in _2TAG: tag = _2TAG[tag]
		self.key, _typ, default, self.comment = _TAGS.get(tag, ("Unknown", [0], None, "Undefined tag 0x%x"%tag))
		self.tag = tag
		self.name = name

		self.type = _typ[-1] if type == None else type
		if value != None: self._encode(value)
		elif default != None: self.value = (default,) if not hasattr(default, "len") else default

	def __setattr__(self, attr, value):
		if attr == "type":
			try: object.__setattr__(self, "_encoder", getattr(encoders, "_%s"%hex(self.tag)))
			except AttributeError: object.__setattr__(self, "_encoder", getattr(encoders, "_%s"%value))
			try: object.__setattr__(self, "_decoder", getattr(decoders, "_%s"%hex(self.tag)))
			except AttributeError: object.__setattr__(self, "_decoder", getattr(decoders, "_%s"%value))
		elif attr == "value":
			restricted = getattr(values, self.key, None)
			if restricted != None:
				v = value[0] if isinstance(value, tuple) else value
				self.meaning = restricted.get(v, "no description found [%r]" % (v,))
			self.count = len(value) // (1 if self.type not in [5,10] else 2)
			self._determine_if_offset()
		object.__setattr__(self, attr, value)

	def __repr__(self):
		return "<%s 0x%x: %s = %r>" % (self.name, self.tag, self.key, self.value) + ("" if not self.meaning else ' := %r'%self.meaning)

	def _encode(self, value):
		self.value = self._encoder(value)

	def _decode(self):
		return self._decoder(self.value)

	def _determine_if_offset(self):
		if self.count == 1 and self.type in [1, 2, 3, 4, 6, 7, 8, 9]: setattr(self, "value_is_offset", False)
		elif self.count <= 2 and self.type in [3, 8]: setattr(self, "value_is_offset", False)
		elif self.count <= 4 and self.type in [1, 2, 6, 7]: setattr(self, "value_is_offset", False)
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

	exif_ifd = property(lambda obj: obj.private_ifd.get(34665, {}), None, None, "shortcut toprivate ifd")
	gps_ifd = property(lambda obj: obj.private_ifd.get(34853, {}), None, None, "shortcut toprivate ifd")
	has_raster = property(lambda obj: bool(len(obj.stripes+obj.tiles+obj.free)), None, None, "return true if it contains raster data")
	raster = property(lambda obj: reduce(bytes.__add__, obj.stripes+obj.tiles+obj.free), None, None, "raster data")
	size = property(
		lambda obj: {
			"ifd": struct.calcsize("H" + (len(obj)*"HHLL") + "L"),
			"data": reduce(int.__add__, [t.calcsize() for t in dict.values(obj)])
		}, None, None, "return ifd-packed size and data-packed size")

	def __init__(self, *args, **kwargs):
		setattr(self, "tagname", kwargs.pop("tagname", "Tiff tag"))
		dict.__init__(self)

		self.private_ifd = {}
		self.stripes = ()
		self.tiles = ()
		self.free = ()
		self.jpegIF = b""

	def __setitem__(self, tag, value):
		if isinstance(tag, str): tag = _2TAG[tag]
		if tag in tags.exfT:
			if not 34665 in self.private_ifd:
				# self.addtag(TiffTag(34665, 4, 0, name=self.tagname))
				self.private_ifd[34665] = Ifd(tagname="Exif tag")
			self.private_ifd[34665].addtag(TiffTag(tag, value=value))
		elif tag in tags.gpsT:
			if not 34853 in self.private_ifd:
				# self.addtag(TiffTag(34853, 4, 0, name=self.tagname))
				self.private_ifd[34853] = Ifd(tagname="GPS tag")
			self.private_ifd[34853].addtag(TiffTag(tag, value=value))
		else:
			dict.__setitem__(self, tag, TiffTag(tag, value=value, name=self.tagname))

	def __getitem__(self, tag):
		for i in self.private_ifd.values():
			try: return i[tag]
			except KeyError: pass
		if isinstance(tag, str): tag = _2TAG[tag]
		return dict.__getitem__(self, tag)._decode()

	def _check_sub_ifd(self):
		for key in self.private_ifd:
			if key not in self:
				self.addtag(TiffTag(key, 4, 0, name=self.tagname))

	def set(self, tag, typ, count, value):
		tifftag = TiffTag(tag=tag, type=typ, name=self.tagname)
		tifftag.count = count
		tifftag.value = (value,) if count == 1 and typ not in [5, 10] else value
		dict.__setitem__(self, tag, tifftag)

	def get(self, tag):
		for i in self.private_ifd.values():
			if tag in i: return i.get(tag)
		return dict.get(self, _2TAG[tag] if isinstance(tag, str) else tag)

	def addtag(self, tifftag):
		if isinstance(tifftag, TiffTag):
			dict.__setitem__(self, tifftag.tag, tifftag)

	def tags(self):
		for v in sorted(dict.values(self), key=lambda e:e.tag):
			yield v
		for i in self.private_ifd.values():
			for v in sorted(dict.values(i), key=lambda e:e.tag):
				yield v

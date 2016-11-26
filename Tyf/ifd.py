# -*- encoding:utf-8 -*-
# Copyright 2012-2015, THOORENS Bruno - http://bruno.thoorens.free.fr/licences/tyf.html

from . import io, os, tags, encoders, decoders, reduce, values, TYPES, urllib, StringIO
import struct


class Tag(object):
	meaning = None

	def __init__(self, tag, value=None, **kwargs):
		db = kwargs.pop("db", False)
		self.name = kwargs.pop("name", "Orphan tag")
		if not db: tag, db = tags.get(tag)

		self.tag, (self.key, _typ, default, self.comment) = tag, db
		self.type = _typ[-1]

		if value != None: self._encode(value)
		elif default != None: self._encode(default)
		else: self.value = "" if self.type in [2,7] else ()

	def __setattr__(self, attr, value):
		# define encoder and decoder according to type
		if attr == "type":
			# find encoder
			hex_enc = "_%s"%hex(self.tag)
			if hasattr(encoders, hex_enc): object.__setattr__(self, "_encoder",  getattr(encoders, hex_enc))
			else: object.__setattr__(self, "_encoder", getattr(encoders, "_%s"%value))
			# find decoder
			hex_dec = "_%s"%hex(self.tag)
			if hasattr(decoders, hex_dec): object.__setattr__(self, "_decoder",  getattr(decoders, hex_dec))
			else: object.__setattr__(self, "_decoder", getattr(decoders, "_%s"%value))
		# 
		elif attr == "value":
			restricted = getattr(values, self.key, None)
			if restricted != None:
				v = value[0] if isinstance(value, tuple) and len(value) == 1 else value
				self.meaning = restricted.get(v, "no description found ["+str(v)+"]")
			self.count = len(value) // (1 if self.type not in [5,10] else 2)
			self._determine_if_offset()
		object.__setattr__(self, attr, value)

	def __repr__(self):
		return "<%s 0x%x: %s = %r>" % (self.name, self.tag, self.key, self.value) + ("" if not self.meaning else ' :: %s'%self.meaning)

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
		if not self.value_is_offset:
			s = struct.calcsize("="+TYPES[self.type][0])
			voidspace = (struct.calcsize("=L") - self.count*s)//s
			if self.type in [2, 7]: return self.value + b"\x00"*voidspace
			elif self.type in [1, 3, 6, 8]: return self.value + ((0,)*voidspace)
		return self.value

	def calcsize(self):
		return struct.calcsize("=" + TYPES[self.type][0] * (self.count*(2 if self.type in [5,10] else 1))) if self.value_is_offset else 0


class Ifd(dict):
	# possible sub IFD with according tag, sub IFD name and tags family
	sub_ifd = {
		34665: ("Exif tag", tags.exfT),
		34853: ("GPS tag", tags.gpsT),
		40965: ("Interop tag", tags.itrT),
	}

	size = property(
		lambda obj: {
			"ifd": struct.calcsize("=H" + (len(obj)*"HHLL") + "L"),
			"data": reduce(int.__add__, [t.calcsize() for t in dict.values(obj)])
		}, None, None, "return ifd-packed size and data-packed size")

	interop = property(lambda obj: getattr(obj, "_40965", {}), None, None, "shortcut to Interoperability sub ifd")
	exif = property(lambda obj: getattr(obj, "_34665", {}), None, None, "shortcut to EXIF sub ifd")
	gps = property(lambda obj: getattr(obj, "_34853", {}), None, None, "shortcut to GPS sub ifd")
	has_raster = property(lambda obj: 273 in obj or 288 in obj or 324 in obj or 513 in obj, None, None, "return true if it contains raster data")
	raster_loaded = property(lambda obj: not(obj.has_raster) or bool(len(obj.stripes+obj.tiles+obj.free)+len(obj.jpegIF)), None, None, "")

	def __init__(self, **kwargs):
		self.tag_name = kwargs.pop("tag_name", "Tiff tag")
		self.tag_family = kwargs.pop("tag_family", [tags.bTT])

		dict.__init__(self)

		self.stripes = ()
		self.tiles = ()
		self.free = ()
		self.jpegIF = b""

	def __iter__(self):
		for tag in self.tags():
			yield tag.key, tag._decode()

	def __setitem__(self, tag, value):
		for tf in self.tag_family:
			tag = tags._2tag(tag, family=tf)
			if tag in tf:
				if tag in Ifd.sub_ifd:
					name, family = Ifd.sub_ifd[tag]
					setattr(self, "_%s"%tag, value if isinstance(value, Ifd) else Ifd(tag_name=name, tag_family=[family]))
					dict.__setitem__(self, tag, Tag(tag, 0, name=self.tag_name, db=tf[tag]))
				else:
					dict.__setitem__(self, tag, Tag(tag, value, name=self.tag_name, db=tf[tag]))
				return
		raise KeyError("%s tag not a valid tag for this ifd" % tag)

	def __getitem__(self, tag):
		for tf in self.tag_family:
			tag = tags._2tag(tag, family=tf)
			if tag in tf:
				if tag in Ifd.sub_ifd:
					if not hasattr(self, "_%s"%tag):
						name, family = Ifd.sub_ifd[tag]
						setattr(self, "_%s"%tag, Ifd(tag_name=name, tag_family=[family]))
						dict.__setitem__(self, tag, Tag(tag, 0, name=self.tag_name, db=tf[tag]))
					return getattr(self, "_%s"%tag)
				return dict.__getitem__(self, tag)._decode()
		return dict.__getitem__(self, tag)

	def __delitem__(self, tag):
		for tf in self.tag_family:
			tag = tags._2tag(tag, family=tf)
			if tag in tf:
				if tag in Ifd.sub_ifd:
					if hasattr(self, "_%s"%tag): delattr(self, "_%s"%tag)
					else: raise KeyError("Ifd does not contains %s sub ifd" % tag)
				return dict.__delitem__(self, tag)
		return dict.__delitem__(self, tag)

	def from_db(self, tag):
		for tf in self.tag_family:
			if tag in tf: return tf[tag]
		return ("Undefined", [7], None, "Undefined tag %r"%tag)

	def set(self, tag, typ, value):
		for tf in self.tag_family:
			tag = tags._2tag(tag, family=tf)
			if tag in tf:
				obj = Tag(tag, name=self.tag_name, db=tf[tag])
				obj.type = typ
				obj.value = (value,) if not hasattr(value, "__len__") else value
				return dict.__setitem__(self, tag, obj)
		raise KeyError("%s tag not a valid tag for this ifd" % tag)

	def get(self, tag):
		for tf in self.tag_family:
			tag = tags._2tag(tag, family=tf)
			if tag in tf:
				return dict.__getitem__(self, tag)
		raise KeyError("%s tag not found in ifd" % tag)

	def append(self, elem):
		if isinstance(elem, Tag):
			# print(self.tag_name, elem.count, elem.tag, elem.key, elem.value)
			elem.name = self.tag_name
			if elem.tag in Ifd.sub_ifd:
				return dict.__setitem__(self, elem.tag, elem)
			for tf in self.tag_family:
				if elem.tag in tf:
					return dict.__setitem__(self, elem.tag, elem)
			raise KeyError("%s tag not a valid tag for this ifd" % elem.tag)
		else: raise TypeError("%s is not a valid tag object" % elem)

	def set_location(self, longitude, latitude, altitude=0.):
		ifd = self["GPS IFD"]
		ifd[1] = ifd[2] = latitude
		ifd[3] = ifd[4] = longitude
		ifd[5] = ifd[6] = altitude

	def get_location(self):
		ifd = self["GPS IFD"]
		if set([1,2,3,4,5,6]) <= set(ifd.keys()):
			return (
				ifd[3] * ifd[4],
				ifd[1] * ifd[2],
				ifd[5] * ifd[6]
			)

	def load_location(self, zoom=15, size="256x256", mcolor="0xff00ff", format="png", scale=1):
		ifd = self["GPS IFD"]
		if set([1,2,3,4]) <= set(ifd.keys()):
			latitude = ifd[1] * ifd[2]
			longitude = ifd[3] * ifd[4]
			try:
				opener = urllib.urlopen("https://maps.googleapis.com/maps/api/staticmap?center=%s,%s&zoom=%s&size=%s&markers=color:%s%%7C%s,%s&format=%s&scale=%s" % (
					latitude, longitude,
					zoom, size, mcolor,
					latitude, longitude,
					format, scale
				))
			except:
				return StringIO()
			else:
				return StringIO(opener.read())
				print("googleapis connexion error")
		else:
			return StringIO()

	def dump_location(self, tilename, zoom=15, size="256x256", mcolor="0xff00ff", format="png", scale=1):
		ifd = self["GPS IFD"]
		if set([1,2,3,4]) <= set(ifd.keys()):
			latitude = ifd[1] * ifd[2]
			longitude = ifd[3] * ifd[4]
			try:
				urllib.urlretrieve("https://maps.googleapis.com/maps/api/staticmap?center=%s,%s&zoom=%s&size=%s&markers=color:%s%%7C%s,%s&format=%s&scale=%s" % (
						latitude, longitude,
						zoom, size, mcolor,
						latitude, longitude,
						format, scale
					),
					os.path.splitext(tilename)[0] + "."+format
				)
			except:
				print("googleapis connexion error")

	def tags(self):
		for v in sorted(dict.values(self), key=lambda e:e.tag):
			yield v
		for tag in Ifd.sub_ifd.keys():
			if hasattr(self, "_%s"%tag):
				for v in getattr(self, "_%s"%tag).tags():
					yield v

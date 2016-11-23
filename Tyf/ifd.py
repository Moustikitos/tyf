# -*- encoding:utf-8 -*-
# Copyright 2012-2015, THOORENS Bruno - http://bruno.thoorens.free.fr/licences/tyf.html

from . import io, os, tags, encoders, decoders, reduce, values, TYPES, urllib, StringIO
import struct


class Tag(object):
	meaning = None

	def __init__(self, tag, value=None, name="Abstract tag", db=("Undefined", [7], b"", "Nothing about abstract tag")):
		self.tag = tag
		self.key, _typ, default, self.comment = db
		self.type = _typ[-1]
		self.name = name
		if value: self._encode(value)
		elif default: self._encode(default)

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
		elif attr == "value":
			restricted = getattr(values, self.key, None)
			if restricted != None:
				v = value[0] if isinstance(value, tuple) and len(value) == 1 else value
				self.meaning = restricted.get(v, "no description found [%r]" % v)
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
		if not self.value_is_offset:
			s = struct.calcsize("="+TYPES[self.type][0])
			voidspace = (struct.calcsize("=L") - self.count*s)//s
			if self.type in [2, 7]: return self.value + b"\x00"*voidspace
			elif self.type in [1, 3, 6, 8]: return self.value + ((0,)*voidspace)
		return self.value

	def calcsize(self):
		return struct.calcsize("=" + TYPES[self.type][0] * (self.count*(2 if self.type in [5,10] else 1))) if self.value_is_offset else 0


class Ifd(dict):
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

	exif_ifd = property(lambda obj: getattr(obj, "_34665", None), None, None, "shortcut to EXIF sub ifd")
	gps_ifd = property(lambda obj: getattr(obj, "_34853", None), None, None, "shortcut to GPS sub ifd")
	has_raster = property(lambda obj: 273 in obj or 288 in obj or 324 in obj or 513 in obj, None, None, "return true if it contains raster data")
	raster_loaded = property(lambda obj: not(obj.has_raster) or bool(len(obj.stripes+obj.tiles+obj.free)+len(obj.jpegIF)), None, None, "")

	def __init__(self, **kwargs):
		setattr(self, "tagname", kwargs.pop("tagname", "Tiff tag"))
		setattr(self, "tag_family", kwargs.pop("tag_family", [tags.bTT]))

		dict.__init__(self)

		self.stripes = ()
		self.tiles = ()
		self.free = ()
		self.jpegIF = b""

	def from_db(self, tag):
		for tf in self.tag_family:
			if tag in tf: return tf[tag]
		return ("Undefined", [7], b"", "Nothing about abstract tag")

	# def create_sub_ifd(self, tag):
	# 	for tf in self.tag_family:
	# 		tag = tags._2tag(tag, family=tf)
	# 		if tag in Ifd.sub_ifd:
	# 			name, family = Ifd.sub_ifd[tag]
	# 			setattr(self, "_%s"%tag, Ifd(tag_name=name, tag_family=[family]))

	def __setitem__(self, tag, value):
		for tf in self.tag_family:
			tag = tags._2tag(tag, family=tf)
			if tag in tf:
				if tag in Ifd.sub_ifd:
					name, family = Ifd.sub_ifd[tag]
					setattr(self, "_%s"%tag, value if isinstance(value, Ifd) else Ifd(tag_name=name, tag_family=[family]))
					dict.__setitem__(self, tag, Tag(tag, 0, name=self.tagname, db=tf[tag]))
				else:
					dict.__setitem__(self, tag, Tag(tag, value, name=self.tagname, db=tf[tag]))
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

	def set(self, tag, typ, value):
		for tf in self.tag_family:
			tag = tags._2tag(tag, family=tf)
			if tag in tf:
				obj = Tag(tag, name=self.tagname, db=tf[tag])
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
			elem.name = self.tagname
			if elem.tag in Ifd.sub_ifd:
				return dict.__setitem__(self, elem.tag, elem)
			for tf in self.tag_family:
				if elem.tag in tf:
					return dict.__setitem__(self, elem.tag, elem)
			raise KeyError("%s tag not a valid tag for this ifd" % elem.tag)
		else: raise TypeError("%s is not a valid tag object" % elem)

	def set_location(self, longitude, latitude, altitude=0.):
		ifd = Ifd(tagname="GPS tag", tag_family=[tags.gpsT]) if 34853 not in self else self[34853]
		ifd[1] = ifd[2] = latitude
		ifd[3] = ifd[4] = longitude
		ifd[5] = ifd[6] = altitude

	def get_location(self):
		ifd = Ifd(tagname="GPS tag", tag_family=[tags.gpsT]) if 34853 not in self else self[34853]
		if set([1,2,3,4,5,6]) <= set(ifd.keys()):
			return (
				ifd[3] * ifd[4],
				ifd[1] * ifd[2],
				ifd[5] * ifd[6]
			)

	def load_location(self, zoom=15, size="256x256", mcolor="0xff00ff", format="png", scale=1):
		ifd = Ifd(tagname="GPS tag", tag_family=[tags.gpsT]) if 34853 not in self else self[34853]
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
		ifd = Ifd(tagname="GPS tag", tag_family=[tags.gpsT]) if 34853 not in self else self[34853]
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
				for v in sorted(getattr(self, "_%s"%tag).values(), key=lambda e:e.tag):
					yield v
























# class TiffTag(object):

# 	# IFD entries values
# 	tag = 0x0
# 	type = 0
# 	count = 0
# 	value = None

# 	# end user side values
# 	key = "Undefined"
# 	name = "Undefined tag"
# 	comment = "Nothing about this tag"
# 	meaning = None

# 	def __init__(self, tag, type=None, value=None, name="Tiff tag"):
# 		self.key, _typ, default, self.comment = tags.get(tag)
# 		self.tag = tag
# 		self.name = name
# 		self.type = _typ[-1] if type == None else type

# 		if value != None: self._encode(value)
# 		elif default != None: self.value = (default,) if not hasattr(default, "len") else default

# 	def __setattr__(self, attr, value):
# 		if attr == "type":
# 			try: object.__setattr__(self, "_encoder", getattr(encoders, "_%s"%hex(self.tag)))
# 			except AttributeError: object.__setattr__(self, "_encoder", getattr(encoders, "_%s"%value))
# 			try: object.__setattr__(self, "_decoder", getattr(decoders, "_%s"%hex(self.tag)))
# 			except AttributeError: object.__setattr__(self, "_decoder", getattr(decoders, "_%s"%value))
# 		elif attr == "value":
# 			restricted = getattr(values, self.key, None)
# 			if restricted != None:
# 				v = value[0] if isinstance(value, tuple) else value
# 				self.meaning = restricted.get(v, "no description found [%r]" % (v,))
# 			self.count = len(value) // (1 if self.type not in [5,10] else 2)
# 			self._determine_if_offset()
# 		object.__setattr__(self, attr, value)

# 	def __repr__(self):
# 		return "<%s 0x%x: %s = %r>" % (self.name, self.tag, self.key, self.value) + ("" if not self.meaning else ' := %r'%self.meaning)

# 	def _encode(self, value):
# 		self.value = self._encoder(value)

# 	def _decode(self):
# 		return self._decoder(self.value)

# 	def _determine_if_offset(self):
# 		if self.count == 1 and self.type in [1, 2, 3, 4, 6, 7, 8, 9]: setattr(self, "value_is_offset", False)
# 		elif self.count <= 2 and self.type in [3, 8]: setattr(self, "value_is_offset", False)
# 		elif self.count <= 4 and self.type in [1, 2, 6, 7]: setattr(self, "value_is_offset", False)
# 		else: setattr(self, "value_is_offset", True)

# 	def _fill(self):
# 		s = struct.calcsize("="+TYPES[self.type][0])
# 		voidspace = (struct.calcsize("=L") - self.count*s)//s
# 		if self.type in [2, 7]: return self.value + b"\x00"*voidspace
# 		elif self.type in [1, 3, 6, 8]: return self.value + ((0,)*voidspace)
# 		return self.value

# 	def calcsize(self):
# 		return struct.calcsize("=" + TYPES[self.type][0] * (self.count*(2 if self.type in [5,10] else 1))) if self.value_is_offset else 0


# class xIfd(dict):
# 	tagname = "Tiff Tag"

# 	exif_ifd = property(lambda obj: obj.sub_ifd.get(34665, {}), None, None, "shortcut to EXIF sub ifd")
# 	gps_ifd = property(lambda obj: obj.sub_ifd.get(34853, {}), None, None, "shortcut to GPS sub ifd")
# 	has_raster = property(lambda obj: 273 in obj or 288 in obj or 324 in obj or 513 in obj, None, None, "return true if it contains raster data")
# 	raster_loaded = property(lambda obj: not(obj.has_raster) or bool(len(obj.stripes+obj.tiles+obj.free)+len(obj.jpegIF)), None, None, "")
# 	size = property(
# 		lambda obj: {
# 			"ifd": struct.calcsize("=H" + (len(obj)*"HHLL") + "L"),
# 			"data": reduce(int.__add__, [t.calcsize() for t in dict.values(obj)])
# 		}, None, None, "return ifd-packed size and data-packed size")
		
# 	def __init__(self, sub_ifd={}, **kwargs):
# 		self._sub_ifd = sub_ifd
# 		setattr(self, "tagname", kwargs.pop("tagname", "Tiff tag"))
# 		dict.__init__(self)

# 		self.sub_ifd = {}
# 		self.stripes = ()
# 		self.tiles = ()
# 		self.free = ()
# 		self.jpegIF = b""

# 	def __setitem__(self, tag, value):
# 		for t,(ts,tname) in self._sub_ifd.items():
# 			tag = tags._2tag(tag, family=ts)
# 			if tag in ts:
# 				if not t in self.sub_ifd:
# 					self.sub_ifd[t] = Ifd(sub_ifd={}, tagname=tname)
# 				self.sub_ifd[t].addtag(TiffTag(tag, value=value))
# 				return
# 		else:
# 			tag = tags._2tag(tag)
# 			dict.__setitem__(self, tag, TiffTag(tag, value=value, name=self.tagname))

# 	def __getitem__(self, tag):
# 		for i in self.sub_ifd.values():
# 			try: return i[tag]
# 			except KeyError: pass
# 		return dict.__getitem__(self, tags._2tag(tag))._decode()

# 	def _check(self):
# 		for key in self.sub_ifd:
# 			if key not in self:
# 				self.addtag(TiffTag(key, 4, 0, name=self.tagname))

# 	def set(self, tag, typ, value):
# 		for t,(ts,tname) in self._sub_ifd.items():
# 			if tag in ts:
# 				if not t in self.sub_ifd:
# 					self.sub_ifd[t] = Ifd(sub_ifd={}, tagname=tname)
# 				self.sub_ifd[t].set(tag, typ, value)
# 				return
# 		tifftag = TiffTag(tag=tag, type=typ, name=self.tagname)
# 		tifftag.value = (value,) if not hasattr(value, "__len__") else value
# 		tifftag.name = self.tagname
# 		dict.__setitem__(self, tag, tifftag)

# 	def get(self, tag):
# 		for i in self.sub_ifd.values():
# 			if tag in i: return i.get(tag)
# 		return dict.get(self, tags._2tag(tag))

# 	def addtag(self, tifftag):
# 		if isinstance(tifftag, TiffTag):
# 			tifftag.name = self.tagname
# 			dict.__setitem__(self, tifftag.tag, tifftag)

# 	def tags(self):
# 		for v in sorted(dict.values(self), key=lambda e:e.tag):
# 			yield v
# 		for i in self.sub_ifd.values():
# 			for v in sorted(dict.values(i), key=lambda e:e.tag):
# 				yield v

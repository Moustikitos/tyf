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
		self.name = name
		# if tag == 0: return
		# self.key, types, default, self.comment = _TAGS.get(tag, ("Unknown", [0,], None, "Undefined tag"))
		# value = default if value == None else value

		# self.tag = tag
		# restricted = getattr(values, self.key, None)

		# if restricted:
		# 	if value in restricted: self.meaning = restricted.get(value)
		# 	else: raise ValueError('"%s" value must be one of %s, get %s instead' % (self.key, list(restricted.keys()), value))

		# self.type, self.count, self.value = self._fix(value, types)

	# # use a fix for human use
	# # for example give 1.32 for a type 5 or 10 automaticaly transforms it into rational(33,25)
	# def _fix(self, value, types):
	# 	if not hasattr(value, "__len__"):
	# 		value = (value, )

	# 	# user can give a value that will be converted to rational
	# 	if len(set([5, 10]) & set(types)):
	# 		# convert value to rational
	# 		if isinstance(value, (float, long, int)):
	# 			f = fractions.Fraction(value.__repr__())
	# 			value = f.numerator, f.denominator
	# 		# convert a list of value to list of rational
	# 		elif isinstance(value, (list, tuple)):
	# 			test = value[0]
	# 			cls = test.__class__
	# 			if not bool(len([val for val in value if isinstance(val, cls)]) - len(value)):
	# 				if cls == float:
	# 					value = reduce(tuple.__add__, [(f.numerator, f.denominator) for f in [fractions.Fraction(e.__repr__()) for e in value]])
	# 				elif cls in (int, long):
	# 					value = reduce(tuple.__add__, zip(value[0::2], value[1::2]))
	# 			else:
	# 				raise ValueError("%r is not an uniform array" % (value, ))
	# 		return types[0], len(value)//2, value

	# 	# finalize string or bytes with null byte
	# 	elif 2 in types:
	# 		if isinstance(value, str):
	# 			value += "\x00" if not value.endswith("\x00") else ""
	# 			value = value.encode()
	# 		else:
	# 			value += b"\x00" if not value.endswith(b"\x00") else b""

	# 	if len(set([1,3,4,6,8,9]) & set(types)):
	# 		typ = -1
	# 		if bool(len([val for val in value if val < 0])): # signed
	# 			for v in value:
	# 				typ = 6 if -2**8/2 < v < 2**8/2-1 and typ <= 6 else \
	# 				      8 if -2**16/2 < v < 2**16/2-1 and typ <= 8 else \
	# 				      9
	# 		else:
	# 			for v in value:
	# 				typ = 1 if v < 2**8 and typ <= 1 else \
	# 				      3 if v < 2**16 and typ <= 3  else \
	# 				      4
	# 		types = [typ,] # ...

	# 	return types[0], len(value), value

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


class Ifd(dict):
	readonly = [259, 270, 271, 272, 301, 306, 318, 319, 529, 532, 33432]

	size = property(
		lambda obj: {
			"ifd": struct.calcsize("H" + len(obj)*"HHLL" + "L"),
			"data": struct.calcsize("".join(TYPES[typ][0]*count for (typ,count) in [(t.type,t.count) for t in obj.values()] if count > 1 or typ in [5,10]))
		}, None, None, "")

	def __init__(self, *args, **kwargs):
		dict.__init__(self)

		self.key2tag = dict((v[0], t) for t,v in _TAGS.items())
		self.tag2key = dict((v, k) for k,v in self.key2tag.items())

		self.private_ifd = {}
		self.stripes = ()
		self.tiles = ()
		self.free = ()

	# def __setitem__(self, tag, value):
	# 	if isinstance(tag, str): tag = self.key2tag[tag]
	# 	if tag in self and tag in Ifd.readonly: pass
	# 	else: dict.__setitem__(self, tag, TiffTag(tag, value))

	def __getitem__(self, tag):
		for i in self.private_ifd.values():
			try: return i[tag]
			except KeyError: pass
		if isinstance(tag, str): tag = self.key2tag[tag]
		return dict.__getitem__(self, tag)._unfix()

	def set(self, tag, typ, count, value, name="Tiff tag"):
		tifftag = TiffTag(name=name)
		tifftag.tag = tag
		tifftag.type = typ
		tifftag.count = count
		tifftag.value = (value,) if count == 1 and typ not in [5, 10] else value
		tifftag.key, typ_, default, tifftag.comment = _TAGS.get(tag, ("Unknown", -1, None, "Undefined tag 0x%x"%tag))
		restricted = getattr(values, tifftag.key, None)
		if restricted: tifftag.meaning = restricted.get(value)
		dict.__setitem__(self, tag, tifftag)
		
	def values(self):
		for v in dict.values(self): yield v
		for i in self.private_ifd.values():
			for v in i.values(): yield v

# -*- coding:utf-8 -*-
try:
	from setuptools import setup
	import wheel
except ImportError:
	from distutils.core import setup
kw = {}

f = open("Tyf/VERSION", "r")
long_description = open("./rst/pypi.rst", "r")
kw.update(**{
	"version": f.read().strip(),
	"name": "Tyf",
	"keywords": ["ifd", "tiff", "jpeg", "exif", "gps", "geotiff"],
	"author": "thoons",
	"author_email": "bruno.thoorens@free.fr",
	"maintainer": "thoons",
	"maintainer_email": "bruno.thoorens@free.fr",
	"url": "http://bruno.thoorens.free.fr",
	"download_url": "https://github.com/Moustikitos/tyf",
	"bugtrack_url": "https://github.com/Moustikitos/tyf/issues",
	"description": "Pythonic way to read and edit ifd tag files.",
	"long_description": long_description.read(),
	"packages": ["Tyf"],
	"license": "Copyright 2015, THOORENS Bruno, BSD licence",
	"classifiers": [
		'Development Status :: 3 - Alpha',
		'Environment :: Console',
		'Intended Audience :: Developers',
		'Intended Audience :: Information Technology',
		'License :: OSI Approved :: BSD License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 3',
		'Topic :: Multimedia :: Graphics',
	],
})
long_description.close()
f.close()

setup(**kw)


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

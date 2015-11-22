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
	"keywords": ["IFD", "TIFF", "JPEG", "EXIF", "GPS", "GEOTIFF"],
	"author": "THOORENS Bruno",
	"author_email": "bruno.thoorens@free.fr",
	"url": "http://bruno.thoorens.free.fr",
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

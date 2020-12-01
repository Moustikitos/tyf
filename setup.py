# -*- coding:utf-8 -*-
try:
    from setuptools import setup
    import wheel
except ImportError:
    from distutils.core import setup
kw = {}

f = open("VERSION", "r")
long_description = open("rst/pypi.rst", "r")
kw.update(**{
    "version": f.read().strip(),
    "name": "Tyf",
    "keywords": ["ifd", "tiff", "jpeg", "exif", "gps", "geotiff", "PIL", "Pillow"],
    "author": "Bruno THOORENS",
    "author_email": "bruno.thoorens@free.fr",
    "maintainer": "Bruno THOORENS",
    "maintainer_email": "bruno.thoorens@free.fr",
    "url": "http://bruno.thoorens.free.fr",
    "download_url": "https://github.com/Moustikitos/tyf",
    "description": "Pythonic way to read and edit IFD and EXIF tags.",
    "long_description": long_description.read(),
    "long_description_content_type": "text/markdown",
    "packages": ["Tyf"],
    "license": "Copyright 2015-2016, THOORENS Bruno, BSD licence",
    "classifiers": [
        'Development Status :: 6 - Mature',
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

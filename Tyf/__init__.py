# -*- coding:utf-8 -*-
__copyright__ = "Copyright © 2012-2015, THOORENS Bruno - http://bruno.thoorens.free.fr/licences/tyf.html"
__author__    = "THOORENS Bruno"
__tiff__      = (6,0)
__geotiff__   = (1,8,1)

import io, os, sys, struct, collections

unpack = lambda fmt, fileobj: struct.unpack(fmt, fileobj.read(struct.calcsize(fmt)))
pack = lambda fmt, fileobj, value: fileobj.write(struct.pack(fmt, *value))

TYPES = {
	1:  ("B",  "UCHAR or USHORT"),
	2:  ("c",  "ASCII"),
	3:  ("H",  "UBYTE"),
	4:  ("L",  "ULONG"),
	5:  ("LL", "URATIONAL"),
	6:  ("b",  "CHAR or SHORT"),
	7:  ("c",  "UNDEFINED"),
	8:  ("h",  "BYTE"),
	9:  ("l",  "LONG"),
	10: ("ll", "RATIONAL"),
	11: ("f",  "FLOAT"),
	12: ("d"   "DOUBLE"),
}

# assure compatibility python 2 & 3
if sys.version_info[0] >= 3:
	from io import BytesIO as StringIO
	TYPES[2] = ("s", "ASCII")
	TYPES[7] = ("s", "UDEFINED")
	import functools
	reduce = functools.reduce
	long = int
else:
	from StringIO import StringIO
	reduce = __builtins__["reduce"]

from . import ifd, gkd

def _read_IFD(obj, fileobj, offset, byteorder="<", name="Tiff tag"):
	# fileobj seek must be is on the start offset
	fileobj.seek(offset)
	nb_entry, = unpack(byteorder+"H", fileobj)

	for i in range(nb_entry):
		tag, typ, count = unpack(byteorder+"HHL", fileobj)
		data = fileobj.read(struct.calcsize("L"))
		_typ = TYPES[typ][0]

		if (typ == 2 and count <= 3) or (typ == 7 and count <= 4): 
			if not isinstance(data, bytes): data = data.encode()
			obj.set(tag, typ, count, data[:count], name=name)

		elif count > 1 or typ in [5, 10]:
			value, = struct.unpack(byteorder+"L", data)
			fmt = byteorder + _typ*count
			bckp = fileobj.tell()
			fileobj.seek(value)
			if typ == 2: obj.set(tag, typ, count, b"".join(e for e in unpack(fmt, fileobj)), name=name)
			elif typ == 7: obj.set(tag, typ, count, fileobj.read(count), name=name)
			else: obj.set(tag, typ, count, unpack(fmt, fileobj), name=name)
			fileobj.seek(bckp)

		else:
			fmt = byteorder + _typ
			if typ in [1, 6]: value, = struct.unpack(fmt, data[:struct.calcsize(_typ)])
			elif typ in [3, 8]: value, = struct.unpack(fmt, data[:struct.calcsize(_typ)])
			elif typ == 7: value = data
			else: value, = struct.unpack(fmt, data)
			obj.set(tag, typ, count, value, name=name)


def from_buffer(obj, fileobj, offset, byteorder="<"):
	_read_IFD(obj, fileobj, offset, byteorder)
	next_ifd, = unpack(byteorder+"L", fileobj)

	# manage "Exif IFD"
	if 34665 in obj:
		obj.private_ifd[34665] = ifd.Ifd()
		_read_IFD(obj.private_ifd[34665], fileobj, obj[34665], byteorder, name="Exif tag")

	# Manage "GPS IFD"
	if 34853 in obj:
		obj.private_ifd[34853] = ifd.Ifd()
		_read_IFD(obj.private_ifd[34853], fileobj, obj[34853], byteorder, name="GPS tag")

	# get strip image data
	if 273 in obj:
		for offset,bytecount in zip(obj[273], obj[279]):
			fileobj.seek(offset)
			obj.stripes += (fileobj.read(bytecount), )
	# get free image data
	elif 288 in obj:
		for offset,bytecount in zip(obj[288], obj[289]):
			fileobj.seek(offset)
			obj.free += (fileobj.read(bytecount), )
	# get tile image data
	elif 324 in obj:
		for offset,bytecount in zip(obj[324], obj[325]):
			fileobj.seek(offset)
			obj.tiles += (fileobj.read(bytecount), )

	# fileobj.seek(next_ifd)
	return next_ifd

def _write_IFD(obj, fileobj, offset, byteorder="<"):
	# go where obj have to be written
	fileobj.seek(offset)
	# sort data to be writen
	tags = sorted(list(obj.values()), key=lambda e:e.tag)
	# write number of entries
	pack(byteorder+"H", fileobj, (len(tags),))

	first_entry_offset = fileobj.tell()
	# write all obj first
	for t in tags:
		pack(byteorder+"HHL", fileobj, (t.tag, t.type, t.count))
		if t.type in [1, 6] and t.count == 1:
			pack(byteorder+TYPES[t.type][0]*4, fileobj, t.value + (0,0,0))
		elif t.type in [3, 8] and t.count == 1:
			pack(byteorder+TYPES[t.type][0]*2, fileobj, t.value + (0,))
		elif (t.type == 2 and t.count <= 3) or (t.type == 7 and t.count <= 4):
			pack(byteorder+ ("4%s"%TYPES[t.type][0] if sys.version_info[0] >= 3 else 4*TYPES[t.type][0]), fileobj, t.value + b"\x00"*(4-count))
		elif t.count > 1 or t.type in [5, 10]:
			pack(byteorder+"L", fileobj, (0,))
		else:
			pack(byteorder+"L", fileobj, t.value)

	next_ifd_offset = fileobj.tell()
	pack(byteorder+"L", fileobj, (0,))
	data_offset = fileobj.tell()

	# to prepare jumps
	step1 = struct.calcsize("HHLL")
	step2 = struct.calcsize("HHL")

	# comme back to first ifd entry
	fileobj.seek(first_entry_offset)
	for t in tags:
		if t.count > 1 or t.type in [5, 10, 7]:
			if (t.type == 2 and t.count <= 3) or \
			   (t.type == 7 and t.count <= 4): # or \
			   # (t.type in [1,6] and t.count <= 4) or \
			   # (t.type in [3,8] and t.count <= 2):
				fileobj.seek(step1, 1)
			else:
				fileobj.seek(step2, 1)
				pack(byteorder+"L", fileobj, (data_offset,))
				bckp = fileobj.tell()
				fileobj.seek(data_offset)
				if sys.version_info[0] >= 3 and isinstance(t.value, bytes):
					pack(byteorder+str(t.count)+TYPES[t.type][0], fileobj, (t.value, ))
				else:
					pack(byteorder+TYPES[t.type][0]*t.count, fileobj, t.value)
				data_offset = fileobj.tell()
				fileobj.seek(bckp)
		else:
			fileobj.seek(step1, 1)

	return next_ifd_offset

def to_buffer(obj, fileobj, offset, byteorder="<"):
	size = obj.size
	raw_offset = offset + size["ifd"] + size["data"]
	# add GPS and Exif IFD sizes...
	for tag, p_ifd in obj.private_ifd.items():
		obj[tag] = raw_offset
		size = p_ifd.size
		raw_offset += size["ifd"] + size["data"]

	# knowing where raw image have to be writen, update [Strip/Free/Tile]Offsets
	if 273 in obj:
		_279 = obj[279]
		stripoffsets = (raw_offset,)
		for bytecount in _279[:-1]:
			stripoffsets += (stripoffsets[-1]+bytecount, )
		obj.set(273, 4, len(stripoffsets), stripoffsets)
		next_ifd = stripoffsets[-1] + _279[-1]
	elif 288 in obj:
		_289 = obj[289]
		freeoffsets = (raw_offset,)
		for bytecount in _289[:-1]:
			freeoffsets += (freeoffsets[-1]+bytecount, )
		obj.set(288, 4, len(freeoffsets), freeoffsets)
		next_ifd = freeoffsets[-1] + _289[-1]
	elif 324 in obj:
		_325 = obj[325]
		tileoffsets = (raw_offset,)
		for bytecount in _325[:-1]:
			tileoffsets += (tileoffsets[-1]+bytecount, )
		obj.set(324, 4, len(tileoffsets), tileoffsets)
		next_ifd = tileoffsets[-1] + _325[-1]

	next_ifd_offset = _write_IFD(obj, fileobj, offset, byteorder)
	# write "Exif IFD" and "GPS IFD"
	for tag, p_ifd in obj.private_ifd.items():
		_write_IFD(p_ifd, fileobj, self[tag], byteorder)

	# write raw data
	if len(obj.stripes):
		for offset,data in zip(obj[273], obj.stripes):
			fileobj.seek(offset)
			fileobj.write(data)
	elif len(obj.free):
		for offset,data in zip(obj[288], obj.stripes):
			fileobj.seek(offset)
			fileobj.write(data)
	elif len(obj.tiles):
		for offset,data in zip(obj[324], obj.tiles):
			fileobj.seek(offset)
			fileobj.write(data)

	fileobj.seek(next_ifd_offset)
	return next_ifd_offset


class TiffFile(list):

	def __init__(self, filepath, byteorder=0x4949):
		self.src = os.path.abspath(filepath)
		fileobj = io.open(filepath, "rb")
		fileobj.seek(2)

		byteorder = "<" if byteorder == 0x4949 else ">"
		magic_number, = unpack(byteorder+"H", fileobj)
		if magic_number != 0x2A: # 42
			fileobj.close()
			raise IOError("Bad magic number. Not a valid TIFF file")
		next_ifd, = unpack(byteorder+"L", fileobj)

		ifds = []
		while next_ifd != 0:
			i = ifd.Ifd("private")
			next_ifd = from_buffer(i, fileobj, next_ifd, byteorder)
			ifds.append(i)

		fileobj.close()
		list.__init__(self, ifds)

	def __getitem__(self, item):
		if isinstance(item, tuple): return list.__getitem__(self, item[0])[item[-1]]
		else: return list.__getitem__(self, item)

class JpegFile(collections.OrderedDict):

	raster = property(lambda obj: collections.OrderedDict.__getitem__(obj, 0xffda), None, None, "JPEG raster")
	jfif = property(lambda obj: collections.OrderedDict.__getitem__(obj, 0xffe0), None, None, "JFIF data")

	def __init__(self, filepath):
		self.src = os.path.abspath(filepath)
		fileobj = io.open(filepath, "rb")
		self.ifd = ifd.Ifd()

		markers = collections.OrderedDict()
		marker, = unpack(">H", fileobj)
		while marker != 0xffd9: # EOI (End Of Image) Marker
			marker, count = unpack(">HH", fileobj)
			if marker == 0xffda:
				fileobj.seek(-2, 1)
				markers[0xffda] = fileobj.read()
				marker = 0xffd9
			else:
				markers[marker] = fileobj.read(count-2)
				if marker == 0xffe1:
					string = StringIO(markers[marker][6:])
					first, = unpack(">H", string)
					if first in [0x4D4D, 0x4949]:
						byteorder = "<" if first == 0x4949 else ">"
						magic_number, = unpack(byteorder+"H", string)
						i = ifd.Ifd()
						if magic_number == 0x2A:
							next_ifd, = unpack(byteorder+"L", string)
							from_buffer(i, string, next_ifd, byteorder)		
							setattr(self, "ifd", i)

		collections.OrderedDict.__init__(self, markers)

	def __getitem__(self, item):
		try: return self.ifd[item]
		except KeyError: return collections.OrderedDict.__getitem__(self, item)


def open(filepath):
	fileobj = io.open(filepath, "rb")
	first, = unpack(">H", fileobj)
	fileobj.close()

	if first == 0xffd8:
		return JpegFile(filepath)

	elif first in [0x4d4d, 0x4949]:
		return TiffFile(filepath, first)

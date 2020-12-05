# -*- encoding: utf-8 -*-
# http://www.remotesensing.org/geotiff/spec/geotiffhome.html

from Tyf import values, __geotiff__


_TAGS = {
    # GeoTIFF Configuration GeoKeys
    1024: ("GTModelTypeGeoKey", [3], 0, None),
    1025: ("GTRasterTypeGeoKey", [3], 1, None),
    1026: ("GTCitationGeoKey", [2], None, None),             # ASCII text

    # Geographic CS Parameter GeoKeys
    2048: ("GeographicTypeGeoKey", [3], 4326, None),         # epsg datum code [4001 - 4999]
    2049: ("GeogCitationGeoKey", [2], None, None),           # ASCII text
    2050: ("GeogGeodeticDatumGeoKey", [3], None, None),      # use 2048 !
    2051: ("GeogPrimeMeridianGeoKey", [3], 8901, None),      # epsg prime meridian code [8001 - 8999]
    2052: ("GeogLinearUnitsGeoKey", [3], 9001, None),        # epsg linear unit code [9000 - 9099]
    2053: ("GeogLinearUnitSizeGeoKey", [12], None, None),    # custom unit in meters
    2054: ("GeogAngularUnitsGeoKey", [3], 9101, None),
    2055: ("GeogAngularUnitsSizeGeoKey", [12], None, None),  # custom unit in radians
    2056: ("GeogEllipsoidGeoKey", [3], None, None),          # epsg ellipsoid code [7000 - 7999]
    2057: ("GeogSemiMajorAxisGeoKey", [12], None, None),
    2058: ("GeogSemiMinorAxisGeoKey", [12], None, None),
    2059: ("GeogInvFlatteningGeoKey", [12], None, None),
    2060: ("GeogAzimuthUnitsGeoKey", [3], None, None),
    2061: ("GeogPrimeMeridianLongGeoKey", [12], None, None),  # custom prime meridian value in GeogAngularUnits

    # Projected CS Parameter GeoKeys
    3072: ("ProjectedCSTypeGeoKey", [3], None, None),        # epsg grid code [20000 - 32760]
    3073: ("PCSCitationGeoKey", [2], None, None),            # ASCII text
    3074: ("ProjectionGeoKey", [3], None, None),             # [10000 - 19999]
    3075: ("ProjCoordTransGeoKey", [3], None, None),
    3076: ("ProjLinearUnitsGeoKey", [3], None, None),
    3077: ("ProjLinearUnitSizeGeoKey", [12], None, None),    # custom unit in meters
    3078: ("ProjStdParallel1GeoKey", [12], None, None),
    3079: ("ProjStdParallel2GeoKey", [12], None, None),
    3080: ("ProjNatOriginLongGeoKey", [12], None, None),
    3081: ("ProjNatOriginLatGeoKey", [12], None, None),
    3082: ("ProjFalseEastingGeoKey", [12], None, None),
    3083: ("ProjFalseNorthingGeoKey", [12], None, None),
    3084: ("ProjFalseOriginLongGeoKey", [12], None, None),
    3085: ("ProjFalseOriginLatGeoKey", [12], None, None),
    3086: ("ProjFalseOriginEastingGeoKey", [12], None, None),
    3087: ("ProjFalseOriginNorthingGeoKey", [12], None, None),
    3088: ("ProjCenterLongGeoKey", [12], None, None),
    3089: ("ProjCenterLatGeoKey", [12], None, None),
    3090: ("ProjCenterEastingGeoKey", [12], None, None),
    3091: ("ProjFalseOriginNorthingGeoKey", [12], None, None),
    3092: ("ProjScaleAtNatOriginGeoKey", [12], None, None),
    3093: ("ProjScaleAtCenterGeoKey", [12], None, None),
    3094: ("ProjAzimuthAngleGeoKey", [12], None, None),
    3095: ("ProjStraightVertPoleLongGeoKey", [12], None, None),

    # Vertical CS Parameter Keys
    4096: ("VerticalCSTypeGeoKey", [3], None, None),
    4097: ("VerticalCitationGeoKey", [2], None, None),
    4098: ("VerticalDatumGeoKey", [3], None, None),
    4099: ("VerticalUnitsGeoKey", [3], None, None),
}

_2TAG = dict((v[0], t) for t, v in _TAGS.items())
_2KEY = dict((v, k) for k, v in _2TAG.items())


class GkdTag:
    strict = True

    info = property(
        lambda cls: getattr(
            values, _2KEY.get(cls.tag, cls.key), {}
        ).get(cls._decode(), None),
        None,
        None,
        ""
    )

    def __init__(self, tag, value=None):
        self.key, types, default, self.comment = _TAGS.get(
            tag, ("Unknown", [0], None, "Undefined tag")
        )
        value = default if value is None else value

        self.tag = tag
        restricted = getattr(values, self.key, {})

        if restricted:
            reverse = dict((v, k) for k, v in restricted.items())
            if value in restricted:
                self.meaning = restricted.get(value)
            elif value in reverse:
                value = reverse[value]
                self.meaning = value
            elif GkdTag.strict:
                raise ValueError(
                    '"%s" value must be one of %s, get %s instead' %
                    (self.key, list(restricted.keys()), value)
                )

        self.type, self.count, self.value = self._encode(value, types)

    def __repr__(self):
        return "<GKD tag %s:%r>" % (self.key, self.value, )

    def _encode(self, value, types):
        if isinstance(value, str):
            value = value.encode("utf-8")
        elif not hasattr(value, "__len__"):
            value = (value, )
        typ = 0
        if 2 in types:
            typ = 34737
        elif 12 in types:
            typ = 34736
        return typ, len(value), value

    def _decode(self):
        if self.count == 1:
            return self.value[0]
        else:
            return self.value


class Gkd(dict):
    version = __geotiff__[0]
    revision = __geotiff__[1:]

    def __getitem__(self, tag):
        return dict.__getitem__(self, _2TAG.get(tag, tag))._decode()

    def __setitem__(self, tag, value):
        dict.__setitem__(self, _2TAG.get(tag, tag), GkdTag(tag, value))

    def compute(self):
        directory_tags = (self.version, ) + self.revision + (len(self), )
        double_params = ()
        ascii_params = b""
        for tag in self.tags():
            directory_tags += (tag.tag, tag.type, tag.count)
            if tag.type == 34736:
                double_params += tag.value
                directory_tags += (len(double_params)-1, )
            elif tag.type == 34737:
                directory_tags += (len(ascii_params), )
                ascii_params += tag.value + b"|"
            else:
                directory_tags += tag.value
        self._34735 = directory_tags
        self._34736 = double_params
        self._34737 = ascii_params

    def get(self, tag, error=None):
        if hasattr(self, "_%s" % tag):
            return getattr(self, "_%s" % tag)
        else:
            return dict.get(self, _2TAG.get(tag, tag), error)

    @staticmethod
    def from_ifd(dic={}, **kw):
        cls = Gkd()
        pairs = dict(dic, **kw)
        if "GeoDoubleParamsTag" in pairs:
            _34736 = dic["GeoDoubleParamsTag"]
        if "GeoAsciiParamsTag" in pairs:
            _34737 = dic["GeoAsciiParamsTag"]
        if "GeoKeyDirectoryTag" in pairs:
            _34735 = dic["GeoKeyDirectoryTag"]
            cls.version = _34735[0]
            cls.revision = _34735[1:3]
            for (tag, typ, count, value) in zip(
                _34735[4::4], _34735[5::4], _34735[6::4], _34735[7::4]
            ):
                if typ == 0:
                    value = value
                elif typ == 34736:
                    value = _34736[value]
                elif typ == 34737:
                    value = _34737[value:value + count - 1]
                t = GkdTag(tag, value)
                t.count = count
                dict.__setitem__(cls, tag, t)
        return cls

    def tags(self):
        for v in sorted(dict.values(self), key=lambda e:e.tag):
            yield v

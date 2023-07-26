# -*- encoding:utf-8 -*-

import os
import pickle
import sqlite3

from functools import reduce

def to_sqlite(elem):
    return pickle.dumps(elem)


def to_python(elem):
    return pickle.loads(elem)


sqlite3.register_adapter(list, to_sqlite)
sqlite3.register_adapter(tuple, to_sqlite)
sqlite3.register_adapter(bytes, to_sqlite)
sqlite3.register_converter('BLOB', to_python)

sqlite = sqlite3.connect(
    os.path.join(os.path.dirname(__file__), "tags.sqlite"),
    detect_types=sqlite3.PARSE_DECLTYPES
)


def get(tag_or_key):
    req = sqlite.execute(
        "SELECT * FROM tags WHERE tag=? OR key=?",
        (tag_or_key, tag_or_key)
    ).fetchall()
    if len(req):
        data = req[0]
        return data[1], (data[2], data[3], data[4], data[5])
    else:
        return False, (
            "Undefined", [7], None, "Undefined tag %r" % tag_or_key
        )


def in_family(tag_or_key, family):
    return len(
        sqlite.execute(
            "SELECT * FROM tags WHERE family=? and (tag=? OR key=?)",
            (family, tag_or_key, tag_or_key)
        ).fetchall()
    ) > 0


def keys(family):
    return reduce(
        tuple.__add__,
        sqlite.execute(
            "SELECT key FROM tags WHERE family=?", (family,)
        ).fetchall()
    )

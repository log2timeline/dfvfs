# -*- coding: utf-8 -*-
"""The Python 2 and 3 compatible type definitions."""

import sys


# pylint: disable=invalid-name,undefined-variable

if sys.version_info[0] < 3:
  BYTES_TYPE = str
  INTEGER_TYPES = (int, long)
  STRING_TYPES = (basestring, )
  UNICODE_TYPE = unicode
else:
  BYTES_TYPE = bytes
  INTEGER_TYPES = (int, )
  STRING_TYPES = (str, )
  UNICODE_TYPE = str


PY_3_7_AND_LATER = bool(tuple(sys.version_info[0:2]) >= (3, 7))

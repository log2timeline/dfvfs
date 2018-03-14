# -*- coding: utf-8 -*-
"""Imports for the compression manager."""

from dfvfs.compression import bzip2_decompressor

try:
  from dfvfs.compression import xz_decompressor
except ImportError:
  pass

from dfvfs.compression import zlib_decompressor

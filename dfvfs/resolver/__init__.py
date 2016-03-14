# -*- coding: utf-8 -*-
"""Imports for the path specification resolver."""

try:
  from dfvfs.resolver import bde_resolver_helper
except ImportError:
  pass

from dfvfs.resolver import compressed_stream_resolver_helper
from dfvfs.resolver import cpio_resolver_helper
from dfvfs.resolver import data_range_resolver_helper
from dfvfs.resolver import encoded_stream_resolver_helper
from dfvfs.resolver import encrypted_stream_resolver_helper

try:
  from dfvfs.resolver import ewf_resolver_helper
except ImportError:
  pass

from dfvfs.resolver import fake_resolver_helper
from dfvfs.resolver import gzip_resolver_helper

try:
  from dfvfs.resolver import lvm_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver import ntfs_resolver_helper
except ImportError:
  pass

from dfvfs.resolver import os_resolver_helper

try:
  from dfvfs.resolver import qcow_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver import raw_resolver_helper
except ImportError:
  pass

from dfvfs.resolver import sqlite_blob_resolver_helper
from dfvfs.resolver import tar_resolver_helper

try:
  from dfvfs.resolver import tsk_partition_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver import tsk_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver import vhdi_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver import vmdk_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver import vshadow_resolver_helper
except ImportError:
  pass

from dfvfs.resolver import zip_resolver_helper

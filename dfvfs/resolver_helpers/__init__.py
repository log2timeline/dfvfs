# -*- coding: utf-8 -*-
"""Imports for the path specification resolver."""

try:
  from dfvfs.resolver_helpers import apfs_container_resolver_helper
  from dfvfs.resolver_helpers import apfs_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import bde_resolver_helper
except ImportError:
  pass

from dfvfs.resolver_helpers import compressed_stream_resolver_helper
from dfvfs.resolver_helpers import cpio_resolver_helper

try:
  from dfvfs.resolver_helpers import cs_resolver_helper
except ImportError:
  pass

from dfvfs.resolver_helpers import data_range_resolver_helper
from dfvfs.resolver_helpers import encoded_stream_resolver_helper
from dfvfs.resolver_helpers import encrypted_stream_resolver_helper

try:
  from dfvfs.resolver_helpers import ewf_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import ext_resolver_helper
except ImportError:
  pass

from dfvfs.resolver_helpers import fake_resolver_helper

try:
  from dfvfs.resolver_helpers import fat_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import gpt_resolver_helper
except ImportError:
  pass

from dfvfs.resolver_helpers import gzip_resolver_helper

try:
  from dfvfs.resolver_helpers import hfs_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import luksde_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import lvm_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import modi_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import ntfs_resolver_helper
except ImportError:
  pass

from dfvfs.resolver_helpers import os_resolver_helper

try:
  from dfvfs.resolver_helpers import phdi_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import qcow_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import raw_resolver_helper
except ImportError:
  pass

from dfvfs.resolver_helpers import sqlite_blob_resolver_helper
from dfvfs.resolver_helpers import tar_resolver_helper

try:
  from dfvfs.resolver_helpers import tsk_partition_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import tsk_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import vhdi_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import vmdk_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import vshadow_resolver_helper
except ImportError:
  pass

try:
  from dfvfs.resolver_helpers import xfs_resolver_helper
except ImportError:
  pass

from dfvfs.resolver_helpers import zip_resolver_helper

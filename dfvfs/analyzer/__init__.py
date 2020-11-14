# -*- coding: utf-8 -*-
"""Imports for the format analyzer."""

from dfvfs.analyzer import apfs_analyzer_helper
from dfvfs.analyzer import apfs_container_analyzer_helper
from dfvfs.analyzer import bde_analyzer_helper
from dfvfs.analyzer import bzip2_analyzer_helper
from dfvfs.analyzer import cpio_analyzer_helper
from dfvfs.analyzer import ewf_analyzer_helper
from dfvfs.analyzer import ext_analyzer_helper
from dfvfs.analyzer import fvde_analyzer_helper
from dfvfs.analyzer import gzip_analyzer_helper
from dfvfs.analyzer import hfs_analyzer_helper
from dfvfs.analyzer import luksde_analyzer_helper
from dfvfs.analyzer import lvm_analyzer_helper
from dfvfs.analyzer import ntfs_analyzer_helper
from dfvfs.analyzer import qcow_analyzer_helper
from dfvfs.analyzer import tar_analyzer_helper

try:
  from dfvfs.analyzer import tsk_analyzer_helper
except ImportError:
  pass

try:
  from dfvfs.analyzer import tsk_partition_analyzer_helper
except ImportError:
  pass

from dfvfs.analyzer import vhdi_analyzer_helper
from dfvfs.analyzer import vmdk_analyzer_helper
from dfvfs.analyzer import vshadow_analyzer_helper
from dfvfs.analyzer import xfs_analyzer_helper
from dfvfs.analyzer import xz_analyzer_helper
from dfvfs.analyzer import zip_analyzer_helper

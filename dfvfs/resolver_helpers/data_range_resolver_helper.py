# -*- coding: utf-8 -*-
"""The data range path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import data_range_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import data_range_file_system


class DataRangeResolverHelper(resolver_helper.ResolverHelper):
  """Data range resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_DATA_RANGE

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return data_range_io.DataRange(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return data_range_file_system.DataRangeFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(DataRangeResolverHelper())

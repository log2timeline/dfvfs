# -*- coding: utf-8 -*-
"""The data range path specification resolver helper implementation."""

from __future__ import unicode_literals

# This is necessary to prevent a circular import.
import dfvfs.file_io.data_range_io
import dfvfs.vfs.data_range_file_system

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


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
    return dfvfs.file_io.data_range_io.DataRange(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return dfvfs.vfs.data_range_file_system.DataRangeFileSystem(
        resolver_context)


resolver.Resolver.RegisterHelper(DataRangeResolverHelper())

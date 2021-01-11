# -*- coding: utf-8 -*-
"""The data range path specification resolver helper implementation."""

from dfvfs.file_io import data_range_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import data_range_file_system


class DataRangeResolverHelper(resolver_helper.ResolverHelper):
  """Data range resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_DATA_RANGE

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return data_range_io.DataRange(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return data_range_file_system.DataRangeFileSystem(
        resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(DataRangeResolverHelper())

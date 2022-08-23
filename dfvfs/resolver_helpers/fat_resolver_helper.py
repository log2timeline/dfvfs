# -*- coding: utf-8 -*-
"""The FAT path specification resolver helper implementation."""

from dfvfs.file_io import fat_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import fat_file_system


class FATResolverHelper(resolver_helper.ResolverHelper):
  """FAT resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAT

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return fat_file_io.FATFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return fat_file_system.FATFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(FATResolverHelper())

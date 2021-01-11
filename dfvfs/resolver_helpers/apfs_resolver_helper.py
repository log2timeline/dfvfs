# -*- coding: utf-8 -*-
"""The APFS path specification resolver helper implementation."""

from dfvfs.file_io import apfs_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import apfs_file_system


class APFSResolverHelper(resolver_helper.ResolverHelper):
  """APFS resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APFS

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return apfs_file_io.APFSFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return apfs_file_system.APFSFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(APFSResolverHelper())

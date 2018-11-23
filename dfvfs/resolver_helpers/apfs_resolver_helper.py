# -*- coding: utf-8 -*-
"""The APFS path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import apfs_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import apfs_file_system


class APFSResolverHelper(resolver_helper.ResolverHelper):
  """APFS resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APFS

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return apfs_file_io.APFSFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return apfs_file_system.APFSFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(APFSResolverHelper())

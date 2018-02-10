# -*- coding: utf-8 -*-
"""The NTFS path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import ntfs_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import ntfs_file_system


class NTFSResolverHelper(resolver_helper.ResolverHelper):
  """NTFS resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_NTFS

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return ntfs_file_io.NTFSFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return ntfs_file_system.NTFSFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(NTFSResolverHelper())

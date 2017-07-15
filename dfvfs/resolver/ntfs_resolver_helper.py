# -*- coding: utf-8 -*-
"""The NTFS path specification resolver helper implementation."""

from __future__ import unicode_literals

# This is necessary to prevent a circular import.
import dfvfs.file_io.ntfs_file_io
import dfvfs.vfs.ntfs_file_system

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


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
    return dfvfs.file_io.ntfs_file_io.NTFSFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return dfvfs.vfs.ntfs_file_system.NTFSFileSystem(resolver_context)


resolver.Resolver.RegisterHelper(NTFSResolverHelper())

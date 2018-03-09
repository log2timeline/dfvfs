# -*- coding: utf-8 -*-
"""The CPIO path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import cpio_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import cpio_file_system


class CPIOResolverHelper(resolver_helper.ResolverHelper):
  """CPIO resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_CPIO

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return cpio_file_io.CPIOFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return cpio_file_system.CPIOFileSystem(resolver_context)


# Register the resolver helpers with the resolver.
manager.ResolverHelperManager.RegisterHelper(CPIOResolverHelper())

# -*- coding: utf-8 -*-
"""The ZIP path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import zip_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import zip_file_system


class ZipResolverHelper(resolver_helper.ResolverHelper):
  """ZIP resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ZIP

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return zip_file_io.ZipFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return zip_file_system.ZipFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(ZipResolverHelper())

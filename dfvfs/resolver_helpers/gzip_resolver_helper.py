# -*- coding: utf-8 -*-
"""The gzip file path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import gzip_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import gzip_file_system


class GzipResolverHelper(resolver_helper.ResolverHelper):
  """Gzip file resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GZIP

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return gzip_file_io.GzipFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return gzip_file_system.GzipFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(GzipResolverHelper())

# -*- coding: utf-8 -*-
"""The gzip file path specification resolver helper implementation."""

from __future__ import unicode_literals

# This is necessary to prevent a circular import.
import dfvfs.file_io.gzip_file_io
import dfvfs.vfs.gzip_file_system

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


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
    return dfvfs.file_io.gzip_file_io.GzipFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return dfvfs.vfs.gzip_file_system.GzipFileSystem(resolver_context)


resolver.Resolver.RegisterHelper(GzipResolverHelper())

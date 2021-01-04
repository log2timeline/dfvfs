# -*- coding: utf-8 -*-
"""The gzip file path specification resolver helper implementation."""

from dfvfs.file_io import gzip_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import gzip_file_system


class GzipResolverHelper(resolver_helper.ResolverHelper):
  """Gzip file resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GZIP

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return gzip_file_io.GzipFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return gzip_file_system.GzipFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(GzipResolverHelper())

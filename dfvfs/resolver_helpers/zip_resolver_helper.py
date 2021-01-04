# -*- coding: utf-8 -*-
"""The ZIP path specification resolver helper implementation."""

from dfvfs.file_io import zip_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import zip_file_system


class ZipResolverHelper(resolver_helper.ResolverHelper):
  """ZIP resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ZIP

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return zip_file_io.ZipFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return zip_file_system.ZipFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(ZipResolverHelper())

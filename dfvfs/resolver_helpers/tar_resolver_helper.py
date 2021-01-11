# -*- coding: utf-8 -*-
"""The TAR path specification resolver helper implementation."""

from dfvfs.file_io import tar_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import tar_file_system


class TARResolverHelper(resolver_helper.ResolverHelper):
  """TAR resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TAR

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return tar_file_io.TARFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return tar_file_system.TARFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(TARResolverHelper())

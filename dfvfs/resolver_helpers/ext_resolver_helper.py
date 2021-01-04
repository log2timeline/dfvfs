# -*- coding: utf-8 -*-
"""The EXT path specification resolver helper implementation."""

from dfvfs.file_io import ext_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import ext_file_system


class EXTResolverHelper(resolver_helper.ResolverHelper):
  """EXT resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_EXT

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return ext_file_io.EXTFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return ext_file_system.EXTFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(EXTResolverHelper())

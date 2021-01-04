# -*- coding: utf-8 -*-
"""The operating system path specification resolver helper implementation."""

from dfvfs.file_io import os_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import os_file_system


class OSResolverHelper(resolver_helper.ResolverHelper):
  """Operating system resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OS

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return os_file_io.OSFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return os_file_system.OSFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(OSResolverHelper())

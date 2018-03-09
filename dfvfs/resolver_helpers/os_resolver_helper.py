# -*- coding: utf-8 -*-
"""The operating system path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import os_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import os_file_system


class OSResolverHelper(resolver_helper.ResolverHelper):
  """Operating system resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OS

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return os_file_io.OSFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return os_file_system.OSFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(OSResolverHelper())

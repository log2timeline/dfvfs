# -*- coding: utf-8 -*-
"""The TAR path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import tar_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import tar_file_system


class TARResolverHelper(resolver_helper.ResolverHelper):
  """TAR resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TAR

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return tar_file_io.TARFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return tar_file_system.TARFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(TARResolverHelper())

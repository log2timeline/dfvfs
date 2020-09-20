# -*- coding: utf-8 -*-
"""The EXT path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import ext_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import ext_file_system


class EXTResolverHelper(resolver_helper.ResolverHelper):
  """EXT resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_EXT

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return ext_file_io.EXTFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return ext_file_system.EXTFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(EXTResolverHelper())

# -*- coding: utf-8 -*-
"""The VSS path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import vshadow_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import vshadow_file_system


class VShadowResolverHelper(resolver_helper.ResolverHelper):
  """Volume Shadow Snapshots (VSS) resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VSHADOW

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return vshadow_file_io.VShadowFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return vshadow_file_system.VShadowFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(VShadowResolverHelper())

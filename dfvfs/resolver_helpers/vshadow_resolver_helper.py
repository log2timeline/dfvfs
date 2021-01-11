# -*- coding: utf-8 -*-
"""The VSS path specification resolver helper implementation."""

from dfvfs.file_io import vshadow_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import vshadow_file_system


class VShadowResolverHelper(resolver_helper.ResolverHelper):
  """Volume Shadow Snapshots (VSS) resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VSHADOW

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return vshadow_file_io.VShadowFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return vshadow_file_system.VShadowFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(VShadowResolverHelper())

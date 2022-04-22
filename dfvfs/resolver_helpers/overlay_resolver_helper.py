# -*- coding: utf-8 -*-
"""The Overlay path specification resolver helper implementation."""

from dfvfs.file_io import overlay_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import overlay_file_system


class OverlayResolverHelper(resolver_helper.ResolverHelper):
  """Overlay resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OVERLAY

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return overlay_file_io.OverlayFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return overlay_file_system.OverlayFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(OverlayResolverHelper())

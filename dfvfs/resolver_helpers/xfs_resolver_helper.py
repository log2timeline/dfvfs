# -*- coding: utf-8 -*-
"""The XFS path specification resolver helper implementation."""

from dfvfs.file_io import xfs_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import xfs_file_system


class XFSResolverHelper(resolver_helper.ResolverHelper):
  """XFS resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_XFS

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return xfs_file_io.XFSFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return xfs_file_system.XFSFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(XFSResolverHelper())

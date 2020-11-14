# -*- coding: utf-8 -*-
"""The XFS path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import xfs_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import xfs_file_system


class XFSResolverHelper(resolver_helper.ResolverHelper):
  """XFS resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_XFS

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return xfs_file_io.XFSFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return xfs_file_system.XFSFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(XFSResolverHelper())

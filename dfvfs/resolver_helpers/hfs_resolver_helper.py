# -*- coding: utf-8 -*-
"""The HFS path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import hfs_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import hfs_file_system


class HFSResolverHelper(resolver_helper.ResolverHelper):
  """HFS resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_HFS

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return hfs_file_io.HFSFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return hfs_file_system.HFSFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(HFSResolverHelper())

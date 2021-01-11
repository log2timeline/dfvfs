# -*- coding: utf-8 -*-
"""The HFS path specification resolver helper implementation."""

from dfvfs.file_io import hfs_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import hfs_file_system


class HFSResolverHelper(resolver_helper.ResolverHelper):
  """HFS resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_HFS

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return hfs_file_io.HFSFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return hfs_file_system.HFSFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(HFSResolverHelper())

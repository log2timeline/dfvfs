# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) path specification resolver helper implementation."""

from dfvfs.file_io import tsk_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import tsk_file_system


class TSKResolverHelper(resolver_helper.ResolverHelper):
  """SleuthKit (TSK) resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return tsk_file_io.TSKFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return tsk_file_system.TSKFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(TSKResolverHelper())

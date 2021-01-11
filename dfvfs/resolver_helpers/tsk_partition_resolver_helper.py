# -*- coding: utf-8 -*-
"""The TSK partition path specification resolver helper implementation."""

from dfvfs.file_io import tsk_partition_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import tsk_partition_file_system


class TSKPartitionResolverHelper(resolver_helper.ResolverHelper):
  """SleuthKit (TSK) partition presolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK_PARTITION

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return tsk_partition_file_io.TSKPartitionFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return tsk_partition_file_system.TSKPartitionFileSystem(
        resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(TSKPartitionResolverHelper())

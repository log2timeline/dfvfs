# -*- coding: utf-8 -*-
"""The APM path specification resolver helper implementation."""

from dfvfs.file_io import apm_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import apm_file_system


class APMResolverHelper(resolver_helper.ResolverHelper):
  """Apple Partition Map (APM) resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APM

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return apm_file_io.APMFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return apm_file_system.APMFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(APMResolverHelper())

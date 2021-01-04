# -*- coding: utf-8 -*-
"""The LVM path specification resolver helper implementation."""

from dfvfs.file_io import lvm_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import lvm_file_system


class LVMResolverHelper(resolver_helper.ResolverHelper):
  """Logical Volume Manager (LVM) resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LVM

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return lvm_file_io.LVMFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileSystem: file system.
    """
    return lvm_file_system.LVMFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(LVMResolverHelper())

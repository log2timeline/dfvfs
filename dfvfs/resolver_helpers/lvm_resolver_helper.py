# -*- coding: utf-8 -*-
"""The LVM path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import lvm_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import lvm_file_system


class LVMResolverHelper(resolver_helper.ResolverHelper):
  """Logical Volume Manager (LVM) resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LVM

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return lvm_file_io.LVMFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return lvm_file_system.LVMFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(LVMResolverHelper())

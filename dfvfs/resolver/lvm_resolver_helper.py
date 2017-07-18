# -*- coding: utf-8 -*-
"""The LVM path specification resolver helper implementation."""

from __future__ import unicode_literals

# This is necessary to prevent a circular import.
import dfvfs.file_io.lvm_file_io
import dfvfs.vfs.lvm_file_system

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


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
    return dfvfs.file_io.lvm_file_io.LVMFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return dfvfs.vfs.lvm_file_system.LVMFileSystem(resolver_context)


resolver.Resolver.RegisterHelper(LVMResolverHelper())

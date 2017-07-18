# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) path specification resolver helper implementation."""

from __future__ import unicode_literals

# This is necessary to prevent a circular import.
import dfvfs.file_io.tsk_file_io
import dfvfs.vfs.tsk_file_system

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class TSKResolverHelper(resolver_helper.ResolverHelper):
  """SleuthKit (TSK) resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return dfvfs.file_io.tsk_file_io.TSKFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileSystem: file system.
    """
    return dfvfs.vfs.tsk_file_system.TSKFileSystem(resolver_context)


resolver.Resolver.RegisterHelper(TSKResolverHelper())

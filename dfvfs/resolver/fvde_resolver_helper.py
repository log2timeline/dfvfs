# -*- coding: utf-8 -*-
"""The FVDE volume path specification resolver helper implementation."""

from __future__ import unicode_literals

# This is necessary to prevent a circular import.
import dfvfs.file_io.fvde_file_io
import dfvfs.vfs.fvde_file_system

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class FVDEResolverHelper(resolver_helper.ResolverHelper):
  """FVDE volume resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FVDE

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FVDEFile: file-like object.
    """
    return dfvfs.file_io.fvde_file_io.FVDEFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FVDEFileSystem: file system.
    """
    return dfvfs.vfs.fvde_file_system.FVDEFileSystem(resolver_context)


resolver.Resolver.RegisterHelper(FVDEResolverHelper())

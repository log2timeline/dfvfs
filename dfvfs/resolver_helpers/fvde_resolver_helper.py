# -*- coding: utf-8 -*-
"""The FVDE volume path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import fvde_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import fvde_file_system


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
    return fvde_file_io.FVDEFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FVDEFileSystem: file system.
    """
    return fvde_file_system.FVDEFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(FVDEResolverHelper())

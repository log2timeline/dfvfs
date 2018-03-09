# -*- coding: utf-8 -*-
"""The BDE volume path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import bde_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import bde_file_system


class BDEResolverHelper(resolver_helper.ResolverHelper):
  """BDE volume resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      BDEFile: file-like object.
    """
    return bde_file_io.BDEFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      BDEFileSystem: file system.
    """
    return bde_file_system.BDEFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(BDEResolverHelper())

# -*- coding: utf-8 -*-
"""The BDE volume path specification resolver helper implementation."""

from dfvfs.file_io import bde_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import bde_file_system


class BDEResolverHelper(resolver_helper.ResolverHelper):
  """BDE volume resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      BDEFile: file input/output (IO) object.
    """
    return bde_file_io.BDEFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      BDEFileSystem: file system.
    """
    return bde_file_system.BDEFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(BDEResolverHelper())

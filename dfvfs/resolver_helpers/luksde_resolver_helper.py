# -*- coding: utf-8 -*-
"""The LUKSDE volume path specification resolver helper implementation."""

from dfvfs.file_io import luksde_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import luksde_file_system


class LUKSDEResolverHelper(resolver_helper.ResolverHelper):
  """LUKSDE volume resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LUKSDE

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      LUKSDEFile: file input/output (IO) object.
    """
    return luksde_file_io.LUKSDEFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      LUKSDEFileSystem: file system.
    """
    return luksde_file_system.LUKSDEFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(LUKSDEResolverHelper())

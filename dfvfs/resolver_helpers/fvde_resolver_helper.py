# -*- coding: utf-8 -*-
"""The FVDE volume path specification resolver helper implementation."""

from dfvfs.file_io import fvde_file_io
from dfvfs.lib import decorators
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import fvde_file_system


class FVDEResolverHelper(resolver_helper.ResolverHelper):
  """FVDE volume resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FVDE

  @decorators.deprecated
  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FVDEFile: file input/output (IO) object.
    """
    return fvde_file_io.FVDEFile(resolver_context, path_spec)

  @decorators.deprecated
  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FVDEFileSystem: file system.
    """
    return fvde_file_system.FVDEFileSystem(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(FVDEResolverHelper())

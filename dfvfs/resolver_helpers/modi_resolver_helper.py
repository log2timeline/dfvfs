# -*- coding: utf-8 -*-
"""The Mac OS disk image path specification resolver helper implementation."""

from dfvfs.file_io import modi_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper


class MODIResolverHelper(resolver_helper.ResolverHelper):
  """Mac OS disk image resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_MODI

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return modi_file_io.MODIFile(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(MODIResolverHelper())

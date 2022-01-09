# -*- coding: utf-8 -*-
"""The PHDI image path specification resolver helper implementation."""

from dfvfs.file_io import phdi_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper


class PHDIResolverHelper(resolver_helper.ResolverHelper):
  """PHDI image resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_PHDI

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return phdi_file_io.PHDIFile(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(PHDIResolverHelper())

# -*- coding: utf-8 -*-
"""The AFF4 image path specification resolver helper implementation."""

from dfvfs.file_io import aff4_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper


class AFF4ResolverHelper(resolver_helper.ResolverHelper):
  """AFF4 image resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_AFF4

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return aff4_file_io.AFF4File(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(AFF4ResolverHelper())

# -*- coding: utf-8 -*-
"""The RAW image path specification resolver helper implementation."""

from dfvfs.file_io import raw_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper


class RawResolverHelper(resolver_helper.ResolverHelper):
  """RAW storage media image resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_RAW

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: file input/output (IO) object.
    """
    return raw_file_io.RawFile(resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(RawResolverHelper())

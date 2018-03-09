# -*- coding: utf-8 -*-
"""The RAW image path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import raw_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper


class RawResolverHelper(resolver_helper.ResolverHelper):
  """RAW storage media image resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_RAW

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return raw_file_io.RawFile(resolver_context)


manager.ResolverHelperManager.RegisterHelper(RawResolverHelper())

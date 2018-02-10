# -*- coding: utf-8 -*-
"""The EWF image path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import ewf_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper


class EWFResolverHelper(resolver_helper.ResolverHelper):
  """EWF image resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_EWF

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return ewf_file_io.EWFFile(resolver_context)


manager.ResolverHelperManager.RegisterHelper(EWFResolverHelper())

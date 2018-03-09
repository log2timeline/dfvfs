# -*- coding: utf-8 -*-
"""The VHD image path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import vhdi_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper


class VHDIResolverHelper(resolver_helper.ResolverHelper):
  """VHD image resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VHDI

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return vhdi_file_io.VHDIFile(resolver_context)


manager.ResolverHelperManager.RegisterHelper(VHDIResolverHelper())

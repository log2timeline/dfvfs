# -*- coding: utf-8 -*-
"""The VMDK image path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import vmdk_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper


class VMDKResolverHelper(resolver_helper.ResolverHelper):
  """VMDK image resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VMDK

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      FileIO: file-like object.
    """
    return vmdk_file_io.VMDKFile(resolver_context)


manager.ResolverHelperManager.RegisterHelper(VMDKResolverHelper())

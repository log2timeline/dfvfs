# -*- coding: utf-8 -*-
"""The APFS container path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import apfs_container_file_system


class APFSContainerResolverHelper(resolver_helper.ResolverHelper):
  """APFS container resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APFS_CONTAINER

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      APFSContainerFileSystem: file system.
    """
    return apfs_container_file_system.APFSContainerFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(APFSContainerResolverHelper())

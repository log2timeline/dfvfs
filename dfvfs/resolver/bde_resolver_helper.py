# -*- coding: utf-8 -*-
"""The BDE volume path specification resolver helper implementation."""

from __future__ import unicode_literals

# This is necessary to prevent a circular import.
import dfvfs.file_io.bde_file_io
import dfvfs.vfs.bde_file_system

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class BDEResolverHelper(resolver_helper.ResolverHelper):
  """BDE volume resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      BDEFile: file-like object.
    """
    return dfvfs.file_io.bde_file_io.BDEFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      BDEFileSystem: file system.
    """
    return dfvfs.vfs.bde_file_system.BDEFileSystem(resolver_context)


resolver.Resolver.RegisterHelper(BDEResolverHelper())

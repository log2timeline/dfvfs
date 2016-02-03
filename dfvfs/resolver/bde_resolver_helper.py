# -*- coding: utf-8 -*-
"""The BDE volume path specification resolver helper implementation."""

# This is necessary to prevent a circular import.
import dfvfs.file_io.bde_file_io
import dfvfs.vfs.bde_file_system

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class BDEResolverHelper(resolver_helper.ResolverHelper):
  """Class that implements the BDE volume resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_BDE

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file-like object (instance of file_io.FileIO).
    """
    return dfvfs.file_io.bde_file_io.BDEFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file system object (instance of vfs.FileSystem).
    """
    return dfvfs.vfs.bde_file_system.BDEFileSystem(resolver_context)


resolver.Resolver.RegisterHelper(BDEResolverHelper())

# -*- coding: utf-8 -*-
"""The operating system path specification resolver helper implementation."""

# This is necessary to prevent a circular import.
import dfvfs.file_io.os_file_io
import dfvfs.vfs.os_file_system

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class OSResolverHelper(resolver_helper.ResolverHelper):
  """Class that implements the operating system resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OS

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file-like object (instance of file_io.FileIO).
    """
    return dfvfs.file_io.os_file_io.OSFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file system object (instance of vfs.FileSystem).
    """
    return dfvfs.vfs.os_file_system.OSFileSystem(resolver_context)


resolver.Resolver.RegisterHelper(OSResolverHelper())

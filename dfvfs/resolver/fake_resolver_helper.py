# -*- coding: utf-8 -*-
"""The fake path specification resolver helper implementation."""

# This is necessary to prevent a circular import.
import dfvfs.file_io.fake_file_io
import dfvfs.vfs.fake_file_system

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class FakeResolverHelper(resolver_helper.ResolverHelper):
  """Class that implements the fake resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_FAKE

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file-like object (instance of file_io.FileIO).
    """
    return dfvfs.file_io.fake_file_io.FakeFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file system object (instance of vfs.TSKFileSystem).
    """
    return dfvfs.vfs.fake_file_system.FakeFileSystem(resolver_context)


# Register the resolver helpers with the resolver.
resolver.Resolver.RegisterHelper(FakeResolverHelper())

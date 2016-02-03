# -*- coding: utf-8 -*-
"""The SQLite blob file path specification resolver helper implementation."""

# This is necessary to prevent a circular import.
import dfvfs.file_io.sqlite_blob_file_io
import dfvfs.vfs.sqlite_blob_file_system

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.resolver import resolver_helper


class SQLiteBlobResolverHelper(resolver_helper.ResolverHelper):
  """Class that implements the SQLite blob resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_SQLITE_BLOB

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file-like object (instance of file_io.FileIO).
    """
    return dfvfs.file_io.sqlite_blob_file_io.SQLiteBlobFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).

    Returns:
      The file system object (instance of vfs.SQLiteBlobFileSystem).
    """
    return dfvfs.vfs.sqlite_blob_file_system.SQLiteBlobFileSystem(
        resolver_context)


resolver.Resolver.RegisterHelper(SQLiteBlobResolverHelper())

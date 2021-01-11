# -*- coding: utf-8 -*-
"""The SQLite blob file path specification resolver helper implementation."""

from dfvfs.file_io import sqlite_blob_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import sqlite_blob_file_system


class SQLiteBlobResolverHelper(resolver_helper.ResolverHelper):
  """SQLite blob resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_SQLITE_BLOB

  def NewFileObject(self, resolver_context, path_spec):
    """Creates a new file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      SQLiteBlobFile: file input/output (IO) object.
    """
    return sqlite_blob_file_io.SQLiteBlobFile(resolver_context, path_spec)

  def NewFileSystem(self, resolver_context, path_spec):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.

    Returns:
      SQLiteBlobFileSystem: file system.
    """
    return sqlite_blob_file_system.SQLiteBlobFileSystem(
        resolver_context, path_spec)


manager.ResolverHelperManager.RegisterHelper(SQLiteBlobResolverHelper())

# -*- coding: utf-8 -*-
"""The SQLite blob file path specification resolver helper implementation."""

from __future__ import unicode_literals

from dfvfs.file_io import sqlite_blob_file_io
from dfvfs.lib import definitions
from dfvfs.resolver_helpers import manager
from dfvfs.resolver_helpers import resolver_helper
from dfvfs.vfs import sqlite_blob_file_system


class SQLiteBlobResolverHelper(resolver_helper.ResolverHelper):
  """SQLite blob resolver helper."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_SQLITE_BLOB

  def NewFileObject(self, resolver_context):
    """Creates a new file-like object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      SQLiteBlobFile: file-like object.
    """
    return sqlite_blob_file_io.SQLiteBlobFile(resolver_context)

  def NewFileSystem(self, resolver_context):
    """Creates a new file system object.

    Args:
      resolver_context (Context): resolver context.

    Returns:
      SQLiteBlobFileSystem: file system.
    """
    return sqlite_blob_file_system.SQLiteBlobFileSystem(resolver_context)


manager.ResolverHelperManager.RegisterHelper(SQLiteBlobResolverHelper())

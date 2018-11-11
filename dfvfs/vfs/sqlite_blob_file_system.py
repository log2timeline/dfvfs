# -*- coding: utf-8 -*-
"""The SQLite blob file system implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import sqlite_blob_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import sqlite_blob_file_entry
from dfvfs.vfs import file_system


class SQLiteBlobFileSystem(file_system.FileSystem):
  """Class that implements a file system object using SQLite blob."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_SQLITE_BLOB

  def __init__(self, resolver_context):
    """Initializes a file system.

    Args:
      resolver_context (Context): resolver context.
    """
    super(SQLiteBlobFileSystem, self).__init__(resolver_context)
    self._file_object = None
    self._number_of_rows = None

  def _Close(self):
    """Closes a file system.

    Raises:
      IOError: if the close failed.
    """
    self._file_object.close()
    self._file_object = None
    self._number_of_rows = None

  def _Open(self, path_spec, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)

    self._file_object = file_object

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.
    """
    # All checks for correct path spec is done in SQLiteBlobFile.
    # Therefore, attempt to open the path specification and
    # check if errors occurred.
    try:
      file_object = resolver.Resolver.OpenFileObject(
          path_spec, resolver_context=self._resolver_context)
    except (IOError, ValueError, errors.AccessError, errors.PathSpecError):
      return False

    file_object.close()
    return True

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      FileEntry: a file entry or None.
    """
    row_index = getattr(path_spec, 'row_index', None)
    row_condition = getattr(path_spec, 'row_condition', None)

    # If no row_index or row_condition is provided, return a directory.
    if row_index is None and row_condition is None:
      return sqlite_blob_file_entry.SQLiteBlobFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    return sqlite_blob_file_entry.SQLiteBlobFileEntry(
        self._resolver_context, self, path_spec)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      FileEntry: a file entry or None.
    """
    path_spec = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name=self._path_spec.table_name,
        column_name=self._path_spec.column_name,
        parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

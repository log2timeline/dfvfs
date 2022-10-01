# -*- coding: utf-8 -*-
"""The SQLite blob file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import sqlite_blob_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import sqlite_blob_directory


class SQLiteBlobFileEntry(file_entry.FileEntry):
  """SQLite blob file entry."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_SQLITE_BLOB

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.
    """
    super(SQLiteBlobFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._number_of_entries = None

    if is_virtual:
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    else:
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      SQLiteBlobDirectory: a directory.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return sqlite_blob_directory.SQLiteBlobDirectory(
        self._file_system, self.path_spec)

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      SQLiteBlobFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield SQLiteBlobFileEntry(
            self._resolver_context, self._file_system, path_spec)

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    row_index = getattr(self.path_spec, 'row_index', None)
    if row_index is not None:
      return f'OFFSET {row_index:d}'

    row_condition = getattr(self.path_spec, 'row_condition', None)
    if row_condition is not None and len(row_condition) == 3:
      column_name, operator, value = row_condition
      if isinstance(value, str):
        value = f'\'{value:s}\''
      return f'WHERE {column_name:s} {operator:s} {value!s}'

    # Directory name is full name of column: <table>.<column>
    table_name = getattr(self.path_spec, 'table_name', None)
    column_name = getattr(self.path_spec, 'column_name', None)
    if table_name and column_name:
      return f'{table_name:s}.{column_name:s}'

    return ''

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    size = None
    if not self._is_virtual:
      file_object = self.GetFileObject()
      if file_object:
        size = file_object.get_size()

    return size

  def GetNumberOfRows(self):
    """Retrieves the number of rows in the table.

    Returns:
      int: number of rows.

    Raises:
      BackEndError: when the SQLite blob file-like object is missing.
    """
    file_object = self.GetFileObject()
    if not file_object:
      raise errors.BackEndError(
          'Unable to retrieve SQLite blob file-like object.')

    # TODO: move this function out of SQLiteBlobFile.
    self._number_of_entries = file_object.GetNumberOfRows()

    return self._number_of_entries

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      SQLiteBlobFileEntry: parent file entry or None if not available.
    """
    # If the file entry is a sub entry, return the SQLite blob directory.
    if self._is_virtual:
      return None

    path_spec = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name=self.path_spec.table_name,
        column_name=self.path_spec.column_name,
        parent=self.path_spec.parent)
    return SQLiteBlobFileEntry(
        self._resolver_context, self._file_system,
        path_spec, is_root=True, is_virtual=True)

# -*- coding: utf-8 -*-
"""The SQLite blob file entry implementation."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import sqlite_blob_path_spec
from dfvfs.vfs import file_entry


class SQLiteBlobDirectory(file_entry.Directory):
  """SQLite blob directory."""

  def __init__(self, file_system, path_spec):
    """Initializes a directory.

    Args:
      file_system (SQLiteBlobFileSystem): file system.
      path_spec (SQLiteBlobPathSpec): path specification.
    """
    super(SQLiteBlobDirectory, self).__init__(file_system, path_spec)
    self._number_of_entries = None

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      SQLiteBlobPathSpec: a path specification.

    Raises:
      AccessError: if the access to list the directory was denied.
      BackEndError: if the directory could not be listed.
    """
    table_name = getattr(self.path_spec, 'table_name', None)
    column_name = getattr(self.path_spec, 'column_name', None)

    if table_name and column_name:
      if self._number_of_entries is None:
        # Open the first entry to determine how many entries we have.
        # TODO: change this when there is a move this to a central temp file
        # manager. https://github.com/log2timeline/dfvfs/issues/92
        path_spec = sqlite_blob_path_spec.SQLiteBlobPathSpec(
            table_name=table_name, column_name=column_name, row_index=0,
            parent=self.path_spec.parent)

        sub_file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
        if not file_entry:
          self._number_of_entries = 0
        else:
          self._number_of_entries = sub_file_entry.GetNumberOfRows()

      for row_index in range(0, self._number_of_entries):
        yield sqlite_blob_path_spec.SQLiteBlobPathSpec(
            table_name=table_name, column_name=column_name, row_index=row_index,
            parent=self.path_spec.parent)


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
    if self._directory is None:
      self._directory = SQLiteBlobDirectory(self._file_system, self.path_spec)

    return self._directory

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      SQLiteBlobFileEntry: a sub file entry.
    """
    if self.entry_type == definitions.FILE_ENTRY_TYPE_DIRECTORY:
      directory = self._GetDirectory()
      for path_spec in directory.entries:
        yield SQLiteBlobFileEntry(
            self._resolver_context, self._file_system, path_spec)

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    row_index = getattr(self.path_spec, 'row_index', None)
    if row_index is not None:
      return 'OFFSET {0:d}'.format(row_index)

    row_condition = getattr(self.path_spec, 'row_condition', None)
    if row_condition is not None:
      if len(row_condition) > 2 and isinstance(row_condition[2], str):
        return 'WHERE {0:s} {1:s} \'{2:s}\''.format(*row_condition)
      return 'WHERE {0:s} {1:s} {2!s}'.format(*row_condition)

    # Directory name is full name of column: <table>.<column>
    table_name = getattr(self.path_spec, 'table_name', None)
    column_name = getattr(self.path_spec, 'column_name', None)
    if table_name and column_name:
      return '{0:s}.{1:s}'.format(table_name, column_name)

    return ''

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    size = None
    if not self._is_virtual:
      file_object = self.GetFileObject()
      if file_object:
        try:
          size = file_object.get_size()
        finally:
          file_object.close()

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

    try:
      # TODO: move this function out of SQLiteBlobFile.
      self._number_of_entries = file_object.GetNumberOfRows()
    finally:
      file_object.close()

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

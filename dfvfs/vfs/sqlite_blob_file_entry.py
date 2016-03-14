# -*- coding: utf-8 -*-
"""The SQLite blob file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import sqlite_blob_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


class SQLiteBlobDirectory(file_entry.Directory):
  """Class that implements a SQLite blob directory object."""

  def __init__(self, file_system, path_spec):
    """Initializes the directory object.

    Args:
      file_system: the file system object (instance of FileSystem).
      path_spec: the path specification object (instance of PathSpec).
    """
    super(SQLiteBlobDirectory, self).__init__(file_system, path_spec)
    self._number_of_entries = None

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      A path specification (instance of path.SQLiteBlobPathSpec).

    Raises:
      AccessError: if the access to list the directory was denied.
      BackEndError: if the directory could not be listed.
    """
    table_name = getattr(self.path_spec, u'table_name', None)
    if table_name is None:
      return

    column_name = getattr(self.path_spec, u'column_name', None)
    if column_name is None:
      return

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
  """Class that implements a file entry object using sqlite."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_SQLITE_BLOB

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes the file entry object.

    Args:
      resolver_context: the resolver context (instance of Context).
      file_system: the file system object (instance of FileSystem).
      path_spec: the path specification object (instance of PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system.
    """
    super(SQLiteBlobFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._number_of_entries = None

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the SQLite blob file-like object is missing.
    """
    stat_object = vfs_stat.VFSStat()

    # The root file entry is virtual and should have type directory.
    if self._is_virtual:
      stat_object.type = stat_object.TYPE_DIRECTORY
    else:
      file_object = self.GetFileObject()
      if not file_object:
        raise errors.BackEndError(
            u'Unable to retrieve SQLite blob file-like object.')

      try:
        stat_object.type = stat_object.TYPE_FILE
        stat_object.size = file_object.get_size()
      finally:
        file_object.close()

    return stat_object

  @property
  def name(self):
    """The name of the file entry, which does not include the full path."""
    row_index = getattr(self.path_spec, u'row_index', None)
    if row_index is not None:
      return u'OFFSET {0:d}'.format(row_index)

    row_condition = getattr(self.path_spec, u'row_condition', None)
    if row_condition is not None:
      return u'WHERE {0:s} {1:s} \'{2:s}\''.format(*row_condition)

    # Directory name is full name of column: <table>.<column>
    table_name = getattr(self.path_spec, u'table_name', None)
    column_name = getattr(self.path_spec, u'column_name', None)
    if table_name and column_name:
      return u'{0:s}.{1:s}'.format(table_name, column_name)
    else:
      return u''

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.SQLiteBlobFileEntry).
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield SQLiteBlobFileEntry(
            self._resolver_context, self._file_system, path_spec)

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      A directory object (instance of Directory) or None.
    """
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return SQLiteBlobDirectory(self._file_system, self.path_spec)
    return

  def GetNumberOfRows(self):
    """Retrieves the number of rows in the table.

    Returns:
      An integer containing the number of rows.

    Raises:
      BackEndError: when the SQLite blob file-like object is missing.
    """
    file_object = self.GetFileObject()
    if not file_object:
      raise errors.BackEndError(
          u'Unable to retrieve SQLite blob file-like object.')

    try:
      # TODO: move this function out of SQLiteBlobFile.
      self._number_of_entries = file_object.GetNumberOfRows()
    finally:
      file_object.close()

    return self._number_of_entries

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      The parent file entry (instance of FileEntry) or None.
    """
    # If the file entry is a sub entry, return the SQLite blob directory.
    if self._is_virtual:
      return

    path_spec = sqlite_blob_path_spec.SQLiteBlobPathSpec(
        table_name=self.path_spec.table_name,
        column_name=self.path_spec.column_name,
        parent=self.path_spec.parent)
    return SQLiteBlobFileEntry(
        self._resolver_context, self._file_system,
        path_spec, is_root=True, is_virtual=True)

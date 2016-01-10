# -*- coding: utf-8 -*-
"""The SQLite blob file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import sqlite_blob_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


class SQLiteBlobDirectory(file_entry.Directory):
  """Class that implements a SQLite blob directory object."""

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

    number_of_rows = self._file_system.GetNumberOfRows(self.path_spec)
    for row_index in range(0, number_of_rows):
      yield sqlite_blob_path_spec.SQLiteBlobPathSpec(
          table_name=table_name, column_name=column_name, row_index=row_index,
          parent=self.path_spec.parent)


class SQLiteBlobFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using sqlite."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_SQLITE_BLOB

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the SQLite blob is missing.
    """
    blob_file = self.GetFileObject()
    if not blob_file:
      raise errors.BackEndError(
          u'Unable to open blob file: {0:s}.'.format(self.path_spec.comparable))

    try:
      stat_object = vfs_stat.VFSStat()

      # The root file entry is virtual and should have type directory.
      if self._is_virtual:
        stat_object.type = stat_object.TYPE_DIRECTORY
      else:
        stat_object.type = stat_object.TYPE_FILE
        stat_object.size = blob_file.get_size()

    finally:
      blob_file.close()

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

  @property
  def number_of_sub_file_entries(self):
    """The number of sub file entries."""
    return self._file_system.GetNumberOfRows(self.path_spec)

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      A directory object (instance of Directory) or None.
    """
    return SQLiteBlobDirectory(self._file_system, self.path_spec)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry."""
    # If the file entry is a sub entry, return the SQLite blob directory.
    if not self._is_virtual:
      path_spec = sqlite_blob_path_spec.SQLiteBlobPathSpec(
          table_name=self.path_spec.table_name,
          column_name=self.path_spec.column_name,
          parent=self.path_spec.parent)
      return SQLiteBlobFileEntry(
          self._resolver_context, self._file_system,
          path_spec, is_root=True, is_virtual=True)

# -*- coding: utf-8 -*-
"""The SQLite blob directory implementation."""

from dfvfs.path import sqlite_blob_path_spec
from dfvfs.vfs import directory


class SQLiteBlobDirectory(directory.Directory):
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
        if not sub_file_entry:
          self._number_of_entries = 0
        else:
          self._number_of_entries = sub_file_entry.GetNumberOfRows()

      for row_index in range(0, self._number_of_entries):
        yield sqlite_blob_path_spec.SQLiteBlobPathSpec(
            table_name=table_name, column_name=column_name, row_index=row_index,
            parent=self.path_spec.parent)

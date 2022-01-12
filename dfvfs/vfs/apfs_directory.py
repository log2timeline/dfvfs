# -*- coding: utf-8 -*-
"""The APFS directory implementation."""

from dfvfs.lib import errors
from dfvfs.path import apfs_path_spec
from dfvfs.vfs import directory


class APFSDirectory(directory.Directory):
  """File system directory that uses pyfsapfs."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      APFSPathSpec: APFS path specification.
    """
    try:
      fsapfs_file_entry = self._file_system.GetAPFSFileEntryByPathSpec(
          self.path_spec)
    except errors.PathSpecError:
      return

    location = getattr(self.path_spec, 'location', None)

    for fsapfs_sub_file_entry in fsapfs_file_entry.sub_file_entries:
      directory_entry = fsapfs_sub_file_entry.name

      if not location or location == self._file_system.PATH_SEPARATOR:
        directory_entry = self._file_system.JoinPath([directory_entry])
      else:
        directory_entry = self._file_system.JoinPath([
            location, directory_entry])

      yield apfs_path_spec.APFSPathSpec(
          identifier=fsapfs_sub_file_entry.identifier, location=directory_entry,
          parent=self.path_spec.parent)

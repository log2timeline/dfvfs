# -*- coding: utf-8 -*-
"""The HFS directory implementation."""

from dfvfs.lib import errors
from dfvfs.path import hfs_path_spec
from dfvfs.vfs import directory


class HFSDirectory(directory.Directory):
  """File system directory that uses pyfshfs."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      HFSPathSpec: HFS path specification.
    """
    try:
      fshfs_file_entry = self._file_system.GetHFSFileEntryByPathSpec(
          self.path_spec)
    except errors.PathSpecError:
      return

    location = getattr(self.path_spec, 'location', None)

    for fshfs_sub_file_entry in fshfs_file_entry.sub_file_entries:
      directory_entry = fshfs_sub_file_entry.name

      if not location or location == self._file_system.PATH_SEPARATOR:
        directory_entry = self._file_system.JoinPath([directory_entry])
      else:
        directory_entry = self._file_system.JoinPath([
            location, directory_entry])

      yield hfs_path_spec.HFSPathSpec(
          identifier=fshfs_sub_file_entry.identifier, location=directory_entry,
          parent=self.path_spec.parent)

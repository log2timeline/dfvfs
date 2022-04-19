# -*- coding: utf-8 -*-
"""The HFS directory implementation."""

from dfvfs.path import hfs_path_spec
from dfvfs.vfs import directory


class HFSDirectory(directory.Directory):
  """File system directory that uses pyfshfs."""

  def __init__(self, file_system, path_spec, fshfs_file_entry):
    """Initializes a directory.

    Args:
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      fshfs_file_entry (pyfshfs.file_entry): HFS file entry.
    """
    super(HFSDirectory, self).__init__(file_system, path_spec)
    self._fshfs_file_entry = fshfs_file_entry

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      HFSPathSpec: HFS path specification.
    """
    location = getattr(self.path_spec, 'location', None)

    for fshfs_sub_file_entry in self._fshfs_file_entry.sub_file_entries:
      directory_entry = fshfs_sub_file_entry.name

      if not location or location == self._file_system.PATH_SEPARATOR:
        directory_entry = self._file_system.JoinPath([directory_entry])
      else:
        directory_entry = self._file_system.JoinPath([
            location, directory_entry])

      yield hfs_path_spec.HFSPathSpec(
          identifier=fshfs_sub_file_entry.identifier, location=directory_entry,
          parent=self.path_spec.parent)

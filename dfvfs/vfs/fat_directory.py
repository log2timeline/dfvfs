# -*- coding: utf-8 -*-
"""The FAT directory implementation."""

from dfvfs.path import fat_path_spec
from dfvfs.vfs import directory


class FATDirectory(directory.Directory):
  """File system directory that uses pyfsfat."""

  def __init__(self, file_system, path_spec, fsfat_file_entry):
    """Initializes a directory.

    Args:
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      fsfat_file_entry (pyfsfat.file_entry): FAT file entry.
    """
    super(FATDirectory, self).__init__(file_system, path_spec)
    self._fsfat_file_entry = fsfat_file_entry

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      FATPathSpec: FAT path specification.
    """
    location = getattr(self.path_spec, 'location', None)

    for fsfat_sub_file_entry in self._fsfat_file_entry.sub_file_entries:
      directory_entry = fsfat_sub_file_entry.name

      if not location or location == self._file_system.PATH_SEPARATOR:
        directory_entry = self._file_system.JoinPath([directory_entry])
      else:
        directory_entry = self._file_system.JoinPath([
            location, directory_entry])

      yield fat_path_spec.FATPathSpec(
          identifier=fsfat_sub_file_entry.identifier, location=directory_entry,
          parent=self.path_spec.parent)

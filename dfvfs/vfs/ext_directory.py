# -*- coding: utf-8 -*-
"""The EXT directory implementation."""

from dfvfs.path import ext_path_spec
from dfvfs.vfs import directory


class EXTDirectory(directory.Directory):
  """File system directory that uses pyfsext."""

  def __init__(self, file_system, path_spec, fsext_file_entry):
    """Initializes a directory.

    Args:
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      fsext_file_entry (pyfsext.file_entry): EXT file entry.
    """
    super(EXTDirectory, self).__init__(file_system, path_spec)
    self._fsext_file_entry = fsext_file_entry

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      EXTPathSpec: EXT path specification.
    """
    location = getattr(self.path_spec, 'location', None)

    for fsext_sub_file_entry in self._fsext_file_entry.sub_file_entries:
      directory_entry = fsext_sub_file_entry.name

      if not location or location == self._file_system.PATH_SEPARATOR:
        directory_entry = self._file_system.JoinPath([directory_entry])
      else:
        directory_entry = self._file_system.JoinPath([
            location, directory_entry])

      yield ext_path_spec.EXTPathSpec(
          inode=fsext_sub_file_entry.inode_number, location=directory_entry,
          parent=self.path_spec.parent)

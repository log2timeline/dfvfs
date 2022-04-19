# -*- coding: utf-8 -*-
"""The NTFS directory implementation."""

from dfvfs.path import ntfs_path_spec
from dfvfs.vfs import directory


class NTFSDirectory(directory.Directory):
  """File system directory that uses pyfsntfs."""

  _FILE_REFERENCE_MFT_ENTRY_BITMASK = 0xffffffffffff

  def __init__(self, file_system, path_spec, fsntfs_file_entry):
    """Initializes a directory.

    Args:
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      fsntfs_file_entry (pyfsntfs.file_entry): NTFS file entry.
    """
    super(NTFSDirectory, self).__init__(file_system, path_spec)
    self._fsntfs_file_entry = fsntfs_file_entry

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      NTFSPathSpec: NTFS path specification.
    """
    location = getattr(self.path_spec, 'location', None)

    for fsntfs_sub_file_entry in self._fsntfs_file_entry.sub_file_entries:
      directory_entry = fsntfs_sub_file_entry.name

      # Ignore references to self or parent.
      if directory_entry in ('.', '..'):
        continue

      file_reference = fsntfs_sub_file_entry.file_reference
      directory_entry_mft_entry = (
          file_reference & self._FILE_REFERENCE_MFT_ENTRY_BITMASK)

      if not location or location == self._file_system.PATH_SEPARATOR:
        directory_entry = self._file_system.JoinPath([directory_entry])
      else:
        directory_entry = self._file_system.JoinPath([
            location, directory_entry])

      yield ntfs_path_spec.NTFSPathSpec(
          location=directory_entry,
          mft_attribute=fsntfs_sub_file_entry.name_attribute_index,
          mft_entry=directory_entry_mft_entry, parent=self.path_spec.parent)

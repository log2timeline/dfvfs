# -*- coding: utf-8 -*-
"""The XFS directory implementation."""

from dfvfs.path import xfs_path_spec
from dfvfs.vfs import directory


class XFSDirectory(directory.Directory):
  """File system directory that uses pyfsxfs."""

  def __init__(self, file_system, path_spec, fsxfs_file_entry):
    """Initializes a directory.

    Args:
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      fsxfs_file_entry (pyfsxfs.file_entry): XFS file entry.
    """
    super(XFSDirectory, self).__init__(file_system, path_spec)
    self._fsxfs_file_entry = fsxfs_file_entry

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      XFSPathSpec: XFS path specification.
    """
    location = getattr(self.path_spec, 'location', None)

    for fsxfs_sub_file_entry in self._fsxfs_file_entry.sub_file_entries:
      directory_entry = fsxfs_sub_file_entry.name

      if not location or location == self._file_system.PATH_SEPARATOR:
        directory_entry = self._file_system.JoinPath([directory_entry])
      else:
        directory_entry = self._file_system.JoinPath([
            location, directory_entry])

      yield xfs_path_spec.XFSPathSpec(
          inode=fsxfs_sub_file_entry.inode_number, location=directory_entry,
          parent=self.path_spec.parent)

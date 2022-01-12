# -*- coding: utf-8 -*-
"""The XFS directory implementation."""

from dfvfs.lib import errors
from dfvfs.path import xfs_path_spec
from dfvfs.vfs import directory


class XFSDirectory(directory.Directory):
  """File system directory that uses pyfsxfs."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      XFSPathSpec: XFS path specification.
    """
    try:
      fsxfs_file_entry = self._file_system.GetXFSFileEntryByPathSpec(
          self.path_spec)
    except errors.PathSpecError:
      return

    location = getattr(self.path_spec, 'location', None)

    for fsxfs_sub_file_entry in fsxfs_file_entry.sub_file_entries:
      directory_entry = fsxfs_sub_file_entry.name

      if not location or location == self._file_system.PATH_SEPARATOR:
        directory_entry = self._file_system.JoinPath([directory_entry])
      else:
        directory_entry = self._file_system.JoinPath([
            location, directory_entry])

      yield xfs_path_spec.XFSPathSpec(
          inode=fsxfs_sub_file_entry.inode_number, location=directory_entry,
          parent=self.path_spec.parent)

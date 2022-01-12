# -*- coding: utf-8 -*-
"""The EXT directory implementation."""

from dfvfs.lib import errors
from dfvfs.path import ext_path_spec
from dfvfs.vfs import directory


class EXTDirectory(directory.Directory):
  """File system directory that uses pyfsext."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      EXTPathSpec: EXT path specification.
    """
    try:
      fsext_file_entry = self._file_system.GetEXTFileEntryByPathSpec(
          self.path_spec)
    except errors.PathSpecError:
      return

    location = getattr(self.path_spec, 'location', None)

    for fsext_sub_file_entry in fsext_file_entry.sub_file_entries:
      directory_entry = fsext_sub_file_entry.name

      if not location or location == self._file_system.PATH_SEPARATOR:
        directory_entry = self._file_system.JoinPath([directory_entry])
      else:
        directory_entry = self._file_system.JoinPath([
            location, directory_entry])

      yield ext_path_spec.EXTPathSpec(
          inode=fsext_sub_file_entry.inode_number, location=directory_entry,
          parent=self.path_spec.parent)

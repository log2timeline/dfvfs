# -*- coding: utf-8 -*-
"""The CPIO directory implementation."""

from dfvfs.path import cpio_path_spec
from dfvfs.vfs import directory


class CPIODirectory(directory.Directory):
  """File system directory that uses CPIOArchiveFile."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      CPIOPathSpec: path specification.
    """
    location = getattr(self.path_spec, 'location', None)

    if location and location.startswith(self._file_system.PATH_SEPARATOR):
      cpio_archive_file = self._file_system.GetCPIOArchiveFile()
      sub_directories = set()
      for cpio_archive_file_entry in cpio_archive_file.GetFileEntries(
          path_prefix=location[1:]):

        path = cpio_archive_file_entry.path
        if not path or path == location:
          continue

        prefix, suffix = self._file_system.GetPathSegmentAndSuffix(
            location[1:], path)

        if not suffix:
          path_spec_location = self._file_system.JoinPath([path])
          yield cpio_path_spec.CPIOPathSpec(
              location=path_spec_location, parent=self.path_spec.parent)

        elif prefix not in sub_directories:
          sub_directories.add(prefix)

          # Include prefixes as virtual sub directories.
          path_spec_location = self._file_system.JoinPath([prefix])
          yield cpio_path_spec.CPIOPathSpec(
              location=path_spec_location, parent=self.path_spec.parent)

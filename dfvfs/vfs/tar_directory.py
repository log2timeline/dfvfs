# -*- coding: utf-8 -*-
"""The TAR directory implementation."""

from dfvfs.path import tar_path_spec
from dfvfs.vfs import directory


class TARDirectory(directory.Directory):
  """File system directory that uses tarfile."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      TARPathSpec: TAR path specification.
    """
    location = getattr(self.path_spec, 'location', None)

    if location and location.startswith(self._file_system.PATH_SEPARATOR):
      # The TAR info name does not have the leading path separator as
      # the location string does.
      tar_path = location[1:]

      # Set of top level sub directories that have been yielded.
      processed_directories = set()

      tar_file = self._file_system.GetTARFile()
      for tar_info in tar_file.getmembers():
        path = tar_info.name

        # Determine if the start of the TAR info name is similar to
        # the location string. If not the file TAR info refers to is not in
        # the same directory.
        if not path or not path.startswith(tar_path):
          continue

        # Ignore the directory itself.
        if path == tar_path:
          continue

        path_segment, suffix = self._file_system.GetPathSegmentAndSuffix(
            tar_path, path)
        if not path_segment:
          continue

        # Sometimes the TAR file lacks directories, therefore we will
        # provide virtual ones.
        if suffix:
          path_spec_location = self._file_system.JoinPath([
              location, path_segment])
          is_directory = True

        else:
          path_spec_location = self._file_system.JoinPath([path])
          is_directory = tar_info.isdir()

        if is_directory:
          if path_spec_location in processed_directories:
            continue
          processed_directories.add(path_spec_location)

        yield tar_path_spec.TARPathSpec(
            location=path_spec_location, parent=self.path_spec.parent)

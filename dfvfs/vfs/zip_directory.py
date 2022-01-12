# -*- coding: utf-8 -*-
"""The ZIP directory implementation."""

from dfvfs.path import zip_path_spec
from dfvfs.vfs import directory


class ZIPDirectory(directory.Directory):
  """File system directory that uses zipfile."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      ZipPathSpec: a path specification.
    """
    location = getattr(self.path_spec, 'location', None)

    if location and location.startswith(self._file_system.PATH_SEPARATOR):
      # The zip_info filename does not have the leading path separator
      # as the location string does.
      zip_path = location[1:]

      # Set of top level sub directories that have been yielded.
      processed_directories = set()

      zip_file = self._file_system.GetZipFile()
      for zip_info in zip_file.infolist():
        path = getattr(zip_info, 'filename', None)
        if path is not None and not isinstance(path, str):
          try:
            path = path.decode(self._file_system.encoding)
          except UnicodeDecodeError:
            path = None

        if not path or not path.startswith(zip_path):
          continue

        # Ignore the directory itself.
        if path == zip_path:
          continue

        path_segment, suffix = self._file_system.GetPathSegmentAndSuffix(
            zip_path, path)
        if not path_segment:
          continue

        # Some times the ZIP file lacks directories, therefore we will
        # provide virtual ones.
        if suffix:
          path_spec_location = self._file_system.JoinPath([
              location, path_segment])
          is_directory = True
        else:
          path_spec_location = self._file_system.JoinPath([path])
          is_directory = path.endswith('/')

        if is_directory:
          if path_spec_location in processed_directories:
            continue
          processed_directories.add(path_spec_location)
          # Restore / at end path to indicate a directory.
          path_spec_location += self._file_system.PATH_SEPARATOR

        yield zip_path_spec.ZipPathSpec(
            location=path_spec_location, parent=self.path_spec.parent)

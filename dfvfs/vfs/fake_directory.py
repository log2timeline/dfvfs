# -*- coding: utf-8 -*-
"""The fake directory implementation."""

from dfvfs.path import fake_path_spec
from dfvfs.vfs import directory


class FakeDirectory(directory.Directory):
  """Fake file system directory."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      FakePathSpec: a path specification.
    """
    location = getattr(self.path_spec, 'location', None)
    if location is not None:
      paths = self._file_system.GetPaths()

      for path in paths.keys():
        # Determine if the start of the path is similar to the location string.
        # If not the file the path refers to is not in the same directory.
        if not path or not path.startswith(location):
          continue

        _, suffix = self._file_system.GetPathSegmentAndSuffix(location, path)

        # Ignore anything that is part of a sub directory or the directory
        # itself.
        if suffix or path == location:
          continue

        path_spec_location = self._file_system.JoinPath([path])
        yield fake_path_spec.FakePathSpec(location=path_spec_location)

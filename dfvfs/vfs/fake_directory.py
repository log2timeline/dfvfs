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
        location = getattr(self.path_spec, "location", None)
        if location is not None:
            for path_spec_location in self._file_system.GetDirectoryEntryLocations(
                location
            ):
                yield fake_path_spec.FakePathSpec(location=path_spec_location)

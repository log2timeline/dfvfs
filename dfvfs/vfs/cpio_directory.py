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
        location = getattr(self.path_spec, "location", None)

        if location and location.startswith(self._file_system.PATH_SEPARATOR):
            for path_spec_location in self._file_system.GetDirectoryEntryLocations(
                location
            ):
                yield cpio_path_spec.CPIOPathSpec(
                    location=path_spec_location, parent=self.path_spec.parent
                )

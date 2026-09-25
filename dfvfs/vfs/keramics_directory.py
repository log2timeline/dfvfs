# -*- coding: utf-8 -*-
"""The Keramics directory implementation."""

from dfvfs.lib import errors
from dfvfs.path import keramics_path_spec
from dfvfs.vfs import directory


class KeramicsDirectory(directory.Directory):
    """File system directory that uses pykeramics."""

    def __init__(self, file_system, path_spec, pykeramics_file_entry):
        """Initializes a directory.

        Args:
          file_system (FileSystem): file system.
          path_spec (PathSpec): path specification.
          pykeramics_file_entry (pykeramics.VfsFileEntry): pykeramics file entry.
        """
        super().__init__(file_system, path_spec)
        self._keramics_file_entry = pykeramics_file_entry

    def _EntriesGenerator(self):
        """Retrieves directory entries.

        Since a directory can contain a vast number of entries using
        a generator is more memory efficient.

        Yields:
          KeramicsPathSpec: Keramics path specification.

        Raises:
          BackEndError: if the sub file entries cannot be retrieved.
        """
        pykeramics_location = getattr(self.path_spec, "location", None)

        try:
            number_of_sub_file_entries = (
                self._keramics_file_entry.get_number_of_sub_file_entries()
            )
        except RuntimeError as exception:
            raise errors.BackEndError(exception)

        for sub_file_entry_index in range(number_of_sub_file_entries):
            try:
                sub_file_entry = self._keramics_file_entry.get_sub_file_entry_by_index(
                    sub_file_entry_index
                )
            except RuntimeError as exception:
                raise errors.BackEndError(exception)

            sub_file_entry_path = (
                pykeramics_location.path.new_with_join_path_components(
                    [sub_file_entry.name]
                )
            )
            sub_file_entry_location = pykeramics_location.new_with_parent(
                sub_file_entry_path
            )
            yield keramics_path_spec.KeramicsPathSpec(location=sub_file_entry_location)

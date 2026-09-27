# -*- coding: utf-8 -*-
"""The Keramics file system implementation."""

from pykeramics import vfs as pykeramics_vfs

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.vfs import file_system
from dfvfs.vfs import keramics_file_entry


class KeramicsFileSystem(file_system.FileSystem):
    """File system that uses pykeramics."""

    TYPE_INDICATOR = definitions.TYPE_INDICATOR_KERAMICS

    def __init__(self, resolver_context, path_spec):
        """Initializes a Keramics file system.

        Args:
          resolver_context (Context): resolver context.
          path_spec (PathSpec): a path specification.
        """
        super().__init__(resolver_context, path_spec)
        self._keramics_file_system = None

    def _Close(self):
        """Closes the file system.

        Raises:
          IOError: if the close failed.
        """
        self._keramics_file_system = None

    def _Open(self, mode="rb"):
        """Opens the file system defined by path specification.

        Args:
          mode (Optional[str]): file access mode.

        Raises:
          BackEndError: if the file system could not be opened by pykeramics.
          IOError: if the file system object could not be opened.
        """
        pykeramics_location = getattr(self._path_spec, "location", None)

        try:
            pykeramics_resolver = pykeramics_vfs.VfsResolver()
            pykeramics_file_system = pykeramics_resolver.open_file_system(
                pykeramics_location
            )
        except RuntimeError as exception:
            raise errors.BackEndError(exception)

        if not pykeramics_file_system:
            raise IOError("Unable to open file system.")

        self._keramics_file_system = pykeramics_file_system

    def FileEntryExistsByPathSpec(self, path_spec):
        """Determines if a file entry for a path specification exists.

        Args:
          path_spec (PathSpec): path specification.

        Returns:
          bool: True if the file entry exists.

        Raises:
          BackEndError: if unable to determine if the file entry exists.
        """
        pykeramics_location = getattr(path_spec, "location", None)

        try:
            return self._keramics_file_system.file_entry_exists(
                pykeramics_location.path
            )
        except RuntimeError as exception:
            raise errors.BackEndError(exception)

    def GetFileEntryByPathSpec(self, path_spec):
        """Retrieves a file entry for a path specification.

        Args:
          path_spec (PathSpec): path specification.

        Returns:
          KeramicsFileEntry: file entry or None if not available.

        Raises:
          BackEndError: if the file entry cannot be opened.
        """
        pykeramics_location = getattr(path_spec, "location", None)

        if pykeramics_location.path.is_root():
            return self.GetRootFileEntry()

        pykeramics_file_entry = self.GetKeramicsFileEntryByPathSpec(path_spec)
        if not pykeramics_file_entry:
            return None

        return keramics_file_entry.KeramicsFileEntry(
            self._resolver_context,
            self,
            path_spec,
            pykeramics_file_entry=pykeramics_file_entry,
        )

    def GetKeramicsFileEntryByPathSpec(self, path_spec):
        """Retrieves the Keramics file entry for a path specification.

        Args:
          path_spec (PathSpec): a path specification.

        Returns:
          pykeramics.VfsFileEntry: file entry or None if not available.

        Raises:
          BackEndError: if the file entry cannot be opened.
        """
        pykeramics_location = getattr(path_spec, "location", None)

        try:
            return self._keramics_file_system.get_file_entry_by_path(
                pykeramics_location.path
            )
        except RuntimeError as exception:
            raise errors.BackEndError(exception)

    def GetRootFileEntry(self):
        """Retrieves the root file entry.

        Returns:
          KeramicsFileEntry: file entry or None if not available.
        """
        try:
            pykeramics_file_entry = self._keramics_file_system.get_root_file_entry()
        except RuntimeError as exception:
            raise errors.BackEndError(exception)

        if not pykeramics_file_entry:
            return None

        return keramics_file_entry.KeramicsFileEntry(
            self._resolver_context,
            self,
            self._path_spec,
            is_root=True,
            pykeramics_file_entry=pykeramics_file_entry,
        )

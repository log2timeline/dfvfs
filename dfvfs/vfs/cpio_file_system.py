"""The CPIO archive file system implementation."""

from dfvfs.lib import cpio
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import cpio_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import cpio_file_entry
from dfvfs.vfs import file_system


class CPIOFileSystem(file_system.FileSystem):
    """CPIO archive file system."""

    TYPE_INDICATOR = definitions.TYPE_INDICATOR_CPIO

    def __init__(self, resolver_context, path_spec, encoding="utf-8"):
        """Initializes a CPIO archive file system.

        Args:
          resolver_context (Context): resolver context.
          path_spec (PathSpec): a path specification.
          encoding (Optional[str]): file entry name encoding.
        """
        super().__init__(resolver_context, path_spec)
        self._cpio_archive_file = None
        self._directory_entries = None
        self._file_object = None
        self.encoding = encoding

    def _Close(self):
        """Closes the file system.

        Raises:
          OSError: if the close failed.
        """
        self._cpio_archive_file.Close()
        self._cpio_archive_file = None
        self._directory_entries = None
        self._file_object = None

    def _BuildDirectoryEntries(self):
        """Builds the directory entry index.

        The index is built once when the file system is opened so that listing
        a directory does not need to scan all the file entries of the archive.
        """
        directory_entries = {}

        for cpio_archive_file_entry in self._cpio_archive_file.GetFileEntries():
            path = cpio_archive_file_entry.path
            if not path:
                continue

            # A directory can contain the file entry directly or by one of its sub
            # directories, hence the file entry is evaluated for every parent
            # location. The location of the file entry itself is included since
            # listing it yields the file entry itself.
            segments = [
                segment for segment in path.split(self.PATH_SEPARATOR) if segment
            ]

            locations = [self.LOCATION_ROOT]
            location = ""
            for segment in segments:
                location = f"{location:s}{self.PATH_SEPARATOR:s}{segment:s}"
                locations.append(location)

            for location in locations:
                directory_entry = self._GetDirectoryEntry(location, path)
                if directory_entry is None:
                    continue

                entries, sub_directories = directory_entries.setdefault(
                    location, ([], set())
                )

                path_spec_location, is_sub_directory = directory_entry
                if is_sub_directory:
                    # Include prefixes as virtual sub directories.
                    if path_spec_location in sub_directories:
                        continue
                    sub_directories.add(path_spec_location)

                entries.append(path_spec_location)

        self._directory_entries = {
            location: entries for location, (entries, _) in directory_entries.items()
        }

    def _GetDirectoryEntry(self, location, path):
        """Determines the directory entry of a path for a directory location.

        Args:
          location (str): location of the directory.
          path (str): path of an archive file entry.

        Returns:
          tuple[str, bool]: location of the directory entry and True if the entry
              is a sub directory implied by the path, or None if the path is not
              part of the directory.
        """
        if not path.startswith(location[1:]) or path == location:
            return None

        prefix, suffix = self.GetPathSegmentAndSuffix(location[1:], path)

        if not suffix:
            return self.JoinPath([path]), False

        return self.JoinPath([prefix]), True

    def _Open(self, mode="rb"):
        """Opens the file system defined by path specification.

        Args:
          mode (Optional[str]): file access mode. The default is 'rb' which
              represents read-only binary.

        Raises:
          AccessError: if the access to open the file was denied.
          OSError: if the file system could not be opened.
          PathSpecError: if the path specification is incorrect.
          ValueError: if the path specification is invalid.
        """
        if not self._path_spec.HasParent():
            raise errors.PathSpecError("Unsupported path specification without parent.")

        file_object = resolver.Resolver.OpenFileObject(
            self._path_spec.parent, resolver_context=self._resolver_context
        )

        cpio_archive_file = cpio.CPIOArchiveFile()
        cpio_archive_file.Open(file_object)

        self._file_object = file_object
        self._cpio_archive_file = cpio_archive_file

        self._BuildDirectoryEntries()

    def FileEntryExistsByPathSpec(self, path_spec):
        """Determines if a file entry for a path specification exists.

        Args:
          path_spec (PathSpec): a path specification.

        Returns:
          bool: True if the file entry exists.
        """
        location = getattr(path_spec, "location", None)
        if location is None or not location.startswith(self.LOCATION_ROOT):
            return False

        if len(location) == 1:
            return True

        return self._cpio_archive_file.FileEntryExistsByPath(location[1:])

    def GetCPIOArchiveFile(self):
        """Retrieves the CPIO archive file.

        Returns:
          CPIOArchiveFile: a CPIO archive file.
        """
        return self._cpio_archive_file

    def GetCPIOArchiveFileEntryByPathSpec(self, path_spec):
        """Retrieves the CPIO archive file entry for a path specification.

        Args:
          path_spec (PathSpec): a path specification.

        Returns:
          CPIOArchiveFileEntry: CPIO archive file entry or None if not available.

        Raises:
          PathSpecError: if the path specification is incorrect.
        """
        location = getattr(path_spec, "location", None)
        if location is None:
            raise errors.PathSpecError("Path specification missing location.")

        if not location.startswith(self.LOCATION_ROOT):
            raise errors.PathSpecError("Invalid location in path specification.")

        if len(location) == 1:
            return None

        return self._cpio_archive_file.GetFileEntryByPath(location[1:])

    def GetDirectoryEntryLocations(self, location):
        """Retrieves the locations of the entries of a directory.

        Args:
          location (str): location of the directory.

        Returns:
          list[str]: locations of the directory entries, in archive order.
        """
        location = self.JoinPath([location])
        return self._directory_entries.get(location, [])

    def GetFileEntryByPathSpec(self, path_spec):
        """Retrieves a file entry for a path specification.

        Args:
          path_spec (PathSpec): a path specification.

        Returns:
          CPIOFileEntry: a file entry or None if not available.
        """
        location = getattr(path_spec, "location", None)

        if location is None or not location.startswith(self.LOCATION_ROOT):
            return None

        if len(location) == 1:
            return cpio_file_entry.CPIOFileEntry(
                self._resolver_context, self, path_spec, is_root=True, is_virtual=True
            )

        cpio_archive_file_entry = self._cpio_archive_file.GetFileEntryByPath(
            location[1:]
        )
        if cpio_archive_file_entry is None:
            return None

        return cpio_file_entry.CPIOFileEntry(
            self._resolver_context,
            self,
            path_spec,
            cpio_archive_file_entry=cpio_archive_file_entry,
        )

    def GetRootFileEntry(self):
        """Retrieves the root file entry.

        Returns:
          CPIOFileEntry: a file entry or None if not available.
        """
        path_spec = cpio_path_spec.CPIOPathSpec(
            location=self.LOCATION_ROOT, parent=self._path_spec.parent
        )
        return self.GetFileEntryByPathSpec(path_spec)

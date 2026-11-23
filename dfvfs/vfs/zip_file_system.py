"""The ZIP file system implementation."""

import zipfile

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import zip_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import zip_file_entry


class ZipFileSystem(file_system.FileSystem):
    """File system that uses zipfile.

    Attributes:
      encoding (str): encoding of the file entry name.
    """

    TYPE_INDICATOR = definitions.TYPE_INDICATOR_ZIP

    def __init__(self, resolver_context, path_spec, encoding="utf-8"):
        """Initializes a file system.

        Args:
          resolver_context (Context): a resolver context.
          path_spec (PathSpec): a path specification.
          encoding (Optional[str]): encoding of the file entry name.
        """
        super().__init__(resolver_context, path_spec)
        self._directory_entries = None
        self._directory_paths = None
        self._file_object = None
        self._zip_file = None
        self.encoding = encoding

    def _Close(self):
        """Closes the file system object.

        Raises:
          OSError: if the close failed.
        """
        self._zip_file.close()
        self._zip_file = None
        self._directory_entries = None
        self._directory_paths = None
        self._file_object = None

    def _BuildDirectoryEntries(self):
        """Builds the directory entry index.

        The index is built once when the file system is opened so that listing
        a directory does not need to scan all the members of the archive.
        """
        directory_entries = {}

        for zip_info in self._zip_file.infolist():
            path = getattr(zip_info, "filename", None)
            if path is not None and not isinstance(path, str):
                try:
                    path = path.decode(self.encoding)
                except UnicodeDecodeError:
                    path = None

            if not path:
                continue

            # A directory can contain the member directly or by one of its sub
            # directories, hence the member is evaluated for every parent location.
            segments = [
                segment for segment in path.split(self.PATH_SEPARATOR) if segment
            ]

            locations = [self.LOCATION_ROOT]
            location = ""
            for segment in segments[:-1]:
                location = f"{location:s}{self.PATH_SEPARATOR:s}{segment:s}"
                locations.append(location)

            for location in locations:
                directory_entry = self._GetDirectoryEntry(location, path)
                if directory_entry is None:
                    continue

                entries, processed_directories = directory_entries.setdefault(
                    location, ([], set())
                )

                path_spec_location, is_directory = directory_entry
                if is_directory:
                    if path_spec_location in processed_directories:
                        continue
                    processed_directories.add(path_spec_location)
                    # Restore / at end path to indicate a directory.
                    path_spec_location += self.PATH_SEPARATOR

                entries.append(path_spec_location)

        self._directory_entries = {
            location: entries for location, (entries, _) in directory_entries.items()
        }

    def _GetDirectoryEntry(self, location, path):
        """Determines the directory entry of a path for a directory location.

        Args:
          location (str): location of the directory.
          path (str): path of an archive member.

        Returns:
          tuple[str, bool]: location of the directory entry and True if the entry
              is a directory, or None if the path is not part of the directory.
        """
        # A ZIP archive file can contain paths with and without leading
        # separator.

        if path.startswith(location[1:]):
            zip_path = location[1:]
        elif path.startswith(location):
            zip_path = location
        else:
            return None

        # Ignore the directory itself.
        if path == zip_path:
            return None

        path_segment, suffix = self.GetPathSegmentAndSuffix(zip_path, path)
        if not path_segment:
            return None

        # Sometimes the ZIP file lacks directories, therefore we will provide
        # virtual ones.
        if suffix:
            return self.JoinPath([location, path_segment]), True

        return self.JoinPath([path]), path.endswith("/")

    def _Open(self, mode="rb"):
        """Opens the file system object defined by path specification.

        Args:
          mode (Optional[str]): file access mode. The default is 'rb' which represents
              read-only binary.

        Raises:
          AccessError: if the access to open the file was denied.
          BackEndError: if there was an error opening the ZIP file.
          OSError: if the file system object could not be opened.
          PathSpecError: if the path specification is incorrect.
          ValueError: if the path specification is invalid.
        """
        if not self._path_spec.HasParent():
            raise errors.PathSpecError("Unsupported path specification without parent.")

        file_object = resolver.Resolver.OpenFileObject(
            self._path_spec.parent, resolver_context=self._resolver_context
        )
        try:
            # pylint: disable=consider-using-with
            zip_file = zipfile.ZipFile(file_object, "r")
        except zipfile.BadZipFile as exception:
            raise errors.BackEndError(exception)

        self._file_object = file_object
        self._zip_file = zip_file

        self._BuildDirectoryEntries()

        self._directory_paths = set()
        for name in self._zip_file.namelist():
            if not name:
                continue

            if name[0] == "/":
                name = name[1:]

            if name[-1] == "/":
                directory_name = name[:-1]
            else:
                directory_name, _, _ = name.rpartition("/")

            if directory_name:
                path = ""
                for segment in directory_name.split("/"):
                    if path:
                        path = f"{path:s}/{segment:s}"
                    else:
                        path = f"/{segment:s}"

                    self._directory_paths.add(path)

    def FileEntryExistsByPathSpec(self, path_spec):
        """Determines if a file entry for a path specification exists.

        Args:
          path_spec (PathSpec): path specification of the file entry.

        Returns:
          bool: True if the file entry exists.
        """
        location = getattr(path_spec, "location", None)

        if location is None or not location.startswith(self.LOCATION_ROOT):
            return False

        if len(location) == 1:
            return True

        # A ZIP archive file can contain paths with and without leading separator.

        zip_info = None
        is_virtual = False

        try:
            zip_info = self._zip_file.getinfo(location[1:])
        except KeyError:
            pass

        if not zip_info:
            try:
                # Directories are stored with a trailing separator.
                zip_info = self._zip_file.getinfo(f"{location[1:]:s}/")
            except KeyError:
                pass

        if not zip_info:
            try:
                zip_info = self._zip_file.getinfo(location)
            except KeyError:
                pass

        if not zip_info:
            try:
                # Directories are stored with a trailing separator.
                zip_info = self._zip_file.getinfo(f"{location:s}/")
            except KeyError:
                pass

        if not zip_info:
            # Check if location could be a virtual directory.
            is_virtual = location in self._directory_paths

        return bool(zip_info or is_virtual)

    def GetFileEntryByPathSpec(self, path_spec):
        """Retrieves a file entry for a path specification.

        Args:
          path_spec (PathSpec): path specification of the file entry.

        Returns:
          ZipFileEntry: a file entry or None.
        """
        if not self.FileEntryExistsByPathSpec(path_spec):
            return None

        location = getattr(path_spec, "location", None)

        if len(location) == 1:
            return zip_file_entry.ZipFileEntry(
                self._resolver_context, self, path_spec, is_root=True, is_virtual=True
            )

        # A ZIP archive file can contain paths with and without leading separator.

        zip_info = None
        is_virtual = False

        try:
            zip_info = self._zip_file.getinfo(location[1:])
        except KeyError:
            pass

        if not zip_info:
            try:
                # Directories are stored with a trailing separator.
                zip_info = self._zip_file.getinfo(f"{location[1:]:s}/")
            except KeyError:
                pass

        if not zip_info:
            try:
                zip_info = self._zip_file.getinfo(location)
            except KeyError:
                pass

        if not zip_info:
            try:
                # Directories are stored with a trailing separator.
                zip_info = self._zip_file.getinfo(f"{location:s}/")
            except KeyError:
                pass

        if not zip_info:
            # Check if location could be a virtual directory.
            is_virtual = location in self._directory_paths

        if zip_info or is_virtual:
            kwargs = {}

            if zip_info:
                kwargs["zip_info"] = zip_info
            else:
                kwargs["is_virtual"] = True

            return zip_file_entry.ZipFileEntry(
                self._resolver_context, self, path_spec, **kwargs
            )

        return None

    def GetDirectoryEntryLocations(self, location):
        """Retrieves the locations of the entries of a directory.

        Args:
          location (str): location of the directory.

        Returns:
          list[str]: locations of the directory entries, in archive order.
              The locations of directories have a trailing path separator.
        """
        location = self.JoinPath([location])
        return self._directory_entries.get(location, [])

    def GetRootFileEntry(self):
        """Retrieves the root file entry.

        Returns:
          ZipFileEntry: a file entry or None.
        """
        path_spec = zip_path_spec.ZipPathSpec(
            location=self.LOCATION_ROOT, parent=self._path_spec.parent
        )
        return self.GetFileEntryByPathSpec(path_spec)

    def GetZipFile(self):
        """Retrieves the ZIP file object.

        Returns:
          zipfile.ZipFile: a ZIP file object or None.
        """
        return self._zip_file

    def GetZipInfoByPathSpec(self, path_spec):
        """Retrieves the ZIP info for a path specification.

        Args:
          path_spec (PathSpec): a path specification.

        Returns:
          zipfile.ZipInfo: a ZIP info object or None if not available.

        Raises:
          PathSpecError: if the path specification is incorrect.
        """
        location = getattr(path_spec, "location", None)
        if location is None:
            raise errors.PathSpecError("Path specification missing location.")

        if not location.startswith(self.LOCATION_ROOT):
            raise errors.PathSpecError("Invalid location in path specification.")

        if len(location) > 1:
            return self._zip_file.getinfo(location[1:])

        return None

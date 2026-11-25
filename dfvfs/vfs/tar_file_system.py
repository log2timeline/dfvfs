"""The TAR file system implementation."""

import os
import tarfile

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import tar_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import tar_file_entry


class TARFileSystem(file_system.FileSystem):
    """Class that implements a file system using tarfile.

    Attributes:
      encoding (str): file entry name encoding.
    """

    TYPE_INDICATOR = definitions.TYPE_INDICATOR_TAR

    def __init__(self, resolver_context, path_spec, encoding="utf-8"):
        """Initializes a file system.

        Args:
          resolver_context (Context): resolver context.
          path_spec (PathSpec): a path specification.
          encoding (Optional[str]): file entry name encoding.
        """
        super().__init__(resolver_context, path_spec)
        self._directory_entries = None
        self._directory_paths = None
        self._file_object = None
        self._tar_file = None
        self._tar_info_by_name = None
        self.encoding = encoding

    def _Close(self):
        """Closes the file system.

        Raises:
          OSError: if the close failed.
        """
        self._tar_file.close()
        self._tar_file = None
        self._directory_entries = None
        self._directory_paths = None
        self._file_object = None
        self._tar_info_by_name = None

    def _BuildIndexes(self):
        """Builds the TAR info and directory entry indexes.

        The indexes are built once when the file system is opened so that looking
        up a member or listing a directory does not need to scan all the members.
        """
        # The last occurrence of a member is assumed to be the most up-to-date
        # version, which is also what tarfile.TarFile.getmember does.
        self._tar_info_by_name = {}
        directory_entries = {}

        for tar_info in self._tar_file.getmembers():
            self._tar_info_by_name[tar_info.name] = tar_info

            path = tar_info.name
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
                directory_entry = self._GetDirectoryEntry(location, tar_info)
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

                entries.append(path_spec_location)

        self._directory_entries = {
            location: entries for location, (entries, _) in directory_entries.items()
        }

    def _GetDirectoryEntry(self, location, tar_info):
        """Determines the directory entry of a TAR info for a directory location.

        Args:
          location (str): location of the directory.
          tar_info (tarfile.TarInfo): TAR info.

        Returns:
          tuple[str, bool]: location of the directory entry and True if the entry
              is a directory, or None if the TAR info is not part of the directory.
        """
        path = tar_info.name

        # A tar file can contain paths with and without leading separator.

        if path.startswith(location[1:]):
            tar_path = location[1:]
        elif path.startswith(location):
            tar_path = location
        else:
            return None

        # Ignore the directory itself.
        if path == tar_path:
            return None

        path_segment, suffix = self.GetPathSegmentAndSuffix(tar_path, path)
        if not path_segment:
            return None

        # Sometimes the TAR file lacks directories, therefore we will
        # provide virtual ones.
        if suffix:
            return self.JoinPath([location, path_segment]), True

        return self.JoinPath([path]), tar_info.isdir()

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

        # Set the file offset to 0 because tarfile.open() does not.
        file_object.seek(0, os.SEEK_SET)

        # Explicitly tell tarfile not to use compression. Compression should be
        # handled by the file-like object.
        try:
            # pylint: disable=consider-using-with
            tar_file = tarfile.open(mode="r:", fileobj=file_object)
        except tarfile.ReadError as exception:
            raise OSError(exception)

        self._file_object = file_object
        self._tar_file = tar_file

        self._BuildIndexes()

        self._directory_paths = set()
        for name in self._tar_file.getnames():
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

    def _GetTARInfoByLocation(self, location):
        """Retrieves the TAR info for a location.

        Args:
          location (str): location, with a leading path separator.

        Returns:
          tarfile.TarInfo: TAR info or None if it does not exist.
        """
        # A tar file can contain paths with and without leading separator.
        # Directories are stored with a trailing separator, which is ignored by
        # the lookup.
        tar_info = self._tar_info_by_name.get(location[1:].rstrip("/"))
        if not tar_info:
            tar_info = self._tar_info_by_name.get(location.rstrip("/"))
        return tar_info

    def FileEntryExistsByPathSpec(self, path_spec):
        """Determines if a file entry for a path specification exists.

        Args:
          path_spec (PathSpec): path specification.

        Returns:
          bool: True if the file entry exists.
        """
        location = getattr(path_spec, "location", None)

        if location is None or not location.startswith(self.LOCATION_ROOT):
            return False

        if len(location) == 1:
            return True

        # A tar file can contain paths with and without leading separator.

        tar_info = self._GetTARInfoByLocation(location)
        is_virtual = False

        if not tar_info:
            # Check if location could be a virtual directory.
            is_virtual = location in self._directory_paths

        return bool(tar_info or is_virtual)

    def GetFileEntryByPathSpec(self, path_spec):
        """Retrieves a file entry for a path specification.

        Args:
          path_spec (PathSpec): path specification.

        Returns:
          TARFileEntry: file entry or None.
        """
        if not self.FileEntryExistsByPathSpec(path_spec):
            return None

        location = getattr(path_spec, "location", None)

        if len(location) == 1:
            return tar_file_entry.TARFileEntry(
                self._resolver_context, self, path_spec, is_root=True, is_virtual=True
            )

        # A tar file can contain paths with and without leading separator.

        tar_info = self._GetTARInfoByLocation(location)
        is_virtual = False

        if not tar_info:
            # Check if location could be a virtual directory.
            is_virtual = location in self._directory_paths

        if tar_info or is_virtual:
            kwargs = {}

            if tar_info:
                kwargs["tar_info"] = tar_info
            else:
                kwargs["is_virtual"] = True

            return tar_file_entry.TARFileEntry(
                self._resolver_context, self, path_spec, **kwargs
            )

        return None

    def GetDirectoryEntryLocations(self, location):
        """Retrieves the locations of the entries of a directory.

        Args:
          location (str): location of the directory.

        Returns:
          list[str]: locations of the directory entries, in archive order.
        """
        location = self.JoinPath([location])
        return self._directory_entries.get(location, [])

    def GetRootFileEntry(self):
        """Retrieves the root file entry.

        Returns:
          TARFileEntry: file entry.
        """
        path_spec = tar_path_spec.TARPathSpec(
            location=self.LOCATION_ROOT, parent=self._path_spec.parent
        )
        return self.GetFileEntryByPathSpec(path_spec)

    def GetTARFile(self):
        """Retrieves the TAR file.

        Returns:
          tarfile.TARFile: TAR file.
        """
        return self._tar_file

    def GetTARInfoByName(self, name):
        """Retrieves the TAR info for a name.

        Args:
          name (str): name of the archive member, a trailing path separator is
              ignored.

        Returns:
          tarfile.TarInfo: TAR info or None if it does not exist.
        """
        return self._tar_info_by_name.get(name.rstrip("/"))

    def GetTARInfoByPathSpec(self, path_spec):
        """Retrieves the TAR info for a path specification.

        Args:
          path_spec (PathSpec): a path specification.

        Returns:
          tarfile.TARInfo: TAR info or None if it does not exist.

        Raises:
          PathSpecError: if the path specification is incorrect.
        """
        location = getattr(path_spec, "location", None)
        if location is None:
            raise errors.PathSpecError("Path specification missing location.")

        if not location.startswith(self.LOCATION_ROOT):
            raise errors.PathSpecError("Invalid location in path specification.")

        if len(location) > 1:
            return self._tar_info_by_name.get(location[1:].rstrip("/"))

        return None

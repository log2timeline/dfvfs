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
        self._directory_paths = None
        self._file_object = None

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

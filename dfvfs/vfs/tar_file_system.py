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
        self._directory_paths = None
        self._file_object = None
        self._tar_file = None
        self.encoding = encoding

    def _Close(self):
        """Closes the file system.

        Raises:
          OSError: if the close failed.
        """
        self._tar_file.close()
        self._tar_file = None
        self._directory_paths = None
        self._file_object = None

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

        tar_info = None
        is_virtual = False

        try:
            tar_info = self._tar_file.getmember(location[1:])
        except KeyError:
            pass

        if not tar_info:
            try:
                # Directories are stored with a trailing separator.
                tar_info = self._tar_file.getmember(f"{location[1:]:s}/")
            except KeyError:
                pass

        if not tar_info:
            try:
                tar_info = self._tar_file.getmember(location)
            except KeyError:
                pass

        if not tar_info:
            try:
                # Directories are stored with a trailing separator.
                tar_info = self._tar_file.getmember(f"{location:s}/")
            except KeyError:
                pass

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

        tar_info = None
        is_virtual = False

        try:
            tar_info = self._tar_file.getmember(location[1:])
        except KeyError:
            pass

        if not tar_info:
            try:
                # Directories are stored with a trailing separator.
                tar_info = self._tar_file.getmember(f"{location[1:]:s}/")
            except KeyError:
                pass

        if not tar_info:
            try:
                tar_info = self._tar_file.getmember(location)
            except KeyError:
                pass

        if not tar_info:
            try:
                # Directories are stored with a trailing separator.
                tar_info = self._tar_file.getmember(f"{location:s}/")
            except KeyError:
                pass

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

        tar_file = None
        if len(location) > 1:
            try:
                tar_file = self._tar_file.getmember(location[1:])
            except KeyError:
                pass

        return tar_file

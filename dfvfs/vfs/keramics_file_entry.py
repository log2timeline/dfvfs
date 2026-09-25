# -*- coding: utf-8 -*-
"""The Keramics file entry implementation."""

from dfdatetime import definitions as dfdatetime_definitions
from dfdatetime import fat_date_time as dfdatetime_fat_date_time
from dfdatetime import filetime as dfdatetime_filetime
from dfdatetime import posix_time as dfdatetime_posix_time

from pykeramics import datetime as pykeramics_datetime
from pykeramics import vfs as pykeramics_vfs

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import keramics_path_spec
from dfvfs.vfs import attribute
from dfvfs.vfs import file_entry
from dfvfs.vfs import keramics_attribute
from dfvfs.vfs import keramics_directory


class KeramicsFileEntry(file_entry.FileEntry):
    """File system file entry that uses pykeramics."""

    TYPE_INDICATOR = definitions.TYPE_INDICATOR_KERAMICS

    # Mappings of Keramics file types to dfVFS file entry types.
    _ENTRY_TYPES = {
        pykeramics_vfs.VfsFileType.NAMED_PIPE: definitions.FILE_ENTRY_TYPE_PIPE,
        pykeramics_vfs.VfsFileType.CHARACTER_DEVICE: (
            definitions.FILE_ENTRY_TYPE_CHARACTER_DEVICE
        ),
        pykeramics_vfs.VfsFileType.DEVICE: definitions.FILE_ENTRY_TYPE_DEVICE,
        pykeramics_vfs.VfsFileType.DIRECTORY: (definitions.FILE_ENTRY_TYPE_DIRECTORY),
        pykeramics_vfs.VfsFileType.BLOCK_DEVICE: (
            definitions.FILE_ENTRY_TYPE_BLOCK_DEVICE
        ),
        pykeramics_vfs.VfsFileType.FILE: definitions.FILE_ENTRY_TYPE_FILE,
        pykeramics_vfs.VfsFileType.SYMBOLIC_LINK: (definitions.FILE_ENTRY_TYPE_LINK),
        pykeramics_vfs.VfsFileType.SOCKET: definitions.FILE_ENTRY_TYPE_SOCKET,
        pykeramics_vfs.VfsFileType.WHITEOUT: definitions.FILE_ENTRY_TYPE_WHITEOUT,
    }

    def __init__(
        self,
        resolver_context,
        file_system,
        path_spec,
        is_root=False,
        is_virtual=False,
        pykeramics_file_entry=None,
    ):
        """Initializes a file entry.

        Args:
          resolver_context (Context): resolver context.
          file_system (FileSystem): file system.
          path_spec (PathSpec): path specification.
          is_root (Optional[bool]): True if the file entry is the root file entry
              of the corresponding file system.
          is_virtual (Optional[bool]): True if the file entry is a virtual file
              entry emulated by the corresponding file system.
          pykeramics_file_entry (Optional[pykeramics.VfsFileEntry]): pykeramics file
              entry.

        Raises:
          BackEndError: if the pykeramics file entry is missing.
        """
        if not pykeramics_file_entry:
            raise errors.BackEndError("Missing Keramics file entry.")

        if is_root or pykeramics_file_entry.name is None:
            file_entry_name = ""
        else:
            file_entry_name = pykeramics_file_entry.name.to_string()

        super().__init__(
            resolver_context,
            file_system,
            path_spec,
            is_root=is_root,
            is_virtual=is_virtual,
        )
        self._keramics_file_entry = pykeramics_file_entry

        self.entry_type = self._ENTRY_TYPES.get(pykeramics_file_entry.file_type, None)
        self._name = file_entry_name

    def _GetAttributes(self):
        """Retrieves the attributes.

        Returns:
          list[Attribute]: attributes.

        Raises:
          BackEndError: if the extended attributes cannot be retrieved.
        """
        if self._attributes is None:
            self._attributes = []

            try:
                number_of_extended_attributes = (
                    self._keramics_file_entry.get_number_of_extended_attributes()
                )
            except RuntimeError as exception:
                raise errors.BackEndError(exception)

            for extended_attribute_index in range(number_of_extended_attributes):
                try:
                    pykeramics_extended_attribute = (
                        self._keramics_file_entry.get_extended_attribute_by_index(
                            extended_attribute_index
                        )
                    )
                except RuntimeError as exception:
                    raise errors.BackEndError(exception)

                extended_attribute = keramics_attribute.KeramicsExtendedAttribute(
                    pykeramics_extended_attribute
                )
                self._attributes.append(extended_attribute)

        return self._attributes

    def _GetDateTimeValue(self, pykeramics_datetime_value):
        """Retrieves a date time value.

        Args:
          pykeramics_datetime_value (pykeramics.datetime.DateTime): a pykeramics
              date time value.

        Returns:
          dfdatetime.DateTimeValues: date time value or None if not available.

        Raises:
          BackEndError: if the Keramics date time values is not supported.
        """
        if pykeramics_datetime_value is None:
            return None

        if isinstance(pykeramics_datetime_value, pykeramics_datetime.FatDate):
            return dfdatetime_fat_date_time.FATTimestamp(
                precision=dfdatetime_definitions.PRECISION_1_DAY,
                timestamp=pykeramics_datetime_value.timestamp,
            )

        if isinstance(pykeramics_datetime_value, pykeramics_datetime.FatTimeDate):
            return dfdatetime_fat_date_time.FATTimestamp(
                precision=dfdatetime_definitions.PRECISION_2_SECONDS,
                timestamp=pykeramics_datetime_value.timestamp,
            )

        if isinstance(pykeramics_datetime_value, pykeramics_datetime.FatTimeDate10Ms):
            return dfdatetime_fat_date_time.FATTimestamp(
                precision=dfdatetime_definitions.PRECISION_10_MILLISECONDS,
                timestamp=pykeramics_datetime_value.timestamp,
            )

        if isinstance(pykeramics_datetime_value, pykeramics_datetime.Filetime):
            return dfdatetime_filetime.Filetime(
                timestamp=pykeramics_datetime_value.timestamp
            )

        if isinstance(pykeramics_datetime_value, pykeramics_datetime.PosixTime32):
            return dfdatetime_posix_time.PosixTime(
                timestamp=pykeramics_datetime_value.timestamp
            )

        if isinstance(pykeramics_datetime_value, pykeramics_datetime.PosixTime64Ns):
            return dfdatetime_posix_time.PosixTimeInNanoseconds(
                timestamp=pykeramics_datetime_value.timestamp
            )

        raise errors.BackEndError("Unsupported Keramics date time value.")

    def _GetDirectory(self):
        """Retrieves a directory.

        Returns:
          KeramicsDirectory: directory or None if not available.
        """
        if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
            return None

        return keramics_directory.KeramicsDirectory(
            self._file_system, self.path_spec, self._keramics_file_entry
        )

    def _GetStatAttribute(self):
        """Retrieves a stat attribute.

        Returns:
          StatAttribute: a stat attribute or None if not available.
        """
        stat_attribute = attribute.StatAttribute()

        device_identifier = self._keramics_file_entry.device_identifier
        if device_identifier is None:
            device_number = None
        else:
            device_number = ((device_identifier >> 8) & 0xFF, device_identifier & 0xFF)

        stat_attribute.device_number = device_number
        stat_attribute.group_identifier = self._keramics_file_entry.group_identifier
        stat_attribute.inode_number = self._keramics_file_entry.inode_number
        stat_attribute.mode = self._keramics_file_entry.file_mode
        stat_attribute.number_of_links = self._keramics_file_entry.number_of_links
        stat_attribute.owner_identifier = self._keramics_file_entry.owner_identifier
        stat_attribute.size = self._keramics_file_entry.size
        stat_attribute.type = self.entry_type

        return stat_attribute

    def _GetSubFileEntries(self):
        """Retrieves a sub file entries generator.

        Yields:
          KeramicsFileEntry: a sub file entry.

        Raises:
          BackEndError: if a sub file entry is missing.
        """
        if self._directory is None:
            self._directory = self._GetDirectory()

        if self._directory:
            for path_spec in self._directory.entries:
                pykeramics_file_entry = (
                    self._file_system.GetKeramicsFileEntryByPathSpec(path_spec)
                )
                if not pykeramics_file_entry:
                    raise errors.BackEndError("Missing sub file entry.")

                yield KeramicsFileEntry(
                    self._resolver_context,
                    self,
                    path_spec,
                    pykeramics_file_entry=pykeramics_file_entry,
                )

    @property
    def access_time(self):
        """dfdatetime.DateTimeValues: access time or None if not available."""
        return self._GetDateTimeValue(self._keramics_file_entry.access_time)

    @property
    def change_time(self):
        """dfdatetime.DateTimeValues: change time or None if not available."""
        return self._GetDateTimeValue(self._keramics_file_entry.change_time)

    @property
    def creation_time(self):
        """dfdatetime.DateTimeValues: creation time or None if not available."""
        return self._GetDateTimeValue(self._keramics_file_entry.creation_time)

    @property
    def deletion_time(self):
        """dfdatetime.DateTimeValues: deletion time or None if not available."""
        return self._GetDateTimeValue(self._keramics_file_entry.deletion_time)

    @property
    def name(self):
        """str: name of the file entry, which does not include the full path."""
        return self._name

    @property
    def modification_time(self):
        """dfdatetime.DateTimeValues: modification time or None if not available."""
        return self._GetDateTimeValue(self._keramics_file_entry.modification_time)

    @property
    def size(self):
        """int: size of the file entry in bytes or None if not available."""
        return self._keramics_file_entry.size

    def GetExtents(self):
        """Retrieves the extents.

        Returns:
          list[Extent]: the extents.
        """
        if self.entry_type != definitions.FILE_ENTRY_TYPE_FILE:
            return []

        # TODO: add support for extents
        return []

    def GetKeramicsDataStream(self, name=None):
        """Retrieves the Keramics data stream.

        Args:
          name (Optional[str]): name of the data stream.

        Returns:
          pykeramics.VfsDataStream: pykeramics data stream or None if not available.
        """
        if name:
            raise errors.NotSupported(f"Named data stream: {name:s} not yet supported.")

        return self._keramics_file_entry.get_data_stream()

    def GetLinkedFileEntry(self):
        """Retrieves the linked file entry, e.g. for a symbolic link.

        Returns:
          KeramicsFileEntry: linked file entry or None if not available.
        """
        link_target = self._keramics_file_entry.symbolic_link_target

        if link_target is None:
            return None

        pykeramics_location = getattr(self.path_spec, "location", None)

        if link_target.is_relative():
            parent_path = pykeramics_location.path.new_with_parent_directory()
            link_path = parent_path.new_with_join(link_target)
            link_location = pykeramics_location.new_with_parent(link_path)
        else:
            link_location = pykeramics_location.new_with_parent(link_target)

        path_spec = keramics_path_spec.KeramicsPathSpec(location=link_location)

        pykeramics_file_entry = self._file_system.GetKeramicsFileEntryByPathSpec(
            path_spec
        )
        if not pykeramics_file_entry:
            return None

        is_root = link_target.is_root()

        return KeramicsFileEntry(
            self._resolver_context,
            self,
            path_spec,
            is_root=is_root,
            pykeramics_file_entry=pykeramics_file_entry,
        )

    def GetParentFileEntry(self):
        """Retrieves the parent file entry.

        Returns:
          KeramicsFileEntry: parent file entry or None if not available.
        """
        pykeramics_location = getattr(self.path_spec, "location", None)

        parent_path = pykeramics_location.path.new_with_parent_directory()
        parent_location = pykeramics_location.new_with_parent(parent_path)

        path_spec = keramics_path_spec.KeramicsPathSpec(location=parent_location)

        pykeramics_file_entry = self._file_system.GetKeramicsFileEntryByPathSpec(
            path_spec
        )
        if not pykeramics_file_entry:
            return None

        is_root = parent_path.is_root()

        return KeramicsFileEntry(
            self._resolver_context,
            self,
            path_spec,
            is_root=is_root,
            pykeramics_file_entry=pykeramics_file_entry,
        )

"""The SleuthKit (TSK) attribute implementation."""

import os

from dfdatetime import filetime as dfdatetime_filetime

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import fabric as dtfabric_fabric

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.vfs import attribute


class TSKAttribute(attribute.Attribute):
    """File system attribute that uses pytsk3."""

    def __init__(self, tsk_file, tsk_attribute):
        """Initializes an attribute.

        Args:
          tsk_file (pytsk3.File): TSK file.
          tsk_attribute (pytsk3.Attribute): TSK attribute.

        Raises:
          BackEndError: if the TSK file or attribute is missing.
        """
        if not tsk_file:
            raise errors.BackEndError("Missing TSK file.")

        if not tsk_attribute:
            raise errors.BackEndError("Missing TSK attribute.")

        super().__init__()
        self._attribute_type = getattr(tsk_attribute.info, "type", None)
        self._tsk_attribute = tsk_attribute
        self._tsk_file = tsk_file

    @property
    def attribute_type(self):
        """object: attribute type."""
        return self._attribute_type


class TSKExtendedAttribute(TSKAttribute):
    """File system extended attribute that uses pytsk3."""

    def __init__(self, tsk_file, tsk_attribute):
        """Initializes an attribute.

        Args:
          tsk_file (pytsk3.File): TSK file.
          tsk_attribute (pytsk3.Attribute): TSK attribute.
        """
        super().__init__(tsk_file, tsk_attribute)
        self._current_offset = 0
        self._identifier = getattr(tsk_attribute.info, "id", None)
        self._size = getattr(tsk_attribute.info, "size", None)

    @property
    def name(self):
        """str: name.

        Raises:
          BackEndError: if pytsk3 returns a non UTF-8 formatted name.
        """
        name = getattr(self._tsk_attribute.info, "name", None)
        if name:
            try:
                # pytsk3 returns an UTF-8 encoded byte string.
                return name.decode("utf8")
            except UnicodeError:
                raise errors.BackEndError("pytsk3 returned a non UTF-8 formatted name.")

        return name

    # Note: that the following functions do not follow the style guide
    # because they are part of the file-like object interface.
    # pylint: disable=invalid-name

    def read(self, size=None):
        """Reads a byte string from the file input/output (IO) object.

        The function will read a byte string of the specified size or
        all of the remaining data if no size was specified.

        Args:
          size (Optional[int]): number of bytes to read, where None is all
              remaining data.

        Returns:
          bytes: data read.

        Raises:
          OSError: if the read failed.
        """
        if size is None:
            size = self._size

        data = self._tsk_file.read_random(
            self._current_offset, size, self._attribute_type, self._identifier
        )
        self._current_offset += len(data)
        return data

    def seek(self, offset, whence=os.SEEK_SET):
        """Seeks to an offset within the file input/output (IO) object.

        Args:
          offset (int): offset to seek.
          whence (Optional[int]): value that indicates whether offset is an
              absolute or relative position within the file.

        Raises:
          OSError: if the seek failed.
        """
        if whence == os.SEEK_CUR:
            offset += self._current_offset
        elif whence == os.SEEK_END:
            offset = self._size - offset
        elif whence != os.SEEK_SET:
            raise OSError("Invalid whence")

        if offset < 0:
            raise OSError("Invalid offset")

        self._current_offset = offset

    # get_offset() is preferred above tell() by the libbfio layer used in libyal.
    def get_offset(self):
        """Retrieves the current offset into the file input/output (IO) object.

        Returns:
          int: current offset into the file input/output (IO) object.
        """
        return self._current_offset

    # Pythonesque alias for get_offset().
    def tell(self):
        """Retrieves the current offset into the file input/output (IO) object."""
        return self.get_offset()

    def get_size(self):
        """Retrieves the size of the file input/output (IO) object.

        Returns:
          int: size of the file input/output (IO) object.
        """
        return self._size

    def seekable(self):
        """Determines if a file input/output (IO) object is seekable.

        Returns:
          bool: True since a file IO object provides a seek method.
        """
        return True


class TSKNTFSAttribute(TSKAttribute):
    """NTFS file system attribute that uses pytsk3."""

    _DATA_TYPE_FABRIC_DEFINITION_FILE = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "lib", "ntfs.yaml"
    )

    with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, "rb") as file_object:
        _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

    _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
        yaml_definition=_DATA_TYPE_FABRIC_DEFINITION
    )

    def __init__(self, tsk_file, tsk_attribute):
        """Initializes an attribute.

        Args:
          tsk_file (pytsk3.File): TSK file.
          tsk_attribute (pytsk3.Attribute): TSK attribute.

        Raises:
          BackEndError: if the TSK file or attribute is missing or the attribute
              data cannot be read.
        """
        super().__init__(tsk_file, tsk_attribute)
        self._values = self._ReadValues()

    def _GetDataTypeMap(self, data_size):
        """Retrieves the data type map of the attribute data.

        Args:
          data_size (int): size of the attribute data.

        Returns:
          dtfabric.DataTypeMap: data type map.
        """
        raise NotImplementedError

    def _ReadValues(self):
        """Reads the attribute values.

        Returns:
          object: attribute values.

        Raises:
          BackEndError: if the attribute data cannot be read.
        """
        identifier = getattr(self._tsk_attribute.info, "id", None)
        size = getattr(self._tsk_attribute.info, "size", None) or 0

        try:
            data = self._tsk_file.read_random(0, size, self._attribute_type, identifier)
        except OSError as exception:
            raise errors.BackEndError(
                f"Unable to read attribute data with error: {exception!s}"
            )

        data_type_map = self._GetDataTypeMap(len(data))

        try:
            return data_type_map.MapByteStream(data)
        except (
            dtfabric_errors.ByteStreamTooSmallError,
            dtfabric_errors.MappingError,
        ) as exception:
            raise errors.BackEndError(
                f"Unable to map attribute data with error: {exception!s}"
            )


class TSKFileNameNTFSAttribute(TSKNTFSAttribute):
    """NTFS $FILE_NAME file system attribute that uses pytsk3."""

    TYPE_INDICATOR = definitions.ATTRIBUTE_TYPE_NTFS_FILE_NAME

    _FILE_NAME = TSKNTFSAttribute._DATA_TYPE_FABRIC.CreateDataTypeMap("ntfs_file_name")

    def _GetDataTypeMap(self, data_size):
        """Retrieves the data type map of the attribute data.

        Args:
          data_size (int): size of the attribute data.

        Returns:
          dtfabric.DataTypeMap: data type map.
        """
        return self._FILE_NAME

    @property
    def access_time(self):
        """dfdatetime.Filetime: access time or None if not set."""
        return dfdatetime_filetime.Filetime(timestamp=self._values.access_time)

    @property
    def creation_time(self):
        """dfdatetime.Filetime: creation time or None if not set."""
        return dfdatetime_filetime.Filetime(timestamp=self._values.creation_time)

    @property
    def entry_modification_time(self):
        """dfdatetime.Filetime: entry modification time or None if not set."""
        return dfdatetime_filetime.Filetime(
            timestamp=self._values.entry_modification_time
        )

    @property
    def file_attribute_flags(self):
        """int: file attribute flags or None if not available."""
        return self._values.file_attribute_flags

    @property
    def modification_time(self):
        """dfdatetime.Filetime: modification time."""
        return dfdatetime_filetime.Filetime(timestamp=self._values.modification_time)

    @property
    def name(self):
        """str: name."""
        return self._values.name

    @property
    def name_space(self):
        """int: name_space."""
        return self._values.name_space

    @property
    def parent_file_reference(self):
        """int: parent file reference."""
        return self._values.parent_file_reference


class TSKStandardInformationNTFSAttribute(TSKNTFSAttribute):
    """NTFS $STANDARD_INFORMATION file system attribute that uses pytsk3."""

    TYPE_INDICATOR = definitions.ATTRIBUTE_TYPE_NTFS_STANDARD_INFORMATION

    _STANDARD_INFORMATION_V1 = TSKNTFSAttribute._DATA_TYPE_FABRIC.CreateDataTypeMap(
        "ntfs_standard_information_v1"
    )

    _STANDARD_INFORMATION_V3 = TSKNTFSAttribute._DATA_TYPE_FABRIC.CreateDataTypeMap(
        "ntfs_standard_information_v3"
    )

    _STANDARD_INFORMATION_V3_SIZE = _STANDARD_INFORMATION_V3.GetSizeHint()

    def _GetDataTypeMap(self, data_size):
        """Retrieves the data type map of the attribute data.

        Args:
          data_size (int): size of the attribute data.

        Returns:
          dtfabric.DataTypeMap: data type map.
        """
        if data_size >= self._STANDARD_INFORMATION_V3_SIZE:
            return self._STANDARD_INFORMATION_V3

        return self._STANDARD_INFORMATION_V1

    @property
    def access_time(self):
        """dfdatetime.Filetime: access time or None if not set."""
        return dfdatetime_filetime.Filetime(timestamp=self._values.access_time)

    @property
    def creation_time(self):
        """dfdatetime.Filetime: creation time or None if not set."""
        return dfdatetime_filetime.Filetime(timestamp=self._values.creation_time)

    @property
    def entry_modification_time(self):
        """dfdatetime.Filetime: entry modification time or None if not set."""
        return dfdatetime_filetime.Filetime(
            timestamp=self._values.entry_modification_time
        )

    @property
    def file_attribute_flags(self):
        """int: file attribute flags or None if not available."""
        return self._values.file_attribute_flags

    @property
    def modification_time(self):
        """dfdatetime.Filetime: modification time or None if not set."""
        return dfdatetime_filetime.Filetime(timestamp=self._values.modification_time)

    @property
    def owner_identifier(self):
        """int: owner identifier or None if not available."""
        return getattr(self._values, "owner_identifier", None)

    @property
    def security_descriptor_identifier(self):
        """int: security descriptor identifier or None if not available."""
        return getattr(self._values, "security_descriptor_identifier", None)

    @property
    def update_sequence_number(self):
        """int: update sequence number or None if not available."""
        return getattr(self._values, "update_sequence_number", None)

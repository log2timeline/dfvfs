# -*- coding: utf-8 -*-
"""Copy in and out (CPIO) archive file."""

import os

from dtfabric.runtime import fabric as dtfabric_fabric

from dfvfs.lib import data_format
from dfvfs.lib import errors


class CPIOArchiveFileEntry(object):
  """CPIO archive file entry.

  Attributes:
    data_offset (int): data start offset.
    data_size (int): data size.
    group_identifier (int): group identifier (gid).
    inode_number (int): inode number.
    mode (int): mode.
    modification_time (int): modification POSIX timestamp.
    number_of_links (int): number of hard links.
    path (str): path.
    size (int): archive file entry record size.
    user_identifier (int): user identifier (uid).
  """

  def __init__(self):
    """Initializes a CPIO archive file entry."""
    super(CPIOArchiveFileEntry, self).__init__()
    self.data_offset = None
    self.data_size = None
    self.group_identifier = None
    self.inode_number = None
    self.mode = None
    self.modification_time = None
    self.number_of_links = None
    self.path = None
    self.size = None
    self.user_identifier = None


class CPIOArchiveFile(data_format.DataFormat):
  """CPIO archive file.

  Attributes:
    file_format (str): CPIO file format.
  """
  _DATA_TYPE_FABRIC_DEFINITION_FILE = os.path.join(
      os.path.dirname(__file__), 'cpio.yaml')

  with open(_DATA_TYPE_FABRIC_DEFINITION_FILE, 'rb') as file_object:
    _DATA_TYPE_FABRIC_DEFINITION = file_object.read()

  _DATA_TYPE_FABRIC = dtfabric_fabric.DataTypeFabric(
      yaml_definition=_DATA_TYPE_FABRIC_DEFINITION)

  _CPIO_BINARY_BIG_ENDIAN_FILE_ENTRY = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'cpio_binary_big_endian_file_entry')

  _CPIO_BINARY_LITTLE_ENDIAN_FILE_ENTRY = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'cpio_binary_little_endian_file_entry')

  _CPIO_PORTABLE_ASCII_FILE_ENTRY = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'cpio_portable_ascii_file_entry')

  _CPIO_NEW_ASCII_FILE_ENTRY = _DATA_TYPE_FABRIC.CreateDataTypeMap(
      'cpio_new_ascii_file_entry')

  _CPIO_SIGNATURE_BINARY_BIG_ENDIAN = b'\x71\xc7'
  _CPIO_SIGNATURE_BINARY_LITTLE_ENDIAN = b'\xc7\x71'
  _CPIO_SIGNATURE_PORTABLE_ASCII = b'070707'
  _CPIO_SIGNATURE_NEW_ASCII = b'070701'
  _CPIO_SIGNATURE_NEW_ASCII_WITH_CHECKSUM = b'070702'

  _CPIO_ATTRIBUTE_NAMES_ODC = (
      'device_number', 'inode_number', 'mode', 'user_identifier',
      'group_identifier', 'number_of_links', 'special_device_number',
      'modification_time', 'path_size', 'file_size')

  _CPIO_ATTRIBUTE_NAMES_CRC = (
      'inode_number', 'mode', 'user_identifier', 'group_identifier',
      'number_of_links', 'modification_time', 'path_size',
      'file_size', 'device_major_number', 'device_minor_number',
      'special_device_major_number', 'special_device_minor_number',
      'checksum')

  def __init__(self, encoding='utf-8'):
    """Initializes a CPIO archive file.

    Args:
      encoding (str): encoding of paths within the archive file.
    """
    super(CPIOArchiveFile, self).__init__()
    self._encoding = encoding
    self._file_entries = None
    self._file_object = None
    self._file_size = 0

    self.file_format = None

  @property
  def encoding(self):
    """str: encoding of paths within the archive file."""
    return self._encoding

  def _ReadFileEntry(self, file_object, file_offset):
    """Reads a file entry.

    Args:
      file_object (FileIO): file-like object.
      file_offset (int): offset of the data relative from the start of
          the file-like object.

    Returns:
      CPIOArchiveFileEntry: a file entry.

    Raises:
      FileFormatError: if the file entry cannot be read.
    """
    if self.file_format == 'bin-big-endian':
      data_type_map = self._CPIO_BINARY_BIG_ENDIAN_FILE_ENTRY
    elif self.file_format == 'bin-little-endian':
      data_type_map = self._CPIO_BINARY_LITTLE_ENDIAN_FILE_ENTRY
    elif self.file_format == 'odc':
      data_type_map = self._CPIO_PORTABLE_ASCII_FILE_ENTRY
    elif self.file_format in ('crc', 'newc'):
      data_type_map = self._CPIO_NEW_ASCII_FILE_ENTRY

    file_entry, file_entry_data_size = self._ReadStructureFromFileObject(
        file_object, file_offset, data_type_map)

    file_offset += file_entry_data_size

    if self.file_format in ('bin-big-endian', 'bin-little-endian'):
      file_entry.modification_time = (
          (file_entry.modification_time.upper << 16) |
          file_entry.modification_time.lower)

      file_entry.file_size = (
          (file_entry.file_size.upper << 16) | file_entry.file_size.lower)

    if self.file_format == 'odc':
      for attribute_name in self._CPIO_ATTRIBUTE_NAMES_ODC:
        value = getattr(file_entry, attribute_name, None)
        try:
          value = int(value, 8)
        except ValueError:
          raise errors.FileFormatError((
              f'Unable to convert attribute: {attribute_name:s} into '
              f'an integer'))

        value = setattr(file_entry, attribute_name, value)

    elif self.file_format in ('crc', 'newc'):
      for attribute_name in self._CPIO_ATTRIBUTE_NAMES_CRC:
        value = getattr(file_entry, attribute_name, None)
        try:
          value = int(value, 16)
        except ValueError:
          raise errors.FileFormatError((
              f'Unable to convert attribute: {attribute_name:s} into '
              f'an integer'))

        value = setattr(file_entry, attribute_name, value)

    path_data = file_object.read(file_entry.path_size)

    file_offset += file_entry.path_size

    path = path_data.decode(self._encoding)
    path, _, _ = path.partition('\x00')

    if self.file_format in ('bin-big-endian', 'bin-little-endian'):
      padding_size = file_offset % 2
      if padding_size > 0:
        padding_size = 2 - padding_size

    elif self.file_format == 'odc':
      padding_size = 0

    elif self.file_format in ('crc', 'newc'):
      padding_size = file_offset % 4
      if padding_size > 0:
        padding_size = 4 - padding_size

    file_offset += padding_size

    archive_file_entry = CPIOArchiveFileEntry()

    archive_file_entry.data_offset = file_offset
    archive_file_entry.data_size = file_entry.file_size
    archive_file_entry.group_identifier = file_entry.group_identifier
    archive_file_entry.inode_number = file_entry.inode_number
    archive_file_entry.modification_time = file_entry.modification_time
    archive_file_entry.number_of_links = file_entry.number_of_links
    archive_file_entry.path = path
    archive_file_entry.mode = file_entry.mode
    archive_file_entry.size = (
        file_entry_data_size + file_entry.path_size + padding_size +
        file_entry.file_size)
    archive_file_entry.user_identifier = file_entry.user_identifier

    file_offset += file_entry.file_size

    if self.file_format in ('bin-big-endian', 'bin-little-endian'):
      padding_size = file_offset % 2
      if padding_size > 0:
        padding_size = 2 - padding_size

    elif self.file_format == 'odc':
      padding_size = 0

    elif self.file_format in ('crc', 'newc'):
      padding_size = file_offset % 4
      if padding_size > 0:
        padding_size = 4 - padding_size

    if padding_size > 0:
      archive_file_entry.size += padding_size

    return archive_file_entry

  def _ReadFileEntries(self, file_object):
    """Reads the file entries from the cpio archive.

    Args:
      file_object (FileIO): file-like object.
    """
    self._file_entries = {}

    file_offset = 0
    while file_offset < self._file_size or self._file_size == 0:
      file_entry = self._ReadFileEntry(file_object, file_offset)
      file_offset += file_entry.size
      if file_entry.path == 'TRAILER!!!':
        break

      if file_entry.path in self._file_entries:
        # TODO: alert on file entries with duplicate paths?
        continue

      self._file_entries[file_entry.path] = file_entry

  def Close(self):
    """Closes the CPIO archive file."""
    self._file_entries = None
    self._file_object = None
    self._file_size = None

  def FileEntryExistsByPath(self, path):
    """Determines if file entry for a specific path exists.

    Returns:
      bool: True if the file entry exists.
    """
    if self._file_entries is None:
      return False

    return path in self._file_entries

  def GetFileEntries(self, path_prefix=''):
    """Retrieves the file entries.

    Args:
      path_prefix (str): path prefix.

    Yields:
      CPIOArchiveFileEntry: a CPIO archive file entry.
    """
    if self._file_entries:
      for path, file_entry in self._file_entries.items():
        if path.startswith(path_prefix):
          yield file_entry

  def GetFileEntryByPath(self, path):
    """Retrieves a file entry for a specific path.

    Returns:
      CPIOArchiveFileEntry: a CPIO archive file entry or None if not available.
    """
    if not self._file_entries:
      return None
    return self._file_entries.get(path, None)

  def Open(self, file_object):
    """Opens the CPIO archive file.

    Args:
      file_object (FileIO): a file-like object.

    Raises:
      IOError: if the file format signature is not supported.
      OSError: if the file format signature is not supported.
    """
    file_object.seek(0, os.SEEK_SET)
    signature_data = file_object.read(6)

    self.file_format = None
    if len(signature_data) > 2:
      if signature_data[:2] == self._CPIO_SIGNATURE_BINARY_BIG_ENDIAN:
        self.file_format = 'bin-big-endian'
      elif signature_data[:2] == self._CPIO_SIGNATURE_BINARY_LITTLE_ENDIAN:
        self.file_format = 'bin-little-endian'
      elif signature_data == self._CPIO_SIGNATURE_PORTABLE_ASCII:
        self.file_format = 'odc'
      elif signature_data == self._CPIO_SIGNATURE_NEW_ASCII:
        self.file_format = 'newc'
      elif signature_data == self._CPIO_SIGNATURE_NEW_ASCII_WITH_CHECKSUM:
        self.file_format = 'crc'

    if self.file_format is None:
      raise IOError('Unsupported CPIO format.')

    self._file_object = file_object
    self._file_size = file_object.get_size()

    self._ReadFileEntries(self._file_object)

  def ReadDataAtOffset(self, file_offset, size):
    """Reads a byte string from the file-like object at a specific offset.

    Args:
      file_offset (int): file offset.
      size (int): number of bytes to read.

    Returns:
      bytes: data read.

    Raises:
      IOError: if the read failed.
      OSError: if the read failed.
    """
    self._file_object.seek(file_offset, os.SEEK_SET)
    return self._file_object.read(size)

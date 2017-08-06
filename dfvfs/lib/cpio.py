# -*- coding: utf-8 -*-
"""Helper functions for Copy in and out (CPIO) archive file support."""

from __future__ import unicode_literals

import os

import construct


class CPIOArchiveFileEntry(object):
  """CPIO archive file entry.

  Attributes:
    data_offset (int): data start offset.
    data_size (int): data size.
    group_identifier (int): group identifier (gid).
    inode_number (int): inode number.
    mode (int): mode.
    modification_time (int): modification POSIX timestamp.
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
    self.path = None
    self.size = None
    self.user_identifier = None


class CPIOArchiveFile(object):
  """CPIO archive file.

  Attributes:
    file_format (str): CPIO file format.
  """
  # pylint: disable=no-member

  _CPIO_SIGNATURE_BINARY_BIG_ENDIAN = b'\x71\xc7'
  _CPIO_SIGNATURE_BINARY_LITTLE_ENDIAN = b'\xc7\x71'
  _CPIO_SIGNATURE_PORTABLE_ASCII = b'070707'
  _CPIO_SIGNATURE_NEW_ASCII = b'070701'
  _CPIO_SIGNATURE_NEW_ASCII_WITH_CHECKSUM = b'070702'

  _CPIO_BINARY_BIG_ENDIAN_FILE_ENTRY_STRUCT = construct.Struct(
      'cpio_binary_big_endian_file_entry',
      construct.UBInt16('signature'),
      construct.UBInt16('device_number'),
      construct.UBInt16('inode_number'),
      construct.UBInt16('mode'),
      construct.UBInt16('user_identifier'),
      construct.UBInt16('group_identifier'),
      construct.UBInt16('number_of_links'),
      construct.UBInt16('special_device_number'),
      construct.UBInt16('modification_time_upper'),
      construct.UBInt16('modification_time_lower'),
      construct.UBInt16('path_string_size'),
      construct.UBInt16('file_size_upper'),
      construct.UBInt16('file_size_lower'))

  _CPIO_BINARY_LITTLE_ENDIAN_FILE_ENTRY_STRUCT = construct.Struct(
      'cpio_binary_little_endian_file_entry',
      construct.ULInt16('signature'),
      construct.ULInt16('device_number'),
      construct.ULInt16('inode_number'),
      construct.ULInt16('mode'),
      construct.ULInt16('user_identifier'),
      construct.ULInt16('group_identifier'),
      construct.ULInt16('number_of_links'),
      construct.ULInt16('special_device_number'),
      construct.ULInt16('modification_time_upper'),
      construct.ULInt16('modification_time_lower'),
      construct.ULInt16('path_string_size'),
      construct.ULInt16('file_size_upper'),
      construct.ULInt16('file_size_lower'))

  _CPIO_PORTABLE_ASCII_FILE_ENTRY_STRUCT = construct.Struct(
      'cpio_portable_ascii_file_entry',
      construct.Bytes('signature', 6),
      construct.Bytes('device_number', 6),
      construct.Bytes('inode_number', 6),
      construct.Bytes('mode', 6),
      construct.Bytes('user_identifier', 6),
      construct.Bytes('group_identifier', 6),
      construct.Bytes('number_of_links', 6),
      construct.Bytes('special_device_number', 6),
      construct.Bytes('modification_time', 11),
      construct.Bytes('path_string_size', 6),
      construct.Bytes('file_size', 11))

  _CPIO_NEW_ASCII_FILE_ENTRY_STRUCT = construct.Struct(
      'cpio_portable_ascii_file_entry',
      construct.Bytes('signature', 6),
      construct.Bytes('inode_number', 8),
      construct.Bytes('mode', 8),
      construct.Bytes('user_identifier', 8),
      construct.Bytes('group_identifier', 8),
      construct.Bytes('number_of_links', 8),
      construct.Bytes('modification_time', 8),
      construct.Bytes('file_size', 8),
      construct.Bytes('device_major_number', 8),
      construct.Bytes('device_minor_number', 8),
      construct.Bytes('special_device_major_number', 8),
      construct.Bytes('special_device_minor_number', 8),
      construct.Bytes('path_string_size', 8),
      construct.Bytes('checksum', 8))

  def __init__(self):
    """Initializes the CPIO archive file object."""
    super(CPIOArchiveFile, self).__init__()
    self._file_entries = None
    self._file_object = None
    self._file_object_opened_in_object = False
    self._file_size = 0

    self.file_format = None

  def _ReadFileEntry(self, file_object, file_offset):
    """Reads a file entry.

    Args:
      file_object (FileIO): file-like object.
      file_offset (int): current file offset.

    Raises:
      IOError: if the file entry cannot be read.
    """
    file_object.seek(file_offset, os.SEEK_SET)

    if self.file_format == 'bin-big-endian':
      file_entry_struct = self._CPIO_BINARY_BIG_ENDIAN_FILE_ENTRY_STRUCT
    elif self.file_format == 'bin-little-endian':
      file_entry_struct = self._CPIO_BINARY_LITTLE_ENDIAN_FILE_ENTRY_STRUCT
    elif self.file_format == 'odc':
      file_entry_struct = self._CPIO_PORTABLE_ASCII_FILE_ENTRY_STRUCT
    elif self.file_format in ('crc', 'newc'):
      file_entry_struct = self._CPIO_NEW_ASCII_FILE_ENTRY_STRUCT

    file_entry_struct_size = file_entry_struct.sizeof()

    try:
      file_entry_struct = file_entry_struct.parse_stream(file_object)
    except construct.FieldError as exception:
      raise IOError((
          'Unable to parse file entry data section with error: '
          '{0:s}').format(exception))

    file_offset += file_entry_struct_size

    if self.file_format in ('bin-big-endian', 'bin-little-endian'):
      inode_number = file_entry_struct.inode_number
      mode = file_entry_struct.mode
      user_identifier = file_entry_struct.user_identifier
      group_identifier = file_entry_struct.group_identifier

      modification_time = (
          (file_entry_struct.modification_time_upper << 16) |
          file_entry_struct.modification_time_lower)

      path_string_size = file_entry_struct.path_string_size

      file_size = (
          (file_entry_struct.file_size_upper << 16) |
          file_entry_struct.file_size_lower)

    elif self.file_format == 'odc':
      inode_number = int(file_entry_struct.inode_number, 8)
      mode = int(file_entry_struct.mode, 8)
      user_identifier = int(file_entry_struct.user_identifier, 8)
      group_identifier = int(file_entry_struct.group_identifier, 8)
      modification_time = int(file_entry_struct.modification_time, 8)
      path_string_size = int(file_entry_struct.path_string_size, 8)
      file_size = int(file_entry_struct.file_size, 8)

    elif self.file_format in ('crc', 'newc'):
      inode_number = int(file_entry_struct.inode_number, 16)
      mode = int(file_entry_struct.mode, 16)
      user_identifier = int(file_entry_struct.user_identifier, 16)
      group_identifier = int(file_entry_struct.group_identifier, 16)
      modification_time = int(file_entry_struct.modification_time, 16)
      path_string_size = int(file_entry_struct.path_string_size, 16)
      file_size = int(file_entry_struct.file_size, 16)

    path_string_data = file_object.read(path_string_size)
    file_offset += path_string_size

    # TODO: should this be ASCII?
    path_string = path_string_data.decode('ascii')
    path_string, _, _ = path_string.partition('\x00')

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

    file_entry = CPIOArchiveFileEntry()
    file_entry.data_offset = file_offset
    file_entry.data_size = file_size
    file_entry.group_identifier = group_identifier
    file_entry.inode_number = inode_number
    file_entry.modification_time = modification_time
    file_entry.path = path_string
    file_entry.mode = mode
    file_entry.size = (
        file_entry_struct_size + path_string_size + padding_size + file_size)
    file_entry.user_identifier = user_identifier

    file_offset += file_size

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
      file_entry.size += padding_size

    return file_entry

  def _ReadFileEntries(self, file_object):
    """Reads the file entries from the cpio archive.

    Args:
      file_object (FileIO): file-like object.
    """
    self._file_entries = {}

    file_offset = 0
    while file_offset < self._file_size:
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
      for path, file_entry in iter(self._file_entries.items()):
        if path.startswith(path_prefix):
          yield file_entry

  def GetFileEntryByPath(self, path):
    """Retrieves a file entry for a specific path.

    Returns:
      CPIOArchiveFileEntry: a CPIO archive file entry or None if not available.
    """
    if self._file_entries:
      return self._file_entries.get(path, None)

  def Open(self, file_object):
    """Opens the CPIO archive file.

    Args:
      file_object (FileIO): a file-like object.

    Raises:
      IOError: if the file format signature is not supported.
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
    """
    self._file_object.seek(file_offset, os.SEEK_SET)
    return self._file_object.read(size)

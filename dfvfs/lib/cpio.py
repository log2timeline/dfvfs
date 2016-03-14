# -*- coding: utf-8 -*-
"""Helper functions for Copy in and out (CPIO) archive file support."""

import os

import construct


class CPIOArchiveFileEntry(object):
  """Class that contains a CPIO archive file entry.

  Attributes:
    data_offset: an integer containing the data start offset.
    data_size: an integer containing the data size.
    group_identifier: an integer containing the group identifier (gid).
    inode_number: an integer containing the inode number.
    mode: an integer containing the mode.
    modification_time: an integer containing the modification POSIX timestamp.
    path: a string containing the path.
    size: an integer containing the archive file entry record size.
    user_identifier: an integer containing the user identifier (uid).
  """

  def __init__(self):
    """Initializes the CPIO archive file entry object."""
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
  """Class that contains a CPIO archive file.

  Attributes:
    file_format: a string containing the CPIO file format.
  """
  _CPIO_SIGNATURE_BINARY_BIG_ENDIAN = b'\x71\xc7'
  _CPIO_SIGNATURE_BINARY_LITTLE_ENDIAN = b'\xc7\x71'
  _CPIO_SIGNATURE_PORTABLE_ASCII = b'070707'
  _CPIO_SIGNATURE_NEW_ASCII = b'070701'
  _CPIO_SIGNATURE_NEW_ASCII_WITH_CHECKSUM = b'070702'

  _CPIO_BINARY_BIG_ENDIAN_FILE_ENTRY_STRUCT = construct.Struct(
      u'cpio_binary_big_endian_file_entry',
      construct.UBInt16(u'signature'),
      construct.UBInt16(u'device_number'),
      construct.UBInt16(u'inode_number'),
      construct.UBInt16(u'mode'),
      construct.UBInt16(u'user_identifier'),
      construct.UBInt16(u'group_identifier'),
      construct.UBInt16(u'number_of_links'),
      construct.UBInt16(u'special_device_number'),
      construct.UBInt16(u'modification_time_upper'),
      construct.UBInt16(u'modification_time_lower'),
      construct.UBInt16(u'path_string_size'),
      construct.UBInt16(u'file_size_upper'),
      construct.UBInt16(u'file_size_lower'))

  _CPIO_BINARY_LITTLE_ENDIAN_FILE_ENTRY_STRUCT = construct.Struct(
      u'cpio_binary_little_endian_file_entry',
      construct.ULInt16(u'signature'),
      construct.ULInt16(u'device_number'),
      construct.ULInt16(u'inode_number'),
      construct.ULInt16(u'mode'),
      construct.ULInt16(u'user_identifier'),
      construct.ULInt16(u'group_identifier'),
      construct.ULInt16(u'number_of_links'),
      construct.ULInt16(u'special_device_number'),
      construct.ULInt16(u'modification_time_upper'),
      construct.ULInt16(u'modification_time_lower'),
      construct.ULInt16(u'path_string_size'),
      construct.ULInt16(u'file_size_upper'),
      construct.ULInt16(u'file_size_lower'))

  _CPIO_PORTABLE_ASCII_FILE_ENTRY_STRUCT = construct.Struct(
      u'cpio_portable_ascii_file_entry',
      construct.Bytes(u'signature', 6),
      construct.Bytes(u'device_number', 6),
      construct.Bytes(u'inode_number', 6),
      construct.Bytes(u'mode', 6),
      construct.Bytes(u'user_identifier', 6),
      construct.Bytes(u'group_identifier', 6),
      construct.Bytes(u'number_of_links', 6),
      construct.Bytes(u'special_device_number', 6),
      construct.Bytes(u'modification_time', 11),
      construct.Bytes(u'path_string_size', 6),
      construct.Bytes(u'file_size', 11))

  _CPIO_NEW_ASCII_FILE_ENTRY_STRUCT = construct.Struct(
      u'cpio_portable_ascii_file_entry',
      construct.Bytes(u'signature', 6),
      construct.Bytes(u'inode_number', 8),
      construct.Bytes(u'mode', 8),
      construct.Bytes(u'user_identifier', 8),
      construct.Bytes(u'group_identifier', 8),
      construct.Bytes(u'number_of_links', 8),
      construct.Bytes(u'modification_time', 8),
      construct.Bytes(u'file_size', 8),
      construct.Bytes(u'device_major_number', 8),
      construct.Bytes(u'device_minor_number', 8),
      construct.Bytes(u'special_device_major_number', 8),
      construct.Bytes(u'special_device_minor_number', 8),
      construct.Bytes(u'path_string_size', 8),
      construct.Bytes(u'checksum', 8))

  def __init__(self):
    """Initializes the CPIO archive file object."""
    super(CPIOArchiveFile, self).__init__()
    self._file_entries = None
    self._file_object = None
    self._file_object_opened_in_object = False
    self._file_size = 0

    self.file_format = None

  def _ReadFileEntry(self, file_offset):
    """Reads a file entry.

    Args:
      file_offset: an integer containing the current file offset.

    Raises:
      IOError: if the file entry cannot be read.
    """
    self._file_object.seek(file_offset, os.SEEK_SET)

    if self.file_format == u'bin-big-endian':
      file_entry_struct = self._CPIO_BINARY_BIG_ENDIAN_FILE_ENTRY_STRUCT
    elif self.file_format == u'bin-little-endian':
      file_entry_struct = self._CPIO_BINARY_LITTLE_ENDIAN_FILE_ENTRY_STRUCT
    elif self.file_format == u'odc':
      file_entry_struct = self._CPIO_PORTABLE_ASCII_FILE_ENTRY_STRUCT
    elif self.file_format in (u'crc', u'newc'):
      file_entry_struct = self._CPIO_NEW_ASCII_FILE_ENTRY_STRUCT

    file_entry_struct_size = file_entry_struct.sizeof()

    try:
      file_entry_struct = file_entry_struct.parse_stream(self._file_object)
    except construct.FieldError as exception:
      raise IOError((
          u'Unable to parse file entry data section with error: '
          u'{0:s}').format(exception))

    file_offset += file_entry_struct_size

    if self.file_format in (u'bin-big-endian', u'bin-little-endian'):
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

    elif self.file_format == u'odc':
      inode_number = int(file_entry_struct.inode_number, 8)
      mode = int(file_entry_struct.mode, 8)
      user_identifier = int(file_entry_struct.user_identifier, 8)
      group_identifier = int(file_entry_struct.group_identifier, 8)
      modification_time = int(file_entry_struct.modification_time, 8)
      path_string_size = int(file_entry_struct.path_string_size, 8)
      file_size = int(file_entry_struct.file_size, 8)

    elif self.file_format in (u'crc', u'newc'):
      inode_number = int(file_entry_struct.inode_number, 16)
      mode = int(file_entry_struct.mode, 16)
      user_identifier = int(file_entry_struct.user_identifier, 16)
      group_identifier = int(file_entry_struct.group_identifier, 16)
      modification_time = int(file_entry_struct.modification_time, 16)
      path_string_size = int(file_entry_struct.path_string_size, 16)
      file_size = int(file_entry_struct.file_size, 16)

    path_string_data = self._file_object.read(path_string_size)
    file_offset += path_string_size

    # TODO: should this be ASCII?
    path_string = path_string_data.decode(u'ascii')
    path_string, _, _ = path_string.partition(u'\x00')

    if self.file_format in (u'bin-big-endian', u'bin-little-endian'):
      padding_size = file_offset % 2
      if padding_size > 0:
        padding_size = 2 - padding_size

    elif self.file_format == u'odc':
      padding_size = 0

    elif self.file_format in (u'crc', u'newc'):
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

    if self.file_format in (u'crc', u'newc'):
      file_offset += file_size

      padding_size = file_offset % 4
      if padding_size > 0:
        padding_size = 4 - padding_size

      file_entry.size += padding_size

    return file_entry

  def _ReadFileEntries(self):
    """Reads the file entries from the cpio archive."""
    file_offset = 0
    while file_offset < self._file_size:
      file_entry = self._ReadFileEntry(file_offset)
      file_offset += file_entry.size
      if file_entry.path == u'TRAILER!!!':
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
      A boolean value indicating the file entry exists.
    """
    if self._file_entries is None:
      return False

    return path in self._file_entries

  def GetFileEntries(self, path_prefix=u''):
    """Retrieves the file entries.

    Args:
      path_prefix: a string containing the path prefix.

    Yields:
      A CPIO archive file entry (instance of CPIOArchiveFileEntry).
    """
    for path, file_entry in iter(self._file_entries.items()):
      if path.startswith(path_prefix):
        yield file_entry

  def GetFileEntryByPath(self, path):
    """Retrieves a file entry for a specific path.

    Returns:
      A CPIO archive file entry (instance of CPIOArchiveFileEntry) or None.
    """
    if self._file_entries is None:
      return

    return self._file_entries.get(path, None)

  def Open(self, file_object):
    """Opens the CPIO archive file.

    Args:
      file_object: the file-like object.

    Raises:
      IOError: if the file format signature is not supported.
    """
    file_object.seek(0, os.SEEK_SET)
    signature_data = file_object.read(6)

    self.file_format = None
    if len(signature_data) > 2:
      if signature_data[:2] == self._CPIO_SIGNATURE_BINARY_BIG_ENDIAN:
        self.file_format = u'bin-big-endian'
      elif signature_data[:2] == self._CPIO_SIGNATURE_BINARY_LITTLE_ENDIAN:
        self.file_format = u'bin-little-endian'
      elif signature_data == self._CPIO_SIGNATURE_PORTABLE_ASCII:
        self.file_format = u'odc'
      elif signature_data == self._CPIO_SIGNATURE_NEW_ASCII:
        self.file_format = u'newc'
      elif signature_data == self._CPIO_SIGNATURE_NEW_ASCII_WITH_CHECKSUM:
        self.file_format = u'crc'

    if self.file_format is None:
      raise IOError(u'Unsupported CPIO format.')

    self._file_entries = {}
    self._file_object = file_object
    self._file_size = file_object.get_size()

    self._ReadFileEntries()

  def ReadDataAtOffset(self, file_offset, size):
    """Reads a byte string from the file-like object at a specific offset.

    Args:
      file_offset: an integer value containing the file offset.
      size: an integer value containing the number of bytes to read.

    Returns:
      A byte string containing the data read.

    Raises:
      IOError: if the read failed.
    """
    self._file_object.seek(file_offset, os.SEEK_SET)
    return self._file_object.read(size)

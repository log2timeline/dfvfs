# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) file-like object implementation."""

from __future__ import unicode_literals

import os

import pytsk3

from dfvfs.file_io import file_io
from dfvfs.resolver import resolver


class TSKFile(file_io.FileIO):
  """File-like object using pytsk3."""

  def __init__(self, resolver_context):
    """Initializes a file-like object.

    Args:
      resolver_context (Context): resolver context.
    """
    super(TSKFile, self).__init__(resolver_context)
    self._current_offset = 0
    self._file_system = None
    self._size = 0
    self._tsk_attribute = None
    self._tsk_file = None

  def _Close(self):
    """Closes the file-like object."""
    self._tsk_attribute = None
    self._tsk_file = None

    self._file_system.Close()
    self._file_system = None

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec:
      raise ValueError('Missing path specification.')

    data_stream = getattr(path_spec, 'data_stream', None)

    file_system = resolver.Resolver.OpenFileSystem(
        path_spec, resolver_context=self._resolver_context)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    if not file_entry:
      file_system.Close()
      raise IOError('Unable to retrieve file entry.')

    tsk_file = file_entry.GetTSKFile()
    tsk_attribute = None

    # Note that because pytsk3.File does not explicitly defines info
    # we need to check if the attribute exists and has a value other
    # than None.
    if getattr(tsk_file, 'info', None) is None:
      file_system.Close()
      raise IOError('Missing attribute info in file (pytsk3.File).')

    # Note that because pytsk3.TSK_FS_FILE does not explicitly defines meta
    # we need to check if the attribute exists and has a value other
    # than None.
    if getattr(tsk_file.info, 'meta', None) is None:
      file_system.Close()
      raise IOError(
          'Missing attribute meta in file.info pytsk3.TSK_FS_FILE).')

    # Note that because pytsk3.TSK_FS_META does not explicitly defines size
    # we need to check if the attribute exists.
    if not hasattr(tsk_file.info.meta, 'size'):
      file_system.Close()
      raise IOError(
          'Missing attribute size in file.info.meta (pytsk3.TSK_FS_META).')

    # Note that because pytsk3.TSK_FS_META does not explicitly defines type
    # we need to check if the attribute exists.
    if not hasattr(tsk_file.info.meta, 'type'):
      file_system.Close()
      raise IOError(
          'Missing attribute type in file.info.meta (pytsk3.TSK_FS_META).')

    if data_stream:
      for attribute in tsk_file:
        if getattr(attribute, 'info', None) is None:
          continue

        # The value of the attribute name will be None for the default
        # data stream.
        attribute_name = getattr(attribute.info, 'name', None)
        if attribute_name is None:
          attribute_name = ''

        else:
          try:
            # pytsk3 returns an UTF-8 encoded byte string.
            attribute_name = attribute_name.decode('utf8')
          except UnicodeError:
            # Continue here since we cannot represent the attribute name.
            continue

        attribute_type = getattr(attribute.info, 'type', None)
        if attribute_name == data_stream and attribute_type in (
            pytsk3.TSK_FS_ATTR_TYPE_HFS_DEFAULT,
            pytsk3.TSK_FS_ATTR_TYPE_HFS_DATA,
            pytsk3.TSK_FS_ATTR_TYPE_NTFS_DATA):
          tsk_attribute = attribute
          break

      if tsk_attribute is None:
        file_system.Close()
        raise IOError('Unable to open data stream: {0:s}.'.format(data_stream))

    if (not tsk_attribute and
        tsk_file.info.meta.type != pytsk3.TSK_FS_META_TYPE_REG):
      file_system.Close()
      raise IOError('Not a regular file.')

    self._current_offset = 0
    self._file_system = file_system
    self._tsk_attribute = tsk_attribute
    self._tsk_file = tsk_file

    if self._tsk_attribute:
      self._size = self._tsk_attribute.info.size
    else:
      self._size = self._tsk_file.info.meta.size

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.
  # pylint: disable=invalid-name

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

    The function will read a byte string of the specified size or
    all of the remaining data if no size was specified.

    Args:
      size (Optional[int]): number of bytes to read, where None is all
          remaining data.

    Returns:
      bytes: data read.

    Raises:
      IOError: if the read failed.
      OSError: if the read failed.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    if self._current_offset < 0:
      raise IOError('Invalid current offset value less than zero.')

    # The SleuthKit is not POSIX compliant in its read behavior. Therefore
    # pytsk3 will raise an IOError if the read offset is beyond the data size.
    if self._current_offset >= self._size:
      return b''

    if size is None or self._current_offset + size > self._size:
      size = self._size - self._current_offset

    if self._tsk_attribute:
      data = self._tsk_file.read_random(
          self._current_offset, size, self._tsk_attribute.info.type,
          self._tsk_attribute.info.id)
    else:
      data = self._tsk_file.read_random(self._current_offset, size)

    # It is possible the that returned data size is not the same as the
    # requested data size. At this layer we don't care and this discrepancy
    # should be dealt with on a higher layer if necessary.
    self._current_offset += len(data)

    return data

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks to an offset within the file-like object.

    Args:
      offset (int): offset to seek to.
      whence (Optional(int)): value that indicates whether offset is an absolute
          or relative position within the file.

    Raises:
      IOError: if the seek failed.
      OSError: if the seek failed.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._size
    elif whence != os.SEEK_SET:
      raise IOError('Unsupported whence.')

    if offset < 0:
      raise IOError('Invalid offset value less than zero.')

    self._current_offset = offset

  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    return self._current_offset

  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size of the file-like object data.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    return self._size

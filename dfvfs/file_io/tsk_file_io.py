# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) file-like object implementation."""

import os

import pytsk3

from dfvfs.lib import errors
from dfvfs.file_io import file_io
from dfvfs.resolver import resolver


class TSKFile(file_io.FileIO):
  """File input/output (IO) object using pytsk3."""

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(TSKFile, self).__init__(resolver_context, path_spec)
    self._current_offset = 0
    self._file_system = None
    self._size = 0
    self._tsk_attribute = None
    self._tsk_file = None

  def _Close(self):
    """Closes the file-like object."""
    self._tsk_attribute = None
    self._tsk_file = None

    self._file_system = None

  def _Open(self, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      BackEndError: if pytsk3 returns a non UTF-8 formatted name.
      IOError: if the file-like object could not be opened.
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
    """
    data_stream_name = getattr(self._path_spec, 'data_stream', None)

    file_system = resolver.Resolver.OpenFileSystem(
        self._path_spec, resolver_context=self._resolver_context)

    file_entry = file_system.GetFileEntryByPathSpec(self._path_spec)
    if not file_entry:
      raise IOError('Unable to retrieve file entry.')

    tsk_file = file_entry.GetTSKFile()
    tsk_attribute = None

    # Note that because pytsk3.File does not explicitly defines info
    # we need to check if the attribute exists and has a value other
    # than None.
    if getattr(tsk_file, 'info', None) is None:
      raise IOError('Missing attribute info in file (pytsk3.File).')

    # Note that because pytsk3.TSK_FS_FILE does not explicitly defines meta
    # we need to check if the attribute exists and has a value other
    # than None.
    if getattr(tsk_file.info, 'meta', None) is None:
      raise IOError(
          'Missing attribute meta in file.info pytsk3.TSK_FS_FILE).')

    # Note that because pytsk3.TSK_FS_META does not explicitly defines size
    # we need to check if the attribute exists.
    if not hasattr(tsk_file.info.meta, 'size'):
      raise IOError(
          'Missing attribute size in file.info.meta (pytsk3.TSK_FS_META).')

    # Note that because pytsk3.TSK_FS_META does not explicitly defines type
    # we need to check if the attribute exists.
    if not hasattr(tsk_file.info.meta, 'type'):
      raise IOError(
          'Missing attribute type in file.info.meta (pytsk3.TSK_FS_META).')

    if data_stream_name:
      for pytsk_attribute in tsk_file:
        if getattr(pytsk_attribute, 'info', None) is None:
          continue

        attribute_name = getattr(pytsk_attribute.info, 'name', None)
        if attribute_name:
          try:
            # pytsk3 returns an UTF-8 encoded byte string.
            attribute_name = attribute_name.decode('utf8')
          except UnicodeError:
            raise errors.BackEndError(
                'pytsk3 returned a non UTF-8 formatted name.')

        attribute_type = getattr(pytsk_attribute.info, 'type', None)
        if attribute_type == pytsk3.TSK_FS_ATTR_TYPE_HFS_DATA and (
            not data_stream_name and not attribute_name):
          tsk_attribute = pytsk_attribute
          break

        if attribute_type == pytsk3.TSK_FS_ATTR_TYPE_HFS_RSRC and (
            data_stream_name == 'rsrc'):
          tsk_attribute = pytsk_attribute
          break

        if attribute_type == pytsk3.TSK_FS_ATTR_TYPE_NTFS_DATA and (
            (not data_stream_name and not attribute_name) or
            (data_stream_name == attribute_name)):
          tsk_attribute = pytsk_attribute
          break

        # The data stream is returned as a name-less attribute of type
        # pytsk3.TSK_FS_ATTR_TYPE_DEFAULT.
        if (attribute_type == pytsk3.TSK_FS_ATTR_TYPE_DEFAULT and
            not data_stream_name and not attribute_name):
          tsk_attribute = pytsk_attribute
          break

      if tsk_attribute is None:
        raise IOError(f'Unable to open data stream: {data_stream_name:s}.')

    if (not tsk_attribute and
        tsk_file.info.meta.type != pytsk3.TSK_FS_META_TYPE_REG):
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

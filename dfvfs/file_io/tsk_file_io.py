# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) file-like object implementation."""

import os
import pytsk3

from dfvfs.file_io import file_io
from dfvfs.resolver import resolver


class TSKFile(file_io.FileIO):
  """Class that implements a file-like object using pytsk3."""

  def __init__(self, resolver_context):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(TSKFile, self).__init__(resolver_context)
    self._current_offset = 0
    self._file_system = None
    self._size = 0
    self._tsk_file = None

  def _Close(self):
    """Closes the file-like object.

    Raises:
      IOError: if the close failed.
    """
    self._tsk_file = None

    self._file_system.Close()
    self._file_system = None

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional path specification (instance of path.PathSpec).
                 The default is None.
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec:
      raise ValueError(u'Missing path specfication.')

    self._file_system = resolver.Resolver.OpenFileSystem(
        path_spec, resolver_context=self._resolver_context)

    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    self._tsk_file = file_entry.GetTSKFile()

    # Note that because pytsk3.File does not explicitly defines info
    # we need to check if the attribute exists and has a value other
    # than None.
    if getattr(self._tsk_file, u'info', None) is None:
      raise IOError(u'Missing attribute info in file (pytsk3.File).')

    # Note that because pytsk3.TSK_FS_FILE does not explicitly defines meta
    # we need to check if the attribute exists and has a value other
    # than None.
    if getattr(self._tsk_file.info, u'meta', None) is None:
      raise IOError(
          u'Missing attribute meta in file.info pytsk3.TSK_FS_FILE).')

    # Note that because pytsk3.TSK_FS_META does not explicitly defines size
    # we need to check if the attribute exists.
    if not hasattr(self._tsk_file.info.meta, u'size'):
      raise IOError(
          u'Missing attribute size in file.info.meta (pytsk3.TSK_FS_META).')

    # Note that because pytsk3.TSK_FS_META does not explicitly defines type
    # we need to check if the attribute exists.
    if not hasattr(self._tsk_file.info.meta, u'type'):
      raise IOError(
          u'Missing attribute type in file.info.meta (pytsk3.TSK_FS_META).')

    if self._tsk_file.info.meta.type != pytsk3.TSK_FS_META_TYPE_REG:
      raise IOError(u'Not a regular file.')

    self._current_offset = 0
    self._size = self._tsk_file.info.meta.size

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

       The function will read a byte string of the specified size or
       all of the remaining data if no size was specified.

    Args:
      size: Optional integer value containing the number of bytes to read.
            Default is all remaining data (None).

    Returns:
      A byte string containing the data read.

    Raises:
      IOError: if the read failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if self._current_offset < 0:
      raise IOError(u'Invalid current offset value less than zero.')

    # The SleuthKit is not POSIX compliant in its read behavior. Therefore
    # pytsk3 will raise an IOError if the read offset is beyond the data size.
    if self._current_offset >= self._size:
      return b''

    if size is None or self._current_offset + size > self._size:
      size = self._size - self._current_offset

    data = self._tsk_file.read_random(self._current_offset, size)

    # It is possible the that returned data size is not the same as the
    # requested data size. At this layer we don't care and this discrepancy
    # should be dealt with on a higher layer if necessary.
    self._current_offset += len(data)

    return data

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset: The offset to seek.
      whence: Optional value that indicates whether offset is an absolute
              or relative position within the file. Default is SEEK_SET.

    Raises:
      IOError: if the seek failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._size
    elif whence != os.SEEK_SET:
      raise IOError(u'Unsupported whence.')

    if offset < 0:
      raise IOError(u'Invalid offset value less than zero.')

    self._current_offset = offset

  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._current_offset

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._size

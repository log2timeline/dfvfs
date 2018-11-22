# -*- coding: utf-8 -*-
"""The TAR extracted file-like object implementation."""

from __future__ import unicode_literals

# Note: that tarfile.ExFileObject is not POSIX compliant for seeking
# beyond the file size, hence it is wrapped in an instance of file_io.FileIO.

import os

from dfvfs.file_io import file_io
from dfvfs.resolver import resolver


class TARFile(file_io.FileIO):
  """File-like object using tarfile."""

  def __init__(self, resolver_context):
    """Initializes a file-like object.

    Args:
      resolver_context (Context): resolver context.
    """
    super(TARFile, self).__init__(resolver_context)
    self._current_offset = 0
    self._file_system = None
    self._size = 0
    self._tar_ext_file = None

  def _Close(self):
    """Closes the file-like object."""
    self._tar_ext_file.close()
    self._tar_ext_file = None

    self._file_system.Close()
    self._file_system = None

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (Optional[PathSpec]): path specification.
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

    file_system = resolver.Resolver.OpenFileSystem(
        path_spec, resolver_context=self._resolver_context)

    file_entry = file_system.GetFileEntryByPathSpec(path_spec)
    if not file_entry:
      file_system.Close()
      raise IOError('Unable to retrieve file entry.')

    if not file_entry.IsFile():
      file_system.Close()
      raise IOError('Not a regular file.')

    self._file_system = file_system
    tar_file = self._file_system.GetTARFile()
    tar_info = file_entry.GetTARInfo()

    self._tar_ext_file = tar_file.extractfile(tar_info)

    self._current_offset = 0
    self._size = tar_info.size

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

    if self._current_offset > self._size:
      return b''

    if size is None or self._current_offset + size > self._size:
      size = self._size - self._current_offset

    self._tar_ext_file.seek(self._current_offset, os.SEEK_SET)

    data = self._tar_ext_file.read(size)

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

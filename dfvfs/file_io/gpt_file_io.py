# -*- coding: utf-8 -*-
"""The GUID Partition Table (GPT) file-like object implementation."""

import os

from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.lib import gpt_helper
from dfvfs.resolver import resolver


class GPTFile(file_io.FileIO):
  """File input/output (IO) object using pyvsgpt."""

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(GPTFile, self).__init__(resolver_context, path_spec)
    self._current_offset = None
    self._file_object = None
    self._file_system = None
    self._partition_offset = None
    self._partition_size = None
    self._vsgpt_partition = None

  def _Close(self):
    """Closes the file-like object."""
    self._current_offset = None
    self._partition_offset = None
    self._partition_size = None

    self._vsgpt_partition = None

    self._file_object = None
    self._file_system = None

  def _Open(self, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
    """
    entry_index = gpt_helper.GPTPathSpecGetEntryIndex(self._path_spec)
    if entry_index is None:
      raise errors.PathSpecError(
          'Unable to retrieve entry index from path specification.')

    self._file_system = resolver.Resolver.OpenFileSystem(
        self._path_spec, resolver_context=self._resolver_context)
    vsgpt_volume = self._file_system.GetGPTVolume()

    if not vsgpt_volume.has_partition_with_identifier(entry_index):
      raise errors.PathSpecError(
          f'Missing GPT partition with entry index: {entry_index:d}')

    self._vsgpt_partition = vsgpt_volume.get_partition_by_identifier(
        entry_index)

    # Note that using pass-through IO in Python is faster than using
    # the vsgpt_partition read and seek methods.
    self._file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)

    self._current_offset = 0
    self._partition_offset = self._vsgpt_partition.get_volume_offset()
    self._partition_size = self._vsgpt_partition.get_size()

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

    if self._partition_offset < 0 or self._partition_size < 0:
      raise IOError('Invalid partition data range.')

    if self._current_offset < 0:
      raise IOError((
          f'Invalid current offset: {self._current_offset:d} value less than '
          f'zero.'))

    if self._current_offset >= self._partition_size:
      return b''

    if size is None:
      size = self._partition_size
    if self._current_offset + size > self._partition_size:
      size = self._partition_size - self._current_offset

    self._file_object.seek(
        self._partition_offset + self._current_offset, os.SEEK_SET)

    data = self._file_object.read(size)

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

    if self._current_offset < 0:
      raise IOError((
          f'Invalid current offset: {self._current_offset:d} value less than '
          f'zero.'))

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._partition_size
    elif whence != os.SEEK_SET:
      raise IOError('Unsupported whence.')
    if offset < 0:
      raise IOError('Invalid offset value less than zero.')
    self._current_offset = offset

  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: current offset in the partition.

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
      int: size of the partition.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    return self._partition_size

# -*- coding: utf-8 -*-
"""The Overlay file-like object implementation."""

import os

from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.resolver import resolver


class OverlayFile(file_io.FileIO):
  """File input/output (IO) object"""

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(OverlayFile, self).__init__(resolver_context, path_spec)
    self._file_io = None

  def _Close(self):
    """Closes the file input/output (IO) object.

    Raises:
      IOError: if the close failed.
      OSError: if the close failed.
    """
    self._file_io = None

  def _Open(self, mode='rb'):
    """Opens the file input/output (IO) object defined by path specification.

    Args:
      mode (Optional[str]): file access mode.

    Raises:
      NotSupported: when path specification has a data stream
      PathSpecError: when the parent attribute is None.
    """
    data_stream = getattr(self._path_spec, 'data_stream', None)
    if data_stream:
      raise errors.NotSupported(
          'Open data stream: {0:s} not supported.'.format(data_stream))

    if not self._path_spec.parent:
      raise errors.PathSpecError('Parent of path spec is None.')

    self._file_io = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, self._resolver_context)

  def read(self, size=None):
    """Reads a byte string from the file input/output (IO) object.

    The function will read a byte string of the specified size or
    all of the remaining data if no size was specified.

    Args:
      size (Optional[int]): number of bytes to read, where None is all
          remaining data.

    Returns:
      bytes: data read.
    """
    return self._file_io.read(size)

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks to an offset within the file input/output (IO) object.

    Args:
      offset (int): offset to seek.
      whence (Optional[int]): value that indicates whether offset is an
          absolute or relative position within the file.

    Raises:
      IOError: if the seek failed.
      OSError: if the seek failed.
    """
    self._file_io.seek(offset, whence)

  def get_offset(self):
    """Retrieves the current offset into the file input/output (IO) object.

    Returns:
      int: current offset into the file input/output (IO) object.

    Raises:
      IOError: if the file input/output (IO)-like object has not been opened.
      OSError: if the file input/output (IO)-like object has not been opened.
    """
    return self._file_io.get_offset()

  def get_size(self):
    """Retrieves the size of the file input/output (IO) object.

    Returns:
      int: size of the file input/output (IO) object.

    Raises:
      IOError: if the file input/output (IO) object has not been opened.
      OSError: if the file input/output (IO) object has not been opened.
    """
    return self._file_io.get_size()

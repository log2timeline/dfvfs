# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) file input/output (IO) object interface."""

import abc
import os

class FileIO(object):
  """VFS file input/output (IO) object interface."""

  # pylint: disable=redundant-returns-doc

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(FileIO, self).__init__()
    self._is_open = False
    self._path_spec = path_spec
    self._resolver_context = resolver_context

  def __del__(self):
    """Cleans up the file input/output (IO) object."""
    # In case __init__ fails the "_is_open" instance attribute might not exist
    # hence that getattr is used here.
    is_open = getattr(self, '_is_open', None)
    if is_open:
      self._Close()

  @abc.abstractmethod
  def _Close(self):
    """Closes the file input/output (IO) object.

    Raises:
      IOError: if the close failed.
      OSError: if the close failed.
    """

  @abc.abstractmethod
  def _Open(self, mode='rb'):
    """Opens the file input/output (IO) object defined by path specification.

    Args:
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file input/output (IO) object could not be opened.
      OSError: if the file input/output (IO) object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """

  # Note that path_spec is kept as the second argument for backwards
  # compatibility.
  def Open(self, path_spec=None, mode='rb'):
    """Opens the file input/output (IO) object defined by path specification.

    Args:
      path_spec (Optional[PathSpec]): path specification.
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file input/output (IO) object was already opened or the
          open failed.
      OSError: if the file input/output (IO) object was already opened or the
          open failed.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification or mode is invalid.
    """
    if self._is_open:
      raise IOError('Already open.')

    if mode != 'rb':
      raise ValueError(f'Unsupported mode: {mode:s}.')

    if not self._path_spec:
      self._path_spec = path_spec

    if not self._path_spec:
      raise ValueError('Missing path specification.')

    self._Open(mode=mode)
    self._is_open = True

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.
  # pylint: disable=invalid-name

  @abc.abstractmethod
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
      IOError: if the read failed.
      OSError: if the read failed.
    """

  @abc.abstractmethod
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

  # get_offset() is preferred above tell() by the libbfio layer used in libyal.
  @abc.abstractmethod
  def get_offset(self):
    """Retrieves the current offset into the file input/output (IO) object.

    Returns:
      int: current offset into the file input/output (IO) object.

    Raises:
      IOError: if the file input/output (IO)-like object has not been opened.
      OSError: if the file input/output (IO)-like object has not been opened.
    """

  # Pythonesque alias for get_offset().
  def tell(self):
    """Retrieves the current offset into the file input/output (IO) object."""
    return self.get_offset()

  @abc.abstractmethod
  def get_size(self):
    """Retrieves the size of the file input/output (IO) object.

    Returns:
      int: size of the file input/output (IO) object.

    Raises:
      IOError: if the file input/output (IO) object has not been opened.
      OSError: if the file input/output (IO) object has not been opened.
    """

  def seekable(self):
    """Determines if a file input/output (IO) object is seekable.

    Returns:
      bool: True since a file IO object provides a seek method.
    """
    return True

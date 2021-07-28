# -*- coding: utf-8 -*-
"""The operating system attribute implementation."""

import os

try:
  import xattr
except ImportError:
  xattr = None

from dfvfs.vfs import attribute


class OSExtendedAttribute(attribute.Attribute):
  """Extended attribute that uses the operating system."""

  def __init__(self, location, name):
    """Initializes an attribute.

    Args:
      location (str): path of the file.
      name (str): name of the extended attribute.
    """
    super(OSExtendedAttribute, self).__init__()
    self._current_offset = 0
    self._data = xattr.getxattr(location, name)
    self._location = location
    self._name = name
    self._size = len(self._data)

  @property
  def name(self):
    """str: name."""
    return self._name

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.
  # pylint: disable=invalid-name

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
    if size is None:
      size = self._size

    data = self._data[self._current_offset:self._current_offset + size]
    self._current_offset += len(data)
    return data

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
    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset = self._size - offset
    elif whence != os.SEEK_SET:
      raise IOError('Invalid whence')

    if offset < 0:
      raise IOError('Invalid offset')

    self._current_offset = offset

  # get_offset() is preferred above tell() by the libbfio layer used in libyal.
  def get_offset(self):
    """Retrieves the current offset into the file input/output (IO) object.

    Returns:
      int: current offset into the file input/output (IO) object.
    """
    return self._current_offset

  # Pythonesque alias for get_offset().
  def tell(self):
    """Retrieves the current offset into the file input/output (IO) object."""
    return self.get_offset()

  def get_size(self):
    """Retrieves the size of the file input/output (IO) object.

    Returns:
      int: size of the file input/output (IO) object.
    """
    return self._size

  def seekable(self):
    """Determines if a file input/output (IO) object is seekable.

    Returns:
      bool: True since a file IO object provides a seek method.
    """
    return True

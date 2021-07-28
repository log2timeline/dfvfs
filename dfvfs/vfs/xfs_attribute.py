# -*- coding: utf-8 -*-
"""The XFS attribute implementation."""

import os

from dfvfs.lib import errors
from dfvfs.vfs import attribute


class XFSExtendedAttribute(attribute.Attribute):
  """XFS extended attribute that uses pyfsxfs."""

  def __init__(self, fsxfs_extended_attribute):
    """Initializes an attribute.

    Args:
      fsxfs_extended_attribute (pyfsxfs.extended_attribute): XFS extended
          attribute.

    Raises:
      BackEndError: if the pyfsxfs extended attribute is missing.
    """
    if not fsxfs_extended_attribute:
      raise errors.BackEndError('Missing pyfsxfs extended attribute.')

    super(XFSExtendedAttribute, self).__init__()
    self._fsxfs_extended_attribute = fsxfs_extended_attribute

  @property
  def name(self):
    """str: name."""
    return self._fsxfs_extended_attribute.name

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
    return self._fsxfs_extended_attribute.read_buffer(size)

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
    self._fsxfs_extended_attribute.seek_offset(offset, whence)

  # get_offset() is preferred above tell() by the libbfio layer used in libyal.
  def get_offset(self):
    """Retrieves the current offset into the file input/output (IO) object.

    Returns:
      int: current offset into the file input/output (IO) object.
    """
    return self._fsxfs_extended_attribute.get_offset()

  # Pythonesque alias for get_offset().
  def tell(self):
    """Retrieves the current offset into the file input/output (IO) object."""
    return self.get_offset()

  def get_size(self):
    """Retrieves the size of the file input/output (IO) object.

    Returns:
      int: size of the file input/output (IO) object.
    """
    return self._fsxfs_extended_attribute.get_size()

  def seekable(self):
    """Determines if a file input/output (IO) object is seekable.

    Returns:
      bool: True since a file IO object provides a seek method.
    """
    return True

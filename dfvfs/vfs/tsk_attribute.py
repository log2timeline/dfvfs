# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) attribute implementation."""

import os

from dfvfs.lib import errors
from dfvfs.vfs import attribute


class TSKAttribute(attribute.Attribute):
  """File system attribute that uses pytsk3."""

  def __init__(self, tsk_file, tsk_attribute):
    """Initializes an attribute.

    Args:
      tsk_file (pytsk3.File): TSK file.
      tsk_attribute (pytsk3.Attribute): TSK attribute.

    Raises:
      BackEndError: if the TSK file or attribute is missing.
    """
    if not tsk_file:
      raise errors.BackEndError('Missing TSK file.')

    if not tsk_attribute:
      raise errors.BackEndError('Missing TSK attribute.')

    super(TSKAttribute, self).__init__()
    self._attribute_type = getattr(tsk_attribute.info, 'type', None)
    self._tsk_attribute = tsk_attribute
    self._tsk_file = tsk_file

  @property
  def attribute_type(self):
    """object: attribute type."""
    return self._attribute_type


class TSKExtendedAttribute(TSKAttribute):
  """File system extended attribute that uses pytsk3."""

  def __init__(self, tsk_file, tsk_attribute):
    """Initializes an attribute.

    Args:
      tsk_file (pytsk3.File): TSK file.
      tsk_attribute (pytsk3.Attribute): TSK attribute.
    """
    super(TSKExtendedAttribute, self).__init__(tsk_file, tsk_attribute)
    self._current_offset = 0
    self._identifier = getattr(tsk_attribute.info, 'id', None)
    self._size = getattr(tsk_attribute.info, 'size', None)

  @property
  def name(self):
    """str: name.

    Raises:
      BackEndError: if pytsk3 returns a non UTF-8 formatted name.
    """
    name = getattr(self._tsk_attribute.info, 'name', None)
    if name:
      try:
        # pytsk3 returns an UTF-8 encoded byte string.
        return name.decode('utf8')
      except UnicodeError:
        raise errors.BackEndError(
            'pytsk3 returned a non UTF-8 formatted name.')

    return name

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

    data = self._tsk_file.read_random(
        self._current_offset, size, self._attribute_type, self._identifier)
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

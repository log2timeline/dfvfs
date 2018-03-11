# -*- coding: utf-8 -*-
"""Helper functions for SleuthKit (TSK) image support."""

from __future__ import unicode_literals

import os
import pytsk3


class TSKFileSystemImage(pytsk3.Img_Info):
  """Pytsk3 image object using a file-like object."""

  def __init__(self, file_object):
    """Initializes an image object.

    Args:
      file_object (FileIO): file-like object.

    Raises:
      ValueError: if the file-like object is invalid.
    """
    if not file_object:
      raise ValueError('Missing file-like object.')

    # pytsk3.Img_Info does not let you set attributes after initialization.
    self._file_object = file_object
    # Using the old parent class invocation style otherwise some versions
    # of pylint complain also setting type to RAW or EXTERNAL to make sure
    # Img_Info does not do detection.
    tsk_img_type = getattr(
        pytsk3, 'TSK_IMG_TYPE_EXTERNAL', pytsk3.TSK_IMG_TYPE_RAW)
    # Note that we want url to be a binary string in Python 2 and a Unicode
    # string in Python 3. Hence the string is not prefixed.
    pytsk3.Img_Info.__init__(self, url='', type=tsk_img_type)

  # Note: that the following functions do not follow the style guide
  # because they are part of the pytsk3.Img_Info object interface.
  # pylint: disable=invalid-name

  def close(self):
    """Closes the volume IO object."""
    self._file_object = None

  def read(self, offset, size):
    """Reads a byte string from the image object at the specified offset.

    Args:
      offset (int): offset where to start reading.
      size (int): number of bytes to read.

    Returns:
      bytes: data read.
    """
    self._file_object.seek(offset, os.SEEK_SET)
    return self._file_object.read(size)

  def get_size(self):
    """Retrieves the size."""
    return self._file_object.get_size()

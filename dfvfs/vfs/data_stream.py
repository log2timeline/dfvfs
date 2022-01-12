# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) data stream interface."""


class DataStream(object):
  """Data stream interface."""

  # The data stream object should not have a reference to its
  # file entry since that will create a cyclic reference.

  @property
  def name(self):
    """str: name."""
    return ''

  def IsDefault(self):
    """Determines if the data stream is the default data stream.

    Returns:
      bool: True if the data stream is the default data stream.
    """
    return True

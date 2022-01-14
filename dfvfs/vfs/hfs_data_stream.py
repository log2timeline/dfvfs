# -*- coding: utf-8 -*-
"""The HFS data stream implementation."""

from dfvfs.vfs import data_stream


class HFSDataStream(data_stream.DataStream):
  """File system data stream that uses pyfshfs."""

  def __init__(self, fshfs_data_stream):
    """Initializes the data stream.

    Args:
      fshfs_data_stream (pyfshfs.data_stream): HFS data stream.
    """
    super(HFSDataStream, self).__init__()
    self._fshfs_data_stream = fshfs_data_stream
    self._name = ''

    if fshfs_data_stream:
      self._name = 'rsrc'

  @property
  def name(self):
    """str: name."""
    return self._name

  def IsDefault(self):
    """Determines if the data stream is the default (data fork) data stream.

    Returns:
      bool: True if the data stream is the default (data fork) data stream.
    """
    return not self._fshfs_data_stream

# -*- coding: utf-8 -*-
"""The NTFS data stream implementation."""

from dfvfs.vfs import data_stream


class NTFSDataStream(data_stream.DataStream):
  """File system data stream that uses pyfsntfs."""

  def __init__(self, fsntfs_data_stream):
    """Initializes the data stream object.

    Args:
      fsntfs_data_stream (pyfsntfs.data_stream): NTFS data stream.
    """
    super(NTFSDataStream, self).__init__()
    self._fsntfs_data_stream = fsntfs_data_stream

  @property
  def name(self):
    """str: name."""
    return getattr(self._fsntfs_data_stream, 'name', '')

  def IsDefault(self):
    """Determines if the data stream is the default data stream.

    Returns:
      bool: True if the data stream is the default data stream.
    """
    return not self._fsntfs_data_stream

# -*- coding: utf-8 -*-
"""The NTFS data stream implementation."""

from dfvfs.vfs import data_stream


class NTFSDataStream(data_stream.DataStream):
  """File system data stream that uses pyfsntfs."""

  def __init__(self, fsntfs_data_stream):
    """Initializes the data stream.

    Args:
      fsntfs_data_stream (pyfsntfs.data_stream): NTFS data stream.
    """
    super(NTFSDataStream, self).__init__()
    self._name = getattr(fsntfs_data_stream, 'name', None) or ''

  @property
  def name(self):
    """str: name."""
    return self._name

  def IsDefault(self):
    """Determines if the data stream is the default data stream.

    Returns:
      bool: True if the data stream is the default data stream.
    """
    return not bool(self._name)

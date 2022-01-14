# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) data stream interface."""


class DataStream(object):
  """Data stream interface."""

  def __init__(self, file_entry):
    """Initializes the data stream.

    Args:
      file_entry (FileEntry): file entry.
    """
    super(DataStream, self).__init__()
    self._file_entry = file_entry
    self._name = ''

  @property
  def name(self):
    """str: name."""
    return self._name

  def GetExtents(self):
    """Retrieves the extents.

    Returns:
      list[Extent]: the extents of the data stream.
    """
    if self._file_entry:
      return self._file_entry.GetExtents()
    return []

  def IsDefault(self):
    """Determines if the data stream is the default data stream.

    Returns:
      bool: True if the data stream is the default data stream.
    """
    return not bool(self._name)

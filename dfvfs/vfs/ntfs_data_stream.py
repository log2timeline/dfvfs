# -*- coding: utf-8 -*-
"""The NTFS data stream implementation."""

from dfvfs.lib import definitions
from dfvfs.vfs import data_stream
from dfvfs.vfs import extent


class NTFSDataStream(data_stream.DataStream):
  """File system data stream that uses pyfsntfs."""

  def __init__(self, file_entry, fsntfs_data_stream):
    """Initializes a NTFS data stream.

    Args:
      file_entry (FileEntry): file entry.
      fsntfs_data_stream (pyfsntfs.data_stream): NTFS data stream.
    """
    super(NTFSDataStream, self).__init__(file_entry)
    self._fsntfs_data_stream = fsntfs_data_stream

    if fsntfs_data_stream:
      self._name = fsntfs_data_stream.name

  def GetExtents(self):
    """Retrieves the extents.

    Returns:
      list[Extent]: the extents of the data stream.
    """
    if not self._fsntfs_data_stream:
      return super(NTFSDataStream, self).GetExtents()

    extents = []
    for extent_index in range(self._fsntfs_data_stream.number_of_extents):
      extent_offset, extent_size, extent_flags = (
          self._fsntfs_data_stream.get_extent(extent_index))

      if extent_flags & 0x1:
        extent_type = definitions.EXTENT_TYPE_SPARSE
      else:
        extent_type = definitions.EXTENT_TYPE_DATA

      data_stream_extent = extent.Extent(
          extent_type=extent_type, offset=extent_offset, size=extent_size)
      extents.append(data_stream_extent)

    return extents

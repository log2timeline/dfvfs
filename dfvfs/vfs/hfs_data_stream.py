# -*- coding: utf-8 -*-
"""The HFS data stream implementation."""

from dfvfs.lib import definitions
from dfvfs.vfs import data_stream
from dfvfs.vfs import extent


class HFSDataStream(data_stream.DataStream):
  """File system data stream that uses pyfshfs."""

  def __init__(self, file_entry, fshfs_data_stream):
    """Initializes a HFS data stream.

    Args:
      file_entry (FileEntry): file entry.
      fshfs_data_stream (pyfshfs.data_stream): HFS data stream.
    """
    super(HFSDataStream, self).__init__(file_entry)
    self._fshfs_data_stream = fshfs_data_stream

    if fshfs_data_stream:
      self._name = 'rsrc'

  def GetExtents(self):
    """Retrieves the extents.

    Returns:
      list[Extent]: the extents of the data stream.
    """
    if not self._fshfs_data_stream:
      return super(HFSDataStream, self).GetExtents()

    extents = []
    for extent_index in range(self._fshfs_data_stream.number_of_extents):
      extent_offset, extent_size, extent_flags = (
          self._fshfs_data_stream.get_extent(extent_index))

      if extent_flags & 0x1:
        extent_type = definitions.EXTENT_TYPE_SPARSE
      else:
        extent_type = definitions.EXTENT_TYPE_DATA

      data_stream_extent = extent.Extent(
          extent_type=extent_type, offset=extent_offset, size=extent_size)
      extents.append(data_stream_extent)

    return extents

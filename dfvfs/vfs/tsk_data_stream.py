# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) data stream implementation."""

import pytsk3

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.vfs import data_stream
from dfvfs.vfs import extent


class TSKDataStream(data_stream.DataStream):
  """File system data stream that uses pytsk3."""

  def __init__(self, file_entry, pytsk_attribute):
    """Initializes a data stream.

    Args:
      file_entry (FileEntry): file entry.
      pytsk_attribute (pytsk3.Attribute): TSK attribute.
    """
    super(TSKDataStream, self).__init__(file_entry)
    self._tsk_attribute = pytsk_attribute

    if pytsk_attribute:
      # The value of the attribute name will be None for the default
      # data stream.
      attribute_name = getattr(pytsk_attribute.info, 'name', None)
      attribute_type = getattr(pytsk_attribute.info, 'type', None)
      if attribute_type == pytsk3.TSK_FS_ATTR_TYPE_HFS_RSRC:
        self._name = 'rsrc'

      elif attribute_name:
        try:
          # pytsk3 returns an UTF-8 encoded byte string.
          self._name = attribute_name.decode('utf8')
        except UnicodeError:
          pass

  def GetExtents(self):
    """Retrieves the extents.

    Returns:
      list[Extent]: the extents of the data stream.

    Raises:
      BackEndError: if pytsk3 returns no file system block size or data stream
          size.
    """
    if not self._tsk_attribute:
      return super(TSKDataStream, self).GetExtents()

    extents = []
    file_system = self._file_entry.GetFileSystem()
    tsk_file_system = file_system.GetFsInfo()
    block_size = getattr(tsk_file_system.info, 'block_size', None)
    if not block_size:
      raise errors.BackEndError('pytsk3 returned no file system block size.')

    data_stream_size = getattr(self._tsk_attribute.info, 'size', None)
    if data_stream_size is None:
      raise errors.BackEndError('pytsk3 returned no data stream size.')

    data_stream_number_of_blocks, remainder = divmod(
        data_stream_size, block_size)
    if remainder:
      data_stream_number_of_blocks += 1

    total_number_of_blocks = 0
    for tsk_attr_run in self._tsk_attribute:
      if tsk_attr_run.flags & pytsk3.TSK_FS_ATTR_RUN_FLAG_SPARSE:
        extent_type = definitions.EXTENT_TYPE_SPARSE
      else:
        extent_type = definitions.EXTENT_TYPE_DATA

      extent_offset = tsk_attr_run.addr * block_size
      extent_size = tsk_attr_run.len

      # Note that the attribute data runs can be larger than the actual
      # allocated size.
      if total_number_of_blocks + extent_size > data_stream_number_of_blocks:
        extent_size = data_stream_number_of_blocks - total_number_of_blocks

      total_number_of_blocks += extent_size
      extent_size *= block_size

      data_stream_extent = extent.Extent(
          extent_type=extent_type, offset=extent_offset, size=extent_size)
      extents.append(data_stream_extent)

      if total_number_of_blocks >= data_stream_number_of_blocks:
        break

    return extents

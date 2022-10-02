# -*- coding: utf-8 -*-
"""dtFabric data format helpers."""

import os

from dtfabric import errors as dtfabric_errors
from dtfabric.runtime import data_maps as dtfabric_data_maps

from dfvfs.lib import errors


class DataFormat(object):
  """Data format."""

  def _ReadData(self, file_object, file_offset, data_size):
    """Reads data.

    Args:
      file_object (dfvfs.FileIO): a file-like object to read.
      file_offset (int): offset of the data relative to the start of
          the file-like object.
      data_size (int): size of the data. The resulting data size much match
          the requested data size so that dtFabric can map the data type
          definitions onto the byte stream.

    Returns:
      bytes: byte stream containing the data.

    Raises:
      FileFormatError: if the data cannot be read.
      ValueError: if the file-like object is missing.
    """
    if not file_object:
      raise ValueError('Missing file-like object.')

    file_object.seek(file_offset, os.SEEK_SET)

    read_error = ''

    try:
      data = file_object.read(data_size)

      if len(data) != data_size:
        read_error = 'missing data'

    except IOError as exception:
      read_error = f'{exception!s}'

    if read_error:
      raise errors.FileFormatError((
          f'Unable to read data at offset: 0x{file_offset:08x} with error: '
          f'{read_error:s}'))

    return data

  def _ReadStructureFromFileObject(
      self, file_object, file_offset, data_type_map):
    """Reads a structure from a file-like object.

    If the data type map has a fixed size this method will read the predefined
    number of bytes from the file-like object. If the data type map has a
    variable size, depending on values in the byte stream, this method will
    continue to read from the file-like object until the data type map can be
    successfully mapped onto the byte stream or until an error occurs.

    Args:
      file_object (dfvfs.FileIO): a file-like object to parse.
      file_offset (int): offset of the structure data relative to the start
          of the file-like object.
      data_type_map (dtfabric.DataTypeMap): data type map of the structure.

    Returns:
      tuple[object, int]: structure values object and data size of
          the structure.

    Raises:
      FileFormatError: if the structure cannot be read.
      ValueError: if file-like object or data type map is missing.
    """
    context = None
    data = b''
    last_data_size = 0

    data_size = data_type_map.GetSizeHint()
    while data_size != last_data_size:
      read_offset = file_offset + last_data_size
      read_size = data_size - last_data_size
      data_segment = self._ReadData(file_object, read_offset, read_size)

      data = b''.join([data, data_segment])

      try:
        context = dtfabric_data_maps.DataTypeMapContext()
        structure_values_object = data_type_map.MapByteStream(
            data, context=context)
        return structure_values_object, data_size

      except dtfabric_errors.ByteStreamTooSmallError:
        pass

      except dtfabric_errors.MappingError as exception:
        raise errors.FileFormatError((
            f'Unable to map {data_type_map.name:s} data at offset: '
            f'0x{file_offset:08x} with error: {exception!s}'))

      last_data_size = data_size
      data_size = data_type_map.GetSizeHint(context=context)

    raise errors.FileFormatError((
        f'Unable to read {data_type_map.name:s} at offset: '
        f'0x{file_offset:08x}'))

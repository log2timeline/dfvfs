# -*- coding: utf-8 -*-
"""dtFabric data format helpers."""

from __future__ import unicode_literals

import os

from dtfabric import errors as dtfabric_errors

from dfvfs.lib import errors


class DataFormat(object):
  """Data format."""

  def _ReadData(self, file_object, file_offset, data_size, description):
    """Reads data.

    Args:
      file_object (FileIO): file-like object.
      file_offset (int): offset of the data relative from the start of
          the file-like object.
      data_size (int): size of the data.
      description (str): description of the data.

    Returns:
      bytes: byte stream containing the data.

    Raises:
      FileFormatError: if the structure cannot be read.
      ValueError: if file-like object or date type map are invalid.
    """
    if not file_object:
      raise ValueError('Invalid file-like object.')

    file_object.seek(file_offset, os.SEEK_SET)

    read_error = ''

    try:
      data = file_object.read(data_size)

      if len(data) != data_size:
        read_error = 'missing data'

    except IOError as exception:
      read_error = '{0!s}'.format(exception)

    if read_error:
      raise errors.FileFormatError((
          'Unable to read {0:s} data at offset: 0x{1:08x} with error: '
          '{2:s}').format(description, file_offset, read_error))

    return data

  def _ReadString(
      self, file_object, file_offset, data_type_map, description):
    """Reads a string.

    Args:
      file_object (FileIO): file-like object.
      file_offset (int): offset of the data relative from the start of
          the file-like object.
      data_type_map (dtfabric.DataTypeMap): data type map of the string.
      description (str): description of the string.

    Returns:
      object: structure values object.

    Raises:
      FileFormatError: if the string cannot be read.
      ValueError: if file-like object or date type map are invalid.
    """
    # pylint: disable=protected-access
    element_data_size = (
        data_type_map._element_data_type_definition.GetByteSize())
    elements_terminator = (
        data_type_map._data_type_definition.elements_terminator)

    byte_stream = []

    element_data = file_object.read(element_data_size)
    byte_stream.append(element_data)
    while element_data and element_data != elements_terminator:
      element_data = file_object.read(element_data_size)
      byte_stream.append(element_data)

    byte_stream = b''.join(byte_stream)

    return self._ReadStructureFromByteStream(
        byte_stream, file_offset, data_type_map, description)

  def _ReadStructure(
      self, file_object, file_offset, data_size, data_type_map, description):
    """Reads a structure.

    Args:
      file_object (FileIO): file-like object.
      file_offset (int): offset of the data relative from the start of
          the file-like object.
      data_size (int): data size of the structure.
      data_type_map (dtfabric.DataTypeMap): data type map of the structure.
      description (str): description of the structure.

    Returns:
      object: structure values object.

    Raises:
      FileFormatError: if the structure cannot be read.
      ValueError: if file-like object or date type map are invalid.
    """
    data = self._ReadData(file_object, file_offset, data_size, description)

    return self._ReadStructureFromByteStream(
        data, file_offset, data_type_map, description)

  def _ReadStructureFromByteStream(
      self, byte_stream, file_offset, data_type_map, description, context=None):
    """Reads a structure from a byte stream.

    Args:
      byte_stream (bytes): byte stream.
      file_offset (int): offset of the data relative from the start of
          the file-like object.
      data_type_map (dtfabric.DataTypeMap): data type map of the structure.
      description (str): description of the structure.
      context (Optional[dtfabric.DataTypeMapContext]): data type map context.

    Returns:
      object: structure values object.

    Raises:
      FileFormatError: if the structure cannot be read.
      ValueError: if file-like object or date type map are invalid.
    """
    if not byte_stream:
      raise ValueError('Invalid byte stream.')

    if not data_type_map:
      raise ValueError('Invalid data type map.')

    try:
      return data_type_map.MapByteStream(byte_stream, context=context)
    except dtfabric_errors.MappingError as exception:
      raise errors.FileFormatError((
          'Unable to map {0:s} data at offset: 0x{1:08x} with error: '
          '{2!s}').format(description, file_offset, exception))

# -*- coding: utf-8 -*-
"""The encoded stream file-like object implementation."""

from __future__ import unicode_literals

import os

from dfvfs.encoding import manager as encoding_manager
from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.resolver import resolver


class EncodedStream(file_io.FileIO):
  """File-like object of a encoded stream."""

  # The size of the encoded data buffer.
  _ENCODED_DATA_BUFFER_SIZE = 8 * 1024 * 1024

  def __init__(
      self, resolver_context, encoding_method=None, file_object=None):
    """Initializes a file-like object.

    If the file-like object is chained do not separately use the parent
    file-like object.

    Args:
      resolver_context (Context): resolver context.
      encoding_method (Optional[str]): method used to the encode the data.
      file_object (Optional[file]): parent file-like object.

    Raises:
      ValueError: if file_object provided but encoding_method is not.
    """
    if file_object is not None and encoding_method is None:
      raise ValueError(
          'File-like object provided without corresponding encoding method.')

    super(EncodedStream, self).__init__(resolver_context)
    self._current_offset = 0
    self._decoded_data = b''
    self._decoded_data_offset = 0
    self._decoded_data_size = 0
    self._decoded_stream_size = None
    self._decoder = None
    self._encoded_data = b''
    self._encoding_method = encoding_method
    self._file_object = file_object
    self._file_object_set_in_init = bool(file_object)
    self._realign_offset = True

  def _Close(self):
    """Closes the file-like object.

    If the file-like object was passed in the init function
    the encoded stream file-like object does not control
    the file-like object and should not actually close it.
    """
    if not self._file_object_set_in_init:
      self._file_object.close()
      self._file_object = None

    self._decoder = None
    self._decoded_data = b''
    self._encoded_data = b''

  def _GetDecoder(self):
    """Retrieves the decoder.

    Returns:
      Decoder: decoder.
    """
    return encoding_manager.EncodingManager.GetDecoder(self._encoding_method)

  def _GetDecodedStreamSize(self):
    """Retrieves the decoded stream size.

    Returns:
      int: decoded stream size.
    """
    self._file_object.seek(0, os.SEEK_SET)

    self._decoder = self._GetDecoder()
    self._decoded_data = b''

    encoded_data_offset = 0
    encoded_data_size = self._file_object.get_size()
    decoded_stream_size = 0

    while encoded_data_offset < encoded_data_size:
      read_count = self._ReadEncodedData(self._ENCODED_DATA_BUFFER_SIZE)
      if read_count == 0:
        break

      encoded_data_offset += read_count
      decoded_stream_size += self._decoded_data_size

    return decoded_stream_size

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object.

    Args:
      path_spec (PathSpec): path specification.
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._file_object_set_in_init and not path_spec:
      raise ValueError('Missing path specification.')

    if not self._file_object_set_in_init:
      if not path_spec.HasParent():
        raise errors.PathSpecError(
            'Unsupported path specification without parent.')

      self._encoding_method = getattr(path_spec, 'encoding_method', None)

      if self._encoding_method is None:
        raise errors.PathSpecError(
            'Path specification missing encoding method.')

      self._file_object = resolver.Resolver.OpenFileObject(
          path_spec.parent, resolver_context=self._resolver_context)

  def _AlignDecodedDataOffset(self, decoded_data_offset):
    """Aligns the encoded file with the decoded data offset.

    Args:
      decoded_data_offset (int): decoded data offset.
    """
    self._file_object.seek(0, os.SEEK_SET)

    self._decoder = self._GetDecoder()
    self._decoded_data = b''

    encoded_data_offset = 0
    encoded_data_size = self._file_object.get_size()

    while encoded_data_offset < encoded_data_size:
      read_count = self._ReadEncodedData(self._ENCODED_DATA_BUFFER_SIZE)
      if read_count == 0:
        break

      encoded_data_offset += read_count

      if decoded_data_offset < self._decoded_data_size:
        self._decoded_data_offset = decoded_data_offset
        break

      decoded_data_offset -= self._decoded_data_size

  def _ReadEncodedData(self, read_size):
    """Reads encoded data from the file-like object.

    Args:
      read_size (int): number of bytes of encoded data to read.

    Returns:
      int: number of bytes of encoded data read.
    """
    encoded_data = self._file_object.read(read_size)

    read_count = len(encoded_data)

    self._encoded_data = b''.join([self._encoded_data, encoded_data])

    self._decoded_data, self._encoded_data = (
        self._decoder.Decode(self._encoded_data))

    self._decoded_data_size = len(self._decoded_data)

    return read_count

  def SetDecodedStreamSize(self, decoded_stream_size):
    """Sets the decoded stream size.

    This function is used to set the decoded stream size if it can be
    determined separately.

    Args:
      decoded_stream_size (int): size of the decoded stream in bytes.

    Raises:
      IOError: if the file-like object is already open.
      OSError: if the file-like object is already open.
      ValueError: if the decoded stream size is invalid.
    """
    if self._is_open:
      raise IOError('Already open.')

    if decoded_stream_size < 0:
      raise ValueError((
          'Invalid decoded stream size: {0:d} value out of '
          'bounds.').format(decoded_stream_size))

    self._decoded_stream_size = decoded_stream_size

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.
  # pylint: disable=invalid-name

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

    The function will read a byte string of the specified size or
    all of the remaining data if no size was specified.

    Args:
      size (Optional[int]): number of bytes to read, where None is all
          remaining data.

    Returns:
      bytes: data read.

    Raises:
      IOError: if the read failed.
      OSError: if the read failed.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    if self._current_offset < 0:
      raise IOError(
          'Invalid current offset: {0:d} value less than zero.'.format(
              self._current_offset))

    if self._decoded_stream_size is None:
      self._decoded_stream_size = self._GetDecodedStreamSize()

    if self._decoded_stream_size < 0:
      raise IOError('Invalid decoded stream size.')

    if self._current_offset >= self._decoded_stream_size:
      return b''

    if self._realign_offset:
      self._AlignDecodedDataOffset(self._current_offset)
      self._realign_offset = False

    if size is None:
      size = self._decoded_stream_size
    if self._current_offset + size > self._decoded_stream_size:
      size = self._decoded_stream_size - self._current_offset

    decoded_data = b''

    if size == 0:
      return decoded_data

    while size > self._decoded_data_size:
      decoded_data = b''.join([
          decoded_data,
          self._decoded_data[self._decoded_data_offset:]])

      remaining_decoded_data_size = (
          self._decoded_data_size - self._decoded_data_offset)

      self._current_offset += remaining_decoded_data_size
      size -= remaining_decoded_data_size

      if self._current_offset >= self._decoded_stream_size:
        break

      read_count = self._ReadEncodedData(self._ENCODED_DATA_BUFFER_SIZE)
      self._decoded_data_offset = 0
      if read_count == 0:
        break

    if size > 0:
      slice_start_offset = self._decoded_data_offset
      slice_end_offset = slice_start_offset + size

      decoded_data = b''.join([
          decoded_data,
          self._decoded_data[slice_start_offset:slice_end_offset]])

      self._decoded_data_offset += size
      self._current_offset += size

    return decoded_data

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks to an offset within the file-like object.

    Args:
      offset (int): offset to seek to.
      whence (Optional(int)): value that indicates whether offset is an absolute
          or relative position within the file.

    Raises:
      IOError: if the seek failed.
      OSError: if the seek failed.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    if self._current_offset < 0:
      raise IOError(
          'Invalid current offset: {0:d} value less than zero.'.format(
              self._current_offset))

    if whence == os.SEEK_CUR:
      offset += self._current_offset

    elif whence == os.SEEK_END:
      if self._decoded_stream_size is None:
        self._decoded_stream_size = self._GetDecodedStreamSize()
        if self._decoded_stream_size is None:
          raise IOError('Invalid decoded stream size.')

      offset += self._decoded_stream_size

    elif whence != os.SEEK_SET:
      raise IOError('Unsupported whence.')

    if offset < 0:
      raise IOError('Invalid offset value less than zero.')

    if offset != self._current_offset:
      self._current_offset = offset
      self._realign_offset = True

  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: current offset in the decoded stream.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    return self._current_offset

  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size of the decoded stream.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    if self._decoded_stream_size is None:
      self._decoded_stream_size = self._GetDecodedStreamSize()

    return self._decoded_stream_size

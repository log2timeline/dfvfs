# -*- coding: utf-8 -*-
"""The encrypted stream file-like object implementation."""

import os

from dfvfs.encryption import manager as encryption_manager
from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.resolver import resolver


class EncryptedStream(file_io.FileIO):
  """Class that implements a file-like object of a encrypted stream."""

  # The size of the encrypted data buffer.
  _ENCRYPTED_DATA_BUFFER_SIZE = 8 * 1024 * 1024

  def __init__(
      self, resolver_context, encryption_method=None, file_object=None):
    """Initializes the file-like object.

    If the file-like object is chained do not separately use the parent
    file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      encryption_method: optional method used to the encrypt the data.
      file_object: optional parent file-like object.

    Raises:
      ValueError: if file_object provided but encryption_method is not.
    """
    if file_object is not None and encryption_method is None:
      raise ValueError(
          u'File-like object provided without corresponding encryption method.')

    super(EncryptedStream, self).__init__(resolver_context)
    self._current_offset = 0
    self._decrypted_data = b''
    self._decrypted_data_offset = 0
    self._decrypted_data_size = 0
    self._decrypted_stream_size = None
    self._decrypter = None
    self._encrypted_data = b''
    self._encryption_method = encryption_method
    self._file_object = file_object
    self._path_spec = None
    self._realign_offset = True

    if file_object:
      self._file_object_set_in_init = True
    else:
      self._file_object_set_in_init = False

  def _Close(self):
    """Closes the file-like object.

    If the file-like object was passed in the init function
    the encrypted stream file-like object does not control
    the file-like object and should not actually close it.
    """
    if not self._file_object_set_in_init:
      self._file_object.close()
      self._file_object = None

    self._decrypter = None
    self._decrypted_data = b''
    self._encrypted_data = b''

  def _GetDecrypter(self):
    """Retrieves a decrypter.

    Returns:
      A decrypter object (instance of encryptions.Decrypter).

    Raises:
      IOError: if the decrypter cannot be initialized.
    """
    try:
      credentials = resolver.Resolver.key_chain.GetCredentials(self._path_spec)
      return encryption_manager.EncryptionManager.GetDecrypter(
          self._encryption_method, **credentials)
    except ValueError as exception:
      raise IOError(exception)

  def _GetDecryptedStreamSize(self):
    """Retrieves the decrypted stream size."""
    self._file_object.seek(0, os.SEEK_SET)

    self._decrypter = self._GetDecrypter()
    self._decrypted_data = b''

    encrypted_data_offset = 0
    encrypted_data_size = self._file_object.get_size()
    decrypted_stream_size = 0

    while encrypted_data_offset < encrypted_data_size:
      read_count = self._ReadEncryptedData(self._ENCRYPTED_DATA_BUFFER_SIZE)
      if read_count == 0:
        break

      encrypted_data_offset += read_count
      decrypted_stream_size += self._decrypted_data_size

    return decrypted_stream_size

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object.

    Args:
      path_spec: optional path specification (instance of PathSpec).
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._file_object_set_in_init and not path_spec:
      raise ValueError(u'Missing path specification.')

    if not self._file_object_set_in_init:
      if not path_spec.HasParent():
        raise errors.PathSpecError(
            u'Unsupported path specification without parent.')

      self._encryption_method = getattr(path_spec, u'encryption_method', None)

      if self._encryption_method is None:
        raise errors.PathSpecError(
            u'Path specification missing encryption method.')

      self._file_object = resolver.Resolver.OpenFileObject(
          path_spec.parent, resolver_context=self._resolver_context)

    self._path_spec = path_spec

  def _AlignDecryptedDataOffset(self, decrypted_data_offset):
    """Aligns the encrypted file with the decrypted data offset.

    Args:
      decrypted_data_offset: the decrypted data offset.
    """
    self._file_object.seek(0, os.SEEK_SET)

    self._decrypter = self._GetDecrypter()
    self._decrypted_data = b''

    encrypted_data_offset = 0
    encrypted_data_size = self._file_object.get_size()

    while encrypted_data_offset < encrypted_data_size:
      read_count = self._ReadEncryptedData(self._ENCRYPTED_DATA_BUFFER_SIZE)
      if read_count == 0:
        break

      encrypted_data_offset += read_count

      if decrypted_data_offset < self._decrypted_data_size:
        self._decrypted_data_offset = decrypted_data_offset
        break

      decrypted_data_offset -= self._decrypted_data_size

  def _ReadEncryptedData(self, read_size):
    """Reads encrypted data from the file-like object.

    Args:
      read_size: the number of bytes of encrypted data to read.

    Returns:
      The number of bytes of encrypted data read.
    """
    encrypted_data = self._file_object.read(read_size)

    read_count = len(encrypted_data)

    self._encrypted_data = b''.join([self._encrypted_data, encrypted_data])

    self._decrypted_data, self._encrypted_data = (
        self._decrypter.Decrypt(self._encrypted_data))

    self._decrypted_data_size = len(self._decrypted_data)

    return read_count

  def SetDecryptedStreamSize(self, decrypted_stream_size):
    """Sets the decrypted stream size.

    This function is used to set the decrypted stream size if it can be
    determined separately.

    Args:
      decrypted_stream_size: the size of the decrypted stream in bytes.

    Raises:
      IOError: if the file-like object is already open.
      ValueError: if the decrypted stream size is invalid.
    """
    if self._is_open:
      raise IOError(u'Already open.')

    if decrypted_stream_size < 0:
      raise ValueError((
          u'Invalid decrypted stream size: {0:d} value out of '
          u'bounds.').format(decrypted_stream_size))

    self._decrypted_stream_size = decrypted_stream_size

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

    The function will read a byte string of the specified size or
    all of the remaining data if no size was specified.

    Args:
      size: Optional integer value containing the number of bytes to read.
            Default is all remaining data (None).

    Returns:
      A byte string containing the data read.

    Raises:
      IOError: if the read failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if self._current_offset < 0:
      raise IOError(
          u'Invalid current offset: {0:d} value less than zero.'.format(
              self._current_offset))

    if self._decrypted_stream_size is None:
      self._decrypted_stream_size = self._GetDecryptedStreamSize()

    if self._decrypted_stream_size < 0:
      raise IOError(u'Invalid decrypted stream size.')

    if self._current_offset >= self._decrypted_stream_size:
      return b''

    if self._realign_offset:
      self._AlignDecryptedDataOffset(self._current_offset)
      self._realign_offset = False

    if size is None:
      size = self._decrypted_stream_size
    if self._current_offset + size > self._decrypted_stream_size:
      size = self._decrypted_stream_size - self._current_offset

    decrypted_data = b''

    if size == 0:
      return decrypted_data

    while size > self._decrypted_data_size:
      decrypted_data = b''.join([
          decrypted_data,
          self._decrypted_data[self._decrypted_data_offset:]])

      remaining_decrypted_data_size = (
          self._decrypted_data_size - self._decrypted_data_offset)

      self._current_offset += remaining_decrypted_data_size
      size -= remaining_decrypted_data_size

      if self._current_offset >= self._decrypted_stream_size:
        break

      read_count = self._ReadEncryptedData(self._ENCRYPTED_DATA_BUFFER_SIZE)
      self._decrypted_data_offset = 0
      if read_count == 0:
        break

    if size > 0:
      slice_start_offset = self._decrypted_data_offset
      slice_end_offset = slice_start_offset + size

      decrypted_data = b''.join([
          decrypted_data,
          self._decrypted_data[slice_start_offset:slice_end_offset]])

      self._decrypted_data_offset += size
      self._current_offset += size

    return decrypted_data

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks an offset within the file-like object.

    Args:
      offset: the offset to seek.
      whence: optional value that indicates whether offset is an absolute
              or relative position within the file.

    Raises:
      IOError: if the seek failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if self._current_offset < 0:
      raise IOError(
          u'Invalid current offset: {0:d} value less than zero.'.format(
              self._current_offset))

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self._decrypted_stream_size
    elif whence != os.SEEK_SET:
      raise IOError(u'Unsupported whence.')
    if offset < 0:
      raise IOError(u'Invalid offset value less than zero.')

    if offset != self._current_offset:
      self._current_offset = offset
      self._realign_offset = True

  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    return self._current_offset

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if self._decrypted_stream_size is None:
      self._decrypted_stream_size = self._GetDecryptedStreamSize()

    return self._decrypted_stream_size

# -*- coding: utf-8 -*-
"""The encrypted stream file-like object implementation."""

import os

from dfvfs.encryption import manager as encryption_manager
from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.resolver import resolver


class EncryptedStream(file_io.FileIO):
  """File input/output (IO) object of a encrypted stream."""

  # The size of the encrypted data buffer.
  _ENCRYPTED_DATA_BUFFER_SIZE = 8 * 1024 * 1024

  def __init__(self, resolver_context, path_spec):
    """Initializes a file input/output (IO) object.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(EncryptedStream, self).__init__(resolver_context, path_spec)
    self._current_offset = 0
    self._decrypted_data = b''
    self._decrypted_data_offset = 0
    self._decrypted_data_size = 0
    self._decrypted_stream_size = None
    self._decrypter = None
    self._encrypted_data = b''
    self._encryption_method = None
    self._file_object = None
    self._realign_offset = True

  def _Close(self):
    """Closes the file-like object.

    If the file-like object was passed in the init function
    the encrypted stream file-like object does not control
    the file-like object and should not actually close it.
    """
    self._decrypter = None
    self._decrypted_data = b''
    self._encrypted_data = b''
    self._file_object = None

  def _GetDecrypter(self):
    """Retrieves a decrypter.

    Returns:
      Decrypter: decrypter.

    Raises:
      IOError: if the decrypter cannot be initialized.
      OSError: if the decrypter cannot be initialized.
    """
    resolver.Resolver.key_chain.ExtractCredentialsFromPathSpec(self._path_spec)

    try:
      credentials = resolver.Resolver.key_chain.GetCredentials(self._path_spec)
      return encryption_manager.EncryptionManager.GetDecrypter(
          self._encryption_method, **credentials)
    except ValueError as exception:
      raise IOError(exception)

  def _GetDecryptedStreamSize(self):
    """Retrieves the decrypted stream size.

    Returns:
      int: decrypted stream size.
    """
    self._decrypter = self._GetDecrypter()
    self._decrypted_data = b''
    self._decrypted_data_size = 0

    self._file_object.seek(0, os.SEEK_SET)
    self._encrypted_data = b''

    decrypted_stream_size = 0

    read_count = self._ReadEncryptedData(self._ENCRYPTED_DATA_BUFFER_SIZE)
    while read_count > 0:
      decrypted_stream_size += self._decrypted_data_size

      read_count = self._ReadEncryptedData(self._ENCRYPTED_DATA_BUFFER_SIZE)

    self._ReadEncryptedData(0, finalize=True)
    decrypted_stream_size += self._decrypted_data_size

    return decrypted_stream_size

  def _Open(self, mode='rb'):
    """Opens the file-like object.

    Args:
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    self._encryption_method = getattr(
        self._path_spec, 'encryption_method', None)

    if self._encryption_method is None:
      raise errors.PathSpecError(
          'Path specification missing encryption method.')

    self._file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)

  def _AlignDecryptedDataOffset(self, decrypted_data_offset):
    """Aligns the encrypted file with the decrypted data offset.

    Args:
      decrypted_data_offset (int): decrypted data offset.
    """
    self._decrypter = self._GetDecrypter()
    self._decrypted_data = b''
    self._decrypted_data_size = 0

    self._file_object.seek(0, os.SEEK_SET)
    self._encrypted_data = b''

    read_count = self._ReadEncryptedData(self._ENCRYPTED_DATA_BUFFER_SIZE)
    while read_count > 0:
      if decrypted_data_offset < self._decrypted_data_size:
        self._decrypted_data_offset = decrypted_data_offset
        return

      decrypted_data_offset -= self._decrypted_data_size

      read_count = self._ReadEncryptedData(self._ENCRYPTED_DATA_BUFFER_SIZE)

    self._ReadEncryptedData(0, finalize=True)
    self._decrypted_data_offset = decrypted_data_offset

  def _ReadEncryptedData(self, read_size, finalize=False):
    """Reads encrypted data from the file-like object.

    Args:
      read_size (int): number of bytes of encrypted data to read.
      finalize (Optional[bool]): True if the end of data has been reached and
          the cipher context should be finalized.

    Returns:
      int: number of bytes of encrypted data read.
    """
    encrypted_data = self._file_object.read(read_size)

    read_count = len(encrypted_data)

    self._encrypted_data = b''.join([self._encrypted_data, encrypted_data])

    self._decrypted_data, self._encrypted_data = self._decrypter.Decrypt(
        self._encrypted_data, finalize=finalize)

    self._decrypted_data_size = len(self._decrypted_data)

    return read_count

  def SetDecryptedStreamSize(self, decrypted_stream_size):
    """Sets the decrypted stream size.

    This function is used to set the decrypted stream size if it can be
    determined separately.

    Args:
      decrypted_stream_size (int): size of the decrypted stream in bytes.

    Raises:
      IOError: if the file-like object is already open.
      OSError: if the file-like object is already open.
      ValueError: if the decrypted stream size is invalid.
    """
    if self._is_open:
      raise IOError('Already open.')

    if decrypted_stream_size < 0:
      raise ValueError((
          f'Invalid decrypted stream size: {decrypted_stream_size:d} value '
          f'out of bounds.'))

    self._decrypted_stream_size = decrypted_stream_size

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
      raise IOError((
          f'Invalid current offset: {self._current_offset:d} value less than '
          f'zero.'))

    if self._decrypted_stream_size is None:
      self._decrypted_stream_size = self._GetDecryptedStreamSize()

    if self._decrypted_stream_size < 0:
      raise IOError('Invalid decrypted stream size.')

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
      if read_count == 0:
        self._ReadEncryptedData(0, finalize=True)

      self._decrypted_data_offset = 0

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
    """Seeks to an offset within the file-like object.

    Args:
      offset (int): offset to seek.
      whence (Optional[int]): value that indicates whether offset is an
          absolute or relative position within the file.

    Raises:
      IOError: if the seek failed.
      OSError: if the seek failed.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    if self._current_offset < 0:
      raise IOError((
          f'Invalid current offset: {self._current_offset:d} value less than '
          f'zero.'))

    if whence == os.SEEK_CUR:
      offset += self._current_offset

    elif whence == os.SEEK_END:
      if self._decrypted_stream_size is None:
        self._decrypted_stream_size = self._GetDecryptedStreamSize()
        if self._decrypted_stream_size is None:
          raise IOError('Invalid decrypted stream size.')

      offset += self._decrypted_stream_size

    elif whence != os.SEEK_SET:
      raise IOError('Unsupported whence.')

    if offset < 0:
      raise IOError('Invalid offset value less than zero.')

    if offset != self._current_offset:
      self._current_offset = offset
      self._realign_offset = True

  def get_offset(self):
    """Retrieves the current offset into the decrypted stream.

    Returns:
      int: current offset into the decrypted stream.

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
      int: size of the decrypted stream.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    if self._decrypted_stream_size is None:
      self._decrypted_stream_size = self._GetDecryptedStreamSize()

    return self._decrypted_stream_size

# -*- coding: utf-8 -*-
"""The gzip file-like object."""

from __future__ import unicode_literals

import collections
import os

from dfvfs.file_io import file_io
from dfvfs.lib import errors
from dfvfs.lib import gzipfile
from dfvfs.resolver import resolver


class GzipFile(file_io.FileIO):
  """File-like object of a gzip file.

  The gzip file format is defined in RFC1952: http://www.zlib.org/rfc-gzip.html

  Attributes:
    uncompressed_data_size (int): total size of the decompressed data stored
        in the gzip file.
  """

  def __init__(self, resolver_context):
    """Initializes a file-like object.

    Args:
      resolver_context (Context): resolver context.

    Raises:
      ValueError: when file_object is set.
    """
    super(GzipFile, self).__init__(resolver_context)
    self._compressed_data_size = -1
    self._current_offset = 0
    self._gzip_file_object = None
    self._members_by_end_offset = collections.OrderedDict()

    self.uncompressed_data_size = 0

  @property
  def original_filenames(self):
    """list(str): The original filenames stored in the gzip file."""
    return [member.original_filename
            for member in self._members_by_end_offset.values()]

  @property
  def modification_times(self):
    """list(int): The modification times stored in the gzip file."""
    return [member.modification_time
            for member in self._members_by_end_offset.values()]

  @property
  def operating_systems(self):
    """list(int): The operating system values stored in the gzip file."""
    return [member.operating_system
            for member in self._members_by_end_offset.values()]

  @property
  def comments(self):
    """list(str): The comments in the gzip file."""
    return [member.comment
            for member in self._members_by_end_offset.values()]

  def _GetMemberForOffset(self, offset):
    """Finds the member whose data includes the provided offset.

    Args:
      offset (int): offset in the uncompressed data to find the
          containing member for.

    Returns:
      gzipfile.GzipMember: gzip file member or None if not available.

    Raises:
      ValueError: if the provided offset is outside of the bounds of the
          uncompressed data.
    """
    if offset < 0 or offset >= self.uncompressed_data_size:
      raise ValueError('Offset {0:d} is larger than file size {1:d}.'.format(
          offset, self.uncompressed_data_size))

    for end_offset, member in self._members_by_end_offset.items():
      if offset < end_offset:
        return member

    return None

  def seek(self, offset, whence=os.SEEK_SET):
    """Seeks to an offset within the file-like object.

    Args:
      offset (int): offset to seek to.
      whence (Optional(int)): value that indicates whether offset is an absolute
          or relative position within the file.

    Raises:
      IOError: if the seek failed or the file has not been opened.
      OSError: if the seek failed or the file has not been opened.
    """
    if not self._gzip_file_object:
      raise IOError('Not opened.')

    if whence == os.SEEK_CUR:
      offset += self._current_offset
    elif whence == os.SEEK_END:
      offset += self.uncompressed_data_size
    elif whence != os.SEEK_SET:
      raise IOError('Unsupported whence.')

    if offset < 0:
      raise IOError('Invalid offset value less than zero.')

    self._current_offset = offset

  def read(self, size=None):
    """Reads a byte string from the gzip file at the current offset.

    The function will read a byte string up to the specified size or
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
    data = b''
    while ((size and len(data) < size) and
           self._current_offset < self.uncompressed_data_size):
      member = self._GetMemberForOffset(self._current_offset)
      member_offset = self._current_offset - member.uncompressed_data_offset

      data_read = member.ReadAtOffset(member_offset, size)
      if not data_read:
        break

      self._current_offset += len(data_read)
      data = b''.join([data, data_read])

    return data

  def get_offset(self):
    """Retrieves the current offset into the file-like object.

    Returns:
      int: current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._gzip_file_object:
      raise IOError('Not opened.')
    return self._current_offset

  def get_size(self):
    """Retrieves the size of the file-like object.

    Returns:
      int: size of the file-like object data.

    Raises:
      IOError: if the file-like object has not been opened.
      OSError: if the file-like object has not been opened.
    """
    if not self._gzip_file_object:
      raise IOError('Not opened.')
    return self.uncompressed_data_size

  def _Close(self):
    """Closes the file-like object."""
    self._members_by_end_offset = []
    if self._gzip_file_object:
      self._gzip_file_object.close()

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec (Optional[PathSpec]): path specification.
      mode (Optional[str]): file access mode.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      OSError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec:
      raise ValueError('Missing path specification.')

    if not path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    self._gzip_file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)
    file_size = self._gzip_file_object.get_size()

    self._gzip_file_object.seek(0, os.SEEK_SET)

    uncompressed_data_offset = 0
    next_member_offset = 0

    while next_member_offset < file_size:
      member = gzipfile.GzipMember(
          self._gzip_file_object, next_member_offset, uncompressed_data_offset)
      uncompressed_data_offset = (
          uncompressed_data_offset + member.uncompressed_data_size)
      self._members_by_end_offset[uncompressed_data_offset] = member
      self.uncompressed_data_size += member.uncompressed_data_size
      next_member_offset = member.member_end_offset

# -*- coding: utf-8 -*-
"""The NTFS file-like object implementation."""

import os

from dfvfs import dependencies
from dfvfs.file_io import file_io
from dfvfs.resolver import resolver


dependencies.CheckModuleVersion(u'pyfsntfs')


class NTFSFile(file_io.FileIO):
  """Class that implements a file-like object using pyfsntfs."""

  def __init__(self, resolver_context):
    """Initializes the file-like object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(NTFSFile, self).__init__(resolver_context)
    self._file_system = None
    self._fsntfs_data_stream = None
    self._fsntfs_file_entry = None

  def _Close(self):
    """Closes the file-like object."""
    self._fsntfs_data_stream = None
    self._fsntfs_file_entry = None

    self._file_system.Close()
    self._file_system = None

  def _Open(self, path_spec=None, mode='rb'):
    """Opens the file-like object defined by path specification.

    Args:
      path_spec: optional path specification (instance of PathSpec).
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file-like object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec:
      raise ValueError(u'Missing path specification.')

    data_stream = getattr(path_spec, u'data_stream', None)

    self._file_system = resolver.Resolver.OpenFileSystem(
        path_spec, resolver_context=self._resolver_context)

    file_entry = self._file_system.GetFileEntryByPathSpec(path_spec)
    if not file_entry:
      raise IOError(u'Unable to open file entry.')

    fsntfs_data_stream = None
    fsntfs_file_entry = file_entry.GetNTFSFileEntry()
    if not fsntfs_file_entry:
      raise IOError(u'Unable to open NTFS file entry.')

    if data_stream:
      fsntfs_data_stream = fsntfs_file_entry.get_alternate_data_stream_by_name(
          data_stream)
      if not fsntfs_data_stream:
        raise IOError(u'Unable to open data stream: {0:s}.'.format(
            data_stream))

    elif not fsntfs_file_entry.has_default_data_stream():
      raise IOError(u'Missing default data stream.')

    self._fsntfs_data_stream = fsntfs_data_stream
    self._fsntfs_file_entry = fsntfs_file_entry

  # Note: that the following functions do not follow the style guide
  # because they are part of the file-like object interface.

  def read(self, size=None):
    """Reads a byte string from the file-like object at the current offset.

    The function will read a byte string of the specified size or
    all of the remaining data if no size was specified.

    Args:
      size: optional integer value containing the number of bytes to read.
            Default is all remaining data (None).

    Returns:
      A byte string containing the data read.

    Raises:
      IOError: if the read failed.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if self._fsntfs_data_stream:
      return self._fsntfs_data_stream.read(size=size)
    return self._fsntfs_file_entry.read(size=size)

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

    if self._fsntfs_data_stream:
      self._fsntfs_data_stream.seek(offset, whence)
    else:
      self._fsntfs_file_entry.seek(offset, whence)

  def get_offset(self):
    """Returns the current offset into the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if self._fsntfs_data_stream:
      return self._fsntfs_data_stream.get_offset()
    return self._fsntfs_file_entry.get_offset()

  def get_size(self):
    """Returns the size of the file-like object.

    Raises:
      IOError: if the file-like object has not been opened.
    """
    if not self._is_open:
      raise IOError(u'Not opened.')

    if self._fsntfs_data_stream:
      return self._fsntfs_data_stream.get_size()
    return self._fsntfs_file_entry.get_size()

# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) file system interface."""

from __future__ import unicode_literals

import abc


class FileSystem(object):
  """Virtual file system interface."""

  # Note that redundant-returns-doc is broken for pylint 1.7.x for abstract
  # methods
  # pylint: disable=redundant-returns-doc

  LOCATION_ROOT = '/'
  PATH_SEPARATOR = '/'

  def __init__(self, resolver_context):
    """Initializes a file system.

    Args:
      resolver_context (Context): resolver context.

    Raises:
      ValueError: if a derived file system class does not define a type
          indicator.
    """
    super(FileSystem, self).__init__()
    self._is_cached = False
    self._is_open = False
    self._path_spec = None
    self._resolver_context = resolver_context

    if not getattr(self, 'TYPE_INDICATOR', None):
      raise ValueError('Missing type indicator.')

  @property
  def type_indicator(self):
    """str: type indicator."""
    # pylint: disable=no-member
    return self.TYPE_INDICATOR

  @abc.abstractmethod
  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """

  @abc.abstractmethod
  def _Open(self, path_spec, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      path_spec (PathSpec): a path specification.
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """

  def BasenamePath(self, path):
    """Determines the basename of the path.

    Args:
      path (str): path.

    Returns:
      str: basename of the path.
    """
    if path.endswith(self.PATH_SEPARATOR):
      path = path[:-1]
    _, _, basename = path.rpartition(self.PATH_SEPARATOR)
    return basename

  def Close(self):
    """Closes the file system.

    Raises:
      IOError: if the file system object was not opened or the close failed.
      OSError: if the file system object was not opened or the close failed.
    """
    if not self._is_open:
      raise IOError('Not opened.')

    if not self._is_cached:
      close_file_system = True
    elif self._resolver_context.ReleaseFileSystem(self):
      self._is_cached = False
      close_file_system = True
    else:
      close_file_system = False

    if close_file_system:
      self._Close()
      self._is_open = False
      self._path_spec = None

  def DirnamePath(self, path):
    """Determines the directory name of the path.

    The file system root is represented by an empty string.

    Args:
      path (str): path.

    Returns:
      str: directory name of the path or None.
    """
    if path.endswith(self.PATH_SEPARATOR):
      path = path[:-1]
    if not path:
      return None

    dirname, _, _ = path.rpartition(self.PATH_SEPARATOR)
    return dirname

  @abc.abstractmethod
  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      bool: True if the file entry exists.
    """

  def GetDataStreamByPathSpec(self, path_spec):
    """Retrieves a data stream for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      DataStream: a data stream or None if not available.
    """
    file_entry = self.GetFileEntryByPathSpec(path_spec)
    if not file_entry:
      return None

    data_stream_name = getattr(path_spec, 'data_stream', None)
    return file_entry.GetDataStream(data_stream_name)

  @abc.abstractmethod
  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      FileEntry: a file entry or None if not available.
    """

  def GetFileObjectByPathSpec(self, path_spec):
    """Retrieves a file-like object for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      FileIO: a file-like object or None if not available.
    """
    file_entry = self.GetFileEntryByPathSpec(path_spec)
    if not file_entry:
      return None

    return file_entry.GetFileObject()

  def GetPathSegmentAndSuffix(self, base_path, path):
    """Determines the path segment and suffix of the path.

    None is returned if the path does not start with the base path and
    an empty string if the path exactly matches the base path.

    Args:
      base_path (str): base path.
      path (str): path.

    Returns:
      tuple[str, str]: path segment and suffix string.
    """
    if path is None or base_path is None or not path.startswith(base_path):
      return None, None

    path_index = len(base_path)
    if base_path and not base_path.endswith(self.PATH_SEPARATOR):
      path_index += 1

    if path_index == len(path):
      return '', ''

    path_segment, _, suffix = path[path_index:].partition(self.PATH_SEPARATOR)
    return path_segment, suffix

  @abc.abstractmethod
  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      FileEntry: a file entry or None if not available.
    """

  def JoinPath(self, path_segments):
    """Joins the path segments into a path.

    Args:
      path_segments (list[str]): path segments.

    Returns:
      str: joined path segments prefixed with the path separator.
    """
    # This is an optimized way to combine the path segments into a single path
    # and combine multiple successive path separators to one.

    # Split all the path segments based on the path (segment) separator.
    path_segments = [
        segment.split(self.PATH_SEPARATOR) for segment in path_segments]

    # Flatten the sublists into one list.
    path_segments = [
        element for sublist in path_segments for element in sublist]

    # Remove empty path segments.
    path_segments = list(filter(None, path_segments))

    return '{0:s}{1:s}'.format(
        self.PATH_SEPARATOR, self.PATH_SEPARATOR.join(path_segments))

  def Open(self, path_spec, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      path_spec (PathSpec): a path specification.
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object was already opened or the open failed.
      OSError: if the file system object was already opened or the open failed.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification or mode is invalid.
    """
    if self._is_open and not self._is_cached:
      raise IOError('Already open.')

    if mode != 'rb':
      raise ValueError('Unsupported mode: {0:s}.'.format(mode))

    if not path_spec:
      raise ValueError('Missing path specification.')

    if not self._is_open:
      self._Open(path_spec, mode=mode)
      self._is_open = True
      self._path_spec = path_spec

      if path_spec and not self._resolver_context.GetFileSystem(path_spec):
        self._resolver_context.CacheFileSystem(path_spec, self)
        self._is_cached = True

    if self._is_cached:
      self._resolver_context.GrabFileSystem(path_spec)

  def SplitPath(self, path):
    """Splits the path into path segments.

    Args:
      path (str): path.

    Returns:
      list[str]: path segments without the root path segment, which is
          an empty string.
    """
    # Split the path with the path separator and remove empty path segments.
    return list(filter(None, path.split(self.PATH_SEPARATOR)))

# -*- coding: utf-8 -*-
"""The operating system file system implementation."""

import os
import platform

import pysmdev

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import os_path_spec
from dfvfs.vfs import file_system
from dfvfs.vfs import os_file_entry


class OSFileSystem(file_system.FileSystem):
  """File system that uses the operating system."""

  if platform.system() == 'Windows':
    PATH_SEPARATOR = '\\'
  else:
    PATH_SEPARATOR = '/'

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OS

  def _Close(self):
    """Closes the file system.

    Raises:
      IOError: if the close failed.
    """
    return

  def _Open(self, mode='rb'):
    """Opens the file system defined by path specification.

    Args:
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification with parent.')

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      bool: True if the file entry exists, false otherwise.
    """
    location = getattr(path_spec, 'location', None)

    if location is None:
      return False

    is_device = False
    if platform.system() == 'Windows':
      # Note that os.path.exists() returns False for Windows device files so
      # instead use libsmdev to do the check.
      try:
        is_device = pysmdev.check_device(location)
      except IOError as exception:
        # Since pysmdev will raise IOError when it has no access to the device
        # we check if the exception message contains ' access denied ' and
        # set is_device to True.
        is_device = bool(' access denied ' in str(exception))

    # Note that os.path.exists() returns False for broken symbolic links hence
    # an additional check using os.path.islink() is necessary.
    return is_device or os.path.exists(location) or os.path.islink(location)

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      OSFileEntry: a file entry or None if not available.
    """
    if not self.FileEntryExistsByPathSpec(path_spec):
      return None
    return os_file_entry.OSFileEntry(self._resolver_context, self, path_spec)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      OSFileEntry: a file entry or None if not available.
    """
    if platform.system() == 'Windows':
      # Return the root with the drive letter of the volume the current
      # working directory is on.
      location = os.getcwd()
      location, _, _ = location.partition('\\')
      location = f'{location:s}\\'
    else:
      location = '/'

    if not os.path.exists(location):
      return None

    path_spec = os_path_spec.OSPathSpec(location=location)
    return self.GetFileEntryByPathSpec(path_spec)

  def JoinPath(self, path_segments):
    """Joins the path segments into a path.

    Args:
      path_segments (list[str]): path segments.

    Returns:
      str: joined path segments prefixed with the path separator.
    """
    # For paths on Windows we need to make sure to handle the first path
    # segment correctly.
    first_path_segment = None

    if path_segments and platform.system() == 'Windows':
      # Check if the first path segment contains a "special" path definition.
      first_path_segment = path_segments[0]
      first_path_segment_length = len(first_path_segment)
      first_path_segment_prefix = None

      # In case the path start with: \\.\C:\
      if (first_path_segment_length >= 7 and
          first_path_segment.startswith('\\\\.\\') and
          first_path_segment[5:7] == ':\\'):
        first_path_segment_prefix = first_path_segment[4:6]
        first_path_segment = first_path_segment[7:]

      # In case the path start with: \\.\ or \\?\
      elif (first_path_segment_length >= 4 and
            first_path_segment[:4] in ['\\\\.\\', '\\\\?\\']):
        first_path_segment_prefix = first_path_segment[:4]
        first_path_segment = first_path_segment[4:]

      # In case the path start with: C:
      elif first_path_segment_length >= 2 and first_path_segment[1] == ':':
        first_path_segment_prefix = first_path_segment[:2]
        first_path_segment = first_path_segment[2:]

      # In case the path start with: \\server\share (UNC).
      elif first_path_segment.startswith('\\\\'):
        prefix, _, remainder = first_path_segment[2:].partition(
            self.PATH_SEPARATOR)

        first_path_segment_prefix = f'\\\\{prefix:s}'
        first_path_segment = f'\\{remainder:s}'

      if first_path_segment_prefix:
        first_path_segment, _, remainder = first_path_segment.partition(
            self.PATH_SEPARATOR)

        if not remainder:
          _ = path_segments.pop(0)
        else:
          path_segments[0] = remainder

        first_path_segment = ''.join([
            first_path_segment_prefix, first_path_segment])

      else:
        first_path_segment = None

    # We are not using os.path.join() here since it will not remove all
    # variations of successive path separators.

    # Split all the path segments based on the path (segment) separator.
    path_segments = [
        segment.split(self.PATH_SEPARATOR) for segment in path_segments]

    # Flatten the sublists into one list.
    path_segments = [
        element for sublist in path_segments for element in sublist]

    # Remove empty path segments.
    path_segments = list(filter(None, path_segments))

    if first_path_segment is None:
      path = ''.join([
          self.PATH_SEPARATOR, self.PATH_SEPARATOR.join(path_segments)])
    else:
      path = first_path_segment
      if path_segments:
        path = ''.join([
            path, self.PATH_SEPARATOR, self.PATH_SEPARATOR.join(path_segments)])

    return path

# -*- coding: utf-8 -*-
"""The operating system file system implementation."""

import os
import platform

import pysmdev

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import py2to3
from dfvfs.path import os_path_spec
from dfvfs.vfs import file_system
from dfvfs.vfs import os_file_entry


class OSFileSystem(file_system.FileSystem):
  """Class that implements an operating system file system object."""

  if platform.system() == u'Windows':
    PATH_SEPARATOR = u'\\'
  else:
    PATH_SEPARATOR = u'/'

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OS

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    return

  def _Open(self, path_spec, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification with parent.')

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    location = getattr(path_spec, u'location', None)

    if location is None:
      return False

    is_device = False
    if platform.system() == u'Windows':
      # Windows does not support running os.path.exists on device files
      # so we use libsmdev to do the check.
      try:
        is_device = pysmdev.check_device(location)
      except IOError as exception:
        # Since pysmdev will raise IOError when it has no access to the device
        # we check if the exception message contains ' access denied ' and
        # return true.

        # Note that exception.message no longer works in Python 3.
        exception_string = str(exception)
        if not isinstance(exception_string, py2to3.UNICODE_TYPE):
          exception_string = py2to3.UNICODE_TYPE(
              exception_string, errors=u'replace')

        if u' access denied ' in exception_string:
          is_device = True

    if not is_device and not os.path.exists(location):
      return False

    return True

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    if not self.FileEntryExistsByPathSpec(path_spec):
      return
    return os_file_entry.OSFileEntry(self._resolver_context, self, path_spec)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    if platform.system() == u'Windows':
      # Return the root with the drive letter of the volume the current
      # working directory is on.
      location = os.getcwd()
      location, _, _ = location.partition(u'\\')
      location = u'{0:s}\\'.format(location)
    else:
      location = u'/'

    if not os.path.exists(location):
      return

    path_spec = os_path_spec.OSPathSpec(location=location)
    return self.GetFileEntryByPathSpec(path_spec)

  def JoinPath(self, path_segments):
    """Joins the path segments into a path.

    Args:
      path_segments: a list of path segments.

    Returns:
      A string containing the joined path segments prefixed with the path
      separator.
    """
    # For paths on Windows we need to make sure to handle the first path
    # segment correctly.
    first_path_segment = None

    if path_segments and platform.system() == u'Windows':
      # Check if the first path segment contains a "special" path definition.
      first_path_segment = path_segments[0]
      first_path_segment_length = len(first_path_segment)
      first_path_segment_prefix = None

      # In case the path start with: \\.\C:\
      if (first_path_segment_length >= 7 and
          first_path_segment.startswith(u'\\\\.\\') and
          first_path_segment[5:7] == u':\\'):
        first_path_segment_prefix = first_path_segment[4:6]
        first_path_segment = first_path_segment[7:]

      # In case the path start with: \\.\ or \\?\
      elif (first_path_segment_length >= 4 and
            first_path_segment[:4] in [u'\\\\.\\', u'\\\\?\\']):
        first_path_segment_prefix = first_path_segment[:4]
        first_path_segment = first_path_segment[4:]

      # In case the path start with: C:
      elif first_path_segment_length >= 2 and first_path_segment[1] == u':':
        first_path_segment_prefix = first_path_segment[:2]
        first_path_segment = first_path_segment[2:]

      # In case the path start with: \\server\share (UNC).
      elif first_path_segment.startswith(u'\\\\'):
        prefix, _, remainder = first_path_segment[2:].partition(
            self.PATH_SEPARATOR)

        first_path_segment_prefix = u'\\\\{0:s}'.format(prefix)
        first_path_segment = u'\\{0:s}'.format(remainder)

      if first_path_segment_prefix:
        first_path_segment, _, remainder = first_path_segment.partition(
            self.PATH_SEPARATOR)

        if not remainder:
          _ = path_segments.pop(0)
        else:
          path_segments[0] = remainder

        first_path_segment = u''.join([
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
      path = u'{0:s}{1:s}'.format(
          self.PATH_SEPARATOR, self.PATH_SEPARATOR.join(path_segments))
    else:
      path = first_path_segment
      if path_segments:
        path = u'{0:s}{1:s}{2:s}'.format(
            path, self.PATH_SEPARATOR, self.PATH_SEPARATOR.join(path_segments))

    return path

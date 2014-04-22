#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The dfVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The operating system file system implementation."""

import os
import platform

from dfvfs.lib import definitions
from dfvfs.path import os_path_spec
from dfvfs.vfs import file_system
from dfvfs.vfs import os_file_entry


class OSFileSystem(file_system.FileSystem):
  """Class that implements an operating system file system object."""

  if platform.system() == 'Windows':
    PATH_SEPARATOR = u'\\'
  else:
    PATH_SEPARATOR = u'/'

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OS

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    location = getattr(path_spec, 'location', None)

    if location is None or not os.path.exists(location):
      return False
    return True

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

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
    if platform.system() == 'Windows':
      # Return the root with the drive letter of the volume the current
      # working directory is on.
      location = os.getcwd()
      location, _, _ = location.partition('\\')
      location = u'{0:s}\\'.format(location)
    else:
      location = u'/'

    if not os.path.exists(location):
      return

    path_spec = os_path_spec.OSPathSpec(location=location)
    return os_file_entry.OSFileEntry(
        self._resolver_context, self, path_spec, is_root=True)

  def JoinPath(self, path_segments):
    """Joins the path segments into a path.

    Args:
      path_segments: a list of path segments.

    Returns:
      A string containing the joined path segments prefixed with the path
      separator.
    """
    # We are not using os.path.join() here since it will not remove all
    # variations of successive path separators.

    # Split all the path segments based on the path (segment) separator.
    path_segments = [
        segment.split(self.PATH_SEPARATOR) for segment in path_segments]

    # Flatten the sublists into one list.
    path_segments = [
        element for sublist in path_segments for element in sublist]

    # Remove empty path segments.
    path_segments = filter(None, path_segments)

    # For paths on Windows we need to make sure to handle the first path
    # segment correctly.
    first_path_segment = None
    if platform.system() == 'Windows':
      if path_segments:
        first_path_segment = path_segments[0]
        # Check if the first path segment contains a "special" path definition
        # e.g. \\.\, \\?\, C: or \\server\share (UNC).
        if (len(first_path_segment) > 1 and (
            first_path_segment.startswith(u'\\\\') or
            first_path_segment[1] == u':')):
          path_segments = path_segments[1:]
        else:
          first_path_segment = None

    if first_path_segment:
      path = u'{0:s}{1:s}{2:s}'.format(
          first_path_segment, self.PATH_SEPARATOR,
          self.PATH_SEPARATOR.join(path_segments))
    else:
      path = u'{0:s}{1:s}'.format(
          self.PATH_SEPARATOR, self.PATH_SEPARATOR.join(path_segments))

    return path

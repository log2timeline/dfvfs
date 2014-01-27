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
"""The Virtual File System (VFS) file system object interface."""

import abc


class FileSystem(object):
  """Class that implements the VFS file system object interface."""

  PATH_SEPARATOR = u'/'

  @property
  def type_indicator(self):
    """The type indicator."""
    type_indicator = getattr(self, 'TYPE_INDICATOR', None)
    if type_indicator is None:
      raise NotImplementedError(
          u'Invalid file system missing type indicator.')
    return type_indicator

  def BasenamePath(self, path):
    """Determines the basename of the path.

    Args:
      path: a string containing the path.

    Returns:
      A string containing the basename of the path.
    """
    if path.endswith(self.PATH_SEPARATOR):
      path = path[:-1]
    _, _, basename = path.rpartition(self.PATH_SEPARATOR)
    return basename

  def DirnamePath(self, path):
    """Determines the directory name of the path.

       The file system root is represented by an empty string.

    Args:
      path: a string containing the path.

    Returns:
      A string containing the directory name of the path or None.
    """
    if path.endswith(self.PATH_SEPARATOR):
      path = path[:-1]
    if not path:
      return
    dirname, _, _ = path.rpartition(self.PATH_SEPARATOR)
    return dirname

  @abc.abstractmethod
  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """

  @abc.abstractmethod
  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """

  def GetFileObjectByPathSpec(self, path_spec):
    """Retrieves a file-like object for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file-like object (instance of file_io.FileIO) or None.
    """
    file_entry = self.GetFileEntryByPathSpec(path_spec)
    if file_entry is None:
      return
    return file_entry.GetFileObject()

  def GetPathSegmentAndSuffix(self, base_path, path):
    """Determines the path segment and suffix of the path.

       None is returned if the path does not start with the base path and
       an empty string if the path exactly matches the base path.

    Args:
      base_path: a string containing the base path.
      path: a string containing the path.

    Returns:
      A tuple containing the path segment and suffix string.
    """
    if not path or not base_path or not path.startswith(base_path):
      return None, None

    path_index = len(base_path)
    if not base_path.endswith(self.PATH_SEPARATOR):
      path_index += 1

    if path_index == len(path):
      return u'', u''

    path_segment, _, suffix = path[path_index:].partition(self.PATH_SEPARATOR)
    return path_segment, suffix

  @abc.abstractmethod
  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """

  def JoinPath(self, path_segments):
    """Joins the path segments into a path.

    Args:
      path_segments: a list of path segments.

    Returns:
      A string containing the joined path segments prefixed with the path
      separator.
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
    path_segments = filter(None, path_segments)

    return u'{0:s}{1:s}'.format(
        self.PATH_SEPARATOR, self.PATH_SEPARATOR.join(path_segments))

  def SplitPath(self, path):
    """Splits the path into path segments.

    Args:
      path: a string containing the path.

    Returns:
      A list of path segements without the root path segment, which is an
      empty string.
    """
    path_segments = path.split(self.PATH_SEPARATOR)
    return path_segments[1:]

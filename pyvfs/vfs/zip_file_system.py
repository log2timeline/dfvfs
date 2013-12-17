#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
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
"""The zip file system implementation."""

import zipfile

# This is necessary to prevent a circular import.
import pyvfs.vfs.zip_file_entry

from pyvfs.path import zip_path_spec
from pyvfs.vfs import file_system


class ZipFileSystem(file_system.FileSystem):
  """Class that implements a file system object using zipfile."""

  LOCATION_ROOT = u'/'

  def __init__(self, file_object, path_spec, encoding='utf-8'):
    """Initializes the file system object.

    Args:
      file_object: the file-like object (instance of io.FileIO).
      path_spec: the path specification (instance of path.PathSpec) of
                 the file-like object.
      encoding: optional file entry name encoding. The default is 'utf-8'.
    """
    super(ZipFileSystem, self).__init__()
    self._file_object = file_object
    self._path_spec = path_spec
    self.encoding = encoding

    self._zip_file = zipfile.ZipFile(file_object, 'r')

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    zip_info = None
    location = getattr(path_spec, 'location', None)

    if (location is None or
        not location.startswith(self.LOCATION_ROOT)):
      return

    if len(location) == 1:
      return True

    try:
      zip_info = self._zip_file.getinfo(location[1:])
    except KeyError:
      pass

    return zip_info is not None

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.ZipFileEntry) or None.
    """
    zip_info = None
    location = getattr(path_spec, 'location', None)

    if (location is None or
        not location.startswith(self.LOCATION_ROOT)):
      return None

    if len(location) == 1:
      return self.GetRootFileEntry()

    try:
      zip_info = self._zip_file.getinfo(location[1:])
    except KeyError:
      pass

    if zip_info is None:
      return
    return pyvfs.vfs.zip_file_entry.ZipFileEntry(
        self, path_spec, zip_info=zip_info)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    path_spec = zip_path_spec.ZipPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec)

    return pyvfs.vfs.zip_file_entry.ZipFileEntry(self, path_spec)

  def GetZipFile(self):
    """Retrieves the zip file object.

    Returns:
      The zip file object (instance of zipfile.ZipFile).
    """
    return self._zip_file

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
"""The operating system file system implementation."""

import platform

from pyvfs.path import os_path_spec
from pyvfs.vfs import file_system
from pyvfs.vfs import os_file_entry


class OSFileSystem(file_system.FileSystem):
  """Class that implements a file system object using os."""

  def __init__(self, drive_letter=None):
    """Initializes the file system object.

    Args:
      drive_letter: optional drive letter for Windows volumes,
                    the default is None.
    """
    super(OSFileSystem, self).__init__()

    if drive_letter:
      self._drive_letter = drive_letter
    else:
      self._drive_letter = 'C'

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    if platform.system() == 'Windows':
      location = '{0:s}:\\'.format(self._drive_letter)
    else:
      location = '/'
    path_spec = os_path_spec.OSPathSpec(location)
    return os_file_entry.OSFileEntry(self, path_spec)

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    return os_file_entry.OSFileEntry(self, path_spec)

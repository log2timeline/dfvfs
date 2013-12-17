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

import os
import platform

from pyvfs.path import os_path_spec
from pyvfs.vfs import file_system
from pyvfs.vfs import os_file_entry


class OSFileSystem(file_system.FileSystem):
  """Class that implements a file system object using os."""

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
    return os_file_entry.OSFileEntry(self, path_spec)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry) or None.
    """
    if platform.system() == 'Windows':
      # Return the root with the drive letter of the volume the current
      # working directory is on.
      location = os.getcwd()
      location, _, _ = location.rpartition('\\')
      location = u'{0:s}\\'.format(location)
    else:
      location = u'/'

    if not os.path.exists(location):
      return

    path_spec = os_path_spec.OSPathSpec(location=location)
    return os_file_entry.OSFileEntry(self, path_spec)

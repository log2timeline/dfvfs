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

from pyvfs.vfs import file_system


class OSFileSystem(file_system.FileSystem):
  """Class that implements a file system object using os."""

  def __init__(self, file_object):
    """Initializes the file system object.

    Args:
      file_object: The file-like object (instance of io.FileIO).
    """
    super(OSFileSystem, self).__init__(file_object)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    # TODO: implement.
    pass

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.FileEntry).

    Raises:
      IOError: if the open file entry could not be opened.
      ValueError: if the path specification is incorrect.
    """
    # TODO: implement.
    pass

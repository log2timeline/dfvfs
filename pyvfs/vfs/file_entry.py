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
"""The Virtual File System (VFS) file entry object interface.

The file entry can be various file system elments like a regular file,
a directory or file system metadata.
"""

import abc


class Directory(object):
  """Class that implements the VFS directory object interface."""

  def __init__(self, path_spec):
    """Initializes the directory object.

    Args:
      path_spec: the path specification object (instance of path.PathSpec).
    """
    super(Directory, self).__init__()
    self.path_spec = path_spec
    self._entries = None

  @abc.abstractmethod
  def _GetEntries(self):
    """Retrieves the entries.

    Returns:
      A list of path specifications (instance of path.OSPathSpec).
    """

  @property
  def number_of_entries(self):
    """The number of entries."""
    if self._entries is None:
      self._entries = self._GetEntries()
    return len(self._entries)

  @property
  def entries(self):
    """The entries (list of instance of path.OSPathSpec)."""
    if self._entries is None:
      self._entries = self._GetEntries()
    return self._entries


class FileEntry(object):
  """Class that implements the VFS file entry object interface."""

  def __init__(self, file_system, path_spec):
    """Initializes the file entry object.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification object (instance of path.PathSpec).
    """
    super(FileEntry, self).__init__()
    self._file_system = file_system
    self.path_spec = path_spec

  @abc.abstractproperty
  def name(self):
    """The name of the file entry, which does not include the full path."""

  @abc.abstractproperty
  def number_of_sub_file_entries(self):
    """The number of sub file entries."""

  @abc.abstractproperty
  def sub_file_entries(self):
    """The sub file entries."""

  # TODO: maybe rename this to GetFileIO, GetDataStream or equiv.
  @abc.abstractmethod
  def GetData(self):
    """Retrieves the file-like object (instance of io.FileIO) of the data."""

  @abc.abstractmethod
  def GetStat(self):
    """Retrieves the stat object (instance of vfs.Stat)."""

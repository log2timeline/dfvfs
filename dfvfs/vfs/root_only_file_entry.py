#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The dfVFS Project Authors.
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
"""The root only file entry implementation."""

import abc

from dfvfs.vfs import file_entry


class RootOnlyFileEntry(file_entry.FileEntry):
  """Class that implements a root only file entry object."""

  def _GetDirectory(self):
    """Retrieves the directory object (instance of vfs.Directory)."""
    return

  @abc.abstractmethod
  def _GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat)."""

  @property
  def name(self):
    """The name of the file entry, which does not include the full path."""
    return u''

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    # We are creating an empty generator here. Yield or return None
    # individually don't provide that behavior, neither does raising
    # GeneratorExit or StopIteration.
    # pylint: disable-msg=unreachable
    return
    yield

  @abc.abstractmethod
  def GetFileObject(self):
    """Retrieves the file-like object (instance of file_io.FileIO)."""

  def GetParentFileEntry(self):
    """Retrieves the parent file entry."""
    return

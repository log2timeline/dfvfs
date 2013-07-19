#!/usr/bin/python
# -*- coding: utf-8 -*-
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
"""This file contains BZ2 compressed file support in pyvfs."""
import bz2
import logging

from pyvfs.lib import interface
from pyvfs.proto import transmission_pb2


class Bz2File(interface.PyVFSFile):
  """Provide a file-like object to a file compressed using BZ2."""
  TYPE = 'BZ2'

  def Stat(self):
    """Return a Stats object that contains stats like information."""
    ret = Stats()
    if not self.fh:
      return ret

    ret.ino = self.inode
    ret.fs_type = 'BZ2 container'
    return ret

  def readline(self, size=-1):
    """Read a line from the file.

    Args:
      size: Defines the maximum byte count (including the new line trail)
      and if defined may get the function to return an incomplete line.

    Returns:
      A string containing a single line read from the file.
    """
    if self.fh:
      return self.fh.readline(size)
    else:
      return ''

  def Open(self, filehandle=None):
    """Open the file as it is described in the PathSpec protobuf."""
    if filehandle:
      self.inode = getattr(filehandle.Stat(), 'ino', 0)
      try:
        filehandle.seek(0)
      except NotImplementedError:
        pass
      self.fh = bz2.BZ2File(filehandle, 'r')
      self.display_name = u'%s:%s' % (filehandle.name, self.pathspec.file_path)
    else:
      self.display_name = self.pathspec.file_path
      self.fh = bz2.BZ2File(self.pathspec.file_path, 'r')
      self.inode = os.stat(self.pathspec.file_path).st_ino

    self.name = self.pathspec.file_path


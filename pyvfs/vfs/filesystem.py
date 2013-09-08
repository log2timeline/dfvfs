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
"""An implementation of a pyVFS file using regular OS access to the file."""
import logging
import os

from pyvfs.lib import errors
from pyvfs.lib import interface
from pyvfs.proto import transmission_pb2


class OsFile(interface.PyVFSFile):
  """Class to provide a file-like object to a file stored on a filesystem."""

  TYPE = 'OS'

  def Open(self, filehandle=None):
    """Open the file as it is described in the PathSpec protobuf."""
    self.fh = open(self.pathspec.file_path, 'rb')
    self.name = self.pathspec.file_path
    if filehandle:
      self.display_name = u'%s:%s' % (filehandle.name, self.name)
    else:
      self.display_name = self.name

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

  def Stat(self):
    """Return a Stats object that contains stats like information."""
    ret = Stats()
    if not self.fh:
      return ret

    stat = os.stat(self.name)
    ret.mode = stat.st_mode
    ret.ino = stat.st_ino
    ret.dev = stat.st_dev
    ret.nlink = stat.st_nlink
    ret.uid = stat.st_uid
    ret.gid = stat.st_gid
    ret.size = stat.st_size
    if stat.st_atime > 0:
      ret.atime = stat.st_atime
    if stat.st_mtime > 0:
      ret.mtime = stat.st_mtime
    if stat.st_ctime > 0:
      ret.ctime = stat.st_ctime
    ret.fs_type = 'Unknown'
    ret.allocated = True

    return ret

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
"""This file contains a pyVFS implementation for a GZIP compressed file."""
import gzip
import logging

from pyvfs.lib import errors
from pyvfs.lib import interface
from pyvfs.proto import transmission_pb2


class GzipFile(interface.PyVFSFile):
  """Provide a file-like object to a file compressed using GZIP."""
  TYPE = 'GZIP'

  def Stat(self):
    """Return a Stats object that contains stats like information."""
    ret = Stats()
    if not self.fh:
      return ret

    ret.size = self.size
    ret.ino = self.inode
    ret.fs_type = 'GZ File'

    return ret

  def seek(self, offset, whence=0):
    """Seek into a specific location in a file.

    This method implements a simple method to seek into a
    compressed file from the end, which is not implemented by the
    gzip library.

    Args:
      offset: An integer, indicating the number of bytes to seek in file,
      how that value is interpreted depends on the 'whence' value.
      whence: An integer; 0 means from beginning, 1 from last position
      and 2 indicates we are about to seek from the end of the file.

    Raises:
      RuntimeError: If a seek is attempted to a closed file.
    """
    if not self.fh:
      raise RuntimeError('Unable to seek into a file that is not open.')

    if whence == 2:
      ofs = self.size + offset
      if ofs > self.tell():
        self.fh.seek(ofs - self.fh.offset, 1)
      else:
        self.fh.rewind()
        self.fh.seek(ofs)
    else:
      self.fh.seek(offset, whence)

  def read(self, size=-1):
    """Read size bytes from file and return them."""
    if self.fh:
      return self.fh.read(size)
    else:
      return ''

  def Open(self, filehandle=None):
    """Open the file as it is described in the PathSpec protobuf."""
    if filehandle:
      filehandle.seek(0)
      self.fh = gzip.GzipFile(fileobj=filehandle, mode='rb')
      self.inode = getattr(filehandle.Stat(), 'ino', 0)
    else:
      self.fh = gzip.GzipFile(filename=self.pathspec.file_path, mode='rb')
      self.inode = os.stat(self.pathspec.file_path).st_ino

    self.name = self.pathspec.file_path
    if filehandle:
      self.display_name = u'%s_uncompressed' % filehandle.name
    else:
      self.display_name = self.name

    # To get the size properly calculated.
    try:
      _ = self.fh.read(4)
    except IOError as e:
      dn = self.display_name
      raise IOError('Not able to open the GZIP file %s -> %s [%s]' % (
          self.name, dn, e))
    self.fh.rewind()
    try:
      self.size = self.fh.size
    except AttributeError:
      self.size = 0


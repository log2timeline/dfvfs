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
"""This file contains classes to handle the transmission protobuf.

The classes are designed to create and process the transmission protobuf.
This involves opening up files and returning filehandles and creating
protobufs that can accurately describe files and their locations so they
can be successfully opened by Plaso.

"""
import bz2
import gzip
import logging
import os
import tarfile
import zipfile

from plaso.lib import errors
from plaso.lib import event
from plaso.lib import registry
from plaso.lib import sleuthkit
from plaso.lib import timelib
from plaso.lib import vss
from plaso.proto import transmission_pb2

import pytsk3
import pyvshadow


class TarFile(PlasoFile):
  """Provide a file-like object to a file stored inside a TAR file."""
  TYPE = 'TAR'

  def Stat(self):
    """Return a Stats object that contains stats like information."""
    ret = Stats()
    if not self.fh:
      return ret

    ret.ino = self.inode
    ret.fs_type = 'Tar container'
    return ret

  def Open(self, filehandle=None):
    """Open the file as it is described in the PathSpec protobuf."""
    if filehandle:
      ft = tarfile.open(fileobj=filehandle, mode='r')
      self.display_name = u'%s:%s' % (filehandle.name, self.pathspec.file_path)
      self.inode = getattr(filehandle.Stat(), 'ino', 0)
    else:
      self.display_name = u'%s:%s' % (self.pathspec.container_path,
                                      self.pathspec.file_path)
      ft = tarfile.open(self.pathspec.container_path, 'r')
      self.inode = os.stat(self.pathspec.container_path).st_ino

    self.fh = ft.extractfile(self.pathspec.file_path)
    if not self.fh:
      raise IOError(
          '[TAR] File %s empty or unable to open.' % self.pathspec.file_path)
    self.buffer = ''
    self.name = self.pathspec.file_path
    self.size = self.fh.size

  def read(self, size=None):
    """Read size bytes from file and return them."""
    if not self.fh:
      return ''

    if size and len(self.buffer) >= size:
      ret = self.buffer[:size]
      self.buffer = self.buffer[size:]
      return ret

    ret = self.buffer
    self.buffer = ''

    read_size = None
    if size:
      read_size = size - len(ret)

    ret += self.fh.read(read_size)

    # In my testing I've seen the underlying read operation
    # sometimes read in way more than the size here indicates.
    # Slapping an additional check to make sure we return the amount
    # of bytes that we are really asking for.
    if size and len(ret) > size:
      self.buffer = ret[size:]
      ret = ret[:size]

    return ret

  def readline(self, size=-1):
    """Read a line from the file.

    Args:
      size: Defines the maximum byte count (including the new line trail)
      and if defined may get the function to return an incomplete line.

    Returns:
      A string containing a single line read from the file.
    """
    if not self.fh:
      return ''

    if '\n' not in self.buffer:
      self.buffer += self.fh.readline(size)

    # TODO: Make this more resiliant/optimized. For now this
    # code only checks the size in two places, better to always fill
    # the buffer, make sure it is of certain size before moving on.
    if size > 0 and len(self.buffer) > size:
      ret = self.buffer[:size]
      self.buffer = self.buffer[size:]
    else:
      ret = self.buffer
      self.buffer = ''

    result, sep, ret = ret.partition('\n')
    self.buffer = ret + self.buffer

    return result + sep

  def seek(self, offset, whence=0):
    """Seek into the filehandle."""
    if not self.fh:
      raise RuntimeError('Unable to seek into a file that is not open.')

    if whence == 1:
      if offset > 0 and len(self.buffer) > offset:
        self.buffer = self.buffer[offset:]
      else:
        ofs = offset - len(self.buffer)
        self.buffer = ''
        self.fh.seek(ofs, 1)
    else:
      self.buffer = ''
      self.fh.seek(offset, whence)

  def tell(self):
    """Return the current offset of the filehandle."""
    if not self.fh:
      return 0

    return self.fh.tell() - len(self.buffer)



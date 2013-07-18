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


class ZipFile(PlasoFile):
  """Provide a file-like object to a file stored inside a ZIP file."""
  TYPE = 'ZIP'

  def Stat(self):
    """Return a Stats object that contains stats like information."""
    ret = Stats()

    if not self.fh:
      return ret

    # TODO: Make this a proper stat element with as much information
    # as can be extracted.
    # Also confirm for sure that this is the correct timestamp and it is
    # stored in UTC (or if it is in local timezone, adjust it)
    ret.ctime = timelib.Timetuple2Timestamp(self.zipinfo.date_time)
    ret.ino = self.inode
    ret.size = self.zipinfo.file_size
    ret.fs_type = 'ZIP Container'
    return ret

  def Open(self, filehandle=None):
    """Open the file as it is described in the PathSpec protobuf."""
    if filehandle:
      try:
        zf = zipfile.ZipFile(filehandle, 'r')
      except zipfile.BadZipfile as e:
        raise IOError(
            u'Unable to open ZIP file, not a ZIP file?: {} [{}]'.format(
                filehandle.name, e))
      path_name = filehandle.name
      self.inode = getattr(filehandle.Stat(), 'ino', 0)
    else:
      path_name = self.pathspec.container_path
      zf = zipfile.ZipFile(path_name, 'r')
      self.inode = os.stat(path_name).st_ino

    self.name = self.pathspec.file_path
    if filehandle:
      self.display_name = u'%s:%s' % (filehandle.display_name,
                                      self.pathspec.file_path)
    else:
      self.display_name = u'%s:%s' % (path_name, self.pathspec.file_path)
    self.offset = 0
    self.orig_fh = filehandle
    self.zipinfo = zf.getinfo(self.pathspec.file_path)
    self.size = self.zipinfo.file_size
    try:
      self.fh = zf.open(self.pathspec.file_path, 'r')
    except RuntimeError as e:
      raise IOError(u'Unable to open ZIP file: {%s} -> %s' % (self.name, e))

  def read(self, size=None):
    """Read size bytes from file and return them."""
    if not self.fh:
      return ''

    # There is an error in the ZipExtFile, at least with Python v 2.6.
    # If a readline is called the results are stored in linebuffer,
    # while read uses the readbuffer for buffer, ignoring the content
    # of linebuffer.
    if hasattr(self.fh, 'linebuffer'):
      if self.fh.linebuffer:
        self.fh.readbuffer = self.fh.linebuffer + self.fh.readbuffer
        self.fh.linebuffer = ''

    if size is None:
      size = min(self.size - self.offset, 1024 * 1024 * 24)
      logging.debug(u'[ZIP] Unbound read attempted: %s -> %s', self.name,
                    self.display_name)
      if size != self.size - self.offset:
        logging.debug('[ZIP] Not able to read in the entire file (too large).')

    line = self.fh.read(size)
    self.offset += len(line)
    return line

  def readline(self, size=None):
    """Read a line from the file.

    Args:
      size: Defines the maximum byte count (including the new line trail)
      and if defined may get the function to return an incomplete line.

    Returns:
      A string containing a single line read from the file.
    """
    if self.fh:
      line = self.fh.readline(size)
      self.offset += len(line)
      return line
    else:
      return ''

  def tell(self):
    """Return the current offset into the file.

    A ZipExtFile object maintains an object called fileobj that implements
    a tell function, which reads the offset into the current fileobj.

    However, that object may have some data that has been read in that is
    stored in buffers, so we need to subtract buffer read data to get the
    actual offset into the file.

    Returns:
      An offset into the file, indicating current location.
    """
    if not self.fh:
      return 0

    return self.offset

  def close(self):
    """Close the file."""
    if self.fh:
      self.fh.close()
      self.fh = None
      self.offset = 0

  def seek(self, offset, whence=0):
    """Seek into the file."""
    if not self.fh:
      raise RuntimeError('Unable to seek into a file that is not open.')

    if whence == 0:
      self.close()
      self.Open(self.orig_fh)
      _ = self.read(offset)
    elif whence == 1:
      if offset > 0:
        _ = self.read(offset)
      else:
        ofs = self.offset + offset
        self.seek(ofs)
    elif whence == 2:
      ofs = self.size + offset
      if ofs > self.offset:
        _ = self.read(ofs - self.offset)
      else:
        self.seek(0)
        _ = self.read(ofs)
    else:
      raise RuntimeError('Illegal whence value %s' % whence)


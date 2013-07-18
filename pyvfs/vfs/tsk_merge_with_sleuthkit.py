#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2012 The Plaso Project Authors.
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


class TskFile(PlasoFile):
  """Class to open up files using TSK."""

  TYPE = 'TSK'

  def _OpenFileSystem(self, path, offset):
    """Open the filesystem object and store a copy of it for caching.

    Args:
      path: Path to the image file.
      offset: If this is a disk partition an offset to the filesystem
      is needed.

    Raises:
      IOError: If no pfile.FilesystemCache object is provided.
    """
    if not hasattr(self, '_fscache'):
      raise IOError('No FS cache provided, unable to open a file.')

    fs_obj = self._fscache.Open(path, offset)

    self._fs = fs_obj.fs

  def Stat(self):
    """Return a Stats object that contains stats like information."""
    if hasattr(self, '_stat'):
      return self._stat

    ret = Stats()
    if not self.fh:
      return ret

    try:
      info = self.fh.fileobj.info
      meta = info.meta
    except IOError:
      return ret

    if not meta:
      return ret

    fs_type = ''
    ret.mode = getattr(meta, 'mode', None)
    ret.ino = getattr(meta, 'addr', None)
    ret.nlink = getattr(meta, 'nlink', None)
    ret.uid = getattr(meta, 'uid', None)
    ret.gid = getattr(meta, 'gid', None)
    ret.size = getattr(meta, 'size', None)
    ret.atime = getattr(meta, 'atime', None)
    ret.atime_nano = getattr(meta, 'atime_nano', None)
    ret.crtime = getattr(meta, 'crtime', None)
    ret.crtime_nano = getattr(meta, 'crtime_nano', None)
    ret.mtime = getattr(meta, 'mtime', None)
    ret.mtime_nano = getattr(meta, 'mtime_nano', None)
    ret.ctime = getattr(meta, 'ctime', None)
    ret.ctime_nano = getattr(meta, 'ctime_nano', None)
    ret.dtime = getattr(meta, 'dtime', None)
    ret.dtime_nano = getattr(meta, 'dtime_nano', None)
    ret.bkup_time = getattr(meta, 'bktime', None)
    ret.bkup_time_nano = getattr(meta, 'bktime_nano', None)
    fs_type = str(self._fs.info.ftype)

    check_allocated = getattr(self.fh.fileobj, 'IsAllocated', None)
    if check_allocated:
      ret.allocated = check_allocated()
    else:
      ret.allocated = True

    if fs_type.startswith('TSK_FS_TYPE'):
      ret.fs_type = fs_type[12:]
    else:
      ret.fs_type = fs_type

    self._stat = ret
    return ret

  def Open(self, filehandle=None):
    """Open the file as it is described in the PathSpec protobuf.

    This method reads the content of the PathSpec protobuf and opens
    the filehandle using the Sleuthkit (TSK).

    Args:
      filehandle: A PlasoFile object that the file is contained within.
    """
    if filehandle:
      path = filehandle
    else:
      path = self.pathspec.container_path

    if hasattr(self.pathspec, 'image_offset'):
      self._OpenFileSystem(path, self.pathspec.image_offset)
    else:
      self._OpenFileSystem(path, 0)

    inode = 0
    if hasattr(self.pathspec, 'image_inode'):
      inode = self.pathspec.image_inode

    if not hasattr(self.pathspec, 'file_path'):
      self.pathspec.file_path = 'NA_NotProvided'

    self.fh = sleuthkit.Open(
        self._fs, inode, self.pathspec.file_path)

    self.name = self.pathspec.file_path
    self.size = self.fh.size
    self.display_name = u'%s:%s' % (self.pathspec.container_path,
                                    self.pathspec.file_path)
    if filehandle:
      self.display_name = u'%s:%s' % (filehandle.name, self.display_name)



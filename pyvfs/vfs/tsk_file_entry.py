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
"""The SleuthKit (TSK) file entry implementation."""

from pyvfs.io import tsk_file
from pyvfs.vfs import file_entry
from pyvfs.vfs import stat


class TSKFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using pytsk3."""

  def __init__(self, file_system, path_spec, file_object=None):
    """Initializes the file entry object.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification (instance of path.PathSpec).
      file_object: the file object (instance of io.TSKFile).
    """
    super(TSKFileEntry, self).__init__(file_system, path_spec)
    self._file_object = file_object
    self._stat_object = None

  def _GetFile(self):
    """Retrieves the file-like object (instance of io.TSKFile)."""
    if self._file_object is None:
      self._file_object = tsk_file.TSKFile(self._file_system)
      self._file_object.open(self.path_spec)
    return self._file_object

  def GetData(self):
    """Retrieves the file-like object (instance of io.FileIO) of the data."""
    # TODO: implement.
    pass

  def GetStat(self):
    """Retrieves the stat object (instance of vfs.Stat)."""
    # TODO validate path spec.

    if self._stat_object is None:
      file_object = self._GetFile()
      tsk_fs_meta = file_object.GetFsMeta()

      if not tsk_fs_meta:
        return None

      self._stat_object = stat.Stat()

      # File data stat information.
      self._stat_object.size = getattr(tsk_fs_meta, 'size', None)

      # Date and time stat information.
      self._stat_object.atime = getattr(tsk_fs_meta, 'atime', None)
      self._stat_object.atime_nano = getattr(tsk_fs_meta, 'atime_nano', None)
      self._stat_object.bkup_time = getattr(tsk_fs_meta, 'bkup_time', None)
      self._stat_object.bkup_time_nano = getattr(
          tsk_fs_meta, 'bkup_time_nano', None)
      self._stat_object.ctime = getattr(tsk_fs_meta, 'ctime', None)
      self._stat_object.ctime_nano = getattr(tsk_fs_meta, 'ctime_nano', None)
      self._stat_object.crtime = getattr(tsk_fs_meta, 'crtime', None)
      self._stat_object.crtime_nano = getattr(tsk_fs_meta, 'crtime_nano', None)
      self._stat_object.dtime = getattr(tsk_fs_meta, 'dtime', None)
      self._stat_object.dtime_nano = getattr(tsk_fs_meta, 'dtime_nano', None)
      self._stat_object.mtime = getattr(tsk_fs_meta, 'mtime', None)
      self._stat_object.mtime_nano = getattr(tsk_fs_meta, 'mtime_nano', None)

      # Ownership and permissions stat information.
      self._stat_object.uid = getattr(tsk_fs_meta, 'uid', None)
      self._stat_object.gid = getattr(tsk_fs_meta, 'gid', None)

      # Other stat information.
      self._stat_object.mode = getattr(tsk_fs_meta, 'mode', None)
      self._stat_object.ino = getattr(tsk_fs_meta, 'addr', None)
      # self._stat_object.dev = stat_info.st_dev
      self._stat_object.nlink = getattr(tsk_fs_meta, 'nlink', None)
      self._stat_object.fs_type = 'Unknown'
      self._stat_object.allocated = True

    # check_allocated = getattr(self.fh.fileobj, 'IsAllocated', None)
    # if check_allocated:
    #   ret.allocated = check_allocated()
    # else:
    #   ret.allocated = True

    # fs_type = ''
    # fs_type = str(self._fs.info.ftype)

    # if fs_type.startswith('TSK_FS_TYPE'):
    #   ret.fs_type = fs_type[12:]
    # else:
    #   ret.fs_type = fs_type

    return self._stat_object

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

import pytsk3

# This is necessary to prevent a circular import.
import pyvfs.file_io.tsk_file_io

from pyvfs.path import tsk_path_spec
from pyvfs.vfs import file_entry
from pyvfs.vfs import vfs_stat


class TSKDirectory(file_entry.Directory):
  """Class that implements a directory object using pytsk3."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

       Since a directory can contain a vast number of entries using
       a generator is more memory efficient.

    Yields:
      A path specification (instance of path.TSKPathSpec).
    """
    # Opening a file by inode number is faster than opening a file
    # by location.
    inode = getattr(self.path_spec, 'inode', None)
    location = getattr(self.path_spec, 'location', None)

    tsk_file_system = self._file_system.GetFsInfo()
    if inode is not None:
      tsk_directory = tsk_file_system.open_dir(inode=inode)
    elif location is not None:
      tsk_directory = tsk_file_system.open_dir(path=location)
    else:
      return

    for tsk_directory_entry in tsk_directory:
      # Note that because pytsk3.Directory does not explicitly defines info
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(tsk_directory_entry, 'info', None) is None:
        continue

      # Note that because pytsk3.TSK_FS_FILE does not explicitly defines meta
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(tsk_directory_entry.info, 'meta', None) is None:
        # Most directory entries will have an "inode" but not all, e.g.
        # previously deleted files. Currently directory entries without
        # a pytsk3.TSK_FS_META object are ignored.
        continue

      # Note that because pytsk3.TSK_FS_META does not explicitly defines addr
      # we need to check if the attribute exists.
      if not hasattr(tsk_directory_entry.info.meta, 'addr'):
        continue

      directory_entry_inode = tsk_directory_entry.info.meta.addr
      directory_entry = None

      # Ignore references to inode 0 or self.
      if directory_entry_inode in [0, inode]:
        continue

      # Note that because pytsk3.TSK_FS_FILE does not explicitly defines name
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(tsk_directory_entry.info, 'name', None) is not None:
        directory_entry = getattr(tsk_directory_entry.info.name, 'name', '')

        if directory_entry:
          # Ignore references to self or parent.
          if directory_entry in ['.', '..']:
            continue

          if location == self._file_system.PATH_SEPARATOR:
            directory_entry = self._file_system.JoinPath([directory_entry])
          else:
            directory_entry = self._file_system.JoinPath([
                location, directory_entry])

      yield tsk_path_spec.TSKPathSpec(
          inode=directory_entry_inode, location=directory_entry,
          parent=self.path_spec.parent)


class TSKFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using pytsk3."""

  def __init__(self, file_system, path_spec, tsk_file=None, parent_inode=None):
    """Initializes the file entry object.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification (instance of path.PathSpec).
      tsk_file: optional file object (instance of pytsk3.File).
                The default is None.
      parent_inode: optional parent inode number. The default is None.
    """
    super(TSKFileEntry, self).__init__(file_system, path_spec)
    self._file_object = None
    self._name = None
    self._parent_inode = parent_inode
    self._tsk_file = tsk_file

  def _GetDirectory(self):
    """Retrieves the directory object (instance of TSKDirectory)."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return TSKDirectory(self._file_system, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat)."""
    if self._tsk_file is None:
      self._tsk_file = self.GetTSKFile()

    if not self._tsk_file.info or not self._tsk_file.info.meta:
      return

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = getattr(self._tsk_file.info.meta, 'size', None)

    # Date and time stat information.
    stat_object.atime = getattr(self._tsk_file.info.meta, 'atime', None)
    stat_object.atime_nano = getattr(
        self._tsk_file.info.meta, 'atime_nano', None)
    stat_object.bkup_time = getattr(
        self._tsk_file.info.meta, 'bkup_time', None)
    stat_object.bkup_time_nano = getattr(
        self._tsk_file.info.meta, 'bkup_time_nano', None)
    stat_object.ctime = getattr(self._tsk_file.info.meta, 'ctime', None)
    stat_object.ctime_nano = getattr(
        self._tsk_file.info.meta, 'ctime_nano', None)
    stat_object.crtime = getattr(self._tsk_file.info.meta, 'crtime', None)
    stat_object.crtime_nano = getattr(
        self._tsk_file.info.meta, 'crtime_nano', None)
    stat_object.dtime = getattr(self._tsk_file.info.meta, 'dtime', None)
    stat_object.dtime_nano = getattr(
        self._tsk_file.info.meta, 'dtime_nano', None)
    stat_object.mtime = getattr(self._tsk_file.info.meta, 'mtime', None)
    stat_object.mtime_nano = getattr(
        self._tsk_file.info.meta, 'mtime_nano', None)

    # Ownership and permissions stat information.
    stat_object.mode = getattr(self._tsk_file.info.meta, 'mode', None)
    stat_object.uid = getattr(self._tsk_file.info.meta, 'uid', None)
    stat_object.gid = getattr(self._tsk_file.info.meta, 'gid', None)

    # File entry type stat information.
    # The type is an instance of pytsk3.TSK_FS_META_TYPE_ENUM.
    tsk_fs_meta_type = getattr(
        self._tsk_file.info.meta, 'type', pytsk3.TSK_FS_META_TYPE_UNDEF)

    if tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_REG:
      stat_object.type = stat_object.TYPE_FILE
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_DIR:
      stat_object.type = stat_object.TYPE_DIRECTORY
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_LNK:
      stat_object.type = stat_object.TYPE_LINK
    elif (tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_CHR or
          tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_BLK):
      stat_object.type = stat_object.TYPE_DEVICE
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_FIFO:
      stat_object.type = stat_object.TYPE_PIPE
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_SOCK:
      stat_object.type = stat_object.TYPE_SOCKET
    # TODO: implement support for:
    # pytsk3.TSK_FS_META_TYPE_UNDEF
    # pytsk3.TSK_FS_META_TYPE_SHAD
    # pytsk3.TSK_FS_META_TYPE_WHT
    # pytsk3.TSK_FS_META_TYPE_VIRT

    # Other stat information.
    # stat_object.ino = getattr(self._tsk_file.info.meta, 'addr', None)
    # stat_object.dev = stat_info.st_dev
    # stat_object.nlink = getattr(self._tsk_file.info.meta, 'nlink', None)
    # stat_object.fs_type = 'Unknown'

    flags = getattr(self._tsk_file.info.meta, 'flags', 0)

    # The flags are an instance of pytsk3.TSK_FS_META_FLAG_ENUM.
    if int(flags) & pytsk3.TSK_FS_META_FLAG_ALLOC:
      stat_object.allocated = True
    else:
      stat_object.allocated = False

    return stat_object

  @property
  def name(self):
    """"The name of the file entry, which does not include the full path."""
    if self._name is None:
      if self._tsk_file is None:
        self._tsk_file = self.GetTSKFile()

      # Note that because pytsk3.File does not explicitly defines info
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(self._tsk_file, 'info', None) is None:
        return

      # If pytsk3.FS_Info.open() was used file.info has an attribute name
      # (pytsk3.TSK_FS_FILE) that contains the name string. Otherwise the
      # name from the path specification is used.
      if getattr(self._tsk_file.info, 'name', None) is not None:
        self._name = getattr(self._tsk_file.info.name, 'name', None)
      else:
        location = getattr(self.path_spec, 'location', None)
        if location:
          self._name = self._file_system.BasenamePath(location)

    return self._name

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield TSKFileEntry(self._file_system, path_spec)

  def GetFileObject(self):
    """Retrieves the file-like object (instance of file_io.FileIO)."""
    if self._file_object is None:
      tsk_file_system = self._file_system.GetFsInfo()
      self._file_object = pyvfs.file_io.tsk_file_io.TSKFile(
          tsk_file_system, tsk_file=self._tsk_file)
      self._file_object.open()
    return self._file_object

  def GetParentFileEntry(self):
    """Retrieves the parent file entry."""
    location = getattr(self.path_spec, 'location', None)
    if location is None:
      return
    parent_inode = self._parent_inode
    parent_location = self._file_system.DirnamePath(location)
    if parent_inode is None and parent_location is None:
      return
    if parent_location == u'':
      parent_location = self._file_system.PATH_SEPARATOR

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=parent_inode, location=parent_location, parent=parent_path_spec)
    # TODO: is there a way to determine the parent inode number here?
    return TSKFileEntry(self._file_system, path_spec)

  def GetTSKFile(self):
    """Retrieves the SleuthKit file object (instance of pytsk3.File)."""
    if self._file_object is not None:
      tsk_file = self._file_object.GetTSKFile()

    else:
      tsk_file_system = self._file_system.GetFsInfo()

      # Opening a file by inode number is faster than opening a file
      # by location.
      inode = getattr(self.path_spec, 'inode', None)
      location = getattr(self.path_spec, 'location', None)

      if inode is not None:
        tsk_file = tsk_file_system.open_meta(inode=inode)
      elif location is not None:
        tsk_file = tsk_file_system.open(location)
      else:
        raise RuntimeError(u'Path specification missing inode and location.')

    return tsk_file

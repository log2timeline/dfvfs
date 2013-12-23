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
"""The tar file entry implementation."""

# This is necessary to prevent a circular import.
import pyvfs.file_io.tar_file_io

from pyvfs.path import tar_path_spec
from pyvfs.vfs import file_entry
from pyvfs.vfs import vfs_stat


class TarDirectory(file_entry.Directory):
  """Class that implements a directory object using tarfile."""

  def __init__(self, tar_file, path_spec):
    """Initializes the directory object.

    Args:
      tar_file: the tar file object (instance of tarfile.TarFile).
      path_spec: the path specification (instance of path.PathSpec).
    """
    super(TarDirectory, self).__init__(path_spec)
    self._tar_file = tar_file

  def _EntriesGenerator(self):
    """Retrieves directory entries.

       Since a directory can contain a vast number of entries using
       a generator is more memory efficient.

    Yields:
      A path specification (instance of path.TarPathSpec).
    """
    location = getattr(self.path_spec, 'location', None)

    if (location is None or
        not location.startswith(tar_path_spec.PATH_SEPARATOR)):
      return

    for tar_info in self._tar_file.getmembers():
      path = tar_info.name

      # Determine if the start of the tar info name is similar to
      # the location string. If not the file tar info refers to is not in
      # the same directory.  Note that the tar info name does not have the
      # leading path separator as the location string does.
      if (not path or not path.startswith(location[1:])):
        continue

      if path.endswith(tar_path_spec.PATH_SEPARATOR):
        path = path[:-1]

      path_index = len(location) - 2
      _, _, suffix = path[path_index:].partition(tar_path_spec.PATH_SEPARATOR)

      # Ignore anything that is part of a sub directory.
      if suffix:
        continue

      path_spec_location = '{0:s}{1:s}'.format(
          tar_path_spec.PATH_SEPARATOR, path)
      yield tar_path_spec.TarPathSpec(
          location=path_spec_location, parent=self.path_spec.parent)


class TarFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using tarfile."""

  def __init__(self, file_system, path_spec, tar_info=None):
    """Initializes the file entry object.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification (instance of path.PathSpec).
      tar_info: optional tar info object (instance of tarfile.TarInfo).
                The default is None.
    """
    super(TarFileEntry, self).__init__(file_system, path_spec)
    self._tar_info = tar_info
    self._directory = None
    self._file_object = None
    self._name = None
    self._stat_object = None

  def _GetDirectory(self):
    """Retrieves the directory object (instance of TarDirectory)."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      tar_file = self._file_system.GetTarFile()
      return TarDirectory(tar_file, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat)."""
    if self._tar_info is None:
      self._tar_info = self.GetTarInfo()

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = getattr(self._tar_info, 'size', None)

    # Date and time stat information.
    stat_object.mtime = getattr(self._tar_info, 'mtime', None)

    # Ownership and permissions stat information.
    stat_object.mode = getattr(self._tar_info, 'mode', None)
    stat_object.uid = getattr(self._tar_info, 'uid', None)
    stat_object.gid = getattr(self._tar_info, 'gid', None)

    # TODO: implement support for:
    # stat_object.uname = getattr(self._tar_info, 'uname', None)
    # stat_object.gname = getattr(self._tar_info, 'gname', None)

    # File entry type stat information.

    # The root file entry is virtual and should have type directory.
    if not self._tar_info or self._tar_info.isdir():
      stat_object.type = stat_object.TYPE_DIRECTORY
    elif self._tar_info.isfile():
      stat_object.type = stat_object.TYPE_FILE
    elif self._tar_info.issym() or self._tar_info.islnk():
      stat_object.type = stat_object.TYPE_LINK
    elif self._tar_info.ischr() or self._tar_info.isblk():
      stat_object.type = stat_object.TYPE_DEVICE
    elif self._tar_info.isfifo():
      stat_object.type = stat_object.TYPE_PIPE

    # TODO: determine if this covers all the types:
    # REGTYPE, AREGTYPE, LNKTYPE, SYMTYPE, DIRTYPE, FIFOTYPE, CONTTYPE,
    # CHRTYPE, BLKTYPE, GNUTYPE_SPARSE

    # Other stat information.
    # tar_info.linkname
    # tar_info.pax_headers

    stat_object.allocated = True

    return stat_object

  @property
  def name(self):
    """"The name of the file entry, which does not include the full path."""
    if self._name is None:
      if self._tar_info is None:
        self._tar_info = self.GetTarInfo()

      # Note that the root file entry is virtual and has no tar_info.
      if self._tar_info is None:
        self._name = u''
      else:
        path = getattr(self._tar_info, 'name', None)
        if path is not None:
          try:
            path.decode(self._file_system.encoding)
          except UnicodeDecodeError:
            path = None
        if path.endswith(tar_path_spec.PATH_SEPARATOR):
          path = path[:-1]
        _, _, self._name = path.rpartition(tar_path_spec.PATH_SEPARATOR)
    return self._name

  @property
  def sub_file_entries(self):
    """The sub file entries (list of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    sub_file_entries = []
    if self._directory:
      for path_spec in self._directory.entries:
        sub_file_entries.append(
            TarFileEntry(self._file_system, path_spec))
    return sub_file_entries

  def GetFileObject(self):
    """Retrieves the file-like object (instance of file_io.FileIO)."""
    if self._file_object is None:
      if self._tar_info is None:
        self._tar_info = self.GetTarInfo()

      tar_file_object = self.GetTarExFileObject()
      self._file_object = pyvfs.file_io.tar_file_io.TarFile(
          self._tar_info, tar_file_object)
      self._file_object.open()
    return self._file_object

  def GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat)."""
    if self._stat_object is None:
      self.GetStat()
    return self._stat_object

  def GetTarExFileObject(self):
    """Retrieves the tar extracted file-like object.

    Returns:
      The extracted file-like object (instance of tarfile.ExFileObject).
    """
    if self._tar_info is None:
      self._tar_info = self.GetTarInfo()

    tar_file = self._file_system.GetTarFile()
    return tar_file.extractfile(self._tar_info)

  def GetTarInfo(self):
    """Retrieves the tar info object.

    Returns:
      The tar info object (instance of tarfile.TarInfo).

    Raises:
      ValueError: if the path specification is incorrect.
    """
    location = getattr(self.path_spec, 'location', None)

    if location is None:
      raise ValueError(u'Path specification missing location.')

    if not location.startswith(self._file_system.LOCATION_ROOT):
      raise ValueError(u'Invalid location in path specification.')

    if len(location) == 1:
      return None

    tar_file = self._file_system.GetTarFile()
    return tar_file.getmember(location[1:])

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The dfVFS Project Authors.
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
"""The zip file entry implementation."""

import calendar

# This is necessary to prevent a circular import.
import dfvfs.file_io.zip_file_io

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import zip_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


class ZipDirectory(file_entry.Directory):
  """Class that implements a directory object using zipfile."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

       Since a directory can contain a vast number of entries using
       a generator is more memory efficient.

    Yields:
      A path specification (instance of path.ZipPathSpec).
    """
    location = getattr(self.path_spec, 'location', None)

    if (location is None or
        not location.startswith(self._file_system.PATH_SEPARATOR)):
      return

    zip_file = self._file_system.GetZipFile()
    for zip_info in zip_file.infolist():
      path = zip_info.filename

      if (not path or not path.startswith(location[1:])):
        continue

      _, suffix = self._file_system.GetPathSegmentAndSuffix(location[1:], path)

      # Ignore anything that is part of a sub directory.
      if suffix:
        continue

      path_spec_location = self._file_system.JoinPath([path])
      yield zip_path_spec.ZipPathSpec(
          location=path_spec_location, parent=self.path_spec.parent)


class ZipFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using zipfile."""

  _CREATOR_SYSTEM_MSDOS_COMPATIBLE = 0
  _CREATOR_SYSTEM_UNIX = 3
  _CREATOR_SYSTEM_WINDOWS_NT = 10
  _CREATOR_SYSTEM_VFAT = 14
  _CREATOR_SYSTEM_MACOSX = 19

  _MSDOS_FILE_ATTRIBUTES_IS_DIRECTORY = 0x10

  _UNIX_FILE_ATTRIBUTES_IS_DIRECTORY = 0x8000

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_ZIP

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, zip_info=None):
    """Initializes the file entry object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification (instance of path.PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
               The default is False.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system. The default is False.
      zip_info: optional zip info object (instance of zipfile.ZipInfo).
                The default is None.
    """
    super(ZipFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._zip_info = zip_info
    self._name = None

  def _GetDirectory(self):
    """Retrieves the directory object (instance of ZipDirectory)."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return ZipDirectory(self._file_system, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the zip info is missing in a non-virtual file entry.
    """
    if self._zip_info is None:
      self._zip_info = self.GetZipInfo()

    if not self._is_virtual and self._zip_info is None:
      raise errors.BackEndError(u'Missing zip info in non-virtual file entry.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    if self._zip_info is not None:
      stat_object.size = getattr(self._zip_info, 'size', None)

    # Date and time stat information.
    # TODO: move this to a timelib equivalent.
    date_time = getattr(self._zip_info, 'date_time', None)
    if date_time:
      stat_object.mtime = calendar.timegm(date_time)

    # Ownership and permissions stat information.
    if self._zip_info is not None:
      creator_system = getattr(self._zip_info, 'create_system', 0)
      external_attributes = getattr(self._zip_info, 'external_attr', 0)

      if external_attributes != 0:
        if creator_system == self._CREATOR_SYSTEM_UNIX:
          st_mode = external_attributes >> 16
          stat_object.mode = st_mode & 0x0fff

    # File entry type stat information.

    # The root file entry is virtual and should have type directory.
    if (self._is_virtual or
        external_attributes & self._MSDOS_FILE_ATTRIBUTES_IS_DIRECTORY):
      stat_object.type = stat_object.TYPE_DIRECTORY
    else:
      stat_object.type = stat_object.TYPE_FILE

    # Other stat information.
    # zip_info.compress_type
    # zip_info.comment
    # zip_info.extra
    # zip_info.create_version
    # zip_info.extract_version
    # zip_info.flag_bits
    # zip_info.volume
    # zip_info.internal_attr
    # zip_info.compress_size

    return stat_object

  @property
  def name(self):
    """"The name of the file entry, which does not include the full path."""
    if self._name is None:
      if self._zip_info is None:
        self._zip_info = self.GetZipInfo()

      # Note that the root file entry is virtual and has no zip_info.
      if self._zip_info is None:
        self._name = u''
      else:
        self._name = self._file_system.BasenamePath(self._zip_info.filename)
    return self._name

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield ZipFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetFileObject(self):
    """Retrieves the file-like object (instance of file_io.FileIO)."""
    if self._zip_info is None:
      self._zip_info = self.GetZipInfo()

    zip_file = self.GetZipFile()
    file_object = dfvfs.file_io.zip_file_io.ZipFile(
          self._resolver_context, zip_info=self._zip_info, zip_file=zip_file)
    file_object.open()
    return file_object

  def GetParentFileEntry(self):
    """Retrieves the parent file entry."""
    location = getattr(self.path_spec, 'location', None)
    if location is None:
      return
    parent_location = self._file_system.DirnamePath(location)
    if parent_location is None:
      return
    if parent_location == u'':
      parent_location = self._file_system.PATH_SEPARATOR

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = zip_path_spec.ZipPathSpec(
        location=parent_location, parent=parent_path_spec)
    return ZipFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetZipFile(self):
    """Retrieves the zip file object.

    Returns:
      The zip file object (instance of zipfile.ZipFile).
    """
    return self._file_system.GetZipFile()

  def GetZipInfo(self):
    """Retrieves the zip info object.

    Returns:
      The zip info object (instance of zipfile.ZipInfo).

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

    zip_file = self._file_system.GetZipFile()
    return zip_file.getinfo(location[1:])

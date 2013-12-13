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
"""The zip file entry implementation."""

# This is necessary to prevent a circular import.
import pyvfs.io.zip_file_io

from pyvfs.path import zip_path_spec
from pyvfs.vfs import file_entry
from pyvfs.vfs import vfs_stat


class ZipDirectory(file_entry.Directory):
  """Class that implements a directory object using zipfile."""

  def __init__(self, zip_file, path_spec):
    """Initializes the directory object.

    Args:
      zip_file: the zip file object (instance of zipfile.ZipFile).
      path_spec: the path specification (instance of path.PathSpec).
    """
    super(ZipDirectory, self).__init__(path_spec)
    self._zip_file = zip_file

  def _EntriesGenerator(self):
    """Retrieves directory entries.

       Since a directory can contain a vast number of entries using
       a generator is more memory efficient.

    Yields:
      A path specification (instance of path.ZipPathSpec).
    """
    location = getattr(self.path_spec, 'location', None)

    if (location is None or
        not location.startswith(zip_path_spec.PATH_SEPARATOR)):
      return

    for zip_info in self._zip_file.infolist():
      path = zip_info.filename

      if (not path or not path.startswith(location[1:])):
        continue

      if path.endswith(zip_path_spec.PATH_SEPARATOR):
        path = path[:-1]

      path_index = len(location) - 2
      _, _, suffix = path[path_index:].partition(zip_path_spec.PATH_SEPARATOR)

      # Ignore anything that is part of a sub directory.
      if suffix:
        continue

      path_spec_location = u'{0:s}{1:s}'.format(
          zip_path_spec.PATH_SEPARATOR, path)
      yield zip_path_spec.ZipPathSpec(path_spec_location, self.path_spec.parent)


class ZipFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using zipfile."""

  _CREATOR_SYSTEM_MSDOS_COMPATIBLE = 0
  _CREATOR_SYSTEM_UNIX = 3
  _CREATOR_SYSTEM_WINDOWS_NT = 10
  _CREATOR_SYSTEM_VFAT = 14
  _CREATOR_SYSTEM_MACOSX = 19

  _MSDOS_FILE_ATTRIBUTES_IS_DIRECTORY = 0x10

  _UNIX_FILE_ATTRIBUTES_IS_DIRECTORY = 0x8000

  def __init__(self, file_system, path_spec, zip_info=None):
    """Initializes the file entry object.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification (instance of path.PathSpec).
      zip_info: optional zip info object (instance of zipfile.ZipInfo).
                The default is None.
    """
    super(ZipFileEntry, self).__init__(file_system, path_spec)
    self._zip_info = zip_info
    self._directory = None
    self._file_object = None
    self._name = None
    self._stat_object = None

  def _GetDirectory(self):
    """Retrieves the directory object (instance of ZipDirectory)."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      zip_file = self._file_system.GetZipFile()
      return ZipDirectory(zip_file, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat)."""
    if self._zip_info is None:
      self._zip_info = self.GetZipInfo()

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = getattr(self._zip_info, 'size', None)

    # Date and time stat information.
    # TODO: determine how to standarize these time values.
    # date_time = getattr(self._zip_info, 'date_time', None)
    # year, month, day_of_month, hours, minutes, seconds = date_time

    # Ownership and permissions stat information.
    creator_system = getattr(self._zip_info, 'create_system', 0)
    external_attributes = getattr(self._zip_info, 'external_attr', 0)

    if external_attributes != 0:
      if creator_system == self._CREATOR_SYSTEM_UNIX:
        st_mode = external_attributes >> 16
        stat_object.mode = st_mode & 0x0fff

    # File entry type stat information.

    # The root file entry is virtual and should have type directory.
    if (not self._zip_info or
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

    stat_object.allocated = True

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
        path = self._zip_info.filename
        if path.endswith(zip_path_spec.PATH_SEPARATOR):
          path = path[:-1]
        _, _, self._name = path.rpartition(zip_path_spec.PATH_SEPARATOR)
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
            ZipFileEntry(self._file_system, path_spec))
    return sub_file_entries

  def GetFileObject(self):
    """Retrieves the file-like object (instance of io.FileIO) of the data."""
    if self._file_object is None:
      if self._zip_info is None:
        self._zip_info = self.GetZipInfo()

      zip_file = self.GetZipFile()
      self._file_object = pyvfs.io.zip_file_io.ZipFile(self._zip_info, zip_file)
      self._file_object.open()
    return self._file_object

  def GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat)."""
    if self._stat_object is None:
      self.GetStat()
    return self._stat_object

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

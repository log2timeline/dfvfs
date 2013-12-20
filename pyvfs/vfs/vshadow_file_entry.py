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
"""The Volume Shadow Snapshots (VSS) file entry implementation."""

# This is necessary to prevent a circular import.
import pyvfs.file_io.vshadow_file_io

from pyvfs.path import vshadow_path_spec
from pyvfs.vfs import file_entry
from pyvfs.vfs import vfs_stat


class VShadowDirectory(file_entry.Directory):
  """Class that implements a directory object using pyvshadow."""

  def __init__(self, vshadow_volume, path_spec):
    """Initializes the directory object.

    Args:
      vshadow_volume: the VSS volume file object (instance of pyvshadow.volume).
      path_spec: the path specification (instance of path.PathSpec) of
                 the file-like object.
    """
    super(VShadowDirectory, self).__init__(path_spec)
    self._vshadow_volume = vshadow_volume

  def _EntriesGenerator(self):
    """Retrieves directory entries.

       Since a directory can contain a vast number of entries using
       a generator is more memory efficient.

    Yields:
      A path specification (instance of path.VShadowPathSpec).
    """
    store_index = getattr(self.path_spec, 'store_index', None)

    if store_index is not None:
      return

    for store_index in range(0, self._vshadow_volume.number_of_stores):
      yield vshadow_path_spec.VShadowPathSpec(
          store_index=store_index, parent=self.path_spec.parent)


class VShadowFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using pyvshadow."""

  def __init__(self, file_system, path_spec):
    """Initializes the file entry object.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification (instance of path.PathSpec).
    """
    super(VShadowFileEntry, self).__init__(file_system, path_spec)
    self._directory = None
    self._file_object = None
    self._name = None
    self._stat_object = None
    self._vshadow_store = None

  def _GetDirectory(self):
    """Retrieves the directory object (instance of VShadowDirectory)."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if self._stat_object is None:
      vshadow_volume = self._file_system.GetVShadowVolume()
      return VShadowDirectory(vshadow_volume, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat)."""
    if self._vshadow_store is None:
      self._vshadow_store = self.GetVShadowStore()

    # TODO: rewrite file entry a bit to expose more clear what is virtual
    # and what not.

    # The virtual root file entry has no stat information.
    if self._vshadow_store is None:
      return None

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    stat_object.size = self._vshadow_store.volume_size

    # Date and time stat information.

    # Ownership and permissions stat information.

    # File entry type stat information.

    # The root file entry is virtual and should have type directory.

    return stat_object

  @property
  def name(self):
    """"The name of the file entry, which does not include the full path."""
    if self._name is None:
      store_index = getattr(self.path_spec, 'store_index', None)

      if store_index is None:
        self._name = u''
      else:
        self._name = u'vss{0:d}'.format(store_index + 1)
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
            VShadowFileEntry(self._file_system, path_spec))
    # TODO: change to generator.
    return sub_file_entries

  def GetFileObject(self):
    """Retrieves the file-like object (instance of io.FileIO) of the data."""
    if self._file_object is None:
      if self._vshadow_store is None:
        self._vshadow_store = self.GetVShadowStore()

      vshadow_volume = self._file_system.GetVShadowVolume()
      self._file_object = pyvfs.file_io.vshadow_file_io.VShadowFile(
          vshadow_volume, self._vshadow_store)
      self._file_object.open()
    return self._file_object

  def GetStat(self):
    """Retrieves the stat object (instance of vfs.VFSStat)."""
    if self._stat_object is None:
      self.GetStat()
    return self._stat_object

  def GetVShadowStore(self):
    """Retrieves the VSS store object (instance of pyvshadow.store)."""
    store_index = getattr(self.path_spec, 'store_index', None)

    if store_index is None:
      return

    vshadow_volume = self._file_system.GetVShadowVolume()
    return vshadow_volume.get_store(store_index)

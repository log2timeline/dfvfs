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
"""The Volume Shadow Snapshots (VSS) file entry implementation."""

# This is necessary to prevent a circular import.
import dfvfs.file_io.vshadow_file_io

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import vshadow
from dfvfs.path import vshadow_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


class VShadowDirectory(file_entry.Directory):
  """Class that implements a directory object using pyvshadow."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

       Since a directory can contain a vast number of entries using
       a generator is more memory efficient.

    Yields:
      A path specification (instance of path.VShadowPathSpec).
    """
    # Only the virtual root file has directory entries.
    store_index = getattr(self.path_spec, 'store_index', None)
    if store_index is not None:
      return

    location = getattr(self.path_spec, 'location', None)
    if location is None or location != self._file_system.LOCATION_ROOT:
      return

    vshadow_volume = self._file_system.GetVShadowVolume()

    for store_index in range(0, vshadow_volume.number_of_stores):
      yield vshadow_path_spec.VShadowPathSpec(
          location=u'/vss{0:d}'.format(store_index + 1),
          store_index=store_index, parent=self.path_spec.parent)


class VShadowFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using pyvshadow."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VSHADOW

  def __init__(self, file_system, path_spec, is_root=False, is_virtual=False):
    """Initializes the file entry object.

    Args:
      file_system: the file system object (instance of vfs.FileSystem).
      path_spec: the path specification (instance of path.PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
               The default is False.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system. The default is False.
    """
    super(VShadowFileEntry, self).__init__(
        file_system, path_spec, is_root=is_root, is_virtual=is_virtual)
    self._file_object = None
    self._name = None
    self._vshadow_store = None

  def _GetDirectory(self):
    """Retrieves the directory object (instance of VShadowDirectory)."""
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return VShadowDirectory(self._file_system, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of vfs.VFSStat).

    Raises:
      BackEndError: when the vshadow store is missing in a non-virtual
                    file entry.
    """
    if self._vshadow_store is None:
      self._vshadow_store = self.GetVShadowStore()

    if not self._is_virtual and self._vshadow_store is None:
      raise errors.BackEndError(
          u'Missing vshadow store in non-virtual file entry.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    if self._vshadow_store is not None:
      stat_object.size = self._vshadow_store.volume_size

    # Date and time stat information.

    # Ownership and permissions stat information.

    # File entry type stat information.

    # The root file entry is virtual and should have type directory.
    if self._is_virtual:
      stat_object.type = stat_object.TYPE_DIRECTORY
    else:
      stat_object.type = stat_object.TYPE_FILE

    return stat_object

  @property
  def name(self):
    """"The name of the file entry, which does not include the full path."""
    if self._name is None:
      location = getattr(self.path_spec, 'location', None)
      if location is not None:
        self._name = self._file_system.BasenamePath(location)
      else:
        store_index = getattr(self.path_spec, 'store_index', None)
        if store_index is not None:
          self._name = u'vss{0:d}'.format(store_index + 1)
        else:
          self._name = u''
    return self._name

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of vfs.FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield VShadowFileEntry(self._file_system, path_spec)

  def GetFileObject(self):
    """Retrieves the file-like object (instance of file_io.FileIO)."""
    if self._file_object is None:
      if self._vshadow_store is None:
        self._vshadow_store = self.GetVShadowStore()

      vshadow_volume = self._file_system.GetVShadowVolume()
      self._file_object = dfvfs.file_io.vshadow_file_io.VShadowFile(
          vshadow_volume, self._vshadow_store)
      self._file_object.open()
    return self._file_object

  def GetParentFileEntry(self):
    """Retrieves the parent file entry."""
    return

  def GetVShadowStore(self):
    """Retrieves the VSS store object (instance of pyvshadow.store)."""
    store_index = vshadow.VShadowPathSpecGetStoreIndex(self.path_spec)
    if store_index is None:
      return

    vshadow_volume = self._file_system.GetVShadowVolume()
    return vshadow_volume.get_store(store_index)

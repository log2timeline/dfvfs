# -*- coding: utf-8 -*-
"""The Volume Shadow Snapshots (VSS) file entry implementation."""

from __future__ import unicode_literals

from dfdatetime import filetime as dfdatetime_filetime

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import vshadow
from dfvfs.path import vshadow_path_spec
from dfvfs.vfs import file_entry


class VShadowDirectory(file_entry.Directory):
  """File system directory that uses pyvshadow."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      VShadowPathSpec: a path specification.
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
          location='/vss{0:d}'.format(store_index + 1),
          store_index=store_index, parent=self.path_spec.parent)


class VShadowFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyvshadow."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VSHADOW

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.

    Raises:
      BackEndError: when the vshadow store is missing in a non-virtual
          file entry.
    """
    vshadow_store = file_system.GetVShadowStoreByPathSpec(path_spec)
    if not is_virtual and vshadow_store is None:
      raise errors.BackEndError(
          'Missing vshadow store in non-virtual file entry.')

    super(VShadowFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._name = None
    self._vshadow_store = vshadow_store

    if self._is_virtual:
      self._type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    else:
      self._type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      VShadowDirectory: a directory None if not available.
    """
    if self._type == definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return VShadowDirectory(self._file_system, self.path_spec)

  def _GetStat(self):
    """Retrieves information about the file entry.

    Returns:
      VFSStat: a stat object.
    """
    stat_object = super(VShadowFileEntry, self)._GetStat()

    if self._vshadow_store is not None:
      # File data stat information.
      stat_object.size = self._vshadow_store.volume_size

    # Ownership and permissions stat information.

    # File entry type stat information.

    # The root file entry is virtual and should have type directory.
    return stat_object

  @property
  def creation_time(self):
    """dfdatetime.DateTimeValues: creation time or None if not available."""
    if self._vshadow_store is not None:
      timestamp = self._vshadow_store.get_creation_time_as_integer()
      return dfdatetime_filetime.Filetime(timestamp=timestamp)

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path."""
    if self._name is None:
      location = getattr(self.path_spec, 'location', None)
      if location is not None:
        self._name = self._file_system.BasenamePath(location)
      else:
        store_index = getattr(self.path_spec, 'store_index', None)
        if store_index is not None:
          self._name = 'vss{0:d}'.format(store_index + 1)
        else:
          self._name = ''
    return self._name

  @property
  def sub_file_entries(self):
    """generator[FileEntry]: sub file entries."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield VShadowFileEntry(
            self._resolver_context, self._file_system, path_spec)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      FileEntry: parent file entry or None if not available.
    """
    store_index = vshadow.VShadowPathSpecGetStoreIndex(self.path_spec)
    if store_index is None:
      return

    return self._file_system.GetRootFileEntry()

  def GetVShadowStore(self):
    """Retrieves a VSS store.

    Returns:
      pyvshadow.store: a VSS store or None if not available.
    """
    return self._vshadow_store

  def HasExternalData(self):
    """Determines if the file entry has external stored data.

    Returns:
      bool: True if the file entry has external data.
    """
    if self._vshadow_store is None:
      return False

    return not self._vshadow_store.has_in_volume_data()

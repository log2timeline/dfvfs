# -*- coding: utf-8 -*-
"""The Volume Shadow Snapshots (VSS) file entry implementation."""

from dfdatetime import filetime as dfdatetime_filetime

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
    store_index = getattr(self.path_spec, u'store_index', None)
    if store_index is not None:
      return

    location = getattr(self.path_spec, u'location', None)
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

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes the file entry object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      file_system: the file system object (instance of FileSystem).
      path_spec: the path specification (instance of PathSpec).
      is_root: optional boolean value to indicate if the file entry is
               the root file entry of the corresponding file system.
      is_virtual: optional boolean value to indicate if the file entry is
                  a virtual file entry emulated by the corresponding file
                  system.
    """
    super(VShadowFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._name = None

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      A directory object (instance of Directory) or None.
    """
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
    vshadow_store = self.GetVShadowStore()
    if not self._is_virtual and vshadow_store is None:
      raise errors.BackEndError(
          u'Missing vshadow store in non-virtual file entry.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    if vshadow_store is not None:
      stat_object.size = vshadow_store.volume_size

    # Date and time stat information.
    if vshadow_store is not None:
      timestamp = vshadow_store.get_creation_time_as_integer()
      date_time_values = dfdatetime_filetime.Filetime(timestamp=timestamp)

      stat_time, stat_time_nano = date_time_values.CopyToStatTimeTuple()
      if stat_time is not None:
        stat_object.crtime = stat_time
        stat_object.crtime_nano = stat_time_nano

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
    """The name of the file entry, which does not include the full path."""
    if self._name is None:
      location = getattr(self.path_spec, u'location', None)
      if location is not None:
        self._name = self._file_system.BasenamePath(location)
      else:
        store_index = getattr(self.path_spec, u'store_index', None)
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
        yield VShadowFileEntry(
            self._resolver_context, self._file_system, path_spec)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      The parent file entry (instance of FileEntry) or None.
    """
    store_index = vshadow.VShadowPathSpecGetStoreIndex(self.path_spec)
    if store_index is None:
      return

    return self._file_system.GetRootFileEntry()

  def GetVShadowStore(self):
    """Retrieves a VSS store.

    Returns:
      A VSS store object (instance of pyvshadow.store).
    """
    store_index = vshadow.VShadowPathSpecGetStoreIndex(self.path_spec)
    if store_index is None:
      return

    vshadow_volume = self._file_system.GetVShadowVolume()
    return vshadow_volume.get_store(store_index)

  def HasExternalData(self):
    """Determines if the file entry has external stored data.

    Returns:
      A boolean to indicate the file entry has external data.

    Raises:
      BackEndError: when the vshadow store is missing in a non-virtual
                    file entry.
    """
    vshadow_store = self.GetVShadowStore()
    if not self._is_virtual and vshadow_store is None:
      raise errors.BackEndError(
          u'Missing vshadow store in non-virtual file entry.')

    if vshadow_store is None:
      return False

    return not vshadow_store.has_in_volume_data()

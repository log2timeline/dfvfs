# -*- coding: utf-8 -*-
"""The Volume Shadow Snapshots (VSS) file entry implementation."""

from dfdatetime import filetime as dfdatetime_filetime

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import vshadow_helper
from dfvfs.vfs import file_entry
from dfvfs.vfs import vshadow_directory


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
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    else:
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      VShadowDirectory: a directory.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return vshadow_directory.VShadowDirectory(self._file_system, self.path_spec)

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      VShadowFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield VShadowFileEntry(
            self._resolver_context, self._file_system, path_spec)

  @property
  def creation_time(self):
    """dfdatetime.DateTimeValues: creation time or None if not available."""
    if self._vshadow_store is None:
      return None

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
          vss_store_index = store_index + 1
          self._name = f'vss{vss_store_index:d}'
        else:
          self._name = ''

    return self._name

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    if self._vshadow_store is None:
      return None

    return self._vshadow_store.volume_size

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      FileEntry: parent file entry or None if not available.
    """
    store_index = vshadow_helper.VShadowPathSpecGetStoreIndex(self.path_spec)
    if store_index is None:
      return None

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

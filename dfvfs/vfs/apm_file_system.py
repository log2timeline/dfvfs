# -*- coding: utf-8 -*-
"""The Apple Partition Map (APM) file system implementation."""

import pyvsapm

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import apm_helper
from dfvfs.path import apm_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import apm_file_entry


class APMFileSystem(file_system.FileSystem):
  """File system that uses pyvsapm."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APM

  def __init__(self, resolver_context, path_spec):
    """Initializes a file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(APMFileSystem, self).__init__(resolver_context, path_spec)
    self._file_object = None
    self._vsapm_volume = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._vsapm_volume.close()
    self._vsapm_volume = None
    self._file_object = None

  def _Open(self, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not self._path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        self._path_spec.parent, resolver_context=self._resolver_context)

    vsapm_volume = pyvsapm.volume()
    vsapm_volume.open_file_object(file_object)

    self._file_object = file_object
    self._vsapm_volume = vsapm_volume

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.
    """
    entry_index = apm_helper.APMPathSpecGetEntryIndex(path_spec)

    # The virtual root file has no corresponding partition entry index but
    # should have a location.
    if entry_index is None:
      location = getattr(path_spec, 'location', None)
      return location is not None and location == self.LOCATION_ROOT

    return 0 <= entry_index < self._vsapm_volume.number_of_partitions

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      APMFileEntry: a file entry or None if not available.
    """
    entry_index = apm_helper.APMPathSpecGetEntryIndex(path_spec)

    # The virtual root file has no corresponding partition entry index but
    # should have a location.
    if entry_index is None:
      location = getattr(path_spec, 'location', None)
      if location is None or location != self.LOCATION_ROOT:
        return None

      return apm_file_entry.APMFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    if (0 < entry_index or
        entry_index >= self._vsapm_volume.number_of_partitions):
      return None

    return apm_file_entry.APMFileEntry(self._resolver_context, self, path_spec)

  def GetAPMPartitionByPathSpec(self, path_spec):
    """Retrieves a APM partition for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      pyvsapm.partition: a APM partition or None if not available.
    """
    entry_index = apm_helper.APMPathSpecGetEntryIndex(path_spec)
    if entry_index is None:
      return None
    return self._vsapm_volume.get_partition(entry_index)

  def GetAPMVolume(self):
    """Retrieves the APM volume.

    Returns:
      pyvsapm.volume: a APM volume.
    """
    return self._vsapm_volume

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      APMFileEntry: root file entry or None if not available.
    """
    path_spec = apm_path_spec.APMPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

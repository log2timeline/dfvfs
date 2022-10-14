# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) partition file system implementation."""

import pytsk3

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import tsk_image
from dfvfs.lib import tsk_partition
from dfvfs.path import tsk_partition_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import tsk_partition_file_entry


class TSKPartitionFileSystem(file_system.FileSystem):
  """Class that implements a file system object using pytsk3."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK_PARTITION

  def __init__(self, resolver_context, path_spec):
    """Initializes a file system object.

    Args:
      resolver_context (Context): a resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(TSKPartitionFileSystem, self).__init__(resolver_context, path_spec)
    self._file_object = None
    self._tsk_volume = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._tsk_volume = None
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

    tsk_image_object = tsk_image.TSKFileSystemImage(file_object)
    tsk_volume = pytsk3.Volume_Info(tsk_image_object)

    self._file_object = file_object
    self._tsk_volume = tsk_volume

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      bool: True if the file entry exists or false otherwise.
    """
    tsk_vs_part, _ = tsk_partition.GetTSKVsPartByPathSpec(
        self._tsk_volume, path_spec)

    # The virtual root file has no corresponding TSK volume system part object
    # but should have a location.
    if tsk_vs_part is None:
      location = getattr(path_spec, 'location', None)
      return location is not None and location == self.LOCATION_ROOT

    return True

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Returns:
      TSKPartitionFileEntry: a file entry or None of not available.
    """
    tsk_vs_part, partition_index = tsk_partition.GetTSKVsPartByPathSpec(
        self._tsk_volume, path_spec)

    location = getattr(path_spec, 'location', None)

    # The virtual root file has no corresponding TSK volume system part object
    # but should have a location.
    if tsk_vs_part is None:
      if location is None or location != self.LOCATION_ROOT:
        return None

      return tsk_partition_file_entry.TSKPartitionFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    if location is None and partition_index is not None:
      path_spec.location = f'/p{partition_index:d}'

    return tsk_partition_file_entry.TSKPartitionFileEntry(
        self._resolver_context, self, path_spec)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      TSKPartitionFileEntry: a file entry or None of not available.
    """
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

  def GetTSKVolume(self):
    """Retrieves the TSK volume object.

    Returns:
      pytsk3.Volume_Info: a TSK volume object.
    """
    return self._tsk_volume

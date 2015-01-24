# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) partition file system implementation."""

# This is necessary to prevent a circular import.
import dfvfs.vfs.tsk_partition_file_entry

from dfvfs.lib import definitions
from dfvfs.lib import tsk_partition
from dfvfs.path import tsk_partition_path_spec
from dfvfs.vfs import file_system


class TSKPartitionFileSystem(file_system.FileSystem):
  """Class that implements a file system object using pytsk3."""

  LOCATION_ROOT = u'/'
  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK_PARTITION

  def __init__(self, resolver_context, tsk_volume, path_spec):
    """Initializes the file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
      tsk_volume: the TSK volume object (instance of pytsk.Volume_Info).
      path_spec: the path specification (instance of path.PathSpec) of
                 the file-like object.
    """
    super(TSKPartitionFileSystem, self).__init__(resolver_context)
    self._tsk_volume = tsk_volume
    self._path_spec = path_spec

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    tsk_vs_part, _ = tsk_partition.GetTSKVsPartByPathSpec(
        self._tsk_volume, path_spec)

    # The virtual root file has not corresponding TSK volume system part object
    # but should have a location.
    if tsk_vs_part is None:
      location = getattr(path_spec, 'location', None)
      return location is not None and location == self.LOCATION_ROOT

    return True

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of path.PathSpec).

    Returns:
      A file entry (instance of vfs.TSKPartitionFileEntry) or None.
    """
    tsk_vs_part, partition_index = tsk_partition.GetTSKVsPartByPathSpec(
        self._tsk_volume, path_spec)

    location = getattr(path_spec, 'location', None)

    # The virtual root file has not corresponding TSK volume system part object
    # but should have a location.
    if tsk_vs_part is None:
      if location is None or location != self.LOCATION_ROOT:
        return
      return self.GetRootFileEntry()

    if location is None and partition_index is not None:
      path_spec.location = u'/p{0:d}'.format(partition_index)

    return dfvfs.vfs.tsk_partition_file_entry.TSKPartitionFileEntry(
        self._resolver_context, self, path_spec)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec)
    return dfvfs.vfs.tsk_partition_file_entry.TSKPartitionFileEntry(
        self._resolver_context, self, path_spec, is_root=True, is_virtual=True)

  def GetTSKVolume(self):
    """Retrieves the TSK volume object.

    Returns:
      The TSK volume object (instance of pytsk3.Volume_Info).
    """
    return self._tsk_volume

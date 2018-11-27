# -*- coding: utf-8 -*-
"""The Apple File System (APFS) volume system."""

from __future__ import unicode_literals

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.resolver import resolver
from dfvfs.volume import volume_system


class APFSVolume(volume_system.Volume):
  """Volume that uses pyfsapfs."""

  def __init__(self, file_entry):
    """Initializes an APFS volume.

    Args:
      file_entry (APFSContainerFileEntry): an APFS container file entry.
    """
    super(APFSVolume, self).__init__(file_entry.name)
    self._file_entry = file_entry

  def _Parse(self):
    """Extracts attributes and extents from the volume."""
    fsapfs_volume = self._file_entry.GetAPFSVolume()

    volume_attribute = volume_system.VolumeAttribute(
        'identifier', fsapfs_volume.identifier)
    self._AddAttribute(volume_attribute)

    volume_attribute = volume_system.VolumeAttribute(
        'name', fsapfs_volume.name)
    self._AddAttribute(volume_attribute)

    # TODO: implement in pyfsapfs
    # TODO: add support for creation time
    # TODO: add support for volume size


class APFSVolumeSystem(volume_system.VolumeSystem):
  """Volume system that uses pyfsapfs."""

  def __init__(self):
    """Initializes a volume system.

    Raises:
      VolumeSystemError: if the volume system could not be accessed.
    """
    super(APFSVolumeSystem, self).__init__()
    self._file_system = None

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    root_file_entry = self._file_system.GetRootFileEntry()

    for sub_file_entry in root_file_entry.sub_file_entries:
      volume = APFSVolume(sub_file_entry)
      self._AddVolume(volume)

  def Open(self, path_spec):
    """Opens a volume defined by path specification.

    Args:
      path_spec (PathSpec): a path specification.

    Raises:
      VolumeSystemError: if the APFS virtual file system could not be resolved.
    """
    self._file_system = resolver.Resolver.OpenFileSystem(path_spec)
    if self._file_system is None:
      raise errors.VolumeSystemError('Unable to resolve path specification.')

    type_indicator = self._file_system.type_indicator
    if type_indicator != definitions.TYPE_INDICATOR_APFS_CONTAINER:
      raise errors.VolumeSystemError('Unsupported type indicator.')

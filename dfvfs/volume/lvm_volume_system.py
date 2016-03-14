# -*- coding: utf-8 -*-
"""Volume system object implementation using Logical Volume Manager (LVM)."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.resolver import resolver
from dfvfs.volume import volume_system


class LVMVolume(volume_system.Volume):
  """Class that implements a volume object using pyvslvm."""

  def __init__(self, file_entry):
    """Initializes the volume object.

    Args:
      file_entry: the LVM file entry object (instance of FileEntry).
    """
    super(LVMVolume, self).__init__(file_entry.name)
    self._file_entry = file_entry

  def _Parse(self):
    """Extracts attributes and extents from the volume."""
    vslvm_logical_volume = self._file_entry.GetLVMLogicalVolume()

    self._AddAttribute(volume_system.VolumeAttribute(
        u'identifier', vslvm_logical_volume.identifier))
    # TODO: implement in pyvslvm
    # self._AddAttribute(volume_system.VolumeAttribute(
    #    u'creation_time', vslvm_logical_volume.get_creation_time_as_integer()))

    # TODO: add support for logical volume extents
    volume_extent = volume_system.VolumeExtent(0, vslvm_logical_volume.size)
    self._extents.append(volume_extent)


class LVMVolumeSystem(volume_system.VolumeSystem):
  """Class that implements a volume system object using pyvslvm."""

  def __init__(self):
    """Initializes the volume system object.

    Raises:
      VolumeSystemError: if the volume system could not be accessed.
    """
    super(LVMVolumeSystem, self).__init__()
    self._file_system = None

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    root_file_entry = self._file_system.GetRootFileEntry()

    for sub_file_entry in root_file_entry.sub_file_entries:
      volume = LVMVolume(sub_file_entry)
      self._AddVolume(volume)

  def Open(self, path_spec):
    """Opens a volume object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Raises:
      VolumeSystemError: if the LVM virtual file system could not be resolved.
    """
    self._file_system = resolver.Resolver.OpenFileSystem(path_spec)
    if self._file_system is None:
      raise errors.VolumeSystemError(
          u'Unable to resolve file system from path specification.')

    type_indicator = self._file_system.type_indicator
    if type_indicator != definitions.TYPE_INDICATOR_LVM:
      raise errors.VolumeSystemError(u'Unsupported file system type.')

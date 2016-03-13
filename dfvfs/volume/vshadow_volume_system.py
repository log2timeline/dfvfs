# -*- coding: utf-8 -*-
"""Volume system object implementation using Volume Shadow Snapshots (VSS)."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.resolver import resolver
from dfvfs.volume import volume_system


class VShadowVolume(volume_system.Volume):
  """Class that implements a volume object using pyvshadow."""

  def __init__(self, file_entry):
    """Initializes the volume object.

    Args:
      file_entry: a VSS file entry object (instance of FileEntry).
    """
    super(VShadowVolume, self).__init__(file_entry.name)
    self._file_entry = file_entry

  def _Parse(self):
    """Extracts attributes and extents from the volume."""
    vshadow_store = self._file_entry.GetVShadowStore()

    self._AddAttribute(volume_system.VolumeAttribute(
        u'identifier', vshadow_store.identifier))
    self._AddAttribute(volume_system.VolumeAttribute(
        u'copy_identifier', vshadow_store.copy_identifier))
    self._AddAttribute(volume_system.VolumeAttribute(
        u'copy_set_identifier', vshadow_store.copy_set_identifier))
    self._AddAttribute(volume_system.VolumeAttribute(
        u'creation_time', vshadow_store.get_creation_time_as_integer()))

    volume_extent = volume_system.VolumeExtent(0, vshadow_store.volume_size)
    self._extents.append(volume_extent)

  def HasExternalData(self):
    """Determines if the volume has external stored data.

    Returns:
      A boolean to indicate the volume has external stored data.
    """
    vshadow_store = self._file_entry.GetVShadowStore()

    return not vshadow_store.has_in_volume_data()


class VShadowVolumeSystem(volume_system.VolumeSystem):
  """Class that implements a volume system object using pyvshadow."""

  def __init__(self):
    """Initializes the volume system object.

    Raises:
      VolumeSystemError: if the volume system could not be accessed.
    """
    super(VShadowVolumeSystem, self).__init__()
    self._file_system = None

  def _Parse(self):
    """Extracts sections and volumes from the volume system."""
    root_file_entry = self._file_system.GetRootFileEntry()

    for sub_file_entry in root_file_entry.sub_file_entries:
      volume = VShadowVolume(sub_file_entry)
      self._AddVolume(volume)

  def Open(self, path_spec):
    """Opens a volume object defined by path specification.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Raises:
      VolumeSystemError: if the VSS virtual file system could not be resolved.
    """
    self._file_system = resolver.Resolver.OpenFileSystem(path_spec)
    if self._file_system is None:
      raise errors.VolumeSystemError(
          u'Unable to resolve file system from path specification.')

    type_indicator = self._file_system.type_indicator
    if type_indicator != definitions.TYPE_INDICATOR_VSHADOW:
      raise errors.VolumeSystemError(u'Unsupported file system type.')

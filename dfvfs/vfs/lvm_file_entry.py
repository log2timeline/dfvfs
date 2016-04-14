# -*- coding: utf-8 -*-
"""The Logical Volume Manager (LVM) file entry implementation."""

from dfdatetime import posix_time as dfdatetime_posix_time

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import lvm
from dfvfs.path import lvm_path_spec
from dfvfs.vfs import file_entry
from dfvfs.vfs import vfs_stat


class LVMDirectory(file_entry.Directory):
  """Class that implements a directory object using pyvslvm."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

       Since a directory can contain a vast number of entries using
       a generator is more memory efficient.

    Yields:
      A path specification (instance of PathSpec).
    """
    # Only the virtual root file has directory entries.
    volume_index = getattr(self.path_spec, u'volume_index', None)
    if volume_index is not None:
      return

    location = getattr(self.path_spec, u'location', None)
    if location is None or location != self._file_system.LOCATION_ROOT:
      return

    vslvm_volume_group = self._file_system.GetLVMVolumeGroup()

    for volume_index in range(0, vslvm_volume_group.number_of_logical_volumes):
      yield lvm_path_spec.LVMPathSpec(
          location=u'/lvm{0:d}'.format(volume_index + 1),
          parent=self.path_spec.parent, volume_index=volume_index)


class LVMFileEntry(file_entry.FileEntry):
  """Class that implements a file entry object using pyvslvm."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LVM

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
    super(LVMFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._name = None

  def _GetDirectory(self):
    """Retrieves the directory.

    Returns:
      A directory object (instance of Directory) or None.
    """
    if self._stat_object is None:
      self._stat_object = self._GetStat()

    if (self._stat_object and
        self._stat_object.type == self._stat_object.TYPE_DIRECTORY):
      return LVMDirectory(self._file_system, self.path_spec)
    return

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      The stat object (instance of VFSStat).

    Raises:
      BackEndError: when the vslvm logical volume is missing in a non-virtual
                    file entry.
    """
    vslvm_logical_volume = self.GetLVMLogicalVolume()
    if not self._is_virtual and vslvm_logical_volume is None:
      raise errors.BackEndError(
          u'Missing vslvm logical volume in non-virtual file entry.')

    stat_object = vfs_stat.VFSStat()

    # File data stat information.
    if vslvm_logical_volume is not None:
      stat_object.size = vslvm_logical_volume.size

    # Date and time stat information.
    if vslvm_logical_volume is not None:
      # TODO: implement in pyvslvm
      # timestamp = vslvm_logical_volume.get_creation_time_as_integer()
      timestamp = None
      if timestamp is not None:
        date_time_values = dfdatetime_posix_time.PosixTimestamp(timestamp)

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
        volume_index = getattr(self.path_spec, u'volume_index', None)
        if volume_index is not None:
          self._name = u'lvm{0:d}'.format(volume_index + 1)
        else:
          self._name = u''
    return self._name

  @property
  def sub_file_entries(self):
    """The sub file entries (generator of instance of FileEntry)."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield LVMFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetLVMLogicalVolume(self):
    """Retrieves the LVM logical volume object.

    Returns:
      A LVM logical volume object (instance of pyvslvm.logical_volume).
    """
    volume_index = lvm.LVMPathSpecGetVolumeIndex(self.path_spec)
    if volume_index is None:
      return

    vslvm_volume_group = self._file_system.GetLVMVolumeGroup()
    return vslvm_volume_group.get_logical_volume(volume_index)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      The parent file entry object (instance of FileEntry) or None.
    """
    volume_index = lvm.LVMPathSpecGetVolumeIndex(self.path_spec)
    if volume_index is None:
      return

    return self._file_system.GetRootFileEntry()

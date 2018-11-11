# -*- coding: utf-8 -*-
"""The Logical Volume Manager (LVM) file system implementation."""

from __future__ import unicode_literals

import pyvslvm

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import lvm
from dfvfs.path import lvm_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import lvm_file_entry


class LVMFileSystem(file_system.FileSystem):
  """File system that uses pyvslvm."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LVM

  def __init__(self, resolver_context):
    """Initializes a file system.

    Args:
      resolver_context (Context): resolver context.
    """
    super(LVMFileSystem, self).__init__(resolver_context)
    self._file_object = None
    self._vslvm_volume_group = None
    self._vslvm_handle = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._vslvm_volume_group = None
    self._vslvm_handle.close()
    self._vslvm_handle = None

    self._file_object.close()
    self._file_object = None

  def _Open(self, path_spec, mode='rb'):
    """Opens the file system object defined by path specification.

    Args:
      path_spec (PathSpec): path specification.
      mode (Optional[str]): file access mode. The default is 'rb' which
          represents read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          'Unsupported path specification without parent.')

    file_object = resolver.Resolver.OpenFileObject(
        path_spec.parent, resolver_context=self._resolver_context)

    try:
      vslvm_handle = pyvslvm.handle()
      vslvm_handle.open_file_object(file_object)
      # TODO: implement multi physical volume support.
      vslvm_handle.open_physical_volume_files_as_file_objects([
          file_object])
      vslvm_volume_group = vslvm_handle.get_volume_group()
    except:
      file_object.close()
      raise

    self._file_object = file_object
    self._vslvm_handle = vslvm_handle
    self._vslvm_volume_group = vslvm_volume_group

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.
    """
    volume_index = lvm.LVMPathSpecGetVolumeIndex(path_spec)

    # The virtual root file has not corresponding volume index but
    # should have a location.
    if volume_index is None:
      location = getattr(path_spec, 'location', None)
      return location is not None and location == self.LOCATION_ROOT

    return (
        0 <= volume_index < self._vslvm_volume_group.number_of_logical_volumes)

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      LVMFileEntry: a file entry or None if not available.
    """
    volume_index = lvm.LVMPathSpecGetVolumeIndex(path_spec)

    # The virtual root file has not corresponding volume index but
    # should have a location.
    if volume_index is None:
      location = getattr(path_spec, 'location', None)
      if location is None or location != self.LOCATION_ROOT:
        return None

      return lvm_file_entry.LVMFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    if (volume_index < 0 or
        volume_index >= self._vslvm_volume_group.number_of_logical_volumes):
      return None

    return lvm_file_entry.LVMFileEntry(self._resolver_context, self, path_spec)

  def GetLVMLogicalVolumeByPathSpec(self, path_spec):
    """Retrieves a LVM logical volume for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      pyvslvm.logical_volume: a LVM logical volume or None if not available.
    """
    volume_index = lvm.LVMPathSpecGetVolumeIndex(path_spec)
    if volume_index is None:
      return None
    return self._vslvm_volume_group.get_logical_volume(volume_index)

  def GetLVMVolumeGroup(self):
    """Retrieves the LVM volume group.

    Returns:
      pyvslvm.volume_group: a LVM volume group.
    """
    return self._vslvm_volume_group

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      LVMFileEntry: root file entry or None if not available.
    """
    path_spec = lvm_path_spec.LVMPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

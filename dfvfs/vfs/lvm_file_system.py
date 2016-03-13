# -*- coding: utf-8 -*-
"""The Logical Volume Manager (LVM) file system implementation."""

import pyvslvm

# This is necessary to prevent a circular import.
import dfvfs.vfs.lvm_file_entry

from dfvfs import dependencies
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import lvm
from dfvfs.path import lvm_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system


dependencies.CheckModuleVersion(u'pyvslvm')


class LVMFileSystem(file_system.FileSystem):
  """Class that implements a file system object using pyvslvm."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_LVM

  def __init__(self, resolver_context):
    """Initializes a file system object.

    Args:
      resolver_context: the resolver context (instance of Context).
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
      path_spec: a path specification (instance of PathSpec).
      mode: optional file access mode. The default is 'rb' read-only binary.

    Raises:
      AccessError: if the access to open the file was denied.
      IOError: if the file system object could not be opened.
      PathSpecError: if the path specification is incorrect.
      ValueError: if the path specification is invalid.
    """
    if not path_spec.HasParent():
      raise errors.PathSpecError(
          u'Unsupported path specification without parent.')

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
      path_spec: a path specification (instance of PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    volume_index = lvm.LVMPathSpecGetVolumeIndex(path_spec)

    # The virtual root file has not corresponding volume index but
    # should have a location.
    if volume_index is None:
      location = getattr(path_spec, u'location', None)
      return location is not None and location == self.LOCATION_ROOT

    return (volume_index >= 0 and
            volume_index < self._vslvm_volume_group.number_of_logical_volumes)

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A file entry (instance of FileEntry) or None.
    """
    volume_index = lvm.LVMPathSpecGetVolumeIndex(path_spec)

    # The virtual root file has not corresponding volume index but
    # should have a location.
    if volume_index is None:
      location = getattr(path_spec, u'location', None)
      if location is None or location != self.LOCATION_ROOT:
        return
      return dfvfs.vfs.lvm_file_entry.LVMFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    if (volume_index < 0 or
        volume_index >= self._vslvm_volume_group.number_of_logical_volumes):
      return
    return dfvfs.vfs.lvm_file_entry.LVMFileEntry(
        self._resolver_context, self, path_spec)

  def GetLVMVolumeGroup(self):
    """Retrieves the LVM volume group object.

    Returns:
      The LVM handle object (instance of pyvslvm.volume_group).
    """
    return self._vslvm_volume_group

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of FileEntry).
    """
    path_spec = lvm_path_spec.LVMPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

# -*- coding: utf-8 -*-
"""The Volume Shadow Snapshots (VSS) file system implementation."""

import pyvshadow

# This is necessary to prevent a circular import.
import dfvfs.vfs.vshadow_file_entry

from dfvfs import dependencies
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import vshadow
from dfvfs.path import vshadow_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system


dependencies.CheckModuleVersion(u'pyvshadow')


class VShadowFileSystem(file_system.FileSystem):
  """Class that implements a file system object using pyvshadow."""

  LOCATION_ROOT = u'/'
  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VSHADOW

  def __init__(self, resolver_context):
    """Initializes a file system object.

    Args:
      resolver_context: the resolver context (instance of resolver.Context).
    """
    super(VShadowFileSystem, self).__init__(resolver_context)
    self._file_object = None
    self._vshadow_volume = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._vshadow_volume.close()
    self._vshadow_volume = None

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
      vshadow_volume = pyvshadow.volume()
      vshadow_volume.open_file_object(file_object)
    except:
      file_object.close()
      raise

    self._file_object = file_object
    self._vshadow_volume = vshadow_volume

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      Boolean indicating if the file entry exists.
    """
    store_index = vshadow.VShadowPathSpecGetStoreIndex(path_spec)

    # The virtual root file has not corresponding store index but
    # should have a location.
    if store_index is None:
      location = getattr(path_spec, u'location', None)
      return location is not None and location == self.LOCATION_ROOT

    return (store_index >= 0 and
            store_index < self._vshadow_volume.number_of_stores)

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A file entry (instance of vfs.VShadowFileEntry) or None.
    """
    store_index = vshadow.VShadowPathSpecGetStoreIndex(path_spec)

    # The virtual root file has not corresponding store index but
    # should have a location.
    if store_index is None:
      location = getattr(path_spec, u'location', None)
      if location is None or location != self.LOCATION_ROOT:
        return
      return dfvfs.vfs.vshadow_file_entry.VShadowFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    if store_index < 0 or store_index >= self._vshadow_volume.number_of_stores:
      return
    return dfvfs.vfs.vshadow_file_entry.VShadowFileEntry(
        self._resolver_context, self, path_spec)

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      A file entry (instance of vfs.FileEntry).
    """
    path_spec = vshadow_path_spec.VShadowPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

  def GetVShadowVolume(self):
    """Retrieves the VSS volume object.

    Returns:
      The VSS volume object (instance of pyvshadow.volume).
    """
    return self._vshadow_volume

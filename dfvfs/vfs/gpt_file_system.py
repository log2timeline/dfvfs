# -*- coding: utf-8 -*-
"""The GUID Partition Table (GPT) file system implementation."""

import pyvsgpt

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import gpt_helper
from dfvfs.path import gpt_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_system
from dfvfs.vfs import gpt_file_entry


class GPTFileSystem(file_system.FileSystem):
  """File system that uses pyvsgpt."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GPT

  def __init__(self, resolver_context, path_spec):
    """Initializes a file system.

    Args:
      resolver_context (Context): resolver context.
      path_spec (PathSpec): a path specification.
    """
    super(GPTFileSystem, self).__init__(resolver_context, path_spec)
    self._file_object = None
    self._vsgpt_volume = None

  def _Close(self):
    """Closes the file system object.

    Raises:
      IOError: if the close failed.
    """
    self._vsgpt_volume.close()
    self._vsgpt_volume = None
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

    vsgpt_volume = pyvsgpt.volume()
    vsgpt_volume.open_file_object(file_object)

    self._file_object = file_object
    self._vsgpt_volume = vsgpt_volume

  def FileEntryExistsByPathSpec(self, path_spec):
    """Determines if a file entry for a path specification exists.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the file entry exists.
    """
    entry_index = gpt_helper.GPTPathSpecGetEntryIndex(path_spec)

    # The virtual root file has no corresponding partition entry index but
    # should have a location.
    if entry_index is None:
      location = getattr(path_spec, 'location', None)
      return location is not None and location == self.LOCATION_ROOT

    return self._vsgpt_volume.has_partition_with_identifier(entry_index)

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      GPTFileEntry: a file entry or None if not available.
    """
    entry_index = gpt_helper.GPTPathSpecGetEntryIndex(path_spec)

    # The virtual root file has no corresponding partition entry index but
    # should have a location.
    if entry_index is None:
      location = getattr(path_spec, 'location', None)
      if location is None or location != self.LOCATION_ROOT:
        return None

      return gpt_file_entry.GPTFileEntry(
          self._resolver_context, self, path_spec, is_root=True,
          is_virtual=True)

    if not self._vsgpt_volume.has_partition_with_identifier(entry_index):
      return None

    return gpt_file_entry.GPTFileEntry(self._resolver_context, self, path_spec)

  def GetGPTPartitionByPathSpec(self, path_spec):
    """Retrieves a GPT partition for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      pyvsgpt.partition: a GPT partition or None if not available.
    """
    entry_index = gpt_helper.GPTPathSpecGetEntryIndex(path_spec)
    if entry_index is None:
      return None
    return self._vsgpt_volume.get_partition_by_identifier(entry_index)

  def GetGPTVolume(self):
    """Retrieves the GPT volume.

    Returns:
      pyvsgpt.volume: a GPT volume.
    """
    return self._vsgpt_volume

  def GetRootFileEntry(self):
    """Retrieves the root file entry.

    Returns:
      GPTFileEntry: root file entry or None if not available.
    """
    path_spec = gpt_path_spec.GPTPathSpec(
        location=self.LOCATION_ROOT, parent=self._path_spec.parent)
    return self.GetFileEntryByPathSpec(path_spec)

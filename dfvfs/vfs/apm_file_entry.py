# -*- coding: utf-8 -*-
"""The Apple Partition Map (APM) file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import apm_helper
from dfvfs.vfs import file_entry
from dfvfs.vfs import apm_directory


class APMFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyvsapm."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_APM

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, vsapm_partition=None):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
      vsapm_partition (Optional[pyvsapm.partition]): a APM partition.

    Raises:
      BackEndError: when APM partition is missing for a non-virtual file entry.
    """
    if not is_virtual and vsapm_partition is None:
      vsapm_partition = file_system.GetAPMPartitionByPathSpec(path_spec)
    if not is_virtual and vsapm_partition is None:
      raise errors.BackEndError(
          'Missing vsapm partition in non-virtual file entry.')

    super(APMFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._name = None
    self._vsapm_partition = vsapm_partition

    if self._is_virtual:
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    else:
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetDirectory(self):
    """Retrieves the directory.

    Returns:
      APMDirectory: a directory.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return apm_directory.APMDirectory(self._file_system, self.path_spec)

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      APMFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield APMFileEntry(self._resolver_context, self._file_system, path_spec)

  @property
  def name(self):
    """str: name of the file entry, without the full path."""
    if self._name is None:
      location = getattr(self.path_spec, 'location', None)
      if location is not None:
        self._name = self._file_system.BasenamePath(location)
      else:
        entry_index = getattr(self.path_spec, 'entry_index', None)
        if entry_index is not None:
          apm_entry_index = entry_index + 1
          self._name = f'p{apm_entry_index:d}'
        else:
          self._name = ''
    return self._name

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    if self._vsapm_partition is None:
      return None

    return self._vsapm_partition.size

  def GetAPMPartition(self):
    """Retrieves the APM partition.

    Returns:
      pyvsapm.partition: a APM partition.
    """
    return self._vsapm_partition

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      APMFileEntry: parent file entry or None if not available.
    """
    entry_index = apm_helper.APMPathSpecGetEntryIndex(self.path_spec)
    if entry_index is None:
      return None

    return self._file_system.GetRootFileEntry()

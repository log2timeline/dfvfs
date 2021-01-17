# -*- coding: utf-8 -*-
"""The GUID Partition Table (GPT) file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import gpt
from dfvfs.path import gpt_path_spec
from dfvfs.vfs import file_entry


class GPTDirectory(file_entry.Directory):
  """File system directory that uses pyvsgpt."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      GPTPathSpec: a path specification.
    """
    entry_index = getattr(self.path_spec, 'entry_index', None)
    location = getattr(self.path_spec, 'location', None)

    # Only the virtual root file has directory entries.
    if (entry_index is None and location is not None and
        location == self._file_system.LOCATION_ROOT):
      vsgpt_volume = self._file_system.GetGPTVolume()

      for partition in vsgpt_volume.partitions:
        location = '/p{0:d}'.format(partition.entry_index + 1)
        yield gpt_path_spec.GPTPathSpec(
            entry_index=entry_index, location=location,
            parent=self.path_spec.parent)


class GPTFileEntry(file_entry.FileEntry):
  """File system file entry that uses pyvsgpt."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_GPT

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, vsgpt_partition=None):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
      vsgpt_partition (Optional[pyvsgpt.partition]): a GPT partition.

    Raises:
      BackEndError: when GPT partition is missing for a non-virtual file entry.
    """
    if not is_virtual and vsgpt_partition is None:
      vsgpt_partition = file_system.GetGPTPartitionByPathSpec(path_spec)
    if not is_virtual and vsgpt_partition is None:
      raise errors.BackEndError(
          'Missing vsgpt partition in non-virtual file entry.')

    super(GPTFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._name = None
    self._vsgpt_partition = vsgpt_partition

    if self._is_virtual:
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    else:
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE

  def _GetDirectory(self):
    """Retrieves the directory.

    Returns:
      GPTDirectory: a directory.
    """
    if self._directory is None:
      self._directory = GPTDirectory(self._file_system, self.path_spec)

    return self._directory

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      GPTFileEntry: a sub file entry.
    """
    if self.entry_type == definitions.FILE_ENTRY_TYPE_DIRECTORY:
      directory = self._GetDirectory()
      for path_spec in directory.entries:
        yield GPTFileEntry(self._resolver_context, self._file_system, path_spec)

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
          self._name = 'p{0:d}'.format(entry_index + 1)
        else:
          self._name = ''
    return self._name

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    if self._vsgpt_partition is None:
      return None

    return self._vsgpt_partition.size

  def GetGPTPartition(self):
    """Retrieves the GPT parition.

    Returns:
      pyvsgpt.parition: a GPT parition.
    """
    return self._vsgpt_partition

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      GPTFileEntry: parent file entry or None if not available.
    """
    entry_index = gpt.GPTPathSpecGetEntryIndex(self.path_spec)
    if entry_index is None:
      return None

    return self._file_system.GetRootFileEntry()

# -*- coding: utf-8 -*-
"""The GUID Partition Table (GPT) file entry implementation."""

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import gpt_helper
from dfvfs.vfs import file_entry
from dfvfs.vfs import gpt_directory


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
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return gpt_directory.GPTDirectory(self._file_system, self.path_spec)

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      GPTFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
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
          gpt_entry_index = entry_index + 1
          self._name = f'p{gpt_entry_index:d}'
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
    """Retrieves the GPT partition.

    Returns:
      pyvsgpt.partition: a GPT partition.
    """
    return self._vsgpt_partition

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      GPTFileEntry: parent file entry or None if not available.
    """
    entry_index = gpt_helper.GPTPathSpecGetEntryIndex(self.path_spec)
    if entry_index is None:
      return None

    return self._file_system.GetRootFileEntry()

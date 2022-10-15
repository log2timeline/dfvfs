# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) file entry interface.

The file entry can be various file system elements like a regular file,
a directory or file system metadata.
"""

import abc

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.vfs import data_stream


class FileEntry(object):
  """File entry interface.

  Attributes:
    entry_type (str): file entry type, such as device, directory, file, link,
        socket and pipe or None if not available. The available file entry
        types are defined in dfvfs.lib.definitions for example
        FILE_ENTRY_TYPE_FILE.
    path_spec (PathSpec): path specification.
  """

  # pylint: disable=redundant-returns-doc,redundant-yields-doc

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.

    Raises:
      ValueError: if a derived file entry class does not define a type
          indicator.
    """
    super(FileEntry, self).__init__()
    self._attributes = None
    self._data_streams = None
    self._directory = None
    self._file_system = file_system
    self._is_root = is_root
    self._is_virtual = is_virtual
    self._link = None
    self._resolver_context = resolver_context
    self.entry_type = None
    self.path_spec = path_spec

    if not getattr(self, 'TYPE_INDICATOR', None):
      raise ValueError('Missing type indicator.')

  def _GetAttributes(self):
    """Retrieves the attributes.

    Returns:
      list[Attribute]: attributes.
    """
    if self._attributes is None:
      self._attributes = []

    return self._attributes

  def _GetDataStreams(self):
    """Retrieves the data streams.

    Returns:
      list[DataStream]: data streams.
    """
    if self._data_streams is None:
      self._data_streams = []

      # It is assumed that non-file file entries do not have data streams.
      if self.entry_type == definitions.FILE_ENTRY_TYPE_FILE:
        data_stream_object = data_stream.DataStream(self)
        self._data_streams.append(data_stream_object)

    return self._data_streams

  @abc.abstractmethod
  def _GetDirectory(self):
    """Retrieves the directory.

    Returns:
      Directory: a directory.
    """

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: full path of the linked file entry.
    """
    if self._link is None:
      self._link = ''

    return self._link

  def _GetStatAttribute(self):
    """Retrieves a stat attribute.

    Returns:
      StatAttribute: a stat attribute or None if not available.
    """
    return None

  @abc.abstractmethod
  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      FileEntry: a sub file entry.
    """

  @property
  def access_time(self):
    """dfdatetime.DateTimeValues: access time or None if not available."""
    return None

  @property
  def added_time(self):
    """dfdatetime.DateTimeValues: added time or None if not available."""
    return None

  @property
  def attributes(self):
    """generator[Attribute]: attributes."""
    return self._GetAttributes()

  @property
  def backup_time(self):
    """dfdatetime.DateTimeValues: backup time or None if not available."""
    return None

  @property
  def change_time(self):
    """dfdatetime.DateTimeValues: change time or None if not available."""
    return None

  @property
  def creation_time(self):
    """dfdatetime.DateTimeValues: creation time or None if not available."""
    return None

  @property
  def deletion_time(self):
    """dfdatetime.DateTimeValues: deletion time or None if not available."""
    return None

  @property
  def data_streams(self):
    """generator[DataStream]: data streams."""
    return self._GetDataStreams()

  @property
  def link(self):
    """str: full path of the linked file entry or None if not available."""
    if not self.IsLink():
      return None

    return self._GetLink()

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    return None

  @property
  @abc.abstractmethod
  def name(self):
    """str: name of the file entry, without the full path."""

  @property
  def number_of_attributes(self):
    """int: number of attributes."""
    attributes = self._GetAttributes()
    return len(attributes)

  @property
  def number_of_data_streams(self):
    """int: number of data streams."""
    data_streams = self._GetDataStreams()
    return len(data_streams)

  @property
  def number_of_sub_file_entries(self):
    """int: number of sub file entries."""
    number_of_sub_file_entries = 0
    if self.entry_type == definitions.FILE_ENTRY_TYPE_DIRECTORY:
      directory = self._GetDirectory()
      # We cannot use len(directory.entries) since entries is a generator.
      number_of_sub_file_entries = sum(1 for path_spec in directory.entries)

    return number_of_sub_file_entries

  @property
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return None

  @property
  def sub_file_entries(self):
    """generator[FileEntry]: sub file entries."""
    return self._GetSubFileEntries()

  @property
  def type_indicator(self):
    """str: type indicator."""
    # pylint: disable=no-member
    return self.TYPE_INDICATOR

  def GetDataStream(self, name, case_sensitive=True):
    """Retrieves a data stream by name.

    Args:
      name (str): name of the data stream.
      case_sensitive (Optional[bool]): True if the name is case sensitive.

    Returns:
      DataStream: a data stream or None if not available.

    Raises:
      ValueError: if the name is not string.
    """
    if not isinstance(name, str):
      raise ValueError('Name is not a string.')

    name_lower = name.lower()
    matching_data_stream = None

    for data_stream_object in self._GetDataStreams():
      if data_stream_object.name == name:
        return data_stream_object

      if not case_sensitive and data_stream_object.name.lower() == name_lower:
        if not matching_data_stream:
          matching_data_stream = data_stream_object

    return matching_data_stream

  def GetExtents(self):
    """Retrieves the extents.

    Returns:
      list[Extent]: the extents.
    """
    return []

  def GetFileObject(self, data_stream_name=''):
    """Retrieves a file-like object of a specific data stream.

    Args:
      data_stream_name (Optional[str]): name of the data stream, where an empty
          string represents the default data stream.

    Returns:
      FileIO: a file-like object or None if not available.
    """
    if data_stream_name:
      return None

    return resolver.Resolver.OpenFileObject(
        self.path_spec, resolver_context=self._resolver_context)

  def GetFileSystem(self):
    """Retrieves the file system which contains the file entry.

    Returns:
      FileSystem: a file system.
    """
    return self._file_system

  def GetLinkedFileEntry(self):
    """Retrieves the linked file entry, for example for a symbolic link.

    Returns:
      FileEntry: linked file entry or None if not available.
    """
    return None

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      FileEntry: parent file entry or None if not available.
    """
    return None

  def GetSubFileEntryByName(self, name, case_sensitive=True):
    """Retrieves a sub file entry by name.

    Args:
      name (str): name of the file entry.
      case_sensitive (Optional[bool]): True if the name is case sensitive.

    Returns:
      FileEntry: a file entry or None if not available.
    """
    name_lower = name.lower()
    matching_sub_file_entry = None

    for sub_file_entry in self.sub_file_entries:
      if sub_file_entry.name == name:
        return sub_file_entry

      if not case_sensitive and sub_file_entry.name.lower() == name_lower:
        if not matching_sub_file_entry:
          matching_sub_file_entry = sub_file_entry

    return matching_sub_file_entry

  def GetStatAttribute(self):
    """Retrieves a stat attribute.

    Returns:
      StatAttribute: a stat attribute or None if not available.
    """
    return self._GetStatAttribute()

  def HasDataStream(self, name, case_sensitive=True):
    """Determines if the file entry has specific data stream.

    Args:
      name (str): name of the data stream.
      case_sensitive (Optional[bool]): True if the name is case sensitive.

    Returns:
      bool: True if the file entry has the data stream.

    Raises:
      ValueError: if the name is not string.
    """
    if not isinstance(name, str):
      raise ValueError('Name is not a string.')

    name_lower = name.lower()

    for data_stream_object in self._GetDataStreams():
      if data_stream_object.name == name:
        return True

      if not case_sensitive and data_stream_object.name.lower() == name_lower:
        return True

    return False

  def HasExternalData(self):
    """Determines if the file entry has external stored data.

    Returns:
      bool: True if the file entry has external stored data.
    """
    return False

  def IsAllocated(self):
    """Determines if the file entry is allocated.

    Returns:
      bool: True if the file entry is allocated.
    """
    return True

  def IsDevice(self):
    """Determines if the file entry is a device.

    Returns:
      bool: True if the file entry is a device.
    """
    return self.entry_type in (
        definitions.FILE_ENTRY_TYPE_BLOCK_DEVICE,
        definitions.FILE_ENTRY_TYPE_CHARACTER_DEVICE,
        definitions.FILE_ENTRY_TYPE_DEVICE)

  def IsDirectory(self):
    """Determines if the file entry is a directory.

    Returns:
      bool: True if the file entry is a directory.
    """
    return self.entry_type == definitions.FILE_ENTRY_TYPE_DIRECTORY

  def IsFile(self):
    """Determines if the file entry is a file.

    Returns:
      bool: True if the file entry is a file.
    """
    return self.entry_type == definitions.FILE_ENTRY_TYPE_FILE

  def IsLink(self):
    """Determines if the file entry is a link.

    Returns:
      bool: True if the file entry is a link.
    """
    return self.entry_type == definitions.FILE_ENTRY_TYPE_LINK

  def IsLocked(self):
    """Determines if the file entry is locked.

    Returns:
      bool: True if the file entry is locked.
    """
    return False

  def IsPipe(self):
    """Determines if the file entry is a pipe.

    Returns:
      bool: True if the file entry is a pipe.
    """
    return self.entry_type == definitions.FILE_ENTRY_TYPE_PIPE

  def IsRoot(self):
    """Determines if the file entry is the root file entry.

    Returns:
      bool: True if the file entry is the root file entry.
    """
    return self._is_root

  def IsSocket(self):
    """Determines if the file entry is a socket.

    Returns:
      bool: True if the file entry is a socket.
    """
    return self.entry_type == definitions.FILE_ENTRY_TYPE_SOCKET

  def IsVirtual(self):
    """Determines if the file entry is virtual (emulated by dfVFS).

    Returns:
      bool: True if the file entry is virtual.
    """
    return self._is_virtual

  def Unlock(self):
    """Unlocks the file entry.

    Returns:
      bool: True if the file entry was unlocked.
    """
    return True

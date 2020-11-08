# -*- coding: utf-8 -*-
"""The Virtual File System (VFS) file entry interface.

The file entry can be various file system elements like a regular file,
a directory or file system metadata.
"""

from __future__ import unicode_literals

import abc

from dfvfs.lib import definitions
from dfvfs.resolver import resolver
from dfvfs.vfs import vfs_stat


class Attribute(object):
  """VFS attribute interface."""

  @property
  def type_indicator(self):
    """str: type indicator or None if not known."""
    return getattr(self, 'TYPE_INDICATOR', None)


class DataStream(object):
  """VFS data stream interface."""

  # The data stream object should not have a reference to its
  # file entry since that will create a cyclic reference.

  @property
  def name(self):
    """str: name."""
    return ''

  def IsDefault(self):
    """Determines if the data stream is the default data stream.

    Returns:
      bool: True if the data stream is the default data stream.
    """
    return True


class Directory(object):
  """VFS directory interface.

  Attributes:
    path_spec (PathSpec): path specification of the directory.
  """

  def __init__(self, file_system, path_spec):
    """Initializes a directory.

    Args:
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
    """
    super(Directory, self).__init__()
    self._entries = None
    self._file_system = file_system
    self.path_spec = path_spec

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Returns:
      generator[PathSpec]: path specification generator.
    """
    return iter(())

  @property
  def entries(self):
    """generator[PathSpec]: path specifications of the directory entries."""
    return self._EntriesGenerator()


class FileEntry(object):
  """Virtual file entry interface.

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
    self._file_system = None
    self._is_root = is_root
    self._is_virtual = is_virtual
    self._link = None
    self._resolver_context = resolver_context
    self.entry_type = None
    self.path_spec = path_spec

    if not getattr(self, 'TYPE_INDICATOR', None):
      raise ValueError('Missing type indicator.')

    file_system.Open(path_spec)

    # Set file_system attribute when open was successful otherwise
    # it will interfere with the __del__ function.
    self._file_system = file_system

  def __del__(self):
    """Cleans up the file entry."""
    # Note that __del__ can be invoked before __init__ has completed.

    # Make a local copy of file_system in case the attribute is set to None
    # after the check and before the call to Close.
    file_system = getattr(self, '_file_system', None)
    if file_system:
      file_system.Close()

    self._file_system = None

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
        data_stream = DataStream()
        self._data_streams.append(data_stream)

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

  def _GetStat(self):
    """Retrieves information about the file entry.

    Returns:
      VFSStat: a stat object.
    """
    stat_object = vfs_stat.VFSStat()

    # Date and time stat information.
    access_time = self.access_time
    if access_time:
      stat_time, stat_time_nano = access_time.CopyToStatTimeTuple()
      if stat_time is not None:
        stat_object.atime = stat_time
      if stat_time_nano is not None:
        stat_object.atime_nano = stat_time_nano

    change_time = self.change_time
    if change_time:
      stat_time, stat_time_nano = change_time.CopyToStatTimeTuple()
      if stat_time is not None:
        stat_object.ctime = stat_time
      if stat_time_nano is not None:
        stat_object.ctime_nano = stat_time_nano

    creation_time = self.creation_time
    if creation_time:
      stat_time, stat_time_nano = creation_time.CopyToStatTimeTuple()
      if stat_time is not None:
        stat_object.crtime = stat_time
      if stat_time_nano is not None:
        stat_object.crtime_nano = stat_time_nano

    modification_time = self.modification_time
    if modification_time:
      stat_time, stat_time_nano = modification_time.CopyToStatTimeTuple()
      if stat_time is not None:
        stat_object.mtime = stat_time
      if stat_time_nano is not None:
        stat_object.mtime_nano = stat_time_nano

    # File data stat information.
    stat_object.size = self.size

    # Ownership and permissions stat information.
    # TODO: consider adding stat_object.mode
    # TODO: consider adding stat_object.uid
    # TODO: consider adding stat_object.gid

    # File entry type stat information.
    stat_object.type = self.entry_type

    # Other stat information.
    # TODO: consider adding stat_object.ino
    # TODO: consider adding stat_object.fs_type

    stat_object.is_allocated = self.IsAllocated()

    return stat_object

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

  @abc.abstractproperty
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

    for data_stream in self._GetDataStreams():
      if data_stream.name == name:
        return data_stream

      if not case_sensitive and data_stream.name.lower() == name_lower:
        if not matching_data_stream:
          matching_data_stream = data_stream

    return matching_data_stream

  def GetFileObject(self, data_stream_name=''):
    """Retrieves the file-like object.

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

  def GetStat(self):
    """Retrieves information about the file entry.

    Returns:
      VFSStat: a stat object or None if not available.
    """
    return self._GetStat()

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

    for data_stream in self._GetDataStreams():
      if data_stream.name == name:
        return True

      if not case_sensitive and data_stream.name.lower() == name_lower:
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
    return self.entry_type == definitions.FILE_ENTRY_TYPE_DEVICE

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

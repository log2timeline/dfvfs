# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) file entry implementation."""

from __future__ import unicode_literals

import copy

import pytsk3

from dfdatetime import definitions as dfdatetime_definitions
from dfdatetime import interface as dfdatetime_interface

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import tsk_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_entry


class TSKTime(dfdatetime_interface.DateTimeValues):
  """SleuthKit timestamp."""

  def __init__(self, timestamp=None, timestamp_fragment=None):
    """Initializes a SleuthKit timestamp.

    Args:
      timestamp (Optional[int]): POSIX timestamp.
      timestamp_fragment (Optional[int]): POSIX timestamp fragment.
    """
    # Sleuthkit 4.2.0 switched from 100 nano seconds precision to
    # 1 nano second precision.
    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      precision = dfdatetime_definitions.PRECISION_1_NANOSECOND
    else:
      precision = dfdatetime_definitions.PRECISION_100_NANOSECONDS

    super(TSKTime, self).__init__()
    self.precision = precision
    self.timestamp = timestamp
    self.timestamp_fragment = timestamp_fragment

  def CopyFromString(self, time_string):
    """Copies a POSIX timestamp from a date and time string.

    Args:
      time_string (str): date and time value formatted as:
          YYYY-MM-DD hh:mm:ss.######[+-]##:##

          Where # are numeric digits ranging from 0 to 9 and the seconds
          fraction can be either 3 or 6 digits. The time of day, seconds
          fraction and time zone offset are optional. The default time zone
          is UTC.
    """
    date_time_values = self._CopyDateTimeFromString(time_string)

    year = date_time_values.get('year', 0)
    month = date_time_values.get('month', 0)
    day_of_month = date_time_values.get('day_of_month', 0)
    hours = date_time_values.get('hours', 0)
    minutes = date_time_values.get('minutes', 0)
    seconds = date_time_values.get('seconds', 0)
    microseconds = date_time_values.get('microseconds', 0)

    self.timestamp = self._GetNumberOfSecondsFromElements(
        year, month, day_of_month, hours, minutes, seconds)
    self.timestamp_fragment = microseconds

    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      self.timestamp_fragment *= 1000
    else:
      self.timestamp_fragment *= 10

    self.is_local_time = False

  def CopyToStatTimeTuple(self):
    """Copies the SleuthKit timestamp to a stat timestamp tuple.

    Returns:
      tuple[int, int]: a POSIX timestamp in seconds and the remainder in
          100 nano seconds or (None, None) on error.
    """
    if self.timestamp is None:
      return None, None

    if (self.timestamp_fragment is not None and
        pytsk3.TSK_VERSION_NUM >= 0x040200ff):
      timestamp_fragment, _ = divmod(self.timestamp_fragment, 100)
    else:
      timestamp_fragment = self.timestamp_fragment

    return self.timestamp, timestamp_fragment

  def GetPlasoTimestamp(self):
    """Retrieves a timestamp that is compatible with plaso.

    Returns:
      int: a POSIX timestamp in microseconds or None on error.
    """
    if self.timestamp is None:
      return

    timestamp = self.timestamp
    if self.timestamp_fragment is not None:
      if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
        timestamp_fragment, _ = divmod(self.timestamp_fragment, 1000)
      else:
        timestamp_fragment, _ = divmod(self.timestamp_fragment, 10)

      timestamp *= 1000000
      timestamp += timestamp_fragment

    return timestamp


class TSKAttribute(file_entry.Attribute):
  """File system attribute that uses pytsk3."""

  def __init__(self, tsk_attribute):
    """Initializes an attribute.

    Args:
      tsk_attribute (pytsk3.Attribute): TSK attribute.
    """
    super(TSKAttribute, self).__init__()
    self._tsk_attribute = tsk_attribute

  @property
  def attribute_type(self):
    """object: attribute type."""
    return getattr(self._tsk_attribute.info, 'type', None)


class TSKDataStream(file_entry.DataStream):
  """File system data stream that uses pytks3."""

  def __init__(self, tsk_attribute):
    """Initializes a data stream.

    Args:
      tsk_attribute (pytsk3.Attribute): TSK attribute.
    """
    super(TSKDataStream, self).__init__()
    self._tsk_attribute = tsk_attribute

  @property
  def name(self):
    """str: name."""
    if self._tsk_attribute:
      # The value of the attribute name will be None for the default
      # data stream.
      attribute_name = getattr(self._tsk_attribute.info, 'name', None)
      if attribute_name:
        try:
          # pytsk3 returns an UTF-8 encoded byte string.
          return attribute_name.decode('utf8')
        except UnicodeError:
          pass

    return ''


class TSKDirectory(file_entry.Directory):
  """File system directory that uses pytsk3."""

  def _EntriesGenerator(self):
    """Retrieves directory entries.

    Since a directory can contain a vast number of entries using
    a generator is more memory efficient.

    Yields:
      TSKPathSpec: a path specification.

    Raises:
      BackEndError: if pytsk3 cannot open the directory.
    """
    # Opening a file by inode number is faster than opening a file
    # by location.
    inode = getattr(self.path_spec, 'inode', None)
    location = getattr(self.path_spec, 'location', None)

    fs_info = self._file_system.GetFsInfo()
    tsk_directory = None

    try:
      if inode is not None:
        tsk_directory = fs_info.open_dir(inode=inode)
      elif location is not None:
        tsk_directory = fs_info.open_dir(path=location)

    except IOError as exception:
      raise errors.BackEndError(
          'Unable to open directory with error: {0:s}'.format(exception))

    if not tsk_directory:
      return

    for tsk_directory_entry in tsk_directory:
      # Note that because pytsk3.Directory does not explicitly defines info
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(tsk_directory_entry, 'info', None) is None:
        continue

      # Note that because pytsk3.TSK_FS_FILE does not explicitly defines fs_info
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(tsk_directory_entry.info, 'fs_info', None) is None:
        continue

      # Note that because pytsk3.TSK_FS_FILE does not explicitly defines meta
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(tsk_directory_entry.info, 'meta', None) is None:
        # Most directory entries will have an "inode" but not all, e.g.
        # previously deleted files. Currently directory entries without
        # a pytsk3.TSK_FS_META object are ignored.
        continue

      # Note that because pytsk3.TSK_FS_META does not explicitly defines addr
      # we need to check if the attribute exists.
      if not hasattr(tsk_directory_entry.info.meta, 'addr'):
        continue

      directory_entry_inode = tsk_directory_entry.info.meta.addr
      directory_entry = None

      # Ignore references to self.
      if directory_entry_inode == inode:
        continue

      # On non-NTFS file systems ignore inode 0.
      if directory_entry_inode == 0 and not self._file_system.IsNTFS():
        continue

      # Note that because pytsk3.TSK_FS_FILE does not explicitly defines name
      # we need to check if the attribute exists and has a value other
      # than None.
      if getattr(tsk_directory_entry.info, 'name', None) is not None:
        # Ignore file entries marked as "unallocated".
        flags = getattr(tsk_directory_entry.info.name, 'flags', 0)
        if int(flags) & pytsk3.TSK_FS_NAME_FLAG_UNALLOC:
          continue

        directory_entry = getattr(tsk_directory_entry.info.name, 'name', '')

        try:
          # pytsk3 returns an UTF-8 encoded byte string.
          directory_entry = directory_entry.decode('utf8')
        except UnicodeError:
          # Continue here since we cannot represent the directory entry.
          continue

        if directory_entry:
          # Ignore references to self or parent.
          if directory_entry in ['.', '..']:
            continue

          if location == self._file_system.PATH_SEPARATOR:
            directory_entry = self._file_system.JoinPath([directory_entry])
          else:
            directory_entry = self._file_system.JoinPath([
                location, directory_entry])

      yield tsk_path_spec.TSKPathSpec(
          inode=directory_entry_inode, location=directory_entry,
          parent=self.path_spec.parent)


class TSKFileEntry(file_entry.FileEntry):
  """File system file entry that uses pytsk3."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK

  # pytsk3.TSK_FS_TYPE_ENUM is unhashable, preventing a set
  # based lookup, hence lists are used.

  _TSK_NO_ATIME_FS_TYPES = [pytsk3.TSK_FS_TYPE_ISO9660]

  _TSK_NO_MTIME_FS_TYPES = [pytsk3.TSK_FS_TYPE_ISO9660]

  _TSK_NO_CTIME_FS_TYPES = [
      pytsk3.TSK_FS_TYPE_FAT12, pytsk3.TSK_FS_TYPE_FAT16,
      pytsk3.TSK_FS_TYPE_FAT32, pytsk3.TSK_FS_TYPE_ISO9660,
      pytsk3.TSK_FS_TYPE_EXFAT]

  _TSK_NO_CRTIME_FS_TYPES = [
      pytsk3.TSK_FS_TYPE_FFS1, pytsk3.TSK_FS_TYPE_FFS1B,
      pytsk3.TSK_FS_TYPE_FFS2, pytsk3.TSK_FS_TYPE_YAFFS2,
      pytsk3.TSK_FS_TYPE_EXT2, pytsk3.TSK_FS_TYPE_EXT3]

  _TSK_HAS_NANO_FS_TYPES = [
      pytsk3.TSK_FS_TYPE_EXT4, pytsk3.TSK_FS_TYPE_NTFS, pytsk3.TSK_FS_TYPE_HFS,
      pytsk3.TSK_FS_TYPE_FFS2, pytsk3.TSK_FS_TYPE_EXFAT]

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, parent_inode=None, tsk_file=None):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (FileSystem): file system.
      path_spec (PathSpec): path specification.
      is_root (Optional[bool]): True if the file entry is the root file entry
          of the corresponding file system.
      is_virtual (Optional[bool]): True if the file entry is a virtual file
          entry emulated by the corresponding file system.
      parent_inode (Optional[int]): parent inode number.
      tsk_file (Optional[pytsk3.File]): TSK file.

    Raises:
      BackEndError: if the TSK File .info or .info.meta attribute is missing.
    """
    if (not tsk_file or not tsk_file.info or not tsk_file.info.meta or
        not tsk_file.info.fs_info):
      tsk_file = file_system.GetTSKFileByPathSpec(path_spec)
    if (not tsk_file or not tsk_file.info or not tsk_file.info.meta or
        not tsk_file.info.fs_info):
      raise errors.BackEndError(
          'Missing TSK File .info, .info.meta or .info.fs_info')

    super(TSKFileEntry, self).__init__(
        resolver_context, file_system, path_spec, is_root=is_root,
        is_virtual=is_virtual)
    self._file_system_type = tsk_file.info.fs_info.ftype
    self._name = None
    self._parent_inode = parent_inode
    self._tsk_file = tsk_file

    # The type is an instance of pytsk3.TSK_FS_META_TYPE_ENUM.
    tsk_fs_meta_type = getattr(
        tsk_file.info.meta, 'type', pytsk3.TSK_FS_META_TYPE_UNDEF)

    if tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_REG:
      self._type = definitions.FILE_ENTRY_TYPE_FILE
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_DIR:
      self._type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_LNK:
      self._type = definitions.FILE_ENTRY_TYPE_LINK
    elif (tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_CHR or
          tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_BLK):
      self._type = definitions.FILE_ENTRY_TYPE_DEVICE
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_FIFO:
      self._type = definitions.FILE_ENTRY_TYPE_PIPE
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_SOCK:
      self._type = definitions.FILE_ENTRY_TYPE_SOCKET

    # TODO: implement support for:
    # pytsk3.TSK_FS_META_TYPE_UNDEF
    # pytsk3.TSK_FS_META_TYPE_SHAD
    # pytsk3.TSK_FS_META_TYPE_WHT
    # pytsk3.TSK_FS_META_TYPE_VIRT

  def _GetAttributes(self):
    """Retrieves the attributes.

    Returns:
      list[TSKAttribute]: attributes.
    """
    if self._attributes is None:
      self._attributes = []

      for tsk_attribute in self._tsk_file:
        if getattr(tsk_attribute, 'info', None) is None:
          continue

        # At the moment there is no way to expose the attribute data
        # from pytsk3.
        attribute_object = TSKAttribute(tsk_attribute)
        self._attributes.append(attribute_object)

    return self._attributes

  def _GetDataStreams(self):
    """Retrieves the data streams.

    Returns:
      list[TSKDataStream]: data streams.
    """
    if self._data_streams is None:
      if self._file_system.IsHFS():
        known_data_attribute_types = [
            pytsk3.TSK_FS_ATTR_TYPE_HFS_DEFAULT,
            pytsk3.TSK_FS_ATTR_TYPE_HFS_DATA]

      elif self._file_system.IsNTFS():
        known_data_attribute_types = [pytsk3.TSK_FS_ATTR_TYPE_NTFS_DATA]

      else:
        known_data_attribute_types = None

      self._data_streams = []

      if not known_data_attribute_types:
        tsk_fs_meta_type = getattr(
            self._tsk_file.info.meta, 'type', pytsk3.TSK_FS_META_TYPE_UNDEF)
        if tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_REG:
          self._data_streams.append(TSKDataStream(None))

      else:
        for tsk_attribute in self._tsk_file:
          if getattr(tsk_attribute, 'info', None) is None:
            continue

          attribute_type = getattr(tsk_attribute.info, 'type', None)
          if attribute_type in known_data_attribute_types:
            self._data_streams.append(TSKDataStream(tsk_attribute))

    return self._data_streams

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      TSKDirectory: directory or None.
    """
    if self._type == definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return TSKDirectory(self._file_system, self.path_spec)

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: path of the linked file.
    """
    if self._link is None:
      self._link = ''

      if self._type != definitions.FILE_ENTRY_TYPE_LINK:
        return self._link

      # Note that the SleuthKit does not expose NTFS
      # IO_REPARSE_TAG_MOUNT_POINT or IO_REPARSE_TAG_SYMLINK as a link.
      link = getattr(self._tsk_file.info.meta, 'link', None)

      if link is None:
        return self._link

      try:
        # pytsk3 returns an UTF-8 encoded byte string without a leading
        # path segment separator.
        link = '{0:s}{1:s}'.format(
            self._file_system.PATH_SEPARATOR, link.decode('utf8'))
      except UnicodeError:
        raise errors.BackEndError(
            'pytsk3 returned a non UTF-8 formatted link.')

      self._link = link

    return self._link

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      VFSStat: stat object.
    """
    stat_object = super(TSKFileEntry, self)._GetStat()

    # File data stat information.
    stat_object.size = getattr(self._tsk_file.info.meta, 'size', None)

    # Date and time stat information.
    stat_time, stat_time_nano = self._TSKFileTimeCopyToStatTimeTuple(
        self._tsk_file, 'bkup')
    if stat_time is not None:
      stat_object.bkup = stat_time
      stat_object.bkup_nano = stat_time_nano

    stat_time, stat_time_nano = self._TSKFileTimeCopyToStatTimeTuple(
        self._tsk_file, 'dtime')
    if stat_time is not None:
      stat_object.dtime = stat_time
      stat_object.dtime_nano = stat_time_nano

    # Ownership and permissions stat information.
    mode = getattr(self._tsk_file.info.meta, 'mode', None)
    if mode is not None:
      # We need to cast mode to an int since it is of type
      # pytsk3.TSK_FS_META_MODE_ENUM.
      stat_object.mode = int(mode)

    stat_object.uid = getattr(self._tsk_file.info.meta, 'uid', None)
    stat_object.gid = getattr(self._tsk_file.info.meta, 'gid', None)

    # File entry type stat information.

    # Other stat information.
    stat_object.ino = getattr(self._tsk_file.info.meta, 'addr', None)
    # stat_object.dev = stat_info.st_dev
    # stat_object.nlink = getattr(self._tsk_file.info.meta, 'nlink', None)
    # stat_object.fs_type = 'Unknown'

    flags = getattr(self._tsk_file.info.meta, 'flags', 0)

    # The flags are an instance of pytsk3.TSK_FS_META_FLAG_ENUM.
    if int(flags) & pytsk3.TSK_FS_META_FLAG_ALLOC:
      stat_object.is_allocated = True
    else:
      stat_object.is_allocated = False

    return stat_object

  def _GetTimeValue(self, name):
    """Retrieves a date and time value.

    Args:
      name (str): name of the date and time value, for exmample "atime" or
          "mtime".

    Returns:
      dfdatetime.DateTimeValues: date and time value or None if not available.
    """
    timestamp = getattr(self._tsk_file.info.meta, name, None)

    if self._file_system_type in self._TSK_HAS_NANO_FS_TYPES:
      name_fragment = '{0:s}_nano'.format(name)
      timestamp_fragment = getattr(
          self._tsk_file.info.meta, name_fragment, None)
    else:
      timestamp_fragment = None

    return TSKTime(timestamp=timestamp, timestamp_fragment=timestamp_fragment)

  def _TSKFileTimeCopyToStatTimeTuple(self, tsk_file, time_value):
    """Copies a SleuthKit file object time value to a stat timestamp tuple.

    Args:
      tsk_file (pytsk3.File): TSK file.
      time_value (str): name of the time value.

    Returns:
     tuple containing:
        int: POSIX timestamp in seconds. None on error, or if the file system
          does not include the requested timestamp.
        int: remainder in 100 nano seconds. None on error, or if the file system
          does not support sub-second precision.

    Raises:
      BackEndError: if the TSK File .info, .info.meta or info.fs_info
        attribute is missing.
    """
    if (not tsk_file or not tsk_file.info or not tsk_file.info.meta or
        not tsk_file.info.fs_info):
      raise errors.BackEndError(
          'Missing TSK File .info, .info.meta. or .info.fs_info')

    stat_time = getattr(tsk_file.info.meta, time_value, None)
    stat_time_nano = None
    if self._file_system_type in self._TSK_HAS_NANO_FS_TYPES:
      time_value_nano = '{0:s}_nano'.format(time_value)
      stat_time_nano = getattr(tsk_file.info.meta, time_value_nano, None)

    # Sleuthkit 4.2.0 switched from 100 nano seconds precision to
    # 1 nano seconds precision.
    if stat_time_nano is not None and pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      stat_time_nano /= 100

    return stat_time, stat_time_nano

  @property
  def access_time(self):
    """dfdatetime.DateTimeValues: access time or None if not available."""
    if self._file_system_type in self._TSK_NO_ATIME_FS_TYPES:
      return

    return self._GetTimeValue('atime')

  @property
  def change_time(self):
    """dfdatetime.DateTimeValues: change time or None if not available."""
    if self._file_system_type in self._TSK_NO_CTIME_FS_TYPES:
      return

    return self._GetTimeValue('ctime')

  @property
  def creation_time(self):
    """dfdatetime.DateTimeValues: creation time or None if not available."""
    if self._file_system_type in self._TSK_NO_CRTIME_FS_TYPES:
      return

    return self._GetTimeValue('crtime')

  @property
  def name(self):
    """str: name of the file entry, which does not include the full path.

    Raises:
      BackEndError: if pytsk3 returns a non UTF-8 formatted name.
    """
    if self._name is None:
      # If pytsk3.FS_Info.open() was used file.info has an attribute name
      # (pytsk3.TSK_FS_FILE) that contains the name string. Otherwise the
      # name from the path specification is used.
      if getattr(self._tsk_file.info, 'name', None) is not None:
        name = getattr(self._tsk_file.info.name, 'name', None)

        try:
          # pytsk3 returns an UTF-8 encoded byte string.
          self._name = name.decode('utf8')
        except UnicodeError:
          raise errors.BackEndError(
              'pytsk3 returned a non UTF-8 formatted name.')

      else:
        location = getattr(self.path_spec, 'location', None)
        if location:
          self._name = self._file_system.BasenamePath(location)

    return self._name

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    if self._file_system_type in self._TSK_NO_MTIME_FS_TYPES:
      return

    return self._GetTimeValue('mtime')

  @property
  def sub_file_entries(self):
    """generator(TSKFileEntry): sub file entries."""
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
        yield TSKFileEntry(self._resolver_context, self._file_system, path_spec)

  def GetFileObject(self, data_stream_name=''):
    """Retrieves the file-like object.

    Args:
      data_stream_name (Optional[str]): data stream name, where an empty
          string represents the default data stream.

    Returns:
      TSKFileIO: file-like object or None.
    """
    data_stream_names = [
        data_stream.name for data_stream in self._GetDataStreams()]
    if data_stream_name and data_stream_name not in data_stream_names:
      return

    path_spec = copy.deepcopy(self.path_spec)
    if data_stream_name:
      setattr(path_spec, 'data_stream', data_stream_name)

    return resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

  def GetLinkedFileEntry(self):
    """Retrieves the linked file entry, e.g. for a symbolic link.

    Returns:
      TSKFileEntry: linked file entry or None.
    """
    link = self._GetLink()
    if not link:
      return

    # TODO: is there a way to determine the link inode number here?
    link_inode = None

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = tsk_path_spec.TSKPathSpec(
        location=link, parent=parent_path_spec)

    root_inode = self._file_system.GetRootInode()
    if (link == self._file_system.LOCATION_ROOT or
        (link_inode is not None and root_inode is not None and
         link_inode == root_inode)):
      is_root = True
    else:
      is_root = False

    return TSKFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      TSKFileEntry: parent file entry or None.
    """
    location = getattr(self.path_spec, 'location', None)
    if location is None:
      return
    parent_inode = self._parent_inode
    parent_location = self._file_system.DirnamePath(location)
    if parent_inode is None and parent_location is None:
      return
    if parent_location == '':
      parent_location = self._file_system.PATH_SEPARATOR

    root_inode = self._file_system.GetRootInode()
    if (parent_location == self._file_system.LOCATION_ROOT or
        (parent_inode is not None and root_inode is not None and
         parent_inode == root_inode)):
      is_root = True
    else:
      is_root = False

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=parent_inode, location=parent_location, parent=parent_path_spec)
    return TSKFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)

  def GetTSKFile(self):
    """Retrieves the SleuthKit file object.

    Returns:
      pytsk3.File: TSK file.

    Raises:
      PathSpecError: if the path specification is missing inode and location.
    """
    return self._tsk_file

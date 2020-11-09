# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) file entry implementation."""

from __future__ import unicode_literals

import copy
import decimal

from dfdatetime import definitions as dfdatetime_definitions
from dfdatetime import factory as dfdatetime_factory
from dfdatetime import interface as dfdatetime_interface

import pytsk3

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import tsk_path_spec
from dfvfs.resolver import resolver
from dfvfs.vfs import file_entry


class TSKTime(dfdatetime_interface.DateTimeValues):
  """SleuthKit timestamp.

  Attributes:
    fraction_of_second (int): fraction of second, which is an integer that
        contains the number 100 nano seconds before Sleuthkit 4.2.0 or
        number of nano seconds in Sleuthkit 4.2.0 and later.
  """

  _100_NANOSECONDS_PER_SECOND = 10000000
  _NANOSECONDS_PER_SECOND = 1000000000

  def __init__(self, fraction_of_second=None, timestamp=None):
    """Initializes a SleuthKit timestamp.

    Args:
      fraction_of_second (Optional[int]): fraction of second, which is
          an integer that contains the number 100 nano seconds before
          Sleuthkit 4.2.0 or number of nano seconds in Sleuthkit 4.2.0
          and later.
      timestamp (Optional[int]): POSIX timestamp.
    """
    # Sleuthkit 4.2.0 switched from 100 nano seconds precision to
    # 1 nano second precision.
    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      precision = dfdatetime_definitions.PRECISION_1_NANOSECOND
    else:
      precision = dfdatetime_definitions.PRECISION_100_NANOSECONDS

    super(TSKTime, self).__init__()
    self._precision = precision
    self._timestamp = timestamp
    self.fraction_of_second = fraction_of_second

  @property
  def timestamp(self):
    """int: POSIX timestamp in microseconds or None if timestamp is not set."""
    return self._timestamp

  def _GetNormalizedTimestamp(self):
    """Retrieves the normalized timestamp.

    Returns:
      decimal.Decimal: normalized timestamp, which contains the number of
          seconds since January 1, 1970 00:00:00 and a fraction of second used
          for increased precision, or None if the normalized timestamp cannot be
          determined.
    """
    if self._normalized_timestamp is None:
      if self._timestamp is not None:
        self._normalized_timestamp = decimal.Decimal(self._timestamp)

        if self.fraction_of_second is not None:
          fraction_of_second = decimal.Decimal(self.fraction_of_second)

          if self._precision == dfdatetime_definitions.PRECISION_1_NANOSECOND:
            fraction_of_second /= self._NANOSECONDS_PER_SECOND
          else:
            fraction_of_second /= self._100_NANOSECONDS_PER_SECOND

          self._normalized_timestamp += fraction_of_second

    return self._normalized_timestamp

  def CopyFromDateTimeString(self, time_string):
    """Copies a SleuthKit timestamp from a date and time string.

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

    self._timestamp = self._GetNumberOfSecondsFromElements(
        year, month, day_of_month, hours, minutes, seconds, None)
    self.fraction_of_second = microseconds

    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      self.fraction_of_second *= 1000
    else:
      self.fraction_of_second *= 10

    self._normalized_timestamp = None
    self.is_local_time = False

  def CopyToDateTimeString(self):
    """Copies the date time value to a date and time string.

    Returns:
      str: date and time value formatted as:
          YYYY-MM-DD hh:mm:ss or
          YYYY-MM-DD hh:mm:ss.####### or
          YYYY-MM-DD hh:mm:ss.#########
    """
    if self._timestamp is None:
      return None

    number_of_days, hours, minutes, seconds = self._GetTimeValues(
        self._timestamp)

    year, month, day_of_month = self._GetDateValues(number_of_days, 1970, 1, 1)

    if self.fraction_of_second is None:
      return '{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}'.format(
          year, month, day_of_month, hours, minutes, seconds)

    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      return '{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}.{6:09d}'.format(
          year, month, day_of_month, hours, minutes, seconds,
          self.fraction_of_second)

    return '{0:04d}-{1:02d}-{2:02d} {3:02d}:{4:02d}:{5:02d}.{6:07d}'.format(
        year, month, day_of_month, hours, minutes, seconds,
        self.fraction_of_second)

  def CopyToStatTimeTuple(self):
    """Copies the SleuthKit timestamp to a stat timestamp tuple.

    Returns:
      tuple[int, int]: a POSIX timestamp in seconds and the remainder in
          100 nano seconds or (None, None) on error.
    """
    if self.fraction_of_second is None:
      return self._timestamp, None

    return super(TSKTime, self).CopyToStatTimeTuple()

  def GetDate(self):
    """Retrieves the date represented by the date and time values.

    Returns:
       tuple[int, int, int]: year, month, day of month or (None, None, None)
           if the date and time values do not represent a date.
    """
    if self._timestamp is None:
      return None, None, None

    try:
      number_of_days, _, _, _ = self._GetTimeValues(self._timestamp)
      return self._GetDateValues(number_of_days, 1970, 1, 1)
    except ValueError:
      return None, None, None


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
  """File system data stream that uses pytsk3."""

  def __init__(self, file_system, tsk_attribute):
    """Initializes a data stream.

    Args:
      file_system (TSKFileSystem): file system.
      tsk_attribute (pytsk3.Attribute): TSK attribute.
    """
    super(TSKDataStream, self).__init__()
    self._file_system = file_system
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

  def IsDefault(self):
    """Determines if the data stream is the default data stream.

    Returns:
      bool: True if the data stream is the default data stream, false if not.
    """
    if not self._tsk_attribute or not self._file_system:
      return True

    if self._file_system.IsHFS():
      attribute_type = getattr(self._tsk_attribute.info, 'type', None)
      return attribute_type in (
          pytsk3.TSK_FS_ATTR_TYPE_HFS_DEFAULT, pytsk3.TSK_FS_ATTR_TYPE_HFS_DATA)

    if self._file_system.IsNTFS():
      return not bool(self.name)

    return True


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
          'Unable to open directory with error: {0!s}'.format(exception))

    if tsk_directory:
      for tsk_directory_entry in tsk_directory:
        # Note that because pytsk3.Directory does not explicitly define info
        # we need to check if the attribute exists and has a value other
        # than None.
        if getattr(tsk_directory_entry, 'info', None) is None:
          continue

        # Note that because pytsk3.TSK_FS_FILE does not explicitly define
        # fs_info we need to check if the attribute exists and has a value
        # other than None.
        if getattr(tsk_directory_entry.info, 'fs_info', None) is None:
          continue

        # Note that because pytsk3.TSK_FS_FILE does not explicitly define meta
        # we need to check if the attribute exists and has a value other
        # than None.
        if getattr(tsk_directory_entry.info, 'meta', None) is None:
          # Most directory entries will have an "inode" but not all, e.g.
          # previously deleted files. Currently directory entries without
          # a pytsk3.TSK_FS_META object are ignored.
          continue

        # Note that because pytsk3.TSK_FS_META does not explicitly define addr
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

        # Note that because pytsk3.TSK_FS_FILE does not explicitly define name
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

            if not location or location == self._file_system.PATH_SEPARATOR:
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

  _TSK_EXT_FS_TYPES = [
      pytsk3.TSK_FS_TYPE_EXT2,
      pytsk3.TSK_FS_TYPE_EXT3,
      pytsk3.TSK_FS_TYPE_EXT4,
      pytsk3.TSK_FS_TYPE_EXT_DETECT]

  _TSK_FAT_FS_TYPES = [
      pytsk3.TSK_FS_TYPE_EXFAT,
      pytsk3.TSK_FS_TYPE_FAT_DETECT,
      pytsk3.TSK_FS_TYPE_FAT12,
      pytsk3.TSK_FS_TYPE_FAT16,
      pytsk3.TSK_FS_TYPE_FAT32]

  _TSK_HFS_FS_TYPES = [
      pytsk3.TSK_FS_TYPE_HFS,
      pytsk3.TSK_FS_TYPE_HFS_DETECT]

  _TSK_NTFS_FS_TYPES = [
      pytsk3.TSK_FS_TYPE_NTFS,
      pytsk3.TSK_FS_TYPE_NTFS_DETECT]

  _TSK_UFS_FS_TYPES = [
      pytsk3.TSK_FS_TYPE_FFS_DETECT,
      pytsk3.TSK_FS_TYPE_FFS1,
      pytsk3.TSK_FS_TYPE_FFS1B,
      pytsk3.TSK_FS_TYPE_FFS2]

  _TSK_ATIME_FS_TYPES = [pytsk3.TSK_FS_TYPE_YAFFS2]
  _TSK_ATIME_FS_TYPES.extend(_TSK_EXT_FS_TYPES)
  _TSK_ATIME_FS_TYPES.extend(_TSK_FAT_FS_TYPES)
  _TSK_ATIME_FS_TYPES.extend(_TSK_HFS_FS_TYPES)
  _TSK_ATIME_FS_TYPES.extend(_TSK_NTFS_FS_TYPES)
  _TSK_ATIME_FS_TYPES.extend(_TSK_UFS_FS_TYPES)

  _TSK_BKUP_FS_TYPES = _TSK_HFS_FS_TYPES

  _TSK_CTIME_FS_TYPES = [pytsk3.TSK_FS_TYPE_YAFFS2]
  _TSK_CTIME_FS_TYPES.extend(_TSK_EXT_FS_TYPES)
  _TSK_CTIME_FS_TYPES.extend(_TSK_HFS_FS_TYPES)
  _TSK_CTIME_FS_TYPES.extend(_TSK_NTFS_FS_TYPES)
  _TSK_CTIME_FS_TYPES.extend(_TSK_UFS_FS_TYPES)

  _TSK_CRTIME_FS_TYPES = [pytsk3.TSK_FS_TYPE_EXT4]
  _TSK_CRTIME_FS_TYPES.extend(_TSK_FAT_FS_TYPES)
  _TSK_CRTIME_FS_TYPES.extend(_TSK_HFS_FS_TYPES)
  _TSK_CRTIME_FS_TYPES.extend(_TSK_NTFS_FS_TYPES)

  _TSK_DTIME_FS_TYPES = _TSK_EXT_FS_TYPES

  _TSK_MTIME_FS_TYPES = [pytsk3.TSK_FS_TYPE_YAFFS2]
  _TSK_MTIME_FS_TYPES.extend(_TSK_EXT_FS_TYPES)
  _TSK_MTIME_FS_TYPES.extend(_TSK_FAT_FS_TYPES)
  _TSK_MTIME_FS_TYPES.extend(_TSK_HFS_FS_TYPES)
  _TSK_MTIME_FS_TYPES.extend(_TSK_NTFS_FS_TYPES)
  _TSK_MTIME_FS_TYPES.extend(_TSK_UFS_FS_TYPES)

  _TSK_HAS_NANO_FS_TYPES = [
      pytsk3.TSK_FS_TYPE_EXFAT,
      pytsk3.TSK_FS_TYPE_EXT4,
      pytsk3.TSK_FS_TYPE_FFS2,
      pytsk3.TSK_FS_TYPE_HFS,
      pytsk3.TSK_FS_TYPE_NTFS]

  def __init__(
      self, resolver_context, file_system, path_spec, is_root=False,
      is_virtual=False, parent_inode=None, tsk_file=None):
    """Initializes a file entry.

    Args:
      resolver_context (Context): resolver context.
      file_system (TSKFileSystem): file system.
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
      self.entry_type = definitions.FILE_ENTRY_TYPE_FILE
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_DIR:
      self.entry_type = definitions.FILE_ENTRY_TYPE_DIRECTORY
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_LNK:
      self.entry_type = definitions.FILE_ENTRY_TYPE_LINK
    elif tsk_fs_meta_type in (
        pytsk3.TSK_FS_META_TYPE_CHR, pytsk3.TSK_FS_META_TYPE_BLK):
      self.entry_type = definitions.FILE_ENTRY_TYPE_DEVICE
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_FIFO:
      self.entry_type = definitions.FILE_ENTRY_TYPE_PIPE
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_SOCK:
      self.entry_type = definitions.FILE_ENTRY_TYPE_SOCKET

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

      tsk_fs_meta_type = getattr(
          self._tsk_file.info.meta, 'type', pytsk3.TSK_FS_META_TYPE_UNDEF)

      if not known_data_attribute_types:
        if tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_REG:
          data_stream = TSKDataStream(self._file_system, None)
          self._data_streams.append(data_stream)

      else:
        for tsk_attribute in self._tsk_file:
          # NTFS allows directories to have data streams.
          if (not self._file_system.IsNTFS() and
              tsk_fs_meta_type != pytsk3.TSK_FS_META_TYPE_REG):
            continue

          if getattr(tsk_attribute, 'info', None) is None:
            continue

          attribute_type = getattr(tsk_attribute.info, 'type', None)
          if attribute_type in known_data_attribute_types:
            data_stream = TSKDataStream(self._file_system, tsk_attribute)
            self._data_streams.append(data_stream)

    return self._data_streams

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      TSKDirectory: a directory.
    """
    if self._directory is None:
      self._directory = TSKDirectory(self._file_system, self.path_spec)

    return self._directory

  def _GetLink(self):
    """Retrieves the link.

    Returns:
      str: path of the linked file.

    Raises:
      BackEndError: if the link is not formatted in UTF-8.
    """
    if self._link is None:
      self._link = ''

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
        raise errors.BackEndError('pytsk3 returned a non UTF-8 formatted link.')

      self._link = link

    return self._link

  def _GetStat(self):
    """Retrieves the stat object.

    Returns:
      VFSStat: stat object.
    """
    stat_object = super(TSKFileEntry, self)._GetStat()

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

    # Other stat information.
    stat_object.ino = getattr(self._tsk_file.info.meta, 'addr', None)

    return stat_object

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      TSKFileEntry: a sub file entry.
    """
    if self.entry_type == definitions.FILE_ENTRY_TYPE_DIRECTORY:
      directory = self._GetDirectory()
      for path_spec in directory.entries:
        yield TSKFileEntry(self._resolver_context, self._file_system, path_spec)

  def _GetTimeValue(self, name):
    """Retrieves a date and time value.

    Args:
      name (str): name of the date and time value, for example "atime" or
          "mtime".

    Returns:
      dfdatetime.DateTimeValues: date and time value or None if not available.
    """
    timestamp = getattr(self._tsk_file.info.meta, name, None)
    if timestamp is None:
      return None

    if self._file_system_type in self._TSK_HAS_NANO_FS_TYPES:
      name_fragment = '{0:s}_nano'.format(name)
      fraction_of_second = getattr(
          self._tsk_file.info.meta, name_fragment, None)
    else:
      fraction_of_second = None

    return TSKTime(timestamp=timestamp, fraction_of_second=fraction_of_second)

  def _TSKFileTimeCopyToStatTimeTuple(self, tsk_file, time_value):
    """Copies a SleuthKit file object time value to a stat timestamp tuple.

    Args:
      tsk_file (pytsk3.File): TSK file.
      time_value (str): name of the time value.

    Returns:
      tuple[int, int]: number of seconds since 1970-01-01 00:00:00 and fraction
          of second in 100 nano seconds intervals. The number of seconds is None
          on error, or if the file system does not include the requested
          timestamp. The fraction of second is None on error, or if the file
          system does not support sub-second precision.

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
    if self._file_system_type not in self._TSK_ATIME_FS_TYPES:
      return None

    return self._GetTimeValue('atime')

  # TODO: add added time support, at least provided for APFS.

  @property
  def backup_time(self):
    """dfdatetime.DateTimeValues: backup time or None if not available."""
    if self._file_system_type not in self._TSK_BKUP_FS_TYPES:
      return None

    return self._GetTimeValue('bkup')

  @property
  def change_time(self):
    """dfdatetime.DateTimeValues: change time or None if not available."""
    if self._file_system_type not in self._TSK_CTIME_FS_TYPES:
      return None

    return self._GetTimeValue('ctime')

  @property
  def creation_time(self):
    """dfdatetime.DateTimeValues: creation time or None if not available."""
    if self._file_system_type not in self._TSK_CRTIME_FS_TYPES:
      return None

    return self._GetTimeValue('crtime')

  @property
  def deletion_time(self):
    """dfdatetime.DateTimeValues: deletion time or None if not available."""
    if self._file_system_type not in self._TSK_DTIME_FS_TYPES:
      return None

    return self._GetTimeValue('dtime')

  @property
  def modification_time(self):
    """dfdatetime.DateTimeValues: modification time or None if not available."""
    if self._file_system_type not in self._TSK_MTIME_FS_TYPES:
      return None

    return self._GetTimeValue('mtime')

  # pylint: disable=missing-return-doc,missing-return-type-doc
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
  def size(self):
    """int: size of the file entry in bytes or None if not available."""
    return getattr(self._tsk_file.info.meta, 'size', None)

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
      return None

    path_spec = copy.deepcopy(self.path_spec)
    if data_stream_name:
      # For HFS DECOMP fork name is exposed however libtsk 4.6.0 seems to handle
      # these differently when opened and the correct behavior seems to be
      # treating this as the default (nameless) fork instead. For context libtsk
      # 4.5.0 is unable to read the data steam and yields an error.
      if self._file_system.IsHFS() and data_stream_name == 'DECOMP':
        data_stream_name = ''

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
      return None

    # TODO: is there a way to determine the link inode number here?
    link_inode = None

    parent_path_spec = getattr(self.path_spec, 'parent', None)
    path_spec = tsk_path_spec.TSKPathSpec(
        location=link, parent=parent_path_spec)

    root_inode = self._file_system.GetRootInode()
    is_root = bool(
        link == self._file_system.LOCATION_ROOT or (
            link_inode is not None and root_inode is not None and
            link_inode == root_inode))

    return TSKFileEntry(
        self._resolver_context, self._file_system, path_spec, is_root=is_root)

  def GetParentFileEntry(self):
    """Retrieves the parent file entry.

    Returns:
      TSKFileEntry: parent file entry or None.
    """
    location = getattr(self.path_spec, 'location', None)
    if location is None:
      return None
    parent_inode = self._parent_inode
    parent_location = self._file_system.DirnamePath(location)
    if parent_inode is None and parent_location is None:
      return None

    if parent_location == '':
      parent_location = self._file_system.PATH_SEPARATOR

    root_inode = self._file_system.GetRootInode()
    is_root = bool(
        parent_location == self._file_system.LOCATION_ROOT or (
            parent_inode is not None and root_inode is not None and
            parent_inode == root_inode))

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

  def IsAllocated(self):
    """Determines if the file entry is allocated.

    Returns:
      bool: True if the file entry is allocated.
    """
    # The flags are an instance of pytsk3.TSK_FS_META_FLAG_ENUM.
    flags = getattr(self._tsk_file.info.meta, 'flags', 0)
    return bool(int(flags) & pytsk3.TSK_FS_META_FLAG_ALLOC)


dfdatetime_factory.Factory.RegisterDateTimeValues(TSKTime)

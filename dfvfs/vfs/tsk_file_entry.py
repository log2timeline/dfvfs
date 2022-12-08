# -*- coding: utf-8 -*-
"""The SleuthKit (TSK) file entry implementation."""

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
from dfvfs.vfs import attribute
from dfvfs.vfs import extent
from dfvfs.vfs import file_entry
from dfvfs.vfs import tsk_attribute
from dfvfs.vfs import tsk_data_stream
from dfvfs.vfs import tsk_directory


class TSKTime(dfdatetime_interface.DateTimeValues):
  """SleuthKit timestamp.

  Attributes:
    fraction_of_second (int): fraction of second, which is an integer that
        contains the number 100 nano seconds before Sleuthkit 4.2.0 or
        number of nano seconds in Sleuthkit 4.2.0 and later.
  """

  _100_NANOSECONDS_PER_SECOND = 10000000
  _NANOSECONDS_PER_SECOND = 1000000000

  def __init__(
      self, fraction_of_second=None, precision=None, time_zone_offset=None,
      timestamp=None):
    """Initializes a SleuthKit timestamp.

    Args:
      fraction_of_second (Optional[int]): fraction of second, which is
          an integer that contains the number 100 nano seconds before
          Sleuthkit 4.2.0 or number of nano seconds in Sleuthkit 4.2.0
          and later.
      precision (Optional[int]): precision of the date and time value, which
          should be one of the PRECISION_VALUES in dfDateTime definitions.
      time_zone_offset (Optional[int]): time zone offset in number of minutes
          from UTC or None if not set.
      timestamp (Optional[int]): POSIX timestamp.
    """
    # Sleuthkit 4.2.0 switched from 100 nano seconds granularity to
    # 1 nano second granularity.
    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      granularity = dfdatetime_definitions.PRECISION_1_NANOSECOND
    else:
      granularity = dfdatetime_definitions.PRECISION_100_NANOSECONDS

    super(TSKTime, self).__init__(
        precision=precision or granularity, time_zone_offset=time_zone_offset)
    self._granularity = granularity
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

          if self._granularity == dfdatetime_definitions.PRECISION_1_NANOSECOND:
            fraction_of_second /= self._NANOSECONDS_PER_SECOND
          else:
            fraction_of_second /= self._100_NANOSECONDS_PER_SECOND

          self._normalized_timestamp += fraction_of_second

        if self._time_zone_offset:
          self._normalized_timestamp -= self._time_zone_offset * 60

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
    time_zone_offset = date_time_values.get('time_zone_offset', 0)

    self._timestamp = self._GetNumberOfSecondsFromElements(
        year, month, day_of_month, hours, minutes, seconds)
    self.fraction_of_second = microseconds
    self._time_zone_offset = time_zone_offset

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
      return (f'{year:04d}-{month:02d}-{day_of_month:02d} '
              f'{hours:02d}:{minutes:02d}:{seconds:02d}')

    if pytsk3.TSK_VERSION_NUM >= 0x040200ff:
      return (f'{year:04d}-{month:02d}-{day_of_month:02d} '
              f'{hours:02d}:{minutes:02d}:{seconds:02d}'
              f'.{self.fraction_of_second:09d}')

    return (f'{year:04d}-{month:02d}-{day_of_month:02d} '
            f'{hours:02d}:{minutes:02d}:{seconds:02d}'
            f'.{self.fraction_of_second:07d}')

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

  _TSK_ISO9660_FS_TYPES = [
      pytsk3.TSK_FS_TYPE_ISO9660,
      pytsk3.TSK_FS_TYPE_ISO9660_DETECT]

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
  _TSK_CRTIME_FS_TYPES.extend(_TSK_ISO9660_FS_TYPES)
  _TSK_CRTIME_FS_TYPES.extend(_TSK_NTFS_FS_TYPES)

  _TSK_DTIME_FS_TYPES = _TSK_EXT_FS_TYPES

  _TSK_MTIME_FS_TYPES = [pytsk3.TSK_FS_TYPE_YAFFS2]
  _TSK_MTIME_FS_TYPES.extend(_TSK_EXT_FS_TYPES)
  _TSK_MTIME_FS_TYPES.extend(_TSK_FAT_FS_TYPES)
  _TSK_MTIME_FS_TYPES.extend(_TSK_HFS_FS_TYPES)
  _TSK_MTIME_FS_TYPES.extend(_TSK_NTFS_FS_TYPES)
  _TSK_MTIME_FS_TYPES.extend(_TSK_UFS_FS_TYPES)

  _TSK_HAS_NANO_FS_TYPES = frozenset([
      pytsk3.TSK_FS_TYPE_EXFAT,
      pytsk3.TSK_FS_TYPE_EXT4,
      pytsk3.TSK_FS_TYPE_FFS2,
      pytsk3.TSK_FS_TYPE_HFS,
      pytsk3.TSK_FS_TYPE_NTFS])

  _TSK_INTERNAL_ATTRIBUTE_TYPES = frozenset([
      pytsk3.TSK_FS_ATTR_TYPE_APFS_COMP_REC,
      pytsk3.TSK_FS_ATTR_TYPE_APFS_DATA,
      pytsk3.TSK_FS_ATTR_TYPE_APFS_RSRC,
      pytsk3.TSK_FS_ATTR_TYPE_HFS_COMP_REC,
      pytsk3.TSK_FS_ATTR_TYPE_HFS_DATA,
      pytsk3.TSK_FS_ATTR_TYPE_HFS_RSRC,
      pytsk3.TSK_FS_ATTR_TYPE_UNIX_EXTENT,
      pytsk3.TSK_FS_ATTR_TYPE_UNIX_INDIR])

  _ATTRIBUTE_TYPE_CLASS_MAPPINGS = {
      pytsk3.TSK_FS_ATTR_TYPE_HFS_EXT_ATTR: tsk_attribute.TSKExtendedAttribute}

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
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_CHR:
      self.entry_type = definitions.FILE_ENTRY_TYPE_CHARACTER_DEVICE
    elif tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_BLK:
      self.entry_type = definitions.FILE_ENTRY_TYPE_BLOCK_DEVICE
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

      for pytsk_attribute in self._tsk_file:
        if getattr(pytsk_attribute, 'info', None):
          attribute_type = getattr(pytsk_attribute.info, 'type', None)
          if attribute_type in self._TSK_INTERNAL_ATTRIBUTE_TYPES:
            continue

          # The data stream is returned as a name-less attribute of type
          # pytsk3.TSK_FS_ATTR_TYPE_DEFAULT.
          if attribute_type == pytsk3.TSK_FS_ATTR_TYPE_DEFAULT and not getattr(
              pytsk_attribute.info, 'name', None):
            continue

          if self._file_system.IsExt():
            attribute_class = tsk_attribute.TSKExtendedAttribute
          else:
            attribute_class = self._ATTRIBUTE_TYPE_CLASS_MAPPINGS.get(
                attribute_type, tsk_attribute.TSKAttribute)

          attribute_object = attribute_class(self._tsk_file, pytsk_attribute)
          self._attributes.append(attribute_object)

    return self._attributes

  def _GetDataStreams(self):
    """Retrieves the data streams.

    Returns:
      list[TSKDataStream]: data streams.
    """
    if self._data_streams is None:
      if self._file_system.IsHFS():
        known_data_attribute_types = (
            pytsk3.TSK_FS_ATTR_TYPE_HFS_DEFAULT,
            pytsk3.TSK_FS_ATTR_TYPE_HFS_DATA,
            pytsk3.TSK_FS_ATTR_TYPE_HFS_RSRC)

      elif self._file_system.IsNTFS():
        known_data_attribute_types = (pytsk3.TSK_FS_ATTR_TYPE_NTFS_DATA, )

      else:
        known_data_attribute_types = None

      self._data_streams = []

      tsk_fs_meta_type = getattr(
          self._tsk_file.info.meta, 'type', pytsk3.TSK_FS_META_TYPE_UNDEF)

      if not known_data_attribute_types:
        if tsk_fs_meta_type == pytsk3.TSK_FS_META_TYPE_REG:
          data_stream = tsk_data_stream.TSKDataStream(self, None)
          self._data_streams.append(data_stream)

      else:
        for pytsk_attribute in self._tsk_file:
          # NTFS allows directories to have data streams.
          if (not self._file_system.IsNTFS() and
              tsk_fs_meta_type != pytsk3.TSK_FS_META_TYPE_REG):
            continue

          if getattr(pytsk_attribute, 'info', None) is None:
            continue

          attribute_type = getattr(pytsk_attribute.info, 'type', None)
          if attribute_type in known_data_attribute_types:
            data_stream = tsk_data_stream.TSKDataStream(self, pytsk_attribute)
            self._data_streams.append(data_stream)

    return self._data_streams

  def _GetDirectory(self):
    """Retrieves a directory.

    Returns:
      TSKDirectory: a directory.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_DIRECTORY:
      return None

    return tsk_directory.TSKDirectory(self._file_system, self.path_spec)

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
        link = link.decode('utf8')
      except UnicodeError:
        raise errors.BackEndError('pytsk3 returned a non UTF-8 formatted link.')

      self._link = ''.join([self._file_system.PATH_SEPARATOR, link])

    return self._link

  def _GetStatAttribute(self):
    """Retrieves a stat attribute.

    Returns:
      StatAttribute: a stat attribute or None if not available.
    """
    mode = getattr(self._tsk_file.info.meta, 'mode', None)
    if mode is not None:
      # We need to cast mode to an int since it is of type
      # pytsk3.TSK_FS_META_MODE_ENUM.
      mode = int(mode)

    stat_attribute = attribute.StatAttribute()
    stat_attribute.group_identifier = getattr(
        self._tsk_file.info.meta, 'gid', None)
    stat_attribute.inode_number = getattr(
        self._tsk_file.info.meta, 'addr', None)
    stat_attribute.mode = mode
    stat_attribute.number_of_links = getattr(
        self._tsk_file.info.meta, 'nlink', None)
    stat_attribute.owner_identifier = getattr(
        self._tsk_file.info.meta, 'uid', None)
    stat_attribute.size = getattr(self._tsk_file.info.meta, 'size', None)
    stat_attribute.type = self.entry_type

    return stat_attribute

  def _GetSubFileEntries(self):
    """Retrieves sub file entries.

    Yields:
      TSKFileEntry: a sub file entry.
    """
    if self._directory is None:
      self._directory = self._GetDirectory()

    if self._directory:
      for path_spec in self._directory.entries:
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
      fraction_of_second = getattr(
          self._tsk_file.info.meta, f'{name:s}_nano', None)
    else:
      fraction_of_second = None

    is_local_time = False
    precision = None

    if self._file_system_type in (
        pytsk3.TSK_FS_TYPE_EXT2, pytsk3.TSK_FS_TYPE_EXT3):
      precision = dfdatetime_definitions.PRECISION_1_SECOND

    elif self._file_system_type == pytsk3.TSK_FS_TYPE_EXT4:
      # Note that pytsk3 can return 0 for an ext4 creation time even if the
      # inode does not contain it.
      if name == 'crtime' and timestamp == 0:
        return None

    elif self._file_system_type in (
        pytsk3.TSK_FS_TYPE_FAT12, pytsk3.TSK_FS_TYPE_FAT16,
        pytsk3.TSK_FS_TYPE_FAT32):
      is_local_time = True
      if name == 'atime':
        precision = dfdatetime_definitions.PRECISION_1_DAY
      else:
        precision = dfdatetime_definitions.PRECISION_2_SECONDS

    elif self._file_system_type == pytsk3.TSK_FS_TYPE_NTFS:
      precision = dfdatetime_definitions.PRECISION_100_NANOSECONDS

    # TODO: determine if file system type is traditional HFS and set
    # is_local_time accordingly.

    date_time = TSKTime(
        fraction_of_second=fraction_of_second, precision=precision,
        timestamp=timestamp)
    date_time.is_local_time = is_local_time
    return date_time

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

  def GetExtents(self):
    """Retrieves the extents.

    Returns:
      list[Extent]: the extents.

    Raises:
      BackEndError: if pytsk3 returns no file system block size or data stream
          size.
    """
    if self.entry_type != definitions.FILE_ENTRY_TYPE_FILE:
      return []

    data_attribute = None
    for pytsk_attribute in self._tsk_file:
      if not getattr(pytsk_attribute, 'info', None):
        continue

      attribute_name = getattr(pytsk_attribute.info, 'name', None)
      attribute_type = getattr(pytsk_attribute.info, 'type', None)

      # The data stream is returned as a name-less attribute of type
      # pytsk3.TSK_FS_ATTR_TYPE_DEFAULT, pytsk3.TSK_FS_ATTR_TYPE_NTFS_DATA or
      # pytsk3.TSK_FS_ATTR_TYPE_NTFS_DATA
      if not attribute_name and attribute_type in (
          pytsk3.TSK_FS_ATTR_TYPE_DEFAULT, pytsk3.TSK_FS_ATTR_TYPE_HFS_DATA,
          pytsk3.TSK_FS_ATTR_TYPE_NTFS_DATA):
        data_attribute = pytsk_attribute
        break

    extents = []
    if data_attribute:
      tsk_file_system = self._file_system.GetFsInfo()
      block_size = getattr(tsk_file_system.info, 'block_size', None)
      if not block_size:
        raise errors.BackEndError('pytsk3 returned no file system block size.')

      data_stream_size = getattr(data_attribute.info, 'size', None)
      if data_stream_size is None:
        raise errors.BackEndError('pytsk3 returned no data stream size.')

      data_stream_number_of_blocks, remainder = divmod(
          data_stream_size, block_size)
      if remainder:
        data_stream_number_of_blocks += 1

      total_number_of_blocks = 0
      for tsk_attr_run in data_attribute:
        if tsk_attr_run.flags & pytsk3.TSK_FS_ATTR_RUN_FLAG_SPARSE:
          extent_type = definitions.EXTENT_TYPE_SPARSE
        else:
          extent_type = definitions.EXTENT_TYPE_DATA

        extent_offset = tsk_attr_run.addr * block_size
        extent_size = tsk_attr_run.len

        # Note that the attribute data runs can be larger than the actual
        # allocated size.
        if total_number_of_blocks + extent_size > data_stream_number_of_blocks:
          extent_size = data_stream_number_of_blocks - total_number_of_blocks

        total_number_of_blocks += extent_size
        extent_size *= block_size

        data_stream_extent = extent.Extent(
            extent_type=extent_type, offset=extent_offset, size=extent_size)
        extents.append(data_stream_extent)

        if total_number_of_blocks >= data_stream_number_of_blocks:
          break

    return extents

  def GetFileObject(self, data_stream_name=''):
    """Retrieves a file-like object of a specific data stream.

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
      if not self._file_system.IsHFS() or data_stream_name != 'DECOMP':
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

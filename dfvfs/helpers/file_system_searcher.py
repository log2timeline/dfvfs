# -*- coding: utf-8 -*-
"""A searcher to find file entries within a file system."""

import re

try:
  import re._constants as sre_constants
except ImportError:
  import sre_constants  # pylint: disable=deprecated-module

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import glob2regex
from dfvfs.path import factory as path_spec_factory


class FindSpec(object):
  """Find specification."""

  def __init__(
      self, case_sensitive=True, file_entry_types=None, is_allocated=True,
      location=None, location_glob=None, location_regex=None,
      location_separator='/'):
    """Initializes a find specification.

    Args:
      case_sensitive (Optional[bool]): True if string matches should be case
          sensitive.
      file_entry_types (Optional[list[str]]): file entry types, where
          None indicates no preference.
      is_allocated (Optional[bool]): True if the file entry should be
          allocated, where None represents no preference.
      location (Optional[str|list[str]]): location or location segments,
          where None indicates no preference. The location should be defined
          relative to the root of the file system. Note that the string will
          be split into segments based on the file system specific path
          segment separator.
      location_glob (Optional[str:list[str]]): location glob or location glob
          segments, where None indicates no preference. The location glob
          should be defined relative to the root of the file system. The default
          is None. Note that the string will be split into segments based on
          the file system specific path segment separator.
      location_regex (Optional[str|list[str]]): location regular expression or
          location regular expression segments, where None indicates no
          preference. The location regular expression should be defined
          relative to the root of the file system. The default is None. Note
          that the string will be split into segments based on the file system
          specific path segment separator.
      location_separator (str): location segment separator.

    Raises:
      TypeError: if the location, location_glob or location_regex type
          is not supported.
      ValueError: if the location, location_glob or location_regex arguments
          are used at the same time, or if location separator is missing and
          the location argument is of type string.
    """
    location_arguments = [argument for argument in (
        location, location_glob, location_regex) if argument]

    if len(location_arguments) > 1:
      raise ValueError((
          'The location, location_glob and location_regex arguments cannot '
          'be used at same time.'))

    if (location_arguments and isinstance(location_arguments[0], str) and
        not location_separator):
      raise ValueError('Missing location separator.')

    super(FindSpec, self).__init__()
    self._file_entry_types = file_entry_types
    self._is_allocated = is_allocated
    self._is_case_sensitive = case_sensitive
    self._is_regex = False
    self._location = None
    self._location_regex = None
    self._location_segments = None
    self._number_of_location_segments = None

    if location is not None:
      if isinstance(location, str):
        self._location = location

      elif isinstance(location, list):
        self._location_segments = location

      else:
        location_type = type(location)
        raise TypeError(f'Unsupported location type: {location_type!s}.')

    elif location_glob is not None:
      if isinstance(location_glob, str):
        self._location_regex = self._ConvertLocationGlob2Regex(location_glob)

      elif isinstance(location_glob, list):
        self._location_segments = []
        for location_segment in location_glob:
          location_regex = self._ConvertLocationGlob2Regex(location_segment)

          self._location_segments.append(location_regex)

      else:
        location_glob_type = type(location_glob)
        raise TypeError(
            f'Unsupported location_glob type: {location_glob_type!s}.')

      self._is_regex = True

    elif location_regex is not None:
      if isinstance(location_regex, str):
        self._location_regex = location_regex

      elif isinstance(location_regex, list):
        self._location_segments = location_regex

      else:
        location_regex_type = type(location_regex)
        raise TypeError(
            f'Unsupported location_regex type: {location_regex_type!s}.')

      self._is_regex = True

    if self._location:
      self._location_segments = self._SplitPath(
          self._location, location_separator)

    elif self._location_regex:
      if location_separator == '\\':
        # The backslash '\' is escaped within a regular expression.
        location_separator = '\\\\'
      self._location_segments = self._SplitPath(
          self._location_regex, location_separator)

    if self._location_segments is not None:
      self._number_of_location_segments = len(self._location_segments)

    # TODO: add support for name
    # TODO: add support for owner (user, group)
    # TODO: add support for permissions (mode)
    # TODO: add support for size
    # TODO: add support for time values
    # TODO: add support for expression e.g.
    # attribute['$FILE_NAME'].creation_type == 'x'

  def _CheckFileEntryType(self, file_entry):
    """Checks the file entry type find specifications.

    Args:
      file_entry (FileEntry): file entry.

    Returns:
      bool: True if the file entry matches the find specification, False if
          not or None if no file entry type specification is defined.
    """
    if not self._file_entry_types:
      return None

    return (
        self._CheckIsDevice(file_entry) or self._CheckIsDirectory(file_entry) or
        self._CheckIsFile(file_entry) or self._CheckIsLink(file_entry) or
        self._CheckIsPipe(file_entry) or self._CheckIsSocket(file_entry))

  def _CheckIsAllocated(self, file_entry):
    """Checks the is_allocated find specification.

    Args:
      file_entry (FileEntry): file entry.

    Returns:
      bool: True if the file entry matches the find specification, False if
          not or None if no allocation specification is defined.
    """
    if self._is_allocated is None:
      return None
    return self._is_allocated == file_entry.IsAllocated()

  def _CheckIsDevice(self, file_entry):
    """Checks the is_device find specification.

    Args:
      file_entry (FileEntry): file entry.

    Returns:
      bool: True if the file entry matches the find specification, False if not.
    """
    if (definitions.FILE_ENTRY_TYPE_BLOCK_DEVICE not in (
           self._file_entry_types) and
       definitions.FILE_ENTRY_TYPE_CHARACTER_DEVICE not in (
           self._file_entry_types) and
       definitions.FILE_ENTRY_TYPE_DEVICE not in self._file_entry_types):
      return False
    return file_entry.IsDevice()

  def _CheckIsDirectory(self, file_entry):
    """Checks the is_directory find specification.

    Args:
      file_entry (FileEntry): file entry.

    Returns:
      bool: True if the file entry matches the find specification, False if not.
    """
    if definitions.FILE_ENTRY_TYPE_DIRECTORY not in self._file_entry_types:
      return False
    return file_entry.IsDirectory()

  def _CheckIsFile(self, file_entry):
    """Checks the is_file find specification.

    Args:
      file_entry (FileEntry): file entry.

    Returns:
      bool: True if the file entry matches the find specification, False if not.
    """
    if definitions.FILE_ENTRY_TYPE_FILE not in self._file_entry_types:
      return False
    return file_entry.IsFile()

  def _CheckIsLink(self, file_entry):
    """Checks the is_link find specification.

    Args:
      file_entry (FileEntry): file entry.

    Returns:
      bool: True if the file entry matches the find specification, False if not.
    """
    if definitions.FILE_ENTRY_TYPE_LINK not in self._file_entry_types:
      return False
    return file_entry.IsLink()

  def _CheckIsPipe(self, file_entry):
    """Checks the is_pipe find specification.

    Args:
      file_entry (FileEntry): file entry.

    Returns:
      bool: True if the file entry matches the find specification, False if not.
    """
    if definitions.FILE_ENTRY_TYPE_PIPE not in self._file_entry_types:
      return False
    return file_entry.IsPipe()

  def _CheckIsSocket(self, file_entry):
    """Checks the is_socket find specification.

    Args:
      file_entry (FileEntry): file entry.

    Returns:
      bool: True if the file entry matches the find specification, False if not.
    """
    if definitions.FILE_ENTRY_TYPE_SOCKET not in self._file_entry_types:
      return False
    return file_entry.IsSocket()

  def _CompareWithLocationSegment(self, location_segment, segment_index):
    """Compares a location segment against a find specification.

    Args:
      location_segment (str): location segment.
      segment_index (int): index of the location segment to compare against,
          where 0 represents the root segment.

    Returns:
      bool: True if the location segment of the file entry matches that of the
          find specification, False if not or if the find specification has no
          location defined.
    """
    if (self._location_segments is None or segment_index < 0 or
        segment_index > self._number_of_location_segments):
      return False

    # Note that the root has no entry in the location segments and
    # no name to match.
    if segment_index == 0:
      return True

    segment_name = self._location_segments[segment_index - 1]

    if self._is_regex:
      if isinstance(segment_name, str):
        # Allow '\n' to be matched by '.' and make '\w', '\W', '\b', '\B',
        # '\d', '\D', '\s' and '\S' Unicode safe.
        flags = re.DOTALL | re.UNICODE
        if not self._is_case_sensitive:
          flags |= re.IGNORECASE

        try:
          segment_name = re.compile(f'^{segment_name:s}$', flags=flags)
        except sre_constants.error:
          # TODO: set self._location_segments[segment_index - 1] to None ?
          return False

        self._location_segments[segment_index - 1] = segment_name

    elif not self._is_case_sensitive:
      segment_name = segment_name.lower()
      self._location_segments[segment_index - 1] = segment_name

    if self._is_regex:
      return bool(segment_name.match(location_segment))  # pylint: disable=no-member

    if self._is_case_sensitive:
      return bool(segment_name == location_segment)

    return bool(segment_name == location_segment.lower())

  def _ConvertLocationGlob2Regex(self, location_glob):
    """Converts a location glob into a regular expression.

    Args:
      location_glob (str): location glob pattern.

    Returns:
      str: location regular expression pattern.
    """
    location_regex = glob2regex.Glob2Regex(location_glob)

    # The regular expression from glob2regex contains escaped forward
    # slashes "/", which needs to be undone.
    return location_regex.replace('\\/', '/')

  def _SplitPath(self, path, path_separator):
    """Splits the path into path segments.

    Args:
      path (str): path.
      path_separator (str): path separator.

    Returns:
      list[str]: path segments without the root path segment, which is
          an empty string.
    """
    # Split the path with the path separator and remove empty path segments.
    return list(filter(None, path.split(path_separator)))

  def AtLastLocationSegment(self, segment_index):
    """Determines if the a location segment is the last one or greater.

    Args:
      segment_index (int): index of the location path segment.

    Returns:
      bool: True if at maximum depth, False if not.
    """
    return bool(self._location_segments is not None and
                segment_index >= self._number_of_location_segments)

  def CompareLocation(self, file_entry, mount_point=None):
    """Compares a file entry location against the find specification.

    Args:
      file_entry (FileEntry): file entry.
      mount_point (Optional[PathSpec]): mount point path specification that
          refers to the base location of the file system. The mount point
          is ignored if it is not an OS path specification.

    Returns:
      bool: True if the location of the file entry matches that of the find
          specification, False if not or if the find specification has no
          location defined.

    Raises:
      ValueError: if mount point is set and is of type OS and the location of
          the path specification of the file entry falls outside the mount
          point.
    """
    location = getattr(file_entry.path_spec, 'location', None)
    if self._location_segments is None or location is None:
      return False

    if (mount_point and
        mount_point.type_indicator == definitions.TYPE_INDICATOR_OS and
        file_entry.path_spec.type_indicator == definitions.TYPE_INDICATOR_OS):
      if not location.startswith(mount_point.location):
        raise ValueError(
            'File entry path specification location not inside mount point.')

      location = location[len(mount_point.location):]

    file_system = file_entry.GetFileSystem()
    location_segments = file_system.SplitPath(location)

    for segment_index in range(self._number_of_location_segments):
      try:
        location_segment = location_segments[segment_index]
      except IndexError:
        return False

      if not self._CompareWithLocationSegment(
          location_segment, segment_index + 1):
        return False

    return True

  def CompareNameWithLocationSegment(self, file_entry, segment_index):
    """Compares a file entry name against a find specification location segment.

    Args:
      file_entry (FileEntry): file entry.
      segment_index (int): index of the location segment to compare against,
          where 0 represents the root segment.

    Returns:
      bool: True if the location segment of the file entry matches that of the
          find specification, False if not or if the find specification has no
          location defined.
    """
    return self._CompareWithLocationSegment(file_entry.name, segment_index)

  def CompareTraits(self, file_entry):
    """Compares a file entry traits against the find specification.

    Args:
      file_entry (FileEntry): file entry.

    Returns:
      bool: True if the traits of the file entry, such as type, matches the
          find specification, False otherwise.
    """
    match = self._CheckFileEntryType(file_entry)
    if match is not None and not match:
      return False

    match = self._CheckIsAllocated(file_entry)
    if match is not None and not match:
      return False

    return True

  def HasLocation(self):
    """Determines if the find specification has a location defined.

    Returns:
      bool: True if find specification has a location defined, False if not.
    """
    return bool(self._location_segments)

  def IsLastLocationSegment(self, segment_index):
    """Determines if the a location segment is the last one.

    Args:
      segment_index (int): index of the location path segment.

    Returns:
      bool: True if at maximum depth, False if not.
    """
    return bool(self._location_segments is not None and
                segment_index == self._number_of_location_segments)


class FileSystemSearcher(object):
  """Searcher to find file entries within a file system."""

  def __init__(self, file_system, mount_point):
    """Initializes a file system searcher.

    Args:
      file_system (FileSystem): file system.
      mount_point (PathSpec): mount point path specification that refers
          to the base location of the file system.

    Raises:
      PathSpecError: if the mount point path specification is incorrect.
      ValueError: when file system or mount point is not set.
    """
    if not file_system or not mount_point:
      raise ValueError('Missing file system or mount point value.')

    if path_spec_factory.Factory.IsSystemLevelTypeIndicator(
        file_system.type_indicator):
      if not hasattr(mount_point, 'location'):
        raise errors.PathSpecError(
            'Mount point path specification missing location.')

    super(FileSystemSearcher, self).__init__()
    self._file_system = file_system
    self._mount_point = mount_point

  def _FindInFileEntry(self, file_entry, find_specs, segment_index):
    """Searches for matching file entries within the file entry.

    Args:
      file_entry (FileEntry): file entry.
      find_specs (list[FindSpec]): find specifications.
      segment_index (int): index of the location path segment to compare.

    Yields:
      PathSpec: path specification of a matching file entry.
    """
    sub_find_specs = []
    for find_spec in find_specs:
      has_location = find_spec.HasLocation()
      # Do a quick check to see if the current location segment matches.
      location_match = find_spec.CompareNameWithLocationSegment(
          file_entry, segment_index)
      is_last_location_segment = find_spec.IsLastLocationSegment(
          segment_index)

      if location_match and is_last_location_segment:
        # Check if the full location matches.
        location_match = find_spec.CompareLocation(
            file_entry, mount_point=self._mount_point)

      if not has_location or (location_match and is_last_location_segment):
        if find_spec.CompareTraits(file_entry):
          yield file_entry.path_spec

      at_last_location_segment = find_spec.AtLastLocationSegment(segment_index)
      if (not has_location or location_match) and not at_last_location_segment:
        sub_find_specs.append(find_spec)

    if sub_find_specs:
      segment_index += 1
      try:
        for sub_file_entry in file_entry.sub_file_entries:
          for matching_path_spec in self._FindInFileEntry(
              sub_file_entry, sub_find_specs, segment_index):
            yield matching_path_spec

      except errors.AccessError:
        pass

  def Find(self, find_specs=None):
    """Searches for matching file entries within the file system.

    Args:
      find_specs (list[FindSpec]): find specifications. where None
          will return all allocated file entries.

    Yields:
      PathSpec: path specification of a matching file entry.
    """
    if not find_specs:
      find_specs.append(FindSpec())

    if path_spec_factory.Factory.IsSystemLevelTypeIndicator(
        self._file_system.type_indicator):
      file_entry = self._file_system.GetFileEntryByPathSpec(self._mount_point)
    else:
      file_entry = self._file_system.GetRootFileEntry()

    # Note that APFS can have a volume without a root directory.
    if file_entry:
      for matching_path_spec in self._FindInFileEntry(
          file_entry, find_specs, 0):
        yield matching_path_spec

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      FileEntry: file entry or None.
    """
    return self._file_system.GetFileEntryByPathSpec(path_spec)

  def GetRelativePath(self, path_spec):
    """Returns the relative path based on a resolved path specification.

    The relative path is the location of the upper most path specification.
    The the location of the mount point is stripped off if relevant.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      str: corresponding relative path or None if the relative path could not
          be determined.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    location = getattr(path_spec, 'location', None)
    if location is None:
      raise errors.PathSpecError('Path specification missing location.')

    if path_spec_factory.Factory.IsSystemLevelTypeIndicator(
        self._file_system.type_indicator):
      if not location.startswith(self._mount_point.location):
        raise errors.PathSpecError(
            'Path specification does not contain mount point.')
    else:
      if not hasattr(path_spec, 'parent'):
        raise errors.PathSpecError('Path specification missing parent.')

      if path_spec.parent != self._mount_point:
        raise errors.PathSpecError(
            'Path specification does not contain mount point.')

    path_segments = self._file_system.SplitPath(location)

    if path_spec_factory.Factory.IsSystemLevelTypeIndicator(
        self._file_system.type_indicator):
      mount_point_path_segments = self._file_system.SplitPath(
          self._mount_point.location)
      path_segments = path_segments[len(mount_point_path_segments):]

    return ''.join([
        self._file_system.PATH_SEPARATOR,
        self._file_system.PATH_SEPARATOR.join(path_segments)])

  def SplitPath(self, path):
    """Splits the path into path segments.

    Args:
      path (str): path.

    Returns:
      list[str]: path segments without the root path segment, which is an
          empty string.
    """
    return self._file_system.SplitPath(path)

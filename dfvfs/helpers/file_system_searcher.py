# -*- coding: utf-8 -*-
"""A searcher to find file entries within a file system."""

import fnmatch
import re
import sre_constants

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import py2to3
from dfvfs.path import factory as path_spec_factory


class FindSpec(object):
  """Find specification object."""

  def __init__(
      self, file_entry_types=None, is_allocated=True, location=None,
      location_glob=None, location_regex=None, case_sensitive=True):
    """Initializes the find specification object.

    Args:
      file_entry_types: optional file entry types list or None to indicate
                        no preference.
      is_allocated: optional boolean value to indicate the file entry should
                    be allocated, where None represents no preference.
      location: optional location string or list of location segments, or None
                to indicate no preference. The location should be defined
                relative to the root of the file system.
                Note that the string will be split into segments based on the
                file system specific path segment separator.
      location_glob: optional location glob string or list of location glob
                     segments, or None to indicate no preference. The location
                     glob should be defined relative to the root of the file
                     system. The default is None. Note that the string will be
                     split into segments based on the file system specific
                     path segment separator.
      location_regex: optional location regular expression string or list of
                      location regular expression segments, or None to indicate
                      no preference. The location regular expression should be
                      defined relative to the root of the file system. The
                      default is None. Note that the string will be split into
                      segments based on the file system specific path segment
                      separator.
      case_sensitive: optional boolean value to indicate string matches should
                      be case sensitive.

    Raises:
      TypeError: if the location, location_glob or location_regex type
                 is not supported.
      ValueError: if the location, location_glob or location_regex arguments
                  are used at the same time.
    """
    if (location is not None and location_glob is not None and
        location_regex is not None):
      raise ValueError((
          u'The location, location_glob and location_regex arguments cannot '
          u'be used at same time.'))

    super(FindSpec, self).__init__()
    self._file_entry_types = file_entry_types
    self._is_allocated = is_allocated
    self._is_case_sensitive = case_sensitive
    self._is_regex = False
    self._location = None
    self._location_regex = None
    self._location_segments = None
    self._number_of_location_segments = 0

    if location is not None:
      if isinstance(location, py2to3.STRING_TYPES):
        self._location = location
      elif isinstance(location, list):
        self._location_segments = location
      else:
        raise TypeError(u'Unsupported location type: {0:s}.'.format(
            type(location)))

    elif location_glob is not None:
      # fnmatch.translate() is used to convert a glob into a regular expression.
      # The resulting regular expression has "\Z(?ms)" defined at its end,
      # which needs to be removed and escapes the forward slash "/", which
      # needs to be undone.
      if isinstance(location_glob, py2to3.STRING_TYPES):
        fnmatch_regex = fnmatch.translate(location_glob)
        fnmatch_regex, _, _ = fnmatch_regex.rpartition(r'\Z(?ms)')
        fnmatch_regex = fnmatch_regex.replace(u'\\/', '/')
        self._location_regex = fnmatch_regex
      elif isinstance(location_glob, list):
        self._location_segments = []
        for location_segment in location_glob:
          fnmatch_regex = fnmatch.translate(location_segment)
          fnmatch_regex, _, _ = fnmatch_regex.rpartition(r'\Z(?ms)')
          fnmatch_regex = fnmatch_regex.replace(u'\\/', '/')
          self._location_segments.append(fnmatch_regex)
      else:
        raise TypeError(u'Unsupported location_glob type: {0:s}.'.format(
            type(location_glob)))

      self._is_regex = True

    elif location_regex is not None:
      if isinstance(location_regex, py2to3.STRING_TYPES):
        self._location_regex = location_regex
      elif isinstance(location_regex, list):
        self._location_segments = location_regex
      else:
        raise TypeError(u'Unsupported location_regex type: {0:s}.'.format(
            type(location_regex)))

      self._is_regex = True

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
      file_entry: the file entry (instance of FileEntry).

    Returns:
      True if the file entry matches the find specification, False if not or
      None if no file entry type specification is defined.
    """
    if self._file_entry_types is None:
      return

    return (self._CheckIsDevice(file_entry) or
            self._CheckIsDirectory(file_entry) or
            self._CheckIsFile(file_entry) or
            self._CheckIsLink(file_entry) or
            self._CheckIsPipe(file_entry) or
            self._CheckIsSocket(file_entry))

  def _CheckIsAllocated(self, file_entry):
    """Checks the is_allocated find specification.

    Args:
      file_entry: the file entry (instance of FileEntry).

    Returns:
      True if the file entry matches the find specification, False if not or
      None if no allocation specification is defined.
    """
    if self._is_allocated is None:
      return
    return self._is_allocated == file_entry.IsAllocated()

  def _CheckIsDevice(self, file_entry):
    """Checks the is_device find specification.

    Args:
      file_entry: the file entry (instance of FileEntry).

    Returns:
      True if the file entry matches the find specification, False if not.
    """
    if definitions.FILE_ENTRY_TYPE_DEVICE not in self._file_entry_types:
      return False
    return file_entry.IsDevice()

  def _CheckIsDirectory(self, file_entry):
    """Checks the is_directory find specification.

    Args:
      file_entry: the file entry (instance of FileEntry).

    Returns:
      True if the file entry matches the find specification, False if not.
    """
    if definitions.FILE_ENTRY_TYPE_DIRECTORY not in self._file_entry_types:
      return False
    return file_entry.IsDirectory()

  def _CheckIsFile(self, file_entry):
    """Checks the is_file find specification.

    Args:
      file_entry: the file entry (instance of FileEntry).

    Returns:
      True if the file entry matches the find specification, False if not.
    """
    if definitions.FILE_ENTRY_TYPE_FILE not in self._file_entry_types:
      return False
    return file_entry.IsFile()

  def _CheckIsLink(self, file_entry):
    """Checks the is_link find specification.

    Args:
      file_entry: the file entry (instance of FileEntry).

    Returns:
      True if the file entry matches the find specification, False if not.
    """
    if definitions.FILE_ENTRY_TYPE_LINK not in self._file_entry_types:
      return False
    return file_entry.IsLink()

  def _CheckIsPipe(self, file_entry):
    """Checks the is_pipe find specification.

    Args:
      file_entry: the file entry (instance of FileEntry).

    Returns:
      True if the file entry matches the find specification, False if not.
    """
    if definitions.FILE_ENTRY_TYPE_PIPE not in self._file_entry_types:
      return False
    return file_entry.IsPipe()

  def _CheckIsSocket(self, file_entry):
    """Checks the is_socket find specification.

    Args:
      file_entry: the file entry (instance of FileEntry).

    Returns:
      True if the file entry matches the find specification, False if not.
    """
    if definitions.FILE_ENTRY_TYPE_SOCKET not in self._file_entry_types:
      return False
    return file_entry.IsSocket()

  def _CheckLocation(self, file_entry, search_depth):
    """Checks the location find specification.

    Args:
      file_entry: the file entry (instance of FileEntry).
      search_depth: the search depth.

    Returns:
      True if the file entry matches the find specification, False if not.
    """
    if self._location_segments is None:
      return False

    if search_depth < 0 or search_depth > self._number_of_location_segments:
      return False

    # Note that the root has no entry in the location segments and
    # no name to match.
    if search_depth == 0:
      segment_name = u''
    else:
      segment_name = self._location_segments[search_depth - 1]

      if self._is_regex:
        if isinstance(segment_name, py2to3.STRING_TYPES):
          # Allow '\n' to be matched by '.' and make '\w', '\W', '\b', '\B',
          # '\d', '\D', '\s' and '\S' Unicode safe.
          flags = re.DOTALL | re.UNICODE
          if not self._is_case_sensitive:
            flags |= re.IGNORECASE

          try:
            segment_name = r'^{0:s}$'.format(segment_name)
            segment_name = re.compile(segment_name, flags=flags)
          except sre_constants.error:
            # TODO: set self._location_segments[search_depth - 1] to None ?
            return False

          self._location_segments[search_depth - 1] = segment_name

      elif not self._is_case_sensitive:
        segment_name = segment_name.lower()
        self._location_segments[search_depth - 1] = segment_name

    if search_depth > 0:
      if self._is_regex:
        if not segment_name.match(file_entry.name):
          return False

      elif self._is_case_sensitive:
        if segment_name != file_entry.name:
          return False

      elif segment_name != file_entry.name.lower():
        return False

    return True

  def _SplitPath(self, path, path_separator):
    """Splits the path into path segments.

    Args:
      path: a string containing the path.
      path_separator: a string containing the path separator.

    Returns:
      A list of path segements without the root path segment, which is an
      empty string.
    """
    # Split the path with the path separator and remove empty path segments.
    return list(filter(None, path.split(path_separator)))

  def AtMaximumDepth(self, search_depth):
    """Determines if the find specification is at maximum depth.

    Args:
      search_depth: the search depth.

    Returns:
      True if at maximum depth, False if not.
    """
    if self._location_segments is not None:
      if search_depth == self._number_of_location_segments:
        return True

    return False

  def Initialize(self, file_system):
    """Initializes find specification for matching.

    Args:
      file_system: the file system object (instance of FileSystem).
    """
    if self._location is not None:
      self._location_segments = self._SplitPath(
          self._location, file_system.PATH_SEPARATOR)

    elif self._location_regex is not None:
      path_separator = file_system.PATH_SEPARATOR
      if path_separator == u'\\':
        # The backslash '\' is escaped within a regular expression.
        path_separator = u'\\\\'

      self._location_segments = self._SplitPath(
          self._location_regex, path_separator)

    if self._location_segments is not None:
      self._number_of_location_segments = len(self._location_segments)

  def Matches(self, file_entry, search_depth):
    """Determines if the file entry matches the find specification.

    Args:
      file_entry: the file entry (instance of FileEntry).
      search_depth: the search depth.

    Returns:
      A tuple containing:
        True if the file entry matches the find specification, False otherwise.
        True if the location matches, False if not or None if no location
        specified.
    """
    if self._location_segments is None:
      location_match = None
    else:
      location_match = self._CheckLocation(file_entry, search_depth)
      if not location_match:
        return False, location_match

      if search_depth != self._number_of_location_segments:
        return False, location_match

    match = self._CheckFileEntryType(file_entry)
    if match is not None and not match:
      return False, location_match

    match = self._CheckIsAllocated(file_entry)
    if match is not None and not match:
      return False, location_match

    return True, location_match


class FileSystemSearcher(object):
  """Searcher object to find file entries within a file system."""

  def __init__(self, file_system, mount_point):
    """Initializes the file system searcher.

    Args:
      file_system: the file system object (instance of FileSystem).
      mount_point: the mount point path specification (instance of PathSpec).

    Raises:
      PathSpecError: if the mount point path specification is incorrect.
      ValueError: when file system or mount point is not set.
    """
    if not file_system or not mount_point:
      raise ValueError(u'Missing file system or mount point value.')

    if path_spec_factory.Factory.IsSystemLevelTypeIndicator(
        file_system.type_indicator):
      if not hasattr(mount_point, u'location'):
        raise errors.PathSpecError(
            u'Mount point path specification missing location.')

    super(FileSystemSearcher, self).__init__()

    self._file_system = file_system
    self._mount_point = mount_point

  def _FindInFileEntry(self, file_entry, find_specs, search_depth):
    """Searches for matching file entries within the file entry.

    Args:
      file_entry: the file entry (instance of FileEntry).
      find_specs: a list of find specifications (instances of FindSpec).
      search_depth: the search depth.

    Yields:
      The path specification of the matching file entries (instances of
      PathSpec).
    """
    sub_find_specs = []
    for find_spec in find_specs:
      match, location_match = find_spec.Matches(file_entry, search_depth)
      if match:
        yield file_entry.path_spec

      if location_match != False and not find_spec.AtMaximumDepth(search_depth):
        sub_find_specs.append(find_spec)

    if not sub_find_specs:
      return

    search_depth += 1
    try:
      for sub_file_entry in file_entry.sub_file_entries:
        for matching_path_spec in self._FindInFileEntry(
            sub_file_entry, sub_find_specs, search_depth):
          yield matching_path_spec
    except errors.AccessError:
      pass

  def Find(self, find_specs=None):
    """Searches for matching file entries within the file system.

    Args:
      find_specs: a list of find specifications (instances of FindSpec).
                  The default is None, which will return all allocated
                  file entries.

    Yields:
      The path specification of the matching file entries (instances of
      PathSpec).
    """
    if not find_specs:
      find_specs.append(FindSpec())

    for find_spec in find_specs:
      find_spec.Initialize(self._file_system)

    if path_spec_factory.Factory.IsSystemLevelTypeIndicator(
        self._file_system.type_indicator):
      file_entry = self._file_system.GetFileEntryByPathSpec(self._mount_point)
    else:
      file_entry = self._file_system.GetRootFileEntry()

    for matching_path_spec in self._FindInFileEntry(file_entry, find_specs, 0):
      yield matching_path_spec

  def GetFileEntryByPathSpec(self, path_spec):
    """Retrieves a file entry for a path specification.

    Args:
      path_spec: a path specification (instance of PathSpec).

    Returns:
      A file entry (instance of FileEntry) or None.
    """
    return self._file_system.GetFileEntryByPathSpec(path_spec)

  def GetRelativePath(self, path_spec):
    """Returns the relative path based on a resolved path specification.

    The relative path is the location of the upper most path specification.
    The the location of the mount point is stripped off if relevant.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Returns:
      The corresponding relative path or None if the relative path could not
      be determined.

    Raises:
      PathSpecError: if the path specification is incorrect.
    """
    location = getattr(path_spec, u'location', None)
    if location is None:
      raise errors.PathSpecError(u'Path specification missing location.')

    if path_spec_factory.Factory.IsSystemLevelTypeIndicator(
        self._file_system.type_indicator):
      if not location.startswith(self._mount_point.location):
        raise errors.PathSpecError(
            u'Path specification does not contain mount point.')
    else:
      if not hasattr(path_spec, u'parent'):
        raise errors.PathSpecError(u'Path specification missing parent.')

      if path_spec.parent != self._mount_point:
        raise errors.PathSpecError(
            u'Path specification does not contain mount point.')

    path_segments = self._file_system.SplitPath(location)

    if path_spec_factory.Factory.IsSystemLevelTypeIndicator(
        self._file_system.type_indicator):
      mount_point_path_segments = self._file_system.SplitPath(
          self._mount_point.location)
      path_segments = path_segments[len(mount_point_path_segments):]

    return u'{0:s}{1:s}'.format(
        self._file_system.PATH_SEPARATOR,
        self._file_system.PATH_SEPARATOR.join(path_segments))

  def SplitPath(self, path):
    """Splits the path into path segments.

    Args:
      path: a string containing the path.

    Returns:
      A list of path segements without the root path segment, which is an
      empty string.
    """
    return self._file_system.SplitPath(path)

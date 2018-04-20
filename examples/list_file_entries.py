#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to list file entries."""

from __future__ import print_function
from __future__ import unicode_literals

import abc
import argparse
import logging
import os
import stat
import sys

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import fvde_analyzer_helper
from dfvfs.lib import definitions
from dfvfs.lib import raw
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver
from dfvfs.volume import tsk_volume_system


try:
  # Disable experimental FVDE support.
  analyzer.Analyzer.DeregisterHelper(fvde_analyzer_helper.FVDEAnalyzerHelper())
except KeyError:
  pass


class FileEntryLister(object):
  """File entry lister."""

  # Class constant that defines the default read buffer size.
  _READ_BUFFER_SIZE = 32768

  # For context see: http://en.wikipedia.org/wiki/Byte
  _UNITS_1000 = ['B', 'kB', 'MB', 'GB', 'TB', 'EB', 'ZB', 'YB']
  _UNITS_1024 = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'EiB', 'ZiB', 'YiB']

  def __init__(self):
    """Initializes a file entry lister."""
    super(FileEntryLister, self).__init__()
    self._list_only_files = False

  def _GetHumanReadableSize(self, size):
    """Retrieves a human readable string of the size.

    Args:
      size (int): size in bytes.

    Returns:
      str: human readable string of the size.
    """
    magnitude_1000 = 0
    size_1000 = float(size)
    while size_1000 >= 1000:
      size_1000 /= 1000
      magnitude_1000 += 1

    magnitude_1024 = 0
    size_1024 = float(size)
    while size_1024 >= 1024:
      size_1024 /= 1024
      magnitude_1024 += 1

    size_string_1000 = None
    if magnitude_1000 > 0 and magnitude_1000 <= 7:
      size_string_1000 = '{0:.1f}{1:s}'.format(
          size_1000, self._UNITS_1000[magnitude_1000])

    size_string_1024 = None
    if magnitude_1024 > 0 and magnitude_1024 <= 7:
      size_string_1024 = '{0:.1f}{1:s}'.format(
          size_1024, self._UNITS_1024[magnitude_1024])

    if not size_string_1000 or not size_string_1024:
      return '{0:d} B'.format(size)

    return '{0:s} / {1:s} ({2:d} B)'.format(
        size_string_1024, size_string_1000, size)

  def _GetNextLevelTSKPartionVolumeSystemPathSpec(self, source_path_spec):
    """Determines the next level volume system path specification.

    Args:
      source_path_spec (dfvfs.PathSpec): source path specification.

    Returns:
      dfvfs.PathSpec: next level volume system path specification.

    Raises:
      RuntimeError: if the format of or within the source is not supported.
    """
    volume_system_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location='/',
        parent=source_path_spec)

    volume_system = tsk_volume_system.TSKVolumeSystem()
    volume_system.Open(volume_system_path_spec)

    volume_identifiers = []
    for volume in volume_system.volumes:
      volume_identifier = getattr(volume, 'identifier', None)
      if volume_identifier:
        volume_identifiers.append(volume_identifier)

    if not volume_identifiers:
      logging.warning('No supported partitions found.')
      return source_path_spec

    if len(volume_identifiers) == 1:
      return path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_TSK_PARTITION, location='/p1',
          parent=source_path_spec)

    print('The following partitions were found:')
    print('Identifier\tOffset\t\t\tSize')

    for volume_identifier in sorted(volume_identifiers):
      volume = volume_system.GetVolumeByIdentifier(volume_identifier)
      if not volume:
        raise RuntimeError(
            'Volume missing for identifier: {0:s}.'.format(volume_identifier))

      volume_extent = volume.extents[0]
      print(
          '{0:s}\t\t{1:d} (0x{1:08x})\t{2:s}'.format(
              volume.identifier, volume_extent.offset,
              self._GetHumanReadableSize(volume_extent.size)))

    print('')

    while True:
      print(
          'Please specify the identifier of the partition that should '
          'be processed:')

      selected_volume_identifier = sys.stdin.readline()
      selected_volume_identifier = selected_volume_identifier.strip()

      if selected_volume_identifier in volume_identifiers:
        break

      print('')
      print(
          'Unsupported partition identifier, please try again or abort '
          'with Ctrl^C.')
      print('')

    location = '/{0:s}'.format(selected_volume_identifier)

    return path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location=location,
        parent=source_path_spec)

  def _GetNextLevelVshadowVolumeSystemPathSpec(self, source_path_spec):
    """Determines the next level volume system path specification.

    Args:
      source_path_spec (dfvfs.PathSpec): source path specification.

    Returns:
      dfvfs.PathSpec: next level volume system path specification.

    Raises:
      RuntimeError: if the format of or within the source is not supported.
    """
    # TODO: implement.
    return source_path_spec

  def _GetUpperLevelVolumeSystemPathSpec(self, source_path_spec):
    """Determines the upper level volume system path specification.

    Args:
      source_path_spec (dfvfs.PathSpec): source path specification.

    Returns:
      dfvfs.PathSpec: upper level volume system path specification.

    Raises:
      RuntimeError: if the format of or within the source is not supported.
    """
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        source_path_spec)

    if not type_indicators:
      # No supported volume system found, we are at the upper level.
      return source_path_spec

    if len(type_indicators) > 1:
      raise RuntimeError(
          'Unsupported source found more than one volume system types.')

    if type_indicators[0] == definitions.TYPE_INDICATOR_TSK_PARTITION:
      path_spec = self._GetNextLevelTSKPartionVolumeSystemPathSpec(
          source_path_spec)

    elif type_indicators[0] == definitions.TYPE_INDICATOR_VSHADOW:
      path_spec = self._GetNextLevelVshadowVolumeSystemPathSpec(
          source_path_spec)

    else:
      raise RuntimeError((
          'Unsupported source found unsupported volume system '
          'type: {0:s}.').format(type_indicators[0]))

    return path_spec

  def _ListFileEntry(
      self, file_system, file_entry, parent_full_path, output_writer):
    """Lists a file entry.

    Args:
      file_system (dfvfs.FileSystem): file system that contains the file entry.
      file_entry (dfvfs.FileEntry): file entry to list.
      parent_full_path (str): full path of the parent file entry.
      output_writer (StdoutWriter): output writer.
    """
    # Since every file system implementation can have their own path
    # segment separator we are using JoinPath to be platform and file system
    # type independent.
    full_path = file_system.JoinPath([parent_full_path, file_entry.name])
    if not self._list_only_files or file_entry.IsFile():
      output_writer.WriteFileEntry(full_path)

    for sub_file_entry in file_entry.sub_file_entries:
      self._ListFileEntry(file_system, sub_file_entry, full_path, output_writer)

  def ListFileEntries(self, base_path_spec, output_writer):
    """Lists file entries in the base path specification.

    Args:
      base_path_spec (dfvfs.PathSpec): base path specification.
      output_writer (StdoutWriter): output writer.
    """
    file_system = resolver.Resolver.OpenFileSystem(base_path_spec)
    file_entry = resolver.Resolver.OpenFileEntry(base_path_spec)
    if file_entry is None:
      logging.warning(
          'Unable to open base path specification:\n{0:s}'.format(
              base_path_spec.comparable))
      return

    self._ListFileEntry(file_system, file_entry, '', output_writer)

  def GetBasePathSpec(self, source_path):
    """Determines the base path specification.

    Args:
      source_path (str): path of the source.

    Returns:
      dfvfs.PathSpec: base path specification.

    Raises:
      RuntimeError: if the source path does not exists, or if the source path
          is not a file or directory, or if the format of or within the source
          file is not supported.
    """
    if not os.path.exists(source_path):
      raise RuntimeError('No such source: {0:s}.'.format(source_path))

    stat_info = os.stat(source_path)

    if (not stat.S_ISDIR(stat_info.st_mode) and
        not stat.S_ISREG(stat_info.st_mode)):
      raise RuntimeError(
          'Unsupported source: {0:s} not a file or directory.'.format(
              source_path))

    if stat.S_ISDIR(stat_info.st_mode):
      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_OS, location=source_path)

    elif stat.S_ISREG(stat_info.st_mode):
      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_OS, location=source_path)

      type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
          path_spec)

      if len(type_indicators) > 1:
        raise RuntimeError((
            'Unsupported source: {0:s} found more than one storage media '
            'image types.').format(source_path))

      if len(type_indicators) == 1:
        path_spec = path_spec_factory.Factory.NewPathSpec(
            type_indicators[0], parent=path_spec)

      if not type_indicators:
        # The RAW storage media image type cannot be detected based on
        # a signature so we try to detect it based on common file naming
        # schemas.
        file_system = resolver.Resolver.OpenFileSystem(path_spec)
        raw_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_RAW, parent=path_spec)

        glob_results = raw.RawGlobPathSpec(file_system, raw_path_spec)
        if glob_results:
          path_spec = raw_path_spec

      # In case we did not find a storage media image type we keep looking
      # since not all RAW storage media image naming schemas are known and
      # its type can only detected by its content.

      path_spec = self._GetUpperLevelVolumeSystemPathSpec(path_spec)

      # In case we did not find a volume system type we keep looking
      # since we could be dealing with a store media image that contains
      # a single volume.

      type_indicators = analyzer.Analyzer.GetFileSystemTypeIndicators(
          path_spec)

      if len(type_indicators) > 1:
        raise RuntimeError((
            'Unsupported source: {0:s} found more than one file system '
            'types.').format(source_path))

      if not type_indicators:
        logging.warning('Unable to find a supported file system.')
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=source_path)

      elif type_indicators[0] != definitions.TYPE_INDICATOR_TSK:
        raise RuntimeError((
            'Unsupported source: {0:s} found unsupported file system '
            'type: {1:s}.').format(source_path, type_indicators[0]))

      else:
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TSK, location='/',
            parent=path_spec)

    return path_spec


class OutputWriter(object):
  """Output writer interface."""

  def __init__(self, encoding='utf-8'):
    """Initializes an output writer.

    Args:
      encoding (Optional[str]): input encoding.
    """
    super(OutputWriter, self).__init__()
    self._encoding = encoding
    self._errors = 'strict'

  def _EncodeString(self, string):
    """Encodes the string.

    Args:
      string (str): string to encode.

    Returns:
      bytes: encoded string.
    """
    try:
      # Note that encode() will first convert string into a Unicode string
      # if necessary.
      encoded_string = string.encode(self._encoding, errors=self._errors)
    except UnicodeEncodeError:
      if self._errors == 'strict':
        logging.error(
            'Unable to properly write output due to encoding error. '
            'Switching to error tolerant encoding which can result in '
            'non Basic Latin (C0) characters to be replaced with "?" or '
            '"\\ufffd".')
        self._errors = 'replace'

      encoded_string = string.encode(self._encoding, errors=self._errors)

    return encoded_string

  @abc.abstractmethod
  def Close(self):
    """Closes the output writer object."""

  @abc.abstractmethod
  def Open(self):
    """Opens the output writer object."""

  @abc.abstractmethod
  def WriteFileEntry(self, path):
    """Writes the file path.

    Args:
      path (str): path of the file.
    """


class FileOutputWriter(OutputWriter):
  """Output writer that writes to a file."""

  def __init__(self, path, encoding='utf-8'):
    """Initializes an output writer.

    Args:
      path (str): name of the path.
      encoding (Optional[str]): input encoding.
    """
    super(FileOutputWriter, self).__init__(encoding=encoding)
    self._file_object = None
    self._path = path

  def Close(self):
    """Closes the output writer object."""
    self._file_object.close()

  def Open(self):
    """Opens the output writer object."""
    # Using binary mode to make sure to write Unix end of lines, so we can
    # compare output files cross-platform.
    self._file_object = open(self._path, 'wb')

  def WriteFileEntry(self, path):
    """Writes the file path to file.

    Args:
      path (str): path of the file.
    """
    string = '{0:s}\n'.format(path)

    encoded_string = self._EncodeString(string)
    self._file_object.write(encoded_string)


class StdoutWriter(OutputWriter):
  """Output writer that writes to stdout."""

  def Close(self):
    """Closes the output writer object."""
    pass

  def Open(self):
    """Opens the output writer object."""
    pass

  def WriteFileEntry(self, path):
    """Writes the file path to stdout.

    Args:
      path (str): path of the file.
    """
    string = '{0:s}\n'.format(path)

    encoded_string = self._EncodeString(string)
    print(encoded_string)


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Lists file entries in a directory or storage media image.'))

  argument_parser.add_argument(
      '--output_file', '--output-file', dest='output_file', action='store',
      metavar='source.hashes', default=None, help=(
          'path of the output file, default is to output to stdout.'))

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='image.raw',
      default=None, help='path of the directory or storage media image.')

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  if options.output_file:
    output_writer = FileOutputWriter(options.output_file)
  else:
    output_writer = StdoutWriter()

  try:
    output_writer.Open()
  except IOError as exception:
    print('Unable to open output writer with error: {0!s}.'.format(
        exception))
    print('')
    return False

  return_value = True
  file_entry_lister = FileEntryLister()

  try:
    base_path_spec = file_entry_lister.GetBasePathSpec(options.source)

    file_entry_lister.ListFileEntries(base_path_spec, output_writer)

    print('')
    print('Completed.')

  except KeyboardInterrupt:
    return_value = False

    print('')
    print('Aborted by user.')

  output_writer.Close()

  return return_value


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)

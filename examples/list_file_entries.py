#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to list file entries."""

from __future__ import print_function
from __future__ import unicode_literals

import abc
import argparse
import logging
import sys

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import fvde_analyzer_helper
from dfvfs.helpers import command_line
from dfvfs.helpers import volume_scanner
from dfvfs.lib import errors
from dfvfs.resolver import resolver


try:
  # Disable experimental FVDE support.
  analyzer.Analyzer.DeregisterHelper(fvde_analyzer_helper.FVDEAnalyzerHelper())
except KeyError:
  pass


class FileEntryLister(volume_scanner.VolumeScanner):
  """File entry lister."""

  def __init__(self, mediator=None):
    """Initializes a file entry lister.

    Args:
      mediator (VolumeScannerMediator): a volume scanner mediator.
    """
    super(FileEntryLister, self).__init__(mediator=mediator)
    self._list_only_files = False

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

  def ListFileEntries(self, base_path_specs, output_writer):
    """Lists file entries in the base path specification.

    Args:
      base_path_specs (list[dfvfs.PathSpec]): source path specification.
      output_writer (StdoutWriter): output writer.
    """
    for base_path_spec in base_path_specs:
      file_system = resolver.Resolver.OpenFileSystem(base_path_spec)
      file_entry = resolver.Resolver.OpenFileEntry(base_path_spec)
      if file_entry is None:
        logging.warning(
            'Unable to open base path specification:\n{0:s}'.format(
                base_path_spec.comparable))
        return

      self._ListFileEntry(file_system, file_entry, '', output_writer)


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
    return

  def Open(self):
    """Opens the output writer object."""
    return

  def WriteFileEntry(self, path):
    """Writes the file path to stdout.

    Args:
      path (str): path of the file.
    """
    encoded_path = self._EncodeString(path)
    print(encoded_path)


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
  mediator = command_line.CLIVolumeScannerMediator()
  file_entry_lister = FileEntryLister(mediator=mediator)

  try:
    base_path_specs = file_entry_lister.GetBasePathSpecs(options.source)
    if not base_path_specs:
      print('No supported file system found in source.')
      print('')
      return False

    file_entry_lister.ListFileEntries(base_path_specs, output_writer)

    print('')
    print('Completed.')

  except errors.ScannerError as exception:
    return_value = False

    print('')
    print('[ERROR] {0!s}'.format(exception))

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

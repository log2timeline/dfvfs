#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to recursively calculate a message digest hash for every file."""

# If you update this script make sure to update the corresponding wiki page
# as well: https://github.com/log2timeline/dfvfs/wiki/Development

from __future__ import print_function
from __future__ import unicode_literals

import abc
import argparse
import getpass
import hashlib
import locale
import logging
import sys
import textwrap

try:
  import win32console
except ImportError:
  win32console = None

from dfdatetime import filetime as dfdatetime_filetime

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import fvde_analyzer_helper
from dfvfs.lib import definitions as dfvfs_definitions
from dfvfs.lib import errors
from dfvfs.lib import py2to3
from dfvfs.helpers import volume_scanner
from dfvfs.resolver import resolver


try:
  # Disable experimental FVDE support.
  analyzer.Analyzer.DeregisterHelper(fvde_analyzer_helper.FVDEAnalyzerHelper())
except KeyError:
  pass


class CLITabularTableView(object):
  """Command line interface tabular table view."""

  _NUMBER_OF_SPACES_IN_TAB = 8

  def __init__(self, column_names=None, column_sizes=None):
    """Initializes a command line interface tabular table view.

    Args:
      column_names (Optional[list[str]]): column names.
      column_sizes (Optional[list[int]]): minimum column sizes, in number of
          characters. If a column name or row value is larger than the
          minimum column size the column will be enlarged. Note that the
          minimum columns size will be rounded up to the number of spaces
          of the next tab.
    """
    super(CLITabularTableView, self).__init__()
    self._columns = column_names or []
    self._column_sizes = column_sizes or []
    self._number_of_columns = len(self._columns)
    self._rows = []

  def _PrintRow(self, values, in_bold=False):
    """Prints a row of values aligned to the column width to stdout.

    Args:
      values (list[object]): values.
      in_bold (Optional[bool]): True if the row should be written in bold.
    """
    row_strings = []
    for value_index, value_string in enumerate(values):
      padding_size = self._column_sizes[value_index] - len(value_string)
      padding_string = ' ' * padding_size

      row_strings.extend([value_string, padding_string])

    row_strings.pop()

    row_strings = ''.join(row_strings)

    if in_bold and not win32console:
      # TODO: for win32console get current color and set intensity,
      # write the header separately then reset intensity.
      row_strings = '\x1b[1m{0:s}\x1b[0m'.format(row_strings)

    row_strings = '{0:s}'.format(row_strings)
    print(row_strings)

  def AddRow(self, values):
    """Adds a row of values.

    Args:
      values (list[object]): values.

    Raises:
      ValueError: if the number of values is out of bounds.
    """
    if self._number_of_columns and len(values) != self._number_of_columns:
      raise ValueError('Number of values is out of bounds.')

    if not self._column_sizes and self._columns:
      self._column_sizes = [len(column) for column in self._columns]

    value_strings = []
    for value_index, value_string in enumerate(values):
      if not isinstance(value_string, py2to3.UNICODE_TYPE):
        value_string = '{0!s}'.format(value_string)
      value_strings.append(value_string)

      self._column_sizes[value_index] = max(
          self._column_sizes[value_index], len(value_string))

    self._rows.append(value_strings)

    if not self._number_of_columns:
      self._number_of_columns = len(value_strings)

  def Print(self):
    """Prints the table to stdout."""
    # Round up the column sizes to the nearest tab.
    for column_index, column_size in enumerate(self._column_sizes):
      column_size, _ = divmod(column_size, self._NUMBER_OF_SPACES_IN_TAB)
      column_size = (column_size + 1) * self._NUMBER_OF_SPACES_IN_TAB
      self._column_sizes[column_index] = column_size

    if self._columns:
      self._PrintRow(self._columns, in_bold=True)

    for values in self._rows:
      self._PrintRow(values)


class RecursiveHasherVolumeScannerMediator(
    volume_scanner.VolumeScannerMediator):
  """Volume scanner mediator for the recursive hasher."""

  # For context see: http://en.wikipedia.org/wiki/Byte
  _UNITS_1000 = ['B', 'kB', 'MB', 'GB', 'TB', 'EB', 'ZB', 'YB']
  _UNITS_1024 = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'EiB', 'ZiB', 'YiB']

  def __init__(self):
    """Initializes a volume scanner mediator."""
    super(RecursiveHasherVolumeScannerMediator, self).__init__()
    self._encode_errors = 'strict'
    self._preferred_encoding = locale.getpreferredencoding()
    self._textwrapper = textwrap.TextWrapper()

  def _EncodeString(self, string):
    """Encodes a string in the preferred encoding.

    Returns:
      bytes: encoded string.
    """
    try:
      # Note that encode() will first convert string into a Unicode string
      # if necessary.
      encoded_string = string.encode(
          self._preferred_encoding, errors=self._encode_errors)
    except UnicodeEncodeError:
      if self._encode_errors == 'strict':
        logging.error(
            'Unable to properly write output due to encoding error. '
            'Switching to error tolerant encoding which can result in '
            'non Basic Latin (C0) characters being replaced with "?" or '
            '"\\ufffd".')
        self._encode_errors = 'replace'

      encoded_string = string.encode(
          self._preferred_encoding, errors=self._encode_errors)

    return encoded_string

  def _FormatHumanReadableSize(self, size):
    """Formats the size as a human readable string.

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

  def _ParseVSSStoresString(self, vss_stores):
    """Parses the user specified VSS stores string.

    A range of stores can be defined as: 3..5. Multiple stores can
    be defined as: 1,3,5 (a list of comma separated values). Ranges
    and lists can also be combined as: 1,3..5. The first store is 1.
    All stores can be defined as "all".

    Args:
      vss_stores (str): user specified VSS stores.

    Returns:
      list[int|str]: Individual VSS stores numbers or the string "all".

    Raises:
      ValueError: if the VSS stores option is invalid.
    """
    if not vss_stores:
      return []

    if vss_stores == 'all':
      return ['all']

    stores = []
    for vss_store_range in vss_stores.split(','):
      # Determine if the range is formatted as 1..3 otherwise it indicates
      # a single store number.
      if '..' in vss_store_range:
        first_store, last_store = vss_store_range.split('..')
        try:
          first_store = int(first_store, 10)
          last_store = int(last_store, 10)
        except ValueError:
          raise ValueError('Invalid VSS store range: {0:s}.'.format(
              vss_store_range))

        for store_number in range(first_store, last_store + 1):
          if store_number not in stores:
            stores.append(store_number)
      else:
        if vss_store_range.startswith('vss'):
          vss_store_range = vss_store_range[3:]

        try:
          store_number = int(vss_store_range, 10)
        except ValueError:
          raise ValueError('Invalid VSS store range: {0:s}.'.format(
              vss_store_range))

        if store_number not in stores:
          stores.append(store_number)

    return sorted(stores)

  def GetPartitionIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves partition identifiers.

    This method can be used to prompt the user to provide partition identifiers.

    Args:
      volume_system (dfvfs.TSKVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers.

    Returns:
      list[str]: selected partition identifiers or None.

    Raises:
      ScannerError: if the source cannot be processed.
    """
    print('The following partitions were found:')

    table_view = CLITabularTableView(column_names=[
        'Identifier', 'Offset (in bytes)', 'Size (in bytes)'])

    for volume_identifier in sorted(volume_identifiers):
      volume = volume_system.GetVolumeByIdentifier(volume_identifier)
      if not volume:
        raise errors.ScannerError(
            'Partition missing for identifier: {0:s}.'.format(
                volume_identifier))

      volume_extent = volume.extents[0]
      volume_offset = '{0:d} (0x{0:08x})'.format(volume_extent.offset)
      volume_size = self._FormatHumanReadableSize(volume_extent.size)

      table_view.AddRow([volume.identifier, volume_offset, volume_size])

    print('')
    table_view.Print()
    print('')

    while True:
      text = (
          'Please specify the identifier of the partition that should be '
          'processed. All partitions can be defined as: "all". Note that '
          'you can abort with Ctrl^C.')

      for line in self._textwrapper.wrap(text):
        print(line)

      selected_partition_identifier = sys.stdin.readline()
      selected_partition_identifier = selected_partition_identifier.strip()

      if not selected_partition_identifier.startswith('p'):
        try:
          partition_number = int(selected_partition_identifier, 10)
          selected_partition_identifier = 'p{0:d}'.format(partition_number)
        except ValueError:
          pass

      if selected_partition_identifier == 'all':
        return volume_identifiers

      if selected_partition_identifier in volume_identifiers:
        break

      print('')

      text = (
          'Unsupported partition identifier, please try again or abort '
          'with Ctrl^C.')

      for line in self._textwrapper.wrap(text):
        print(line)

      print('')

    print('')
    return [selected_partition_identifier]

  def GetVSSStoreIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves VSS store identifiers.

    This method can be used to prompt the user to provide VSS store identifiers.

    Args:
      volume_system (VShadowVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers.

    Returns:
      list[int]: selected VSS store numbers or None.

    Raises:
      ScannerError: if the source cannot be processed.
    """
    normalized_volume_identifiers = []
    for volume_identifier in volume_identifiers:
      volume = volume_system.GetVolumeByIdentifier(volume_identifier)
      if not volume:
        raise errors.ScannerError(
            'Volume missing for identifier: {0:s}.'.format(volume_identifier))

      try:
        volume_identifier = int(volume.identifier[3:], 10)
        normalized_volume_identifiers.append(volume_identifier)
      except ValueError:
        pass

    print_header = True
    while True:
      if print_header:
        print('The following Volume Shadow Snapshots (VSS) were found:')

        table_view = CLITabularTableView(column_names=[
            'Identifier', 'Creation Time'])

        for volume_identifier in volume_identifiers:
          volume = volume_system.GetVolumeByIdentifier(volume_identifier)
          if not volume:
            raise errors.ScannerError(
                'Volume missing for identifier: {0:s}.'.format(
                    volume_identifier))

          vss_creation_time = volume.GetAttribute('creation_time')
          filetime = dfdatetime_filetime.Filetime(
              timestamp=vss_creation_time.value)
          vss_creation_time = filetime.CopyToDateTimeString()

          if volume.HasExternalData():
            vss_creation_time = (
                '{0:s}\tWARNING: data stored outside volume').format(
                    vss_creation_time)

          table_view.AddRow([volume.identifier, vss_creation_time])

        print('')
        table_view.Print()
        print('')

        print_header = False

      text = (
          'Please specify the identifier(s) of the VSS that should be '
          'processed: Note that a range of stores can be defined as: 3..5. '
          'Multiple stores can be defined as: 1,3,5 (a list of comma '
          'separated values). Ranges and lists can also be combined as: '
          '1,3..5. The first store is 1. All stores can be defined as "all". '
          'If no stores are specified none will be processed. You can abort '
          'with Ctrl^C.')

      for line in self._textwrapper.wrap(text):
        print(line)

      selected_vss_stores = sys.stdin.readline()

      selected_vss_stores = selected_vss_stores.strip()
      if not selected_vss_stores:
        selected_vss_stores = []
        break

      try:
        selected_vss_stores = self._ParseVSSStoresString(selected_vss_stores)
      except ValueError:
        selected_vss_stores = []

      if selected_vss_stores == ['all']:
        # We need to set the stores to cover all vss stores.
        selected_vss_stores = range(1, volume_system.number_of_volumes + 1)

      if not set(selected_vss_stores).difference(normalized_volume_identifiers):
        break

      print('')

      text = (
          'Unsupported VSS identifier(s), please try again or abort with '
          'Ctrl^C.')

      for line in self._textwrapper.wrap(text):
        print(line)

      print('')

    return selected_vss_stores

  def UnlockEncryptedVolume(
      self, source_scanner_object, scan_context, locked_scan_node, credentials):
    """Unlocks an encrypted volume.

    This method can be used to prompt the user to provide encrypted volume
    credentials.

    Args:
      source_scanner_object (dfvfs.SourceScanner): source scanner.
      scan_context (dfvfs.SourceScannerContext): source scanner context.
      locked_scan_node (dfvfs.SourceScanNode): locked scan node.
      credentials (dfvfs.Credentials): credentials supported by the locked
          scan node.

    Returns:
      bool: True if the volume was unlocked.
    """
    # TODO: print volume description.
    if locked_scan_node.type_indicator == dfvfs_definitions.TYPE_INDICATOR_BDE:
      print('Found a BitLocker encrypted volume.')
    else:
      print('Found an encrypted volume.')

    credentials_list = list(credentials.CREDENTIALS)
    credentials_list.append('skip')

    print('Supported credentials:')
    print('')
    for index, name in enumerate(credentials_list):
      print('  {0:d}. {1:s}'.format(index, name))
    print('')
    print('Note that you can abort with Ctrl^C.')
    print('')

    result = False
    while not result:
      print('Select a credential to unlock the volume: ', end='')
      # TODO: add an input reader.
      input_line = sys.stdin.readline()
      input_line = input_line.strip()

      if input_line in credentials_list:
        credential_type = input_line
      else:
        try:
          credential_type = int(input_line, 10)
          credential_type = credentials_list[credential_type]
        except (IndexError, ValueError):
          print('Unsupported credential: {0:s}'.format(input_line))
          continue

      if credential_type == 'skip':
        break

      getpass_string = 'Enter credential data: '
      if sys.platform.startswith('win') and sys.version_info[0] < 3:
        # For Python 2 on Windows getpass (win_getpass) requires an encoded
        # byte string. For Python 3 we need it to be a Unicode string.
        getpass_string = self._EncodeString(getpass_string)

      credential_data = getpass.getpass(getpass_string)
      print('')

      if credential_type == 'key':
        try:
          credential_data = credential_data.decode('hex')
        except TypeError:
          print('Unsupported credential data.')
          continue

      result = source_scanner_object.Unlock(
          scan_context, locked_scan_node.path_spec, credential_type,
          credential_data)

      if not result:
        print('Unable to unlock volume.')
        print('')

    return result


class RecursiveHasher(volume_scanner.VolumeScanner):
  """Recursively calculates message digest hashes of data streams."""

  # Class constant that defines the default read buffer size.
  _READ_BUFFER_SIZE = 32768

  def _CalculateHashDataStream(self, file_entry, data_stream_name):
    """Calculates a message digest hash of the data of the file entry.

    Args:
      file_entry (dfvfs.FileEntry): file entry.
      data_stream_name (str): name of the data stream.

    Returns:
      bytes: digest hash or None.
    """
    hash_context = hashlib.sha256()

    try:
      file_object = file_entry.GetFileObject(data_stream_name=data_stream_name)
    except IOError as exception:
      logging.warning((
          'Unable to open path specification:\n{0:s}'
          'with error: {1!s}').format(
              file_entry.path_spec.comparable, exception))
      return

    if not file_object:
      return

    try:
      data = file_object.read(self._READ_BUFFER_SIZE)
      while data:
        hash_context.update(data)
        data = file_object.read(self._READ_BUFFER_SIZE)
    except IOError as exception:
      logging.warning((
          'Unable to read from path specification:\n{0:s}'
          'with error: {1!s}').format(
              file_entry.path_spec.comparable, exception))
      return

    finally:
      file_object.close()

    return hash_context.hexdigest()

  def _CalculateHashesFileEntry(
      self, file_system, file_entry, parent_full_path, output_writer):
    """Recursive calculates hashes starting with the file entry.

    Args:
      file_system (dfvfs.FileSystem): file system.
      file_entry (dfvfs.FileEntry): file entry.
      parent_full_path (str): full path of the parent file entry.
      output_writer (StdoutWriter): output writer.
    """
    # Since every file system implementation can have their own path
    # segment separator we are using JoinPath to be platform and file system
    # type independent.
    full_path = file_system.JoinPath([parent_full_path, file_entry.name])
    for data_stream in file_entry.data_streams:
      hash_value = self._CalculateHashDataStream(file_entry, data_stream.name)
      display_path = self._GetDisplayPath(
          file_entry.path_spec, full_path, data_stream.name)
      output_writer.WriteFileHash(display_path, hash_value or 'N/A')

    for sub_file_entry in file_entry.sub_file_entries:
      self._CalculateHashesFileEntry(
          file_system, sub_file_entry, full_path, output_writer)

  def _GetDisplayPath(self, path_spec, full_path, data_stream_name):
    """Retrieves a path to display.

    Args:
      path_spec (dfvfs.PathSpec): path specification of the file entry.
      full_path (str): full path of the file entry.
      data_stream_name (str): name of the data stream.

    Returns:
      str: path to display.
    """
    display_path = ''

    if path_spec.HasParent():
      parent_path_spec = path_spec.parent
      if parent_path_spec and parent_path_spec.type_indicator == (
          dfvfs_definitions.TYPE_INDICATOR_TSK_PARTITION):
        display_path = ''.join([display_path, parent_path_spec.location])

    display_path = ''.join([display_path, full_path])
    if data_stream_name:
      display_path = ':'.join([display_path, data_stream_name])

    return display_path

  def CalculateHashes(self, base_path_specs, output_writer):
    """Recursive calculates hashes starting with the base path specification.

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
        continue

      self._CalculateHashesFileEntry(
          file_system, file_entry, '', output_writer)


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
  def WriteFileHash(self, path, hash_value):
    """Writes the file path and hash.

    Args:
      path (str): path of the file.
      hash_value (str): message digest hash calculated over the file data.
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

  def WriteFileHash(self, path, hash_value):
    """Writes the file path and hash to file.

    Args:
      path (str): path of the file.
      hash_value (str): message digest hash calculated over the file data.
    """
    string = '{0:s}\t{1:s}\n'.format(hash_value, path)

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

  def WriteFileHash(self, path, hash_value):
    """Writes the file path and hash to stdout.

    Args:
      path (str): path of the file.
      hash_value (str): message digest hash calculated over the file data.
    """
    string = '{0:s}\t{1:s}'.format(hash_value, path)

    encoded_string = self._EncodeString(string)
    print(encoded_string)


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Calculates a message digest hash for every file in a directory or '
      'storage media image.'))

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
  mediator = RecursiveHasherVolumeScannerMediator()
  recursive_hasher = RecursiveHasher(mediator=mediator)

  try:
    base_path_specs = recursive_hasher.GetBasePathSpecs(options.source)
    if not base_path_specs:
      print('No supported file system found in source.')
      print('')
      return False

    recursive_hasher.CalculateHashes(base_path_specs, output_writer)

    print('')
    print('Completed.')

  except errors.ScannerError as exception:
    return_value = False

    print('')
    print('[ERROR] {0!s}'.format(exception))

  except errors.UserAbort as exception:
    return_value = False

    print('')
    print('Aborted.')

  output_writer.Close()

  return return_value


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)

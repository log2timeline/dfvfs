#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to recursively calculate a message digest hash for every file."""

# If you update this script make sure to update the corresponding wiki page
# as well: https://github.com/log2timeline/dfvfs/wiki/Development

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import getpass
import hashlib
import locale
import logging
import sys

from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.helpers import volume_scanner
from dfvfs.resolver import resolver


class RecursiveHasherVolumeScannerMediator(
    volume_scanner.VolumeScannerMediator):
  """Class that defines a volume scanner mediator."""

  # For context see: http://en.wikipedia.org/wiki/Byte
  _UNITS_1000 = ['B', 'kB', 'MB', 'GB', 'TB', 'EB', 'ZB', 'YB']
  _UNITS_1024 = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'EiB', 'ZiB', 'YiB']

  def __init__(self):
    """Initializes the scanner mediator object."""
    super(RecursiveHasherVolumeScannerMediator, self).__init__()
    self._encode_errors = 'strict'
    self._preferred_encoding = locale.getpreferredencoding()

  def _EncodeString(self, string):
    """Encodes a string in the preferred encoding.

    Returns:
      A byte string containing the encoded string.
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
      size: The size in bytes.

    Returns:
      A human readable string of the size.
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
      volume_system: the volume system (instance of dfvfs.TSKVolumeSystem).
      volume_identifiers: a list of strings containing the volume identifiers.

    Returns:
      A list of strings containing the selected partition identifiers or None.

    Raises:
      ScannerError: if the source cannot be processed.
    """
    print('The following partitions were found:')
    print('Identifier\tOffset (in bytes)\tSize (in bytes)')

    for volume_identifier in sorted(volume_identifiers):
      volume = volume_system.GetVolumeByIdentifier(volume_identifier)
      if not volume:
        raise errors.ScannerError(
            'Volume missing for identifier: {0:s}.'.format(volume_identifier))

      volume_extent = volume.extents[0]
      print('{0:s}\t\t{1:d} (0x{1:08x})\t{2:s}'.format(
          volume.identifier, volume_extent.offset,
          self._FormatHumanReadableSize(volume_extent.size)))

    while True:
      print(
          'Please specify the identifier of the partition that should be '
          'processed.')
      print(
          'All partitions can be defined as: "all". Note that you '
          'can abort with Ctrl^C.')

      selected_volume_identifier = sys.stdin.readline()
      selected_volume_identifier = selected_volume_identifier.strip()

      if not selected_volume_identifier.startswith('p'):
        try:
          partition_number = int(selected_volume_identifier, 10)
          selected_volume_identifier = 'p{0:d}'.format(partition_number)
        except ValueError:
          pass

      if selected_volume_identifier == 'all':
        return volume_identifiers

      if selected_volume_identifier in volume_identifiers:
        break

      print('')
      print(
          'Unsupported partition identifier, please try again or abort '
          'with Ctrl^C.')
      print('')

    return [selected_volume_identifier]

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
        print('Identifier\tVSS store identifier')

        for volume_identifier in volume_identifiers:
          volume = volume_system.GetVolumeByIdentifier(volume_identifier)
          if not volume:
            raise errors.ScannerError(
                'Volume missing for identifier: {0:s}.'.format(
                    volume_identifier))

          vss_identifier = volume.GetAttribute('identifier')
          print('{0:s}\t\t{1:s}'.format(
              volume.identifier, vss_identifier.value))

        print('')

        print_header = False

      print(
          'Please specify the identifier(s) of the VSS that should be '
          'processed:')
      print(
          'Note that a range of stores can be defined as: 3..5. Multiple '
          'stores can')
      print(
          'be defined as: 1,3,5 (a list of comma separated values). Ranges '
          'and lists can')
      print(
          'also be combined as: 1,3..5. The first store is 1. All stores '
          'can be defined')
      print('as "all". If no stores are specified none will be processed. Yo')
      print('can abort with Ctrl^C.')

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
      print(
          'Unsupported VSS identifier(s), please try again or abort with '
          'Ctrl^C.')
      print('')

    return selected_vss_stores

  def UnlockEncryptedVolume(
      self, source_scanner_object, scan_context, locked_scan_node, credentials):
    """Unlocks an encrypted volume.

    This method can be used to prompt the user to provide encrypted volume
    credentials.

    Args:
      source_scanner_object: the source scanner (instance of SourceScanner).
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      locked_scan_node: the locked scan node (instance of SourceScanNode).
      credentials: the credentials supported by the locked scan node (instance
                   of dfvfs.Credentials).

    Returns:
      A boolean value indicating whether the volume was unlocked.
    """
    # TODO: print volume description.
    if locked_scan_node.type_indicator == definitions.TYPE_INDICATOR_BDE:
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
  """Class that recursively calculates message digest hashes of files."""

  # Class constant that defines the default read buffer size.
  _READ_BUFFER_SIZE = 32768

  def _CalculateHashFileEntry(self, file_entry, data_stream_name):
    """Calculates a message digest hash of the data of the file entry.

    Args:
      file_entry: the file entry (instance of dfvfs.FileEntry).
      data_stream_name: the data stream name.

    Returns:
      A binary string containing the digest hash or None.
    """
    hash_context = hashlib.md5()

    try:
      file_object = file_entry.GetFileObject(data_stream_name=data_stream_name)
    except IOError as exception:
      logging.warning((
          'Unable to open path specification:\n{0:s}'
          'with error: {1:s}').format(
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
          'with error: {1:s}').format(
              file_entry.path_spec.comparable, exception))
      return

    finally:
      file_object.close()

    return hash_context.hexdigest()

  def _CalculateHashesFileEntry(
      self, file_system, file_entry, parent_full_path, output_writer):
    """Recursive calculates hashes starting with the file entry.

    Args:
      file_system: the file system (instance of dfvfs.FileSystem).
      file_entry: the file entry (instance of dfvfs.FileEntry).
      parent_full_path: the full path of the parent file entry.
      output_writer: the output writer (instance of StdoutWriter).
    """
    # Since every file system implementation can have their own path
    # segment separator we are using JoinPath to be platform and file system
    # type independent.
    full_path = file_system.JoinPath([parent_full_path, file_entry.name])
    for data_stream in file_entry.data_streams:
      hash_value = self._CalculateHashFileEntry(file_entry, data_stream.name)
      if not hash_value:
        hash_value = 'N/A'

      # TODO: print volume.
      if data_stream.name:
        display_path = '{0:s}:{1:s}'.format(full_path, data_stream.name)
      else:
        display_path = full_path

      output_writer.WriteFileHash(display_path, hash_value)

    for sub_file_entry in file_entry.sub_file_entries:
      self._CalculateHashesFileEntry(
          file_system, sub_file_entry, full_path, output_writer)

  def CalculateHashes(self, base_path_specs, output_writer):
    """Recursive calculates hashes starting with the base path specification.

    Args:
      base_path_specs: a list of source path specification (instances
                       of dfvfs.PathSpec).
      output_writer: the output writer (instance of StdoutWriter).
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


class StdoutWriter(object):
  """Class that defines a stdout output writer."""

  def __init__(self, encoding='utf-8'):
    """Initializes the output writer object.

    Args:
      encoding: optional input encoding.
    """
    super(StdoutWriter, self).__init__()
    self._encoding = encoding
    self._errors = 'strict'

  def Open(self):
    """Opens the output writer object.

    Returns:
      A boolean containing True if successful or False if not.
    """
    return True

  def Close(self):
    """Closes the output writer object."""
    pass

  def WriteFileHash(self, path, hash_value):
    """Writes the file path and hash to stdout.

    Args:
      path: the path of the file.
      hash_value: the message digest hash calculated over the file data.
    """
    string = '{0:s}\t{1:s}'.format(hash_value, path)

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

    print(encoded_string)


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Calculates a message digest hash for every file in a directory or '
      'storage media image.'))

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='image.raw',
      default=None, help=(
          'path of the directory or filename of a storage media image '
          'containing the file.'))

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  output_writer = StdoutWriter()

  if not output_writer.Open():
    print('Unable to open output writer.')
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

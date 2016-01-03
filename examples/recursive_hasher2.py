#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to recursively calculate a message digest hash for every file."""

# If you update this script make sure to update the corresponding wiki page
# as well: https://github.com/log2timeline/dfvfs/wiki/Development

from __future__ import print_function
import argparse
import getpass
import hashlib
import logging
import os
import sys

from dfvfs.credentials import manager as credentials_manager
from dfvfs.helpers import source_scanner
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver
from dfvfs.volume import tsk_volume_system
from dfvfs.volume import vshadow_volume_system


class RecursiveHasher(object):
  """Class that recursively calculates message digest hashes of files."""

  # Class constant that defines the default read buffer size.
  _READ_BUFFER_SIZE = 32768

  # For context see: http://en.wikipedia.org/wiki/Byte
  _UNITS_1000 = [u'B', u'kB', u'MB', u'GB', u'TB', u'EB', u'ZB', u'YB']
  _UNITS_1024 = [u'B', u'KiB', u'MiB', u'GiB', u'TiB', u'EiB', u'ZiB', u'YiB']

  def __init__(self):
    """Initializes the recursive hasher object."""
    super(RecursiveHasher, self).__init__()
    self._source_scanner = source_scanner.SourceScanner()

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
          u'Unable to open path specification:\n{0:s}'
          u'with error: {1:s}').format(
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
          u'Unable to read from path specification:\n{0:s}'
          u'with error: {1:s}').format(
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
        display_path = u'{0:s}:{1:s}'.format(full_path, data_stream.name)
      else:
        display_path = full_path

      output_writer.WriteFileHash(display_path, hash_value)

    for sub_file_entry in file_entry.sub_file_entries:
      self._CalculateHashesFileEntry(
          file_system, sub_file_entry, full_path, output_writer)

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
      size_string_1000 = u'{0:.1f}{1:s}'.format(
          size_1000, self._UNITS_1000[magnitude_1000])

    size_string_1024 = None
    if magnitude_1024 > 0 and magnitude_1024 <= 7:
      size_string_1024 = u'{0:.1f}{1:s}'.format(
          size_1024, self._UNITS_1024[magnitude_1024])

    if not size_string_1000 or not size_string_1024:
      return u'{0:d} B'.format(size)

    return u'{0:s} / {1:s} ({2:d} B)'.format(
        size_string_1024, size_string_1000, size)

  def _GetTSKPartitionIdentifiers(self, scan_node):
    """Determines the TSK partition identifiers.

    Args:
      scan_node: the scan node (instance of dfvfs.ScanNode).

    Returns:
      A list of partition identifiers.

    Raises:
      RuntimeError: if the format of or within the source is not supported or
                    the the scan node is invalid or if the volume for
                    a specific identifier cannot be retrieved.
    """
    if not scan_node or not scan_node.path_spec:
      raise RuntimeError(u'Invalid scan node.')

    volume_system = tsk_volume_system.TSKVolumeSystem()
    volume_system.Open(scan_node.path_spec)

    volume_identifiers = self._source_scanner.GetVolumeIdentifiers(
        volume_system)
    if not volume_identifiers:
      print(u'[WARNING] No partitions found.')
      return

    if len(volume_identifiers) == 1:
      return volume_identifiers

    try:
      selected_volume_identifier = self._PromptUserForPartitionIdentifier(
          volume_system, volume_identifiers)
    except KeyboardInterrupt:
      raise RuntimeError(u'File system scan aborted.')

    if selected_volume_identifier == u'all':
      return volume_identifiers

    return [selected_volume_identifier]

  def _GetVSSStoreIdentifiers(self, scan_node):
    """Determines the VSS store identifiers.

    Args:
      scan_node: the scan node (instance of dfvfs.ScanNode).

    Returns:
      A list of VSS store identifiers.

    Raises:
      RuntimeError: if the format of or within the source
                    is not supported or the the scan node is invalid.
    """
    if not scan_node or not scan_node.path_spec:
      raise RuntimeError(u'Invalid scan node.')

    volume_system = vshadow_volume_system.VShadowVolumeSystem()
    volume_system.Open(scan_node.path_spec)

    volume_identifiers = self._source_scanner.GetVolumeIdentifiers(
        volume_system)
    if not volume_identifiers:
      return []

    try:
      selected_store_identifiers = self._PromptUserForVSSStoreIdentifiers(
          volume_system, volume_identifiers)
    except KeyboardInterrupt:
      raise errors.UserAbort(u'File system scan aborted.')

    return selected_store_identifiers

  def _ParseVSSStoresString(self, vss_stores):
    """Parses the user specified VSS stores string.

    A range of stores can be defined as: 3..5. Multiple stores can
    be defined as: 1,3,5 (a list of comma separated values). Ranges
    and lists can also be combined as: 1,3..5. The first store is 1.
    All stores can be defined as "all".

    Args:
      vss_stores: a string containing the VSS stores.

    Returns:
      A list containing the individual VSS stores numbers or the string "all".

    Raises:
      BadConfigOption: if the VSS stores option is invalid.
    """
    if not vss_stores:
      return []

    if vss_stores == u'all':
      return [u'all']

    stores = []
    for vss_store_range in vss_stores.split(u','):
      # Determine if the range is formatted as 1..3 otherwise it indicates
      # a single store number.
      if u'..' in vss_store_range:
        first_store, last_store = vss_store_range.split(u'..')
        try:
          first_store = int(first_store, 10)
          last_store = int(last_store, 10)
        except ValueError:
          raise errors.BadConfigOption(
              u'Invalid VSS store range: {0:s}.'.format(vss_store_range))

        for store_number in range(first_store, last_store + 1):
          if store_number not in stores:
            stores.append(store_number)
      else:
        if vss_store_range.startswith(u'vss'):
          vss_store_range = vss_store_range[3:]

        try:
          store_number = int(vss_store_range, 10)
        except ValueError:
          raise errors.BadConfigOption(
              u'Invalid VSS store range: {0:s}.'.format(vss_store_range))

        if store_number not in stores:
          stores.append(store_number)

    return sorted(stores)

  def _PromptUserForEncryptedVolumeCredential(
      self, scan_context, locked_scan_node, credentials):
    """Prompts the user to provide a credential for an encrypted volume.

    Args:
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
      print(u'Found a BitLocker encrypted volume.')
    else:
      print(u'Found an encrypted volume.')

    credentials_list = list(credentials.CREDENTIALS)
    credentials_list.append(u'skip')

    print(u'Supported credentials:')
    print(u'')
    for index, name in enumerate(credentials_list):
      print(u'  {0:d}. {1:s}'.format(index, name))
    print(u'')
    print(u'Note that you can abort with Ctrl^C.')
    print(u'')

    result = False
    while not result:
      print(u'Select a credential to unlock the volume: ', end=u'')
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
          print(u'Unsupported credential: {0:s}'.format(input_line))
          continue

      if credential_type == u'skip':
        break

      credential_data = getpass.getpass(u'Enter credential data: ')
      print(u'')

      if credential_type == u'key':
        try:
          credential_data = credential_data.decode(u'hex')
        except TypeError:
          print(u'Unsupported credential data.')
          continue

      result = self._source_scanner.Unlock(
          scan_context, locked_scan_node.path_spec, credential_type,
          credential_data)

      if not result:
        print(u'Unable to unlock volume.')
        print(u'')

    return result

  def _PromptUserForPartitionIdentifier(
      self, volume_system, volume_identifiers):
    """Prompts the user to provide a partition identifier.

    Args:
      volume_system: The volume system (instance of dfvfs.TSKVolumeSystem).
      volume_identifiers: List of allowed volume identifiers.

    Returns:
      A string containing the partition identifier or "all".

    Raises:
      FileSystemScannerError: if the source cannot be processed.
    """
    print(u'The following partitions were found:')
    print(u'Identifier\tOffset (in bytes)\tSize (in bytes)')

    for volume_identifier in sorted(volume_identifiers):
      volume = volume_system.GetVolumeByIdentifier(volume_identifier)
      if not volume:
        raise errors.FileSystemScannerError(
            u'Volume missing for identifier: {0:s}.'.format(volume_identifier))

      volume_extent = volume.extents[0]
      print(u'{0:s}\t\t{1:d} (0x{1:08x})\t{2:s}'.format(
          volume.identifier, volume_extent.offset,
          self._FormatHumanReadableSize(volume_extent.size)))

    while True:
      print(
          u'Please specify the identifier of the partition that should be '
          u'processed.')
      print(
          u'All partitions can be defined as: "all". Note that you '
          u'can abort with Ctrl^C.')

      selected_volume_identifier = sys.stdin.readline()
      selected_volume_identifier = selected_volume_identifier.strip()

      if not selected_volume_identifier.startswith(u'p'):
        try:
          partition_number = int(selected_volume_identifier, 10)
          selected_volume_identifier = u'p{0:d}'.format(partition_number)
        except ValueError:
          pass

      if (selected_volume_identifier == u'all' or
          selected_volume_identifier in volume_identifiers):
        break

      print(u'')
      print(
          u'Unsupported partition identifier, please try again or abort '
          u'with Ctrl^C.')
      print(u'')

    return selected_volume_identifier

  def _PromptUserForVSSStoreIdentifiers(
      self, volume_system, volume_identifiers):
    """Prompts the user to provide the VSS store identifiers.

    This method first checks for the preferred VSS stores and falls back
    to prompt the user if no usable preferences were specified.

    Args:
      volume_system: The volume system (instance of dfvfs.VShadowVolumeSystem).
      volume_identifiers: List of allowed volume identifiers.

    Returns:
      The list of selected VSS store identifiers or None.

    Raises:
      SourceScannerError: if the source cannot be processed.
    """
    normalized_volume_identifiers = []
    for volume_identifier in volume_identifiers:
      volume = volume_system.GetVolumeByIdentifier(volume_identifier)
      if not volume:
        raise errors.SourceScannerError(
            u'Volume missing for identifier: {0:s}.'.format(volume_identifier))

      try:
        volume_identifier = int(volume.identifier[3:], 10)
        normalized_volume_identifiers.append(volume_identifier)
      except ValueError:
        pass

    print_header = True
    while True:
      if print_header:
        print(u'The following Volume Shadow Snapshots (VSS) were found:')
        print(u'Identifier\tVSS store identifier')

        for volume_identifier in volume_identifiers:
          volume = volume_system.GetVolumeByIdentifier(volume_identifier)
          if not volume:
            raise errors.SourceScannerError(
                u'Volume missing for identifier: {0:s}.'.format(
                    volume_identifier))

          vss_identifier = volume.GetAttribute(u'identifier')
          print(u'{0:s}\t\t{1:s}'.format(
              volume.identifier, vss_identifier.value))

        print(u'')

        print_header = False

      print(
          u'Please specify the identifier(s) of the VSS that should be '
          u'processed:')
      print(
          u'Note that a range of stores can be defined as: 3..5. Multiple '
          u'stores can')
      print(
          u'be defined as: 1,3,5 (a list of comma separated values). Ranges '
          u'and lists can')
      print(
          u'also be combined as: 1,3..5. The first store is 1. All stores '
          u'can be defined')
      print(u'as "all". If no stores are specified none will be processed. You')
      print(u'can abort with Ctrl^C.')

      selected_vss_stores = sys.stdin.readline()

      selected_vss_stores = selected_vss_stores.strip()
      if not selected_vss_stores:
        break

      try:
        selected_vss_stores = self._ParseVSSStoresString(selected_vss_stores)
      except errors.BadConfigOption:
        selected_vss_stores = []

      if selected_vss_stores == [u'all']:
        # We need to set the stores to cover all vss stores.
        selected_vss_stores = range(1, volume_system.number_of_volumes + 1)

      if not set(selected_vss_stores).difference(normalized_volume_identifiers):
        break

      print(u'')
      print(
          u'Unsupported VSS identifier(s), please try again or abort with '
          u'Ctrl^C.')
      print(u'')

    return selected_vss_stores

  def _ScanVolume(self, scan_context, volume_scan_node, base_path_specs):
    """Scans the volume scan node for volume and file systems.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      volume_scan_node: the volume scan node (instance of dfvfs.ScanNode).
      base_path_specs: a list of source path specification (instances
                       of dfvfs.PathSpec).

    Raises:
      RuntimeError: if the format of or within the source
                    is not supported or the the scan node is invalid.
    """
    if not volume_scan_node or not volume_scan_node.path_spec:
      raise RuntimeError(u'Invalid or missing volume scan node.')

    if len(volume_scan_node.sub_nodes) == 0:
      self._ScanVolumeScanNode(scan_context, volume_scan_node, base_path_specs)

    else:
      # Some volumes contain other volume or file systems e.g. BitLocker ToGo
      # has an encrypted and unencrypted volume.
      for sub_scan_node in volume_scan_node.sub_nodes:
        self._ScanVolumeScanNode(scan_context, sub_scan_node, base_path_specs)

  def _ScanVolumeScanNode(
      self, scan_context, volume_scan_node, base_path_specs):
    """Scans an individual volume scan node for volume and file systems.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      volume_scan_node: the volume scan node (instance of dfvfs.ScanNode).
      base_path_specs: a list of source path specification (instances
                       of dfvfs.PathSpec).

    Raises:
      RuntimeError: if the format of or within the source
                    is not supported or the the scan node is invalid.
    """
    if not volume_scan_node or not volume_scan_node.path_spec:
      raise RuntimeError(u'Invalid or missing volume scan node.')

    # Get the first node where where we need to decide what to process.
    scan_node = volume_scan_node
    while len(scan_node.sub_nodes) == 1:
      # Make sure that we prompt the user about VSS selection.
      if scan_node.type_indicator == definitions.TYPE_INDICATOR_VSHADOW:
        location = getattr(scan_node.path_spec, u'location', None)
        if location == u'/':
          break

      scan_node = scan_node.sub_nodes[0]

    # The source scanner found an encrypted volume and we need
    # a credential to unlock the volume.
    if scan_node.type_indicator in definitions.ENCRYPTED_VOLUME_TYPE_INDICATORS:
      self._ScanVolumeScanNodeEncrypted(
          scan_context, scan_node, base_path_specs)

    elif scan_node.type_indicator == definitions.TYPE_INDICATOR_VSHADOW:
      self._ScanVolumeScanNodeVSS(scan_node, base_path_specs)

    elif scan_node.type_indicator in definitions.FILE_SYSTEM_TYPE_INDICATORS:
      base_path_specs.append(scan_node.path_spec)

  def _ScanVolumeScanNodeEncrypted(
      self, scan_context, volume_scan_node, base_path_specs):
    """Scans an encrypted volume scan node for volume and file systems.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      volume_scan_node: the volume scan node (instance of dfvfs.ScanNode).
      base_path_specs: a list of source path specification (instances
                       of dfvfs.PathSpec).
    """
    result = not scan_context.IsLockedScanNode(volume_scan_node.path_spec)
    if not result:
      credentials = credentials_manager.CredentialsManager.GetCredentials(
          volume_scan_node.path_spec)

      result = self._PromptUserForEncryptedVolumeCredential(
          scan_context, volume_scan_node, credentials)

    if result:
      self._source_scanner.Scan(
          scan_context, scan_path_spec=volume_scan_node.path_spec)
      self._ScanVolume(scan_context, volume_scan_node, base_path_specs)

  def _ScanVolumeScanNodeVSS(
      self, volume_scan_node, base_path_specs):
    """Scans a VSS volume scan node for volume and file systems.

    Args:
      volume_scan_node: the volume scan node (instance of dfvfs.ScanNode).
      base_path_specs: a list of source path specification (instances
                       of dfvfs.PathSpec).

    Raises:
      SourceScannerError: if a VSS sub scan node scannot be retrieved.
    """
    # Do not scan inside individual VSS store scan nodes.
    location = getattr(volume_scan_node.path_spec, u'location', None)
    if location != u'/':
      return

    vss_store_identifiers = self._GetVSSStoreIdentifiers(volume_scan_node)

    self._vss_stores = list(vss_store_identifiers)

    # Process VSS stores starting with the most recent one.
    vss_store_identifiers.reverse()
    for vss_store_identifier in vss_store_identifiers:
      location = u'/vss{0:d}'.format(vss_store_identifier)
      sub_scan_node = volume_scan_node.GetSubNodeByLocation(location)
      if not sub_scan_node:
        raise errors.SourceScannerError(
            u'Scan node missing for VSS store identifier: {0:d}.'.format(
                vss_store_identifier))

      # We "optimize" here for user experience, alternatively we could scan for
      # a file system instead of hard coding a TSK child path specification.
      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_TSK, location=u'/',
          parent=sub_scan_node.path_spec)
      base_path_specs.append(path_spec)

      # TODO: look into building VSS store on demand.
      # self._source_scanner.Scan(
      #     scan_context, scan_path_spec=sub_scan_node.path_spec)
      # self._ScanVolume(scan_context, sub_scan_node, base_path_specs)

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
            u'Unable to open base path specification:\n{0:s}'.format(
                base_path_spec.comparable))
        continue

      self._CalculateHashesFileEntry(
          file_system, file_entry, u'', output_writer)

  def GetBasePathSpecs(self, source_path):
    """Determines the base path specifications.

    Args:
      source_path: the source path.

    Returns:
      A list of path specifications (instances of dfvfs.PathSpec).

    Raises:
      RuntimeError: if the source path does not exists, or if the source path
                    is not a file or directory, or if the format of or within
                    the source file is not supported.
    """
    if (not source_path.startswith(u'\\\\.\\') and
        not os.path.exists(source_path)):
      raise RuntimeError(
          u'No such device, file or directory: {0:s}.'.format(source_path))

    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(source_path)

    try:
      self._source_scanner.Scan(scan_context)
    except (errors.BackEndError, ValueError) as exception:
      raise RuntimeError(
          u'Unable to scan source with error: {0:s}.'.format(exception))

    if scan_context.source_type not in [
        definitions.SOURCE_TYPE_STORAGE_MEDIA_DEVICE,
        definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE]:
      scan_node = scan_context.GetRootScanNode()
      return [scan_node.path_spec]

    # Get the first node where where we need to decide what to process.
    scan_node = scan_context.GetRootScanNode()
    while len(scan_node.sub_nodes) == 1:
      scan_node = scan_node.sub_nodes[0]

    # The source scanner found a partition table and we need to determine
    # which partition needs to be processed.
    if scan_node.type_indicator != definitions.TYPE_INDICATOR_TSK_PARTITION:
      partition_identifiers = None

    else:
      partition_identifiers = self._GetTSKPartitionIdentifiers(scan_node)

    base_path_specs = []
    if not partition_identifiers:
      self._ScanVolume(scan_context, scan_node, base_path_specs)

    else:
      for partition_identifier in partition_identifiers:
        location = u'/{0:s}'.format(partition_identifier)
        sub_scan_node = scan_node.GetSubNodeByLocation(location)
        self._ScanVolume(scan_context, sub_scan_node, base_path_specs)

    if not base_path_specs:
      raise RuntimeError(
          u'No supported file system found in source.')

    return base_path_specs


class StdoutWriter(object):
  """Class that defines a stdout output writer."""

  def __init__(self, encoding=u'utf-8'):
    """Initializes the output writer object.

    Args:
      encoding: optional input encoding.
    """
    super(StdoutWriter, self).__init__()
    self._encoding = encoding
    self._errors = u'strict'

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
    string = u'{0:s}\t{1:s}'.format(hash_value, path)

    try:
      # Note that encode() will first convert string into a Unicode string
      # if necessary.
      encoded_string = string.encode(self._encoding, errors=self._errors)
    except UnicodeEncodeError:
      if self._errors == u'strict':
        logging.error(
            u'Unable to properly write output due to encoding error. '
            u'Switching to error tolerant encoding which can result in '
            u'non Basic Latin (C0) characters to be replaced with "?" or '
            u'"\\ufffd".')
        self._errors = u'replace'

      encoded_string = string.encode(self._encoding, errors=self._errors)

    print(encoded_string)


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      u'Calculates a message digest hash for every file in a directory or '
      u'storage media image.'))

  argument_parser.add_argument(
      u'source', nargs=u'?', action=u'store', metavar=u'image.raw',
      default=None, help=(
          u'path of the directory or filename of a storage media image '
          u'containing the file.'))

  options = argument_parser.parse_args()

  if not options.source:
    print(u'Source value is missing.')
    print(u'')
    argument_parser.print_help()
    print(u'')
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  output_writer = StdoutWriter()

  if not output_writer.Open():
    print(u'Unable to open output writer.')
    print(u'')
    return False

  return_value = True
  recursive_hasher = RecursiveHasher()

  try:
    base_path_specs = recursive_hasher.GetBasePathSpecs(options.source)

    recursive_hasher.CalculateHashes(base_path_specs, output_writer)

    print(u'')
    print(u'Completed.')

  except KeyboardInterrupt:
    return_value = False

    print(u'')
    print(u'Aborted by user.')

  output_writer.Close()

  return return_value


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)

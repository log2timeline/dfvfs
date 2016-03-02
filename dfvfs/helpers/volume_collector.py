# -*- coding: utf-8 -*-
"""Classes to implement a Windows volume collector."""

from __future__ import print_function
import getpass
import os
import sys

from dfvfs.credentials import manager as credentials_manager
from dfvfs.lib import definitions as definitions
from dfvfs.lib import errors
from dfvfs.helpers import source_scanner as source_scanner
from dfvfs.helpers import windows_path_resolver as windows_path_resolver
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver
from dfvfs.volume import tsk_volume_system
from dfvfs.volume import vshadow_volume_system


class CollectorError(Exception):
  """Class that defines collector errors."""


class VolumeCollectorMediator(object):
  """Class that defines a volume collector mediator."""

  # For context see: http://en.wikipedia.org/wiki/Byte
  _UNITS_1000 = [u'B', u'kB', u'MB', u'GB', u'TB', u'EB', u'ZB', u'YB']
  _UNITS_1024 = [u'B', u'KiB', u'MiB', u'GiB', u'TiB', u'EiB', u'ZiB', u'YiB']

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

  # TODO: rename prompt to get to make mediator more generic.
  def PromptUserForEncryptedVolumeCredential(
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

  def PromptUserForPartitionIdentifiers(
      self, volume_system, volume_identifiers):
    """Prompts the user to provide a partition identifiers.

    Args:
      volume_system: The volume system (instance of dfvfs.TSKVolumeSystem).
      volume_identifiers: List of allowed volume identifiers.

    Returns:
      A list of strings containing the selected partition identifiers or None.

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

      if selected_volume_identifier == u'all':
        return volume_identifiers

      if selected_volume_identifier in volume_identifiers:
        break

      print(u'')
      print(
          u'Unsupported partition identifier, please try again or abort '
          u'with Ctrl^C.')
      print(u'')

    return [selected_volume_identifier]

  def PromptUserForVSSStoreIdentifiers(self, volume_system, volume_identifiers):
    """Prompts the user to provide the VSS store identifiers.

    This method first checks for the preferred VSS stores and falls back
    to prompt the user if no usable preferences were specified.

    Args:
      volume_system: The volume system (instance of dfvfs.VShadowVolumeSystem).
      volume_identifiers: List of allowed volume identifiers.

    Returns:
      A list of integers containing the selected VSS store identifiers or None.

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


class VolumeCollector(object):
  """Class that defines a volume collector."""

  def __init__(self, mediator=None):
    """Initializes the collector object.

    Args:
      mediator: a volume collector mediator (instance of
                VolumeCollectorMediator) or None.
    """
    super(VolumeCollector, self).__init__()
    self._mediator = mediator
    self._source_scanner = source_scanner.SourceScanner()

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

    if not self._mediator or len(volume_identifiers) == 1:
      return volume_identifiers

    try:
      return self._mediator.PromptUserForPartitionIdentifier(
          volume_system, volume_identifiers)
    except KeyboardInterrupt:
      raise RuntimeError(u'File system scan aborted.')

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
    if not self._mediator and not volume_identifiers:
      return []

    try:
      return self._mediator.PromptUserForVSSStoreIdentifiers(
          volume_system, volume_identifiers)
    except KeyboardInterrupt:
      raise errors.UserAbort(u'File system scan aborted.')

  def _ScanFileSystem(self, path_resolver):
    """Scans a file system for the Windows volume.

    Args:
      path_resolver: the path resolver (instance of dfvfs.WindowsPathResolver).

    Returns:
      True if the Windows directory was found, false otherwise.
    """

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

  def _ScanVolumeScanNodeVSS(self, volume_scan_node, base_path_specs):
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


class WindowsVolumeCollector(VolumeCollector):
  """Class that defines a Windows volume collector."""

  _WINDOWS_DIRECTORIES = frozenset([
      u'C:\\Windows',
      u'C:\\WINNT',
      u'C:\\WTSRV',
      u'C:\\WINNT35',
  ])

  def __init__(self):
    """Initializes the collector object."""
    super(WindowsVolumeCollector, self).__init__()
    self._file_system = None
    self._path_resolver = None
    self._single_file = False
    self._source_path = None
    self._windows_directory = None

  def _ScanFileSystem(self, path_resolver):
    """Scans a file system for the Windows volume.

    Args:
      path_resolver: the path resolver (instance of dfvfs.WindowsPathResolver).

    Returns:
      True if the Windows directory was found, false otherwise.
    """
    result = False

    for windows_path in self._WINDOWS_DIRECTORIES:
      windows_path_spec = path_resolver.ResolvePath(windows_path)

      result = windows_path_spec is not None
      if result:
        self._windows_directory = windows_path
        break

    return result

  def GetWindowsVolumePathSpec(self, source_path):
    """Determines the file system path specification of the Windows volume.

    Args:
      source_path: the source path.

    Returns:
      True if successful or False otherwise.

    Raises:
      CollectorError: if the source path does not exists, or if the source path
                      is not a file or directory, or if the format of or within
                      the source file is not supported.
    """
    # Note that os.path.exists() does not support Windows device paths.
    if (not source_path.startswith(u'\\\\.\\') and
        not os.path.exists(source_path)):
      raise CollectorError(
          u'No such device, file or directory: {0:s}.'.format(source_path))

    self._source_path = source_path
    scan_context = source_scanner.SourceScannerContext()
    scan_context.OpenSourcePath(source_path)

    try:
      self._source_scanner.Scan(scan_context)
    except (errors.BackEndError, ValueError) as exception:
      raise RuntimeError(
          u'Unable to scan source with error: {0:s}.'.format(exception))

    self._single_file = False
    if scan_context.source_type == definitions.SOURCE_TYPE_FILE:
      self._single_file = True
      return True

    windows_path_specs = []
    scan_node = scan_context.GetRootScanNode()
    if scan_context.source_type == definitions.SOURCE_TYPE_DIRECTORY:
      windows_path_specs.append(scan_node.path_spec)

    else:
      # Get the first node where where we need to decide what to process.
      while len(scan_node.sub_nodes) == 1:
        scan_node = scan_node.sub_nodes[0]

      # The source scanner found a partition table and we need to determine
      # which partition needs to be processed.
      if scan_node.type_indicator != (
          definitions.TYPE_INDICATOR_TSK_PARTITION):
        partition_identifiers = None

      else:
        partition_identifiers = self._GetTSKPartitionIdentifiers(scan_node)

      if not partition_identifiers:
        self._ScanVolume(scan_context, scan_node, windows_path_specs)

      else:
        for partition_identifier in partition_identifiers:
          location = u'/{0:s}'.format(partition_identifier)
          sub_scan_node = scan_node.GetSubNodeByLocation(location)
          self._ScanVolume(scan_context, sub_scan_node, windows_path_specs)

    if not windows_path_specs:
      raise CollectorError(
          u'No supported file system found in source.')

    file_system_path_spec = windows_path_specs[0]
    self._file_system = resolver.Resolver.OpenFileSystem(file_system_path_spec)

    if file_system_path_spec.type_indicator == definitions.TYPE_INDICATOR_OS:
      mount_point = file_system_path_spec
    else:
      mount_point = file_system_path_spec.parent

    self._path_resolver = windows_path_resolver.WindowsPathResolver(
        self._file_system, mount_point)

    # The source is a directory or single volume storage media image.
    if not self._windows_directory:
      if not self._ScanFileSystem(self._path_resolver):
        return False

    if not self._windows_directory:
      return False

    self._path_resolver.SetEnvironmentVariable(
        u'SystemRoot', self._windows_directory)
    self._path_resolver.SetEnvironmentVariable(
        u'WinDir', self._windows_directory)

    return True

  def OpenFile(self, windows_path):
    """Opens the file specificed by the Windows path.

    Args:
      windows_path: the Windows path to the file.

    Returns:
      The file-like object (instance of dfvfs.FileIO) or None if
      the file does not exist.
    """
    if self._single_file:
      # TODO: check name or move this into WindowsRegistryCollector.
      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_OS, location=self._source_path)
    else:
      path_spec = self._path_resolver.ResolvePath(windows_path)
      if path_spec is None:
        return

    return resolver.Resolver.OpenFileObject(path_spec)

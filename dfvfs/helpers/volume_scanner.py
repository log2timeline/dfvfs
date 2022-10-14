# -*- coding: utf-8 -*-
"""Scanner for supported volume and file systems."""

import abc
import os

from dfvfs.credentials import manager as credentials_manager
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.helpers import source_scanner
from dfvfs.helpers import windows_path_resolver
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver
from dfvfs.volume import factory as volume_system_factory


class VolumeScannerOptions(object):
  """Volume scanner options.

  Attributes:
    credentials (list[tuple[str, str]]): credentials, per type, to unlock
        volumes.
    partitions (list[str]): partition identifiers.
    scan_mode (str): mode that defines how the VolumeScanner should scan
        for volumes and snapshots.
    snapshots (list[str]): snapshot identifiers.
    volumes (list[str]): volume identifiers, e.g. those of an APFS or LVM
        volume system.
  """

  # Scan all volumes and snapshots for available file systems.
  SCAN_MODE_ALL = 'all'

  # Scan all volumes and snapshots for available file systems, but if a volume
  # system with snapshots is found, only scan snapshots not the current volume.
  SCAN_MODE_SNAPSHOTS_ONLY = 'snapshots-only'

  # Only scan volumes for available file systems. Do not scan snapshots.
  SCAN_MODE_VOLUMES_ONLY = 'volumes-only'

  def __init__(self):
    """Initializes volume scanner options."""
    super(VolumeScannerOptions, self).__init__()
    self.credentials = []
    self.partitions = []
    self.scan_mode = self.SCAN_MODE_ALL
    self.snapshots = []
    self.volumes = []


class VolumeScannerMediator(object):
  """Volume scanner mediator."""

  # pylint: disable=redundant-returns-doc

  @abc.abstractmethod
  def GetAPFSVolumeIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves APFS volume identifiers.

    This method can be used to prompt the user to provide APFS volume
    identifiers.

    Args:
      volume_system (APFSVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """

  @abc.abstractmethod
  def GetLVMVolumeIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves LVM volume identifiers.

    This method can be used to prompt the user to provide LVM volume
    identifiers.

    Args:
      volume_system (LVMVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """

  @abc.abstractmethod
  def GetPartitionIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves partition identifiers.

    This method can be used to prompt the user to provide partition identifiers.

    Args:
      volume_system (TSKVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """

  def GetVolumeIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves volume identifiers.

    This method can be used to prompt the user to provide volume identifiers.

    Args:
      volume_system (APFSVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """
    if volume_system.TYPE_INDICATOR == (
        definitions.TYPE_INDICATOR_APFS_CONTAINER):
      return self.GetAPFSVolumeIdentifiers(volume_system, volume_identifiers)

    if volume_system.TYPE_INDICATOR == definitions.TYPE_INDICATOR_LVM:
      return self.GetLVMVolumeIdentifiers(volume_system, volume_identifiers)

    return None

  def GetVolumeSnapshotIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves volume snapshot identifiers.

    This method can be used to prompt the user to provide volume snapshot
    identifiers.

    Args:
      volume_system (APFSVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """
    if volume_system.TYPE_INDICATOR == definitions.TYPE_INDICATOR_VSHADOW:
      return self.GetVSSStoreIdentifiers(volume_system, volume_identifiers)

    return None

  @abc.abstractmethod
  def GetVSSStoreIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves VSS store identifiers.

    This method can be used to prompt the user to provide VSS store identifiers.

    Args:
      volume_system (VShadowVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """

  @abc.abstractmethod
  def UnlockEncryptedVolume(
      self, source_scanner_object, scan_context, locked_scan_node, credentials):
    """Unlocks an encrypted volume.

    This method can be used to prompt the user to provide encrypted volume
    credentials.

    Args:
      source_scanner_object (SourceScanner): source scanner.
      scan_context (SourceScannerContext): source scanner context.
      locked_scan_node (SourceScanNode): locked scan node.
      credentials (Credentials): credentials supported by the locked scan node.

    Returns:
      bool: True if the volume was unlocked.
    """


class VolumeScanner(object):
  """Volume scanner."""

  def __init__(self, mediator=None):
    """Initializes a volume scanner.

    Args:
      mediator (Optional[VolumeScannerMediator]): a volume scanner mediator.
    """
    super(VolumeScanner, self).__init__()
    self._mediator = mediator
    self._source_path = None
    self._source_scanner = source_scanner.SourceScanner()
    self._source_type = None

  def _GetBasePathSpecs(self, scan_context, options):
    """Determines the base path specifications.

    Args:
      scan_context (SourceScannerContext): source scanner context.
      options (VolumeScannerOptions): volume scanner options.

    Returns:
      list[PathSpec]: path specifications.

    Raises:
      ScannerError: if the format of or within the source is not supported.
    """
    scan_node = scan_context.GetRootScanNode()

    if scan_context.source_type not in (
        definitions.SOURCE_TYPE_STORAGE_MEDIA_DEVICE,
        definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE):
      return [scan_node.path_spec]

    # Get the first node where where we need to decide what to process.
    while len(scan_node.sub_nodes) == 1:
      scan_node = scan_node.sub_nodes[0]

    base_path_specs = []
    if scan_node.type_indicator not in (
          definitions.TYPE_INDICATOR_GPT,
          definitions.TYPE_INDICATOR_TSK_PARTITION):
      self._ScanVolume(scan_context, scan_node, options, base_path_specs)

    else:
      # Determine which partition needs to be processed.
      partition_identifiers = self._GetPartitionIdentifiers(scan_node, options)
      for partition_identifier in partition_identifiers:
        sub_scan_node = scan_node.GetSubNodeByLocation(
            f'/{partition_identifier:s}')
        self._ScanVolume(scan_context, sub_scan_node, options, base_path_specs)

    return base_path_specs

  def _GetPartitionIdentifiers(self, scan_node, options):
    """Determines the partition identifiers.

    This function determines which partition identifiers need to be scanned
    based on the volume scanner options. If no options are provided and there
    is more than a single partition the mediator is used to ask the user.

    Args:
      scan_node (SourceScanNode): scan node.
      options (VolumeScannerOptions): volume scanner options.

    Returns:
      list[str]: partition identifiers.

    Raises:
      ScannerError: if the scan node is invalid or the scanner does not know
          how to proceed.
      UserAbort: if the user requested to abort.
    """
    if not scan_node or not scan_node.path_spec:
      raise errors.ScannerError('Invalid scan node.')

    volume_system = volume_system_factory.Factory.NewVolumeSystem(
        scan_node.type_indicator)
    volume_system.Open(scan_node.path_spec)

    volume_identifiers = self._source_scanner.GetVolumeIdentifiers(
        volume_system)
    if not volume_identifiers:
      return []

    if options.partitions:
      if options.partitions == ['all']:
        partitions = volume_system.volume_identifiers
      else:
        partitions = options.partitions

      try:
        selected_volumes = self._NormalizedVolumeIdentifiers(
            volume_system, partitions,
            prefix=volume_system.VOLUME_IDENTIFIER_PREFIX)

        if not set(selected_volumes).difference(volume_identifiers):
          return selected_volumes
      except errors.ScannerError as exception:
        if self._mediator:
          self._mediator.PrintWarning(f'{exception!s}')

    if len(volume_identifiers) > 1:
      if not self._mediator:
        raise errors.ScannerError(
            'Unable to proceed. More than one partitions found but no mediator '
            'to determine how they should be used.')

      try:
        volume_identifiers = self._mediator.GetPartitionIdentifiers(
            volume_system, volume_identifiers)

      except KeyboardInterrupt:
        raise errors.UserAbort('Volume scan aborted.')

    return self._NormalizedVolumeIdentifiers(
        volume_system, volume_identifiers,
        prefix=volume_system.VOLUME_IDENTIFIER_PREFIX)

  def _GetVolumeIdentifiers(self, volume_system, options):
    """Determines the volume identifiers.

    Args:
      volume_system (VolumeSystem): volume system.
      options (VolumeScannerOptions): volume scanner options.

    Returns:
      list[str]: volume identifiers.

    Raises:
      ScannerError: if the scanner does not know how to proceed.
      UserAbort: if the user requested to abort.
    """
    volume_identifiers = self._source_scanner.GetVolumeIdentifiers(
        volume_system)
    if not volume_identifiers:
      return []

    if options.volumes:
      if options.volumes == ['all']:
        volumes = volume_system.volume_identifiers
      else:
        volumes = options.volumes

      try:
        selected_volumes = self._NormalizedVolumeIdentifiers(
            volume_system, volumes,
            prefix=volume_system.VOLUME_IDENTIFIER_PREFIX)

        if not set(selected_volumes).difference(volume_identifiers):
          return selected_volumes
      except errors.ScannerError as exception:
        if self._mediator:
          self._mediator.PrintWarning(f'{exception!s}')

    if len(volume_identifiers) > 1:
      if not self._mediator:
        raise errors.ScannerError((
            f'Unable to proceed. More than one '
            f'{volume_system.TYPE_INDICATOR:s} volume found but no mediator '
            f'to determine how they should be used.'))

      try:
        volume_identifiers = self._mediator.GetVolumeIdentifiers(
            volume_system, volume_identifiers)
      except KeyboardInterrupt:
        raise errors.UserAbort('Volume scan aborted.')

    return self._NormalizedVolumeIdentifiers(
        volume_system, volume_identifiers,
        prefix=volume_system.VOLUME_IDENTIFIER_PREFIX)

  def _GetVolumeSnapshotIdentifiers(self, volume_system, options):
    """Determines volume snapshot identifiers.

    Args:
      volume_system (VolumeSystem): volume system.
      options (VolumeScannerOptions): volume scanner options.

    Returns:
      list[str]: volume snapshot identifiers.

    Raises:
      ScannerError: if the scanner does not know how to proceed.
      UserAbort: if the user requested to abort.
    """
    volume_identifiers = self._source_scanner.GetVolumeIdentifiers(
        volume_system)
    if not volume_identifiers:
      return []

    if options.snapshots:
      if options.snapshots == ['all']:
        snapshots = volume_system.volume_identifiers
      elif options.snapshots == ['none']:
        snapshots = []
      else:
        snapshots = options.snapshots

      try:
        selected_volumes = self._NormalizedVolumeIdentifiers(
            volume_system, snapshots,
            prefix=volume_system.VOLUME_IDENTIFIER_PREFIX)

        if not set(selected_volumes).difference(volume_identifiers):
          return selected_volumes
      except errors.ScannerError as exception:
        if self._mediator:
          self._mediator.PrintWarning(f'{exception!s}')

    if not self._mediator:
      raise errors.ScannerError((
          f'Unable to proceed. {volume_system.TYPE_INDICATOR:s} volume '
          f'snapshots found but no mediator to determine how they should '
          f'be used.'))

    try:
      volume_identifiers = self._mediator.GetVolumeSnapshotIdentifiers(
          volume_system, volume_identifiers)

    except KeyboardInterrupt:
      raise errors.UserAbort('Volume scan aborted.')

    return self._NormalizedVolumeIdentifiers(
        volume_system, volume_identifiers,
        prefix=volume_system.VOLUME_IDENTIFIER_PREFIX)

  def _NormalizedVolumeIdentifiers(
      self, volume_system, volume_identifiers, prefix='v'):
    """Normalizes volume identifiers.

    Args:
      volume_system (VolumeSystem): volume system.
      volume_identifiers (list[int|str]): allowed volume identifiers, formatted
          as an integer or string with prefix.
      prefix (Optional[str]): volume identifier prefix.

    Returns:
      list[str]: volume identifiers with prefix.

    Raises:
      ScannerError: if the volume identifier is not supported or no volume
          could be found that corresponds with the identifier.
    """
    normalized_volume_identifiers = []
    for volume_identifier in volume_identifiers:
      if isinstance(volume_identifier, int):
        volume_identifier = f'{prefix:s}{volume_identifier:d}'

      elif not volume_identifier.startswith(prefix):
        try:
          volume_identifier = int(volume_identifier, 10)
          volume_identifier = f'{prefix:s}{volume_identifier:d}'
        except (TypeError, ValueError):
          pass

      try:
        volume = volume_system.GetVolumeByIdentifier(volume_identifier)
      except KeyError:
        volume = None

      if not volume:
        raise errors.ScannerError(
            f'Volume missing for identifier: {volume_identifier:s}.')

      normalized_volume_identifiers.append(volume_identifier)

    return normalized_volume_identifiers

  def _ScanEncryptedVolume(self, scan_context, scan_node, options):
    """Scans an encrypted volume scan node for volume and file systems.

    Args:
      scan_context (SourceScannerContext): source scanner context.
      scan_node (SourceScanNode): volume scan node.
      options (VolumeScannerOptions): volume scanner options.

    Raises:
      ScannerError: if the format of or within the source is not supported,
          the scan node is invalid, there are no credentials defined for
          the format or no mediator is provided and a locked scan node was
          found, e.g. an encrypted volume,
    """
    if not scan_node or not scan_node.path_spec:
      raise errors.ScannerError('Invalid or missing scan node.')

    credentials = credentials_manager.CredentialsManager.GetCredentials(
        scan_node.path_spec)
    if not credentials:
      raise errors.ScannerError('Missing credentials for scan node.')

    credentials_dict = {}
    for credential_identifier, credential_data in options.credentials:
      if credential_identifier not in credentials_dict:
        credentials_dict[credential_identifier] = []
      credentials_dict[credential_identifier].append(credential_data)

    is_unlocked = False
    for credential_type in sorted(credentials.CREDENTIALS):
      for credential_data in credentials_dict.get(credential_type, []):
        try:
          is_unlocked = self._source_scanner.Unlock(
              scan_context, scan_node.path_spec, credential_type,
              credential_data)
        except errors.BackEndError:
          is_unlocked = False

        if is_unlocked:
          break

      if is_unlocked:
        break

    if not is_unlocked:
      if not self._mediator:
        raise errors.ScannerError(
            'Unable to proceed. Encrypted volume found but no mediator to '
            'determine how it should be unlocked.')

      is_unlocked = self._mediator.UnlockEncryptedVolume(
          self._source_scanner, scan_context, scan_node, credentials)

    if is_unlocked:
      self._source_scanner.Scan(
          scan_context, scan_path_spec=scan_node.path_spec)

  def _ScanFileSystem(self, scan_node, base_path_specs):
    """Scans a file system scan node for file systems.

    Args:
      scan_node (SourceScanNode): file system scan node.
      base_path_specs (list[PathSpec]): file system base path specifications.

    Raises:
      ScannerError: if the scan node is invalid.
    """
    if not scan_node or not scan_node.path_spec:
      raise errors.ScannerError('Invalid or missing file system scan node.')

    if scan_node.type_indicator == definitions.TYPE_INDICATOR_APFS:
      # Note that APFS can have a volume without a root directory.
      file_entry = resolver.Resolver.OpenFileEntry(scan_node.path_spec)
      if not file_entry:
        return

    base_path_specs.append(scan_node.path_spec)

  def _ScanSource(self, source_path):
    """Scans the source for supported formats.

    Args:
      source_path (str): path to the source.

    Returns:
      SourceScannerContext: source scanner context.

    Raises:
      ScannerError: if the source path does not exists, or if the source path
          is not a file or directory, or if the format of or within the source
          file is not supported.
    """
    if not source_path:
      raise errors.ScannerError('Invalid source path.')

    # Note that os.path.exists() does not support Windows device paths.
    if (not source_path.startswith('\\\\.\\') and
        not os.path.exists(source_path)):
      raise errors.ScannerError(
          f'No such device, file or directory: {source_path:s}.')

    source_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=source_path)

    return self._ScanSourcePathSpec(source_path_spec)

  def _ScanSourcePathSpec(self, source_path_spec):
    """Scans the source path specification for supported formats.

    Args:
      source_path_spec (dfvfs.PathSpec): source path specification.

    Returns:
      SourceScannerContext: source scanner context.

    Raises:
      ScannerError: if the source path does not exists, or if the source path
          is not a file or directory, or if the format of or within the source
          file is not supported.
    """
    scan_context = source_scanner.SourceScannerContext()
    scan_context.AddScanNode(source_path_spec, None)

    try:
      self._source_scanner.Scan(scan_context)
    except (ValueError, errors.BackEndError) as exception:
      raise errors.ScannerError(
          f'Unable to scan source with error: {exception!s}')

    return scan_context

  def _ScanVolume(self, scan_context, scan_node, options, base_path_specs):
    """Scans a volume scan node for volume and file systems.

    Args:
      scan_context (SourceScannerContext): source scanner context.
      scan_node (SourceScanNode): volume scan node.
      options (VolumeScannerOptions): volume scanner options.
      base_path_specs (list[PathSpec]): file system base path specifications.

    Raises:
      ScannerError: if the format of or within the source
          is not supported or the scan node is invalid.
    """
    if not scan_node or not scan_node.path_spec:
      raise errors.ScannerError('Invalid or missing scan node.')

    if scan_context.IsLockedScanNode(scan_node.path_spec):
      # The source scanner found a locked volume and we need a credential to
      # unlock it.
      self._ScanEncryptedVolume(scan_context, scan_node, options)

      if scan_context.IsLockedScanNode(scan_node.path_spec):
        return

    if scan_node.IsVolumeSystemRoot():
      if options.scan_mode in (
          options.SCAN_MODE_ALL, options.SCAN_MODE_SNAPSHOTS_ONLY):
        self._ScanVolumeSystemRoot(
            scan_context, scan_node, options, base_path_specs)

    elif scan_node.IsFileSystem():
      self._ScanFileSystem(scan_node, base_path_specs)

    elif scan_node.type_indicator == definitions.TYPE_INDICATOR_VSHADOW:
      # We "optimize" here for user experience, alternatively we could scan for
      # a file system instead of hard coding a TSK child path specification.

      # TODO: look into building VSS store on demand.

      if definitions.PREFERRED_NTFS_BACK_END == definitions.TYPE_INDICATOR_TSK:
        location = '/'
      else:
        location = '\\'

      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.PREFERRED_NTFS_BACK_END, location=location,
          parent=scan_node.path_spec)

      base_path_specs.append(path_spec)

    else:
      for sub_scan_node in scan_node.sub_nodes:
        self._ScanVolume(scan_context, sub_scan_node, options, base_path_specs)

  def _ScanVolumeSystemRoot(
      self, scan_context, scan_node, options, base_path_specs):
    """Scans a volume system root scan node for volume and file systems.

    Args:
      scan_context (SourceScannerContext): source scanner context.
      scan_node (SourceScanNode): volume system root scan node.
      options (VolumeScannerOptions): volume scanner options.
      base_path_specs (list[PathSpec]): file system base path specifications.

    Raises:
      ScannerError: if the scan node is invalid, the scan node type is not
          supported or if a sub scan node cannot be retrieved.
    """
    if not scan_node or not scan_node.path_spec:
      raise errors.ScannerError('Invalid scan node.')

    if scan_node.type_indicator in (
        definitions.TYPE_INDICATOR_APFS_CONTAINER,
        definitions.TYPE_INDICATOR_LVM):
      volume_system = volume_system_factory.Factory.NewVolumeSystem(
          scan_node.type_indicator)
      volume_system.Open(scan_node.path_spec)

      volume_identifiers = self._GetVolumeIdentifiers(volume_system, options)

    elif scan_node.type_indicator == definitions.TYPE_INDICATOR_GPT:
      volume_identifiers = self._GetPartitionIdentifiers(scan_node, options)

    elif scan_node.type_indicator == definitions.TYPE_INDICATOR_VSHADOW:
      volume_system = volume_system_factory.Factory.NewVolumeSystem(
          scan_node.type_indicator)
      volume_system.Open(scan_node.path_spec)

      volume_identifiers = self._GetVolumeSnapshotIdentifiers(
          volume_system, options)
      # Process VSS stores (snapshots) starting with the most recent one.
      volume_identifiers.reverse()

    else:
      raise errors.ScannerError(
          f'Unsupported volume system type: {scan_node.type_indicator:s}.')

    for volume_identifier in volume_identifiers:
      sub_scan_node = scan_node.GetSubNodeByLocation(f'/{volume_identifier:s}')
      if not sub_scan_node:
        raise errors.ScannerError(
            f'Scan node missing for volume identifier: {volume_identifier:s}.')

      self._ScanVolume(scan_context, sub_scan_node, options, base_path_specs)

  def GetBasePathSpecs(self, source_path, options=None):
    """Determines the base path specifications.

    Args:
      source_path (str): source path.
      options (Optional[VolumeScannerOptions]): volume scanner options. If None
          the default volume scanner options are used, which are defined in the
          VolumeScannerOptions class.

    Returns:
      list[PathSpec]: path specifications.

    Raises:
      ScannerError: if the source path does not exists, or if the source path
          is not a file or directory, or if the format of or within the source
          file is not supported.
    """
    if not options:
      options = VolumeScannerOptions()

    scan_context = self._ScanSource(source_path)

    self._source_path = source_path
    self._source_type = scan_context.source_type

    return self._GetBasePathSpecs(scan_context, options)


class WindowsVolumeScanner(VolumeScanner):
  """Windows volume scanner."""

  _WINDOWS_DIRECTORIES = frozenset([
      'C:\\Windows',
      'C:\\WINNT',
      'C:\\WTSRV',
      'C:\\WINNT35',
  ])

  def __init__(self, mediator=None):
    """Initializes a Windows volume scanner.

    Args:
      mediator (VolumeScannerMediator): a volume scanner mediator.
    """
    super(WindowsVolumeScanner, self).__init__(mediator=mediator)
    self._file_system = None
    self._path_resolver = None
    self._windows_directory = None

  def _ScanFileSystem(self, scan_node, base_path_specs):
    """Scans a file system scan node for file systems.

    This method checks if the file system contains a known Windows directory.

    Args:
      scan_node (SourceScanNode): file system scan node.
      base_path_specs (list[PathSpec]): file system base path specifications.

    Raises:
      ScannerError: if the scan node is invalid.
    """
    if not scan_node or not scan_node.path_spec:
      raise errors.ScannerError('Invalid or missing file system scan node.')

    file_system = resolver.Resolver.OpenFileSystem(scan_node.path_spec)
    if file_system:
      path_resolver = windows_path_resolver.WindowsPathResolver(
          file_system, scan_node.path_spec.parent)

      if self._ScanFileSystemForWindowsDirectory(path_resolver):
        base_path_specs.append(scan_node.path_spec)

  def _ScanFileSystemForWindowsDirectory(self, path_resolver):
    """Scans a file system for a known Windows directory.

    Args:
      path_resolver (WindowsPathResolver): Windows path resolver.

    Returns:
      bool: True if a known Windows directory was found.
    """
    result = False
    for windows_path in self._WINDOWS_DIRECTORIES:
      windows_path_spec = path_resolver.ResolvePath(windows_path)

      result = windows_path_spec is not None
      if result:
        self._windows_directory = windows_path
        break

    return result

  def OpenFile(self, windows_path):
    """Opens the file specified by the Windows path.

    Args:
      windows_path (str): Windows path to the file.

    Returns:
      FileIO: file-like object or None if the file does not exist.
    """
    path_spec = self._path_resolver.ResolvePath(windows_path)
    if path_spec is None:
      return None

    return self._file_system.GetFileObjectByPathSpec(path_spec)

  def ScanForWindowsVolume(self, source_path, options=None):
    """Scans for a Windows volume.

    Args:
      source_path (str): source path.
      options (Optional[VolumeScannerOptions]): volume scanner options. If None
          the default volume scanner options are used, which are defined in the
          VolumeScannerOptions class.

    Returns:
      bool: True if a Windows volume was found.

    Raises:
      ScannerError: if the source path does not exists, or if the source path
          is not a file or directory, or if the format of or within the source
          file is not supported.
    """
    if not options:
      options = VolumeScannerOptions()

    scan_context = self._ScanSource(source_path)

    self._source_path = source_path
    self._source_type = scan_context.source_type

    base_path_specs = self._GetBasePathSpecs(scan_context, options)

    if (not base_path_specs or
        scan_context.source_type == definitions.SOURCE_TYPE_FILE):
      return False

    file_system_path_spec = base_path_specs[0]
    self._file_system = resolver.Resolver.OpenFileSystem(file_system_path_spec)

    if file_system_path_spec.type_indicator == definitions.TYPE_INDICATOR_OS:
      mount_point = file_system_path_spec
    else:
      mount_point = file_system_path_spec.parent

    self._path_resolver = windows_path_resolver.WindowsPathResolver(
        self._file_system, mount_point)

    # The source is a directory or single volume storage media image.
    if not self._windows_directory:
      self._ScanFileSystemForWindowsDirectory(self._path_resolver)

    if not self._windows_directory:
      return False

    self._path_resolver.SetEnvironmentVariable(
        'SystemRoot', self._windows_directory)
    self._path_resolver.SetEnvironmentVariable(
        'WinDir', self._windows_directory)

    return True

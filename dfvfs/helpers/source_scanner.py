# -*- coding: utf-8 -*-
"""Scanner for source files, directories and devices.

The source scanner tries to determine what input we are dealing with:
* a file that contains a storage media image;
* a device file of a storage media image device;
* a regular file or directory.

The source scanner scans for different types of elements:
* supported types of storage media images;
* supported types of volume systems;
* supported types of file systems.

These elements are represented as source scan nodes.

The source scanner uses the source scanner context to keep track of
the nodea and user provided context information, such as:
* which partition to default to;
* which VSS stores to default to.
"""

from dfvfs.analyzer import analyzer
from dfvfs.lib import apfs_helper
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import raw_helper
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver


class SourceScanNode(object):
  """Source scan node.

  Attributes:
    credential (tuple[str, str]): credential used to unlock the source scan
        node.
    path_spec (PathSpec): path specification.
    parent_node (SourceScanNode): source scan parent node.
    scanned (bool): True if the source scan node has been fully scanned.
    sub_nodes (list[SourceScanNode]): source scan sub nodes.
  """

  def __init__(self, path_spec):
    """Initializes a source scan node.

    Args:
      path_spec (PathSpec): path specification.
    """
    super(SourceScanNode, self).__init__()
    self.credential = None
    self.path_spec = path_spec
    self.parent_node = None
    self.scanned = False
    self.sub_nodes = []

  @property
  def type_indicator(self):
    """str: path specification type indicator."""
    return self.path_spec.type_indicator

  def GetSubNodeByLocation(self, location):
    """Retrieves a sub scan node based on the location.

    Args:
      location (str): location that should match the location of the path
          specification of a sub scan node.

    Returns:
      SourceScanNode: sub scan node or None if not available.
    """
    for sub_node in self.sub_nodes:
      sub_node_location = getattr(sub_node.path_spec, 'location', None)
      if location == sub_node_location:
        return sub_node

    return None

  def GetUnscannedSubNode(self):
    """Retrieves the first unscanned sub node.

    Returns:
      SourceScanNode: sub scan node or None if not available.
    """
    if not self.sub_nodes and not self.scanned:
      return self

    for sub_node in self.sub_nodes:
      result = sub_node.GetUnscannedSubNode()
      if result:
        return result

    return None

  def IsFileSystem(self):
    """Determines if the scan node represents a file system.

    Returns:
      bool: True if the scan node represents a file system.
    """
    return self.path_spec.IsFileSystem()

  def IsSystemLevel(self):
    """Determines if the scan node has a path specification at system-level.

    System-level is an indication used if the path specification is
    handled by the operating system and should not have a parent.

    Returns:
      bool: True if the scan node has a path specification at system-level.
    """
    return self.path_spec.IsSystemLevel()

  def IsVolumeSystem(self):
    """Determines if the scan node represents a volume system.

    Returns:
      bool: True if the scan node represents a volume system.
    """
    return self.path_spec.IsVolumeSystem()

  def IsVolumeSystemRoot(self):
    """Determines if the scan node represents the root of a volume system.

    Returns:
      bool: True if the scan node represents the root of a volume system.
    """
    return self.path_spec.IsVolumeSystemRoot()

  def SupportsEncryption(self):
    """Determines if the scan node supports encryption.

    Returns:
      bool: True if the scan node supports encryption.
    """
    return self.path_spec.type_indicator in (
        definitions.TYPE_INDICATORS_WITH_ENCRYPTION_SUPPORT)


class SourceScannerContext(object):
  """Contextual information for the source scanner.

  Attributes:
    source_type (str): type of source.
    updated (bool): True if the source scanner context has been updated.
  """

  # Keep for backwards compatibility reasons.
  SOURCE_TYPE_DIRECTORY = definitions.SOURCE_TYPE_DIRECTORY
  SOURCE_TYPE_FILE = definitions.SOURCE_TYPE_FILE
  SOURCE_TYPE_STORAGE_MEDIA_DEVICE = (
      definitions.SOURCE_TYPE_STORAGE_MEDIA_DEVICE)
  SOURCE_TYPE_STORAGE_MEDIA_IMAGE = (
      definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

  def __init__(self):
    """Initializes a source scanner context."""
    super(SourceScannerContext, self).__init__()
    self._file_system_scan_nodes = {}
    self._locked_scan_nodes = {}
    self._root_path_spec = None
    self._scan_nodes = {}

    self.source_type = None
    self.updated = False

  @property
  def locked_scan_nodes(self):
    """list[SourceScanNode]: locked scan nodes."""
    return list(self._locked_scan_nodes.values())

  def AddScanNode(self, path_spec, parent_scan_node):
    """Adds a scan node for a certain path specification.

    Args:
      path_spec (PathSpec): path specification.
      parent_scan_node (SourceScanNode): parent scan node or None.

    Returns:
      SourceScanNode: scan node.

    Raises:
      KeyError: if the scan node already exists.
      RuntimeError: if the parent scan node is not present.
    """
    scan_node = self._scan_nodes.get(path_spec, None)
    if scan_node:
      raise KeyError('Scan node already exists.')

    scan_node = SourceScanNode(path_spec)
    if parent_scan_node:
      if parent_scan_node.path_spec not in self._scan_nodes:
        raise RuntimeError('Parent scan node not present.')
      scan_node.parent_node = parent_scan_node
      parent_scan_node.sub_nodes.append(scan_node)

    if not self._root_path_spec:
      self._root_path_spec = path_spec

    self._scan_nodes[path_spec] = scan_node

    if path_spec.IsFileSystem():
      self._file_system_scan_nodes[path_spec] = scan_node

    self.updated = True
    return scan_node

  def GetRootScanNode(self):
    """Retrieves the root scan node.

    Returns:
      SourceScanNode: scan node or None if not available.
    """
    return self._scan_nodes.get(self._root_path_spec, None)

  def GetScanNode(self, path_spec):
    """Retrieves a scan node for a certain path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      SourceScanNode: scan node or None if not available.
    """
    return self._scan_nodes.get(path_spec, None)

  def GetUnscannedScanNode(self):
    """Retrieves the first unscanned scan node.

    Returns:
      SourceScanNode: scan node or None if not available.
    """
    root_scan_node = self._scan_nodes.get(self._root_path_spec, None)
    if not root_scan_node or not root_scan_node.scanned:
      return root_scan_node

    return root_scan_node.GetUnscannedSubNode()

  def HasFileSystemScanNodes(self):
    """Determines if a file system was detected during the scan.

    Returns:
      bool: True if a file system was detected during the scan.
    """
    return bool(self._file_system_scan_nodes)

  def HasLockedScanNodes(self):
    """Determines if a locked scan node was detected during the scan.

    A locked scan node is e.g. an encrypted volume for which a credential,
    e.g. password, to unlock the volume is not available.

    Returns:
      bool: True if a locked scan node was detected during the scan.
    """
    return bool(self._locked_scan_nodes)

  def HasScanNode(self, path_spec):
    """Determines if there is a scan node for a certain path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if there is a scan node for the path specification.
    """
    return self._scan_nodes.get(path_spec, None) is not None

  def IsLockedScanNode(self, path_spec):
    """Determines if a scan node is locked.

    A locked scan node is e.g. an encrypted volume for which a credential,
    e.g. password, to unlock the volume is not available.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      bool: True if the scan node is locked.
    """
    return path_spec in self._locked_scan_nodes

  def IsSourceTypeDirectory(self):
    """Determines if the source type is a directory.

    Returns:
      bool: True if the source type is a directory, False if not or
          None if not set.
    """
    if not self.source_type:
      return None

    return self.source_type == definitions.SOURCE_TYPE_DIRECTORY

  def IsSourceTypeFile(self):
    """Determines if the source type is a file.

    Returns:
      bool: True if the source type is a file, False if not or None if not set.
    """
    if not self.source_type:
      return None

    return self.source_type == definitions.SOURCE_TYPE_FILE

  def LockScanNode(self, path_spec):
    """Marks a scan node as locked.

    Args:
      path_spec (PathSpec): path specification.

    Raises:
      KeyError: if the scan node does not exists.
    """
    scan_node = self._scan_nodes.get(path_spec, None)
    if not scan_node:
      raise KeyError('Scan node does not exist.')

    self._locked_scan_nodes[path_spec] = scan_node

  def OpenSourcePath(self, source_path):
    """Opens the source path.

    Args:
      source_path (str): source path.
    """
    source_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=source_path)

    self.AddScanNode(source_path_spec, None)

  def RemoveScanNode(self, path_spec):
    """Removes a scan node of a certain path specification.

    Args:
      path_spec (PathSpec): path specification.

    Returns:
      SourceScanNode: parent scan node or None if not available.

    Raises:
      RuntimeError: if the scan node has sub nodes.
    """
    scan_node = self._scan_nodes.get(path_spec, None)
    if not scan_node:
      return None

    if scan_node.sub_nodes:
      raise RuntimeError('Scan node has sub nodes.')

    parent_scan_node = scan_node.parent_node
    if parent_scan_node:
      parent_scan_node.sub_nodes.remove(scan_node)

    if path_spec == self._root_path_spec:
      self._root_path_spec = None
    del self._scan_nodes[path_spec]

    if path_spec.IsFileSystem():
      del self._file_system_scan_nodes[path_spec]

    return parent_scan_node

  def SetSourceType(self, source_type):
    """Sets the source type.

    Args:
      source_type (str): source type.
    """
    if self.source_type is None:
      self.source_type = source_type

  def UnlockScanNode(self, path_spec, credential_identifier, credential_data):
    """Marks a scan node as unlocked.

    Args:
      path_spec (PathSpec): path specification.
      credential_identifier (str): credential identifier used to unlock
          the scan node.
      credential_data (bytes): credential data used to unlock the scan node.

    Raises:
      KeyError: if the scan node does not exists or is not locked.
    """
    if not self.HasScanNode(path_spec):
      raise KeyError('Scan node does not exist.')

    if path_spec not in self._locked_scan_nodes:
      raise KeyError('Scan node is not locked.')

    del self._locked_scan_nodes[path_spec]

    scan_node = self._scan_nodes[path_spec]
    scan_node.credential = (credential_identifier, credential_data)
    # Scan a node again after it has been unlocked.
    scan_node.scanned = False


class SourceScanner(object):
  """Searcher to find volumes within a volume system."""

  def __init__(self, resolver_context=None):
    """Initializes a source scanner.

    Args:
      resolver_context (Optional[Context]): resolver context, where None
          indicates to use the built-in context which is not multi process
          safe.
    """
    super(SourceScanner, self).__init__()
    self._resolver_context = resolver_context

  # TODO: add functions to check if path spec type is a storage media image
  # type, file system type, etc.

  def _ScanNode(self, scan_context, scan_node, auto_recurse=True):
    """Scans a node for supported formats.

    Args:
      scan_context (SourceScannerContext): source scanner context.
      scan_node (SourceScanNode): source scan node.
      auto_recurse (Optional[bool]): True if the scan should automatically
          recurse as far as possible.

    Raises:
      BackEndError: if the source cannot be scanned.
      ValueError: if the scan context or scan node is invalid.
    """
    if not scan_context:
      raise ValueError('Invalid scan context.')

    if not scan_node:
      raise ValueError('Invalid scan node.')

    scan_path_spec = scan_node.path_spec

    system_level_file_entry = None
    if scan_node.IsSystemLevel():
      system_level_file_entry = resolver.Resolver.OpenFileEntry(
          scan_node.path_spec, resolver_context=self._resolver_context)

      if system_level_file_entry is None:
        raise errors.BackEndError('Unable to open file entry.')

      if system_level_file_entry.IsDirectory():
        scan_context.SetSourceType(definitions.SOURCE_TYPE_DIRECTORY)
        return

      source_path_spec = self.ScanForStorageMediaImage(scan_node.path_spec)
      if source_path_spec:
        scan_node.scanned = True
        scan_node = scan_context.AddScanNode(source_path_spec, scan_node)

        if system_level_file_entry.IsDevice():
          source_type = definitions.SOURCE_TYPE_STORAGE_MEDIA_DEVICE
        else:
          source_type = definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE

        scan_context.SetSourceType(source_type)

        if not auto_recurse:
          return

      # In case we did not find a storage media image type we keep looking
      # since not all RAW storage media image naming schemas are known and
      # its type can only detected by its content.

    source_path_spec = None
    while True:
      if scan_node.IsFileSystem():
        # No need to scan a file systems scan node for volume systems.
        break

      if scan_node.SupportsEncryption():
        self._ScanEncryptedVolumeNode(scan_context, scan_node)

      if scan_context.IsLockedScanNode(scan_node.path_spec):
        # Scan node is locked, such as an encrypted volume, and we cannot
        # scan it for a volume system.
        break

      source_path_spec = self.ScanForVolumeSystem(scan_node.path_spec)
      if not source_path_spec:
        # No volume system found continue with a file system scan.
        break

      if not scan_context.HasScanNode(source_path_spec):
        scan_node.scanned = True
        scan_node = scan_context.AddScanNode(source_path_spec, scan_node)

        if system_level_file_entry and system_level_file_entry.IsDevice():
          source_type = definitions.SOURCE_TYPE_STORAGE_MEDIA_DEVICE
        else:
          source_type = definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE

        scan_context.SetSourceType(source_type)

      if scan_node.IsVolumeSystemRoot():
        self._ScanVolumeSystemRootNode(
            scan_context, scan_node, auto_recurse=auto_recurse)

        # We already have already scanned for the file systems.
        return

      if not auto_recurse and scan_context.updated:
        return

      # Nothing new found.
      if not scan_context.updated:
        break

    # In case we did not find a volume system type we keep looking
    # since we could be dealing with a storage media image that contains
    # a single volume.

    # No need to scan the root of a volume system for a file system.
    if scan_node.IsVolumeSystemRoot():
      pass

    elif scan_context.IsLockedScanNode(scan_node.path_spec):
      # Scan node is locked, such as an encrypted volume, and we cannot
      # scan it for a file system.
      pass

    elif (scan_node.type_indicator == definitions.TYPE_INDICATOR_VSHADOW and
          auto_recurse and scan_node.path_spec != scan_path_spec):
      # Since scanning for file systems in VSS snapshot volumes can
      # be expensive we only do this when explicitly asked for.
      pass

    elif not scan_node.IsFileSystem():
      source_path_spec = self.ScanForFileSystem(scan_node.path_spec)
      if not source_path_spec:
        # Since RAW storage media image can only be determined by naming schema
        # we could have single file that is not a RAW storage media image yet
        # matches the naming schema.
        if scan_node.path_spec.type_indicator == definitions.TYPE_INDICATOR_RAW:
          scan_node = scan_context.RemoveScanNode(scan_node.path_spec)

          # Make sure to override the previously assigned source type.
          scan_context.source_type = definitions.SOURCE_TYPE_FILE
        else:
          scan_context.SetSourceType(definitions.SOURCE_TYPE_FILE)

      elif not scan_context.HasScanNode(source_path_spec):
        scan_node.scanned = True
        scan_node = scan_context.AddScanNode(source_path_spec, scan_node)

        if system_level_file_entry and system_level_file_entry.IsDevice():
          source_type = definitions.SOURCE_TYPE_STORAGE_MEDIA_DEVICE
        else:
          source_type = definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE

        scan_context.SetSourceType(source_type)

    # If all scans failed mark the scan node as scanned so we do not scan it
    # again.
    if not scan_node.scanned:
      scan_node.scanned = True

  def _ScanEncryptedVolumeNode(self, scan_context, scan_node):
    """Scans an encrypted volume node for supported formats.

    Args:
      scan_context (SourceScannerContext): source scanner context.
      scan_node (SourceScanNode): source scan node.

    Raises:
      BackEndError: if the scan node cannot be unlocked.
      ValueError: if the scan context or scan node is invalid.
    """
    file_entry = resolver.Resolver.OpenFileEntry(
        scan_node.path_spec, resolver_context=self._resolver_context)
    if not file_entry:
      raise errors.BackEndError('Unable resolve file entry of scan node.')

    if not file_entry.Unlock():
      scan_context.LockScanNode(scan_node.path_spec)

      # For BitLocker To Go add a scan node for the unencrypted part of
      # the volume.
      if scan_node.type_indicator == definitions.TYPE_INDICATOR_BDE:
        path_spec = self.ScanForFileSystem(scan_node.path_spec.parent)
        if path_spec:
          scan_context.AddScanNode(path_spec, scan_node.parent_node)

  def _ScanVolumeSystemRootNode(
      self, scan_context, scan_node, auto_recurse=True):
    """Scans a volume system root node for supported formats.

    Args:
      scan_context (SourceScannerContext): source scanner context.
      scan_node (SourceScanNode): source scan node.
      auto_recurse (Optional[bool]): True if the scan should automatically
          recurse as far as possible.

    Raises:
      ValueError: if the scan context or scan node is invalid.
    """
    if scan_node.type_indicator == definitions.TYPE_INDICATOR_VSHADOW:
      # For VSS add a scan node for the current volume.
      path_spec = self.ScanForFileSystem(scan_node.path_spec.parent)
      if path_spec:
        scan_context.AddScanNode(path_spec, scan_node.parent_node)

    # Determine the path specifications of the sub file entries.
    try:
      file_entry = resolver.Resolver.OpenFileEntry(
          scan_node.path_spec, resolver_context=self._resolver_context)
    except errors.BackEndError:
      # Note that because pytsk returns slots LVM can be prematurely detected
      # and we have to catch the resulting BackEndError exception. Also see:
      # https://github.com/log2timeline/dfvfs/issues/578
      return

    for sub_file_entry in file_entry.sub_file_entries:
      sub_scan_node = scan_context.AddScanNode(
          sub_file_entry.path_spec, scan_node)

      if scan_node.type_indicator == definitions.TYPE_INDICATOR_VSHADOW:
        # Since scanning for file systems in VSS snapshot volumes can
        # be expensive we only do this when explicitly asked for.
        continue

      if auto_recurse or not scan_context.updated:
        self._ScanNode(scan_context, sub_scan_node, auto_recurse=auto_recurse)

  def GetVolumeIdentifiers(self, volume_system):
    """Retrieves the volume identifiers.

    Args:
      volume_system (VolumeSystem): volume system.

    Returns:
      list[str]: sorted volume identifiers.
    """
    volume_identifiers = []
    for volume in volume_system.volumes:
      volume_identifier = getattr(volume, 'identifier', None)
      if volume_identifier:
        volume_identifiers.append(volume_identifier)

    return sorted(volume_identifiers)

  def Scan(self, scan_context, auto_recurse=True, scan_path_spec=None):
    """Scans for supported formats.

    Args:
      scan_context (SourceScannerContext): source scanner context.
      auto_recurse (Optional[bool]): True if the scan should automatically
          recurse as far as possible.
      scan_path_spec (Optional[PathSpec]): path specification to indicate
          where the source scanner should continue scanning, where None
          indicates the scanner will start with the sources.

    Raises:
      ValueError: if the scan context is invalid.
    """
    if not scan_context:
      raise ValueError('Invalid scan context.')

    scan_context.updated = False

    if scan_path_spec:
      scan_node = scan_context.GetScanNode(scan_path_spec)

    else:
      scan_node = scan_context.GetUnscannedScanNode()

    if scan_node:
      self._ScanNode(scan_context, scan_node, auto_recurse=auto_recurse)

  def ScanForFileSystem(self, source_path_spec):
    """Scans the path specification for a supported file system format.

    Args:
      source_path_spec (PathSpec): source path specification.

    Returns:
      PathSpec: file system path specification or None if no supported file
          system type was found.

    Raises:
      BackEndError: if the source cannot be scanned or more than one file
          system type is found.
    """
    if source_path_spec.type_indicator == (
        definitions.TYPE_INDICATOR_APFS_CONTAINER):
      # Currently pyfsapfs does not support reading from a volume as a device.
      # Also see: https://github.com/log2timeline/dfvfs/issues/332
      return path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_APFS, location='/',
          parent=source_path_spec)

    try:
      type_indicators = analyzer.Analyzer.GetFileSystemTypeIndicators(
          source_path_spec, resolver_context=self._resolver_context)
    except RuntimeError as exception:
      raise errors.BackEndError((
          f'Unable to process source path specification with error: '
          f'{exception!s}'))

    if not type_indicators:
      return None

    type_indicator = type_indicators[0]
    if len(type_indicators) > 1:
      if definitions.PREFERRED_EXT_BACK_END in type_indicators:
        type_indicator = definitions.PREFERRED_EXT_BACK_END

      elif definitions.PREFERRED_HFS_BACK_END in type_indicators:
        type_indicator = definitions.PREFERRED_HFS_BACK_END

      elif definitions.PREFERRED_NTFS_BACK_END in type_indicators:
        type_indicator = definitions.PREFERRED_NTFS_BACK_END

      else:
        raise errors.BackEndError(
            'Unsupported source found more than one file system types.')

    # TODO: determine root location from file system or path specification.
    if type_indicator in (
        definitions.TYPE_INDICATOR_FAT, definitions.TYPE_INDICATOR_NTFS):
      root_location = '\\'
    else:
      root_location = '/'

    file_system_path_spec = path_spec_factory.Factory.NewPathSpec(
        type_indicator, location=root_location, parent=source_path_spec)

    if type_indicator == definitions.TYPE_INDICATOR_TSK:
      # Check if the file system can be opened since the file system by
      # signature detection results in false positives.
      try:
        resolver.Resolver.OpenFileSystem(
            file_system_path_spec, resolver_context=self._resolver_context)
      except (KeyError, errors.BackEndError):
        file_system_path_spec = None

    return file_system_path_spec

  def ScanForStorageMediaImage(self, source_path_spec):
    """Scans the path specification for a supported storage media image format.

    Args:
      source_path_spec (PathSpec): source path specification.

    Returns:
      PathSpec: storage media image path specification or None if no supported
          storage media image type was found.

    Raises:
      BackEndError: if the source cannot be scanned or more than one storage
          media image type is found.
    """
    try:
      type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
          source_path_spec, resolver_context=self._resolver_context)
    except RuntimeError as exception:
      raise errors.BackEndError((
          f'Unable to process source path specification with error: '
          f'{exception!s}'))

    if not type_indicators:
      # The RAW storage media image type cannot be detected based on
      # a signature so we try to detect it based on common file naming schemas.
      file_system = resolver.Resolver.OpenFileSystem(
          source_path_spec, resolver_context=self._resolver_context)
      raw_path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_RAW, parent=source_path_spec)

      try:
        # The RAW glob function will raise a PathSpecError if the path
        # specification is unsuitable for globbing.
        glob_results = raw_helper.RawGlobPathSpec(file_system, raw_path_spec)
      except errors.PathSpecError:
        glob_results = None

      if not glob_results:
        return None

      return raw_path_spec

    if len(type_indicators) > 1:
      raise errors.BackEndError(
          'Unsupported source found more than one storage media image types.')

    return path_spec_factory.Factory.NewPathSpec(
        type_indicators[0], parent=source_path_spec)

  def ScanForVolumeSystem(self, source_path_spec):
    """Scans the path specification for a supported volume system format.

    Args:
      source_path_spec (PathSpec): source path specification.

    Returns:
      PathSpec: volume system path specification or None if no supported volume
          system type was found.

    Raises:
      BackEndError: if the source cannot be scanned or more than one volume
          system type is found.
    """
    if source_path_spec.type_indicator == definitions.TYPE_INDICATOR_VSHADOW:
      # It is technically possible to scan for VSS-in-VSS but makes no sense
      # to do so.
      return None

    if source_path_spec.IsVolumeSystemRoot():
      return source_path_spec

    if source_path_spec.type_indicator == (
        definitions.TYPE_INDICATOR_APFS_CONTAINER):
      # Currently pyfsapfs does not support reading from a volume as a device.
      # Also see: https://github.com/log2timeline/dfvfs/issues/332
      return None

    try:
      type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
          source_path_spec, resolver_context=self._resolver_context)
    except (IOError, RuntimeError) as exception:
      raise errors.BackEndError((
          f'Unable to process source path specification with error: '
          f'{exception!s}'))

    if not type_indicators:
      return None

    if len(type_indicators) > 1:
      raise errors.BackEndError(
          'Unsupported source found more than one volume system types.')

    # Ignore the TSK partition table type when detected within other partition
    # table types.
    if (type_indicators[0] == definitions.TYPE_INDICATOR_TSK_PARTITION and
        source_path_spec.type_indicator in (
            definitions.PARTITION_TABLE_TYPE_INDICATORS)):
      return None

    if type_indicators[0] in definitions.VOLUME_SYSTEM_TYPE_INDICATORS:
      return path_spec_factory.Factory.NewPathSpec(
          type_indicators[0], location='/', parent=source_path_spec)

    return path_spec_factory.Factory.NewPathSpec(
        type_indicators[0], parent=source_path_spec)

  def Unlock(
      self, scan_context, path_spec, credential_identifier, credential_data):
    """Unlocks a locked scan node e.g. the scan node of an encrypted volume.

    Args:
      scan_context (SourceScannerContext): source scanner context.
      path_spec (PathSpec): path specification of the locked scan node.
      credential_identifier (str): credential identifier used to unlock
          the scan node.
      credential_data (bytes): credential data used to unlock the scan node.

    Returns:
      bool: True if the scan node was successfully unlocked.

    Raises:
      BackEndError: if the scan node cannot be unlocked.
      KeyError: if the scan node does not exists or is not locked.
    """
    if not scan_context.HasScanNode(path_spec):
      raise KeyError('Scan node does not exist.')

    if not scan_context.IsLockedScanNode(path_spec):
      raise KeyError('Scan node is not locked.')

    resolver.Resolver.key_chain.SetCredential(
        path_spec, credential_identifier, credential_data)

    if path_spec.type_indicator == definitions.TYPE_INDICATOR_APFS_CONTAINER:
      # Currently pyfsapfs does not support reading from a volume as a device.
      # Also see: https://github.com/log2timeline/dfvfs/issues/332
      container_file_entry = resolver.Resolver.OpenFileEntry(
          path_spec, resolver_context=self._resolver_context)
      fsapfs_volume = container_file_entry.GetAPFSVolume()

      try:
        is_locked = not apfs_helper.APFSUnlockVolume(
            fsapfs_volume, path_spec, resolver.Resolver.key_chain)
      except IOError as exception:
        raise errors.BackEndError(
            f'Unable to unlock APFS volume with error: {exception!s}')

    else:
      file_object = resolver.Resolver.OpenFileObject(
          path_spec, resolver_context=self._resolver_context)
      is_locked = not file_object or file_object.is_locked

    if not is_locked:
      scan_context.UnlockScanNode(
          path_spec, credential_identifier, credential_data)

    return not is_locked

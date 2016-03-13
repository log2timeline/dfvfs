# -*- coding: utf-8 -*-
"""Scanner for source files, directories and devices.

The source scanner tries to determine what input we are dealing with:
* a file that contains a storage media image;
* a device file of a storage media image device;
* a regular file or directory.

The source scanner scans for:
* supported types of storage media images;
* supported types of volume systems;
* supported types of file systems.

The source scanner uses the source scanner context to keep track of
previously scanned or user provided context information, e.g.
* which partition to default to;
* which VSS stores to default to.
"""

from dfvfs.analyzer import analyzer
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.lib import raw
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver


class SourceScanNode(object):
  """Class that defines a source scan node."""

  def __init__(self, path_spec):
    """Initializes the source scan node object.

    Args:
      path_spec: the path specification (instance of PathSpec).
    """
    super(SourceScanNode, self).__init__()
    self.path_spec = path_spec
    self.parent_node = None
    self.scanned = False
    self.sub_nodes = []

  @property
  def type_indicator(self):
    """The path specification type indicator."""
    return self.path_spec.type_indicator

  def GetSubNodeByLocation(self, location):
    """Retrieves a sub scan node based on the location.

    Args:
      location: the location string in the sub scan node path specification,
                that should match.

    Return:
      The sub scan node object (instance of SourceScanNode) or None.
    """
    for sub_node in self.sub_nodes:
      sub_node_location = getattr(sub_node.path_spec, u'location', u'')
      if location == sub_node_location:
        return sub_node

  def GetUnscannedSubNode(self):
    """Retrieves the first unscanned sub node.

    Returns:
      A scan node (instance of SourceScanNode) or None.
    """
    if not self.sub_nodes and not self.scanned:
      return self

    for sub_node in self.sub_nodes:
      result = sub_node.GetUnscannedSubNode()
      if result:
        return result

  def IsSystemLevel(self):
    """Determines if the path specification is at system-level."""
    return self.path_spec.IsSystemLevel()


class SourceScannerContext(object):
  """Class that defines contextual information for the source scanner."""

  # Keep for backwards compatibility reasons.
  SOURCE_TYPE_DIRECTORY = definitions.SOURCE_TYPE_DIRECTORY
  SOURCE_TYPE_FILE = definitions.SOURCE_TYPE_FILE
  SOURCE_TYPE_STORAGE_MEDIA_DEVICE = (
      definitions.SOURCE_TYPE_STORAGE_MEDIA_DEVICE)
  SOURCE_TYPE_STORAGE_MEDIA_IMAGE = (
      definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

  def __init__(self):
    """Initializes the source scanner context object."""
    super(SourceScannerContext, self).__init__()
    self._file_system_scan_nodes = {}
    self._locked_scan_nodes = {}
    self._root_path_spec = None
    self._scan_nodes = {}

    self.source_type = None
    self.updated = False

  @property
  def locked_scan_nodes(self):
    """The locked scan nodes."""
    return iter(self._locked_scan_nodes.values())

  def AddScanNode(self, path_spec, parent_scan_node):
    """Adds a scan node for a certain path specifiation.

    Args:
      path_spec: the path specification (instance of PathSpec).
      parent_scan_node: the parent scan node (instance of SourceScanNode)
                        or None.

    Returns:
      The scan node (instance of SourceScanNode).

    Raises:
      KeyError: if the scan node already exists.
      RuntimeError: if the parent scan node is not present.
    """
    scan_node = self._scan_nodes.get(path_spec, None)
    if scan_node:
      raise KeyError(u'Scan node already exists.')

    scan_node = SourceScanNode(path_spec)
    if parent_scan_node:
      if parent_scan_node.path_spec not in self._scan_nodes:
        raise RuntimeError(u'Parent scan node not present.')
      scan_node.parent_node = parent_scan_node
      parent_scan_node.sub_nodes.append(scan_node)

    if not self._root_path_spec:
      self._root_path_spec = path_spec

    self._scan_nodes[path_spec] = scan_node

    if path_spec.type_indicator in definitions.FILE_SYSTEM_TYPE_INDICATORS:
      self._file_system_scan_nodes[path_spec] = scan_node

    self.updated = True
    return scan_node

  def HasFileSystemScanNodes(self):
    """Determines if a file system was detected during the scan."""
    return self._file_system_scan_nodes != {}

  def HasLockedScanNodes(self):
    """Determines if a locked scan node was detected during the scan.

    A locked scan node is e.g. an encrypted volume for which a credential,
    e.g. password, to unlock the volume is not available.
    """
    return self._locked_scan_nodes != {}

  def HasScanNode(self, path_spec):
    """Determines if there is a scan node for a certain path specifiation.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Returns:
      A boolean value indicating if there is a scan node for
      the path specification.
    """
    return self._scan_nodes.get(path_spec, None) is not None

  def GetRootScanNode(self):
    """Retrieves the root scan node.

    Returns:
      A scan node (instance of SourceScanNode) or None.
    """
    return self._scan_nodes.get(self._root_path_spec, None)

  def GetScanNode(self, path_spec):
    """Retrieves a scan node for a certain path specifiation.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Returns:
      A scan node (instance of SourceScanNode) or None.
    """
    return self._scan_nodes.get(path_spec, None)

  def GetUnscannedScanNode(self):
    """Retrieves the first unscanned scan node.

    Returns:
      A scan node (instance of SourceScanNode) or None.
    """
    root_scan_node = self._scan_nodes.get(self._root_path_spec, None)
    if not root_scan_node.scanned:
      return root_scan_node

    return root_scan_node.GetUnscannedSubNode()

  def IsLockedScanNode(self, path_spec):
    """Determines if a scan node is locked.

    A locked scan node is e.g. an encrypted volume for which a credential,
    e.g. password, to unlock the volume is not available.

    Args:
      path_spec: the path specification (instance of PathSpec)
                 of the scan node.

    Returns:
      A boolean value indicating if the scan node is locked.
    """
    return path_spec in self._locked_scan_nodes

  def IsSourceTypeDirectory(self):
    """Determines if the source type is a directory.

    Returns:
      A boolean if the source type is or is not a directory or None if not set.
    """
    if self.source_type:
      return self.source_type == definitions.SOURCE_TYPE_DIRECTORY

  def IsSourceTypeFile(self):
    """Determines if the source type is a file.

    Returns:
      A boolean if the source type is or is not a file or None if not set.
    """
    if self.source_type:
      return self.source_type == definitions.SOURCE_TYPE_FILE

  def LockScanNode(self, path_spec):
    """Marks a scan node as locked.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Raises:
      KeyError: if the scan node does not exists.
    """
    scan_node = self._scan_nodes.get(path_spec, None)
    if not scan_node:
      raise KeyError(u'Scan node does not exist.')

    self._locked_scan_nodes[path_spec] = scan_node

  def OpenSourcePath(self, source_path):
    """Opens the source path.

    Args:
      source_path: Unicode string containing the source path.
    """
    source_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=source_path)

    self.AddScanNode(source_path_spec, None)

  def RemoveScanNode(self, path_spec):
    """Removes a scan node of a certain path specifiation.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Returns:
      The parent scan node (instance of SourceScanNode) or
      None if not available.

    Raises:
      RuntimeError: if the scan node has sub nodes.
    """
    scan_node = self._scan_nodes.get(path_spec, None)
    if not scan_node:
      return

    if scan_node.sub_nodes:
      raise RuntimeError(u'Scan node has sub nodes.')

    parent_scan_node = scan_node.parent_node
    if parent_scan_node:
      parent_scan_node.sub_nodes.remove(scan_node)

    if path_spec == self._root_path_spec:
      self._root_path_spec = None
    del self._scan_nodes[path_spec]

    if path_spec.type_indicator in definitions.FILE_SYSTEM_TYPE_INDICATORS:
      del self._file_system_scan_nodes[path_spec]

    return parent_scan_node

  def SetSourceType(self, source_type):
    """Sets the source type.

    Args:
      source_type: the source type.
    """
    if self.source_type is None:
      self.source_type = source_type

  def UnlockScanNode(self, path_spec):
    """Marks a scan node as unlocked.

    Args:
      path_spec: the path specification (instance of PathSpec).

    Raises:
      KeyError: if the scan node does not exists.
    """
    if not self.HasScanNode(path_spec):
      raise KeyError(u'Scan node does not exist.')

    del self._locked_scan_nodes[path_spec]


class SourceScanner(object):
  """Searcher object to find volumes within a volume system."""

  def __init__(self, resolver_context=None):
    """Initializes the source scanner object.

    Args:
      resolver_context: the optional resolver context (instance of
                        resolver.Context). The default is None which will use
                        the built in context which is not multi process safe.
    """
    super(SourceScanner, self).__init__()
    self._resolver_context = resolver_context

  # TODO: add functions to check if path spec type is an Image type,
  # FS type, etc.

  def _ScanNode(self, scan_context, scan_node, auto_recurse=True):
    """Scans for supported formats using a scan node.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      scan_node: the scan node (instance of SourceScanNode).
      auto_recurse: optional boolean value to indicate if the scan should
                    automatically recurse as far as possible. The default
                    is False.

    Raises:
      BackEndError: if the source cannot be scanned.
      ValueError: if the scan context or scan node is invalid.
    """
    if not scan_context:
      raise ValueError(u'Invalid scan context.')

    if not scan_node:
      raise ValueError(u'Invalid scan node.')

    scan_path_spec = scan_node.path_spec

    if not scan_node.IsSystemLevel():
      system_level_file_entry = None

    else:
      system_level_file_entry = resolver.Resolver.OpenFileEntry(
          scan_node.path_spec, resolver_context=self._resolver_context)

      if system_level_file_entry is None:
        raise errors.BackEndError(u'Unable to open file entry.')

      if system_level_file_entry.IsDirectory():
        scan_context.SetSourceType(definitions.SOURCE_TYPE_DIRECTORY)
        return

      source_path_spec = self.ScanForStorageMediaImage(scan_node.path_spec)
      if source_path_spec:
        scan_node.scanned = True
        scan_node = scan_context.AddScanNode(source_path_spec, scan_node)

        if system_level_file_entry.IsDevice():
          scan_context.SetSourceType(
              definitions.SOURCE_TYPE_STORAGE_MEDIA_DEVICE)
        else:
          scan_context.SetSourceType(
              definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

        if not auto_recurse:
          return

      # In case we did not find a storage media image type we keep looking
      # since not all RAW storage media image naming schemas are known and
      # its type can only detected by its content.

    source_path_spec = None
    while True:
      # No need to scan a file systems scan node for volume systems.
      if scan_node.type_indicator in definitions.FILE_SYSTEM_TYPE_INDICATORS:
        break

      # No need to scan a locked scan node e.g. an encrypted volume.
      if scan_context.IsLockedScanNode(scan_node.path_spec):
        break

      source_path_spec = self.ScanForVolumeSystem(scan_node.path_spec)
      # Nothing found in the volume system scan.
      if not source_path_spec:
        break

      if not scan_context.HasScanNode(source_path_spec):
        scan_node.scanned = True
        scan_node = scan_context.AddScanNode(source_path_spec, scan_node)

        if system_level_file_entry and system_level_file_entry.IsDevice():
          scan_context.SetSourceType(
              definitions.SOURCE_TYPE_STORAGE_MEDIA_DEVICE)
        else:
          scan_context.SetSourceType(
              definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

      if scan_node.type_indicator in definitions.VOLUME_SYSTEM_TYPE_INDICATORS:
        # For VSS add a scan node for the current volume.
        if scan_node.type_indicator == definitions.TYPE_INDICATOR_VSHADOW:
          path_spec = self.ScanForFileSystem(scan_node.path_spec.parent)
          if path_spec:
            scan_context.AddScanNode(path_spec, scan_node.parent_node)

        # Determine the path specifications of the sub file entries.
        file_entry = resolver.Resolver.OpenFileEntry(
            scan_node.path_spec, resolver_context=self._resolver_context)

        for sub_file_entry in file_entry.sub_file_entries:
          sub_scan_node = scan_context.AddScanNode(
              sub_file_entry.path_spec, scan_node)

          # Since scanning for file systems in VSS snapshot volumes can
          # be expensive we only do this when explicitly asked for.
          if scan_node.type_indicator != definitions.TYPE_INDICATOR_VSHADOW:
            if auto_recurse or not scan_context.updated:
              self._ScanNode(
                  scan_context, sub_scan_node, auto_recurse=auto_recurse)

        # We already have already scanned for the file systems in _ScanNode().
        return

      elif scan_node.type_indicator in (
          definitions.ENCRYPTED_VOLUME_TYPE_INDICATORS):
        file_object = resolver.Resolver.OpenFileObject(
            scan_node.path_spec, resolver_context=self._resolver_context)
        is_locked = not file_object or file_object.is_locked
        file_object.close()

        if is_locked:
          scan_context.LockScanNode(scan_node.path_spec)

          # For BitLocker To Go add a scan node for the unencrypted part
          # of the volume.
          if scan_node.type_indicator == definitions.TYPE_INDICATOR_BDE:
            path_spec = self.ScanForFileSystem(scan_node.path_spec.parent)
            if path_spec:
              scan_context.AddScanNode(path_spec, scan_node.parent_node)

      if not auto_recurse and scan_context.updated:
        return

      # Nothing new found.
      if not scan_context.updated:
        break

    # In case we did not find a volume system type we keep looking
    # since we could be dealing with a storage media image that contains
    # a single volume.

    # No need to scan the root of a volume system for a file system.
    if (scan_node.path_spec.type_indicator in (
        definitions.VOLUME_SYSTEM_TYPE_INDICATORS) and
        getattr(scan_node.path_spec, u'location', None) == u'/'):
      pass

    # No need to scan a locked scan node e.g. an encrypted volume.
    elif scan_context.IsLockedScanNode(scan_node.path_spec):
      pass

    # Since scanning for file systems in VSS snapshot volumes can
    # be expensive we only do this when explicitly asked for.
    elif (scan_node.type_indicator == definitions.TYPE_INDICATOR_VSHADOW and
          auto_recurse and scan_node.path_spec != scan_path_spec):
      pass

    elif scan_node.type_indicator not in (
        definitions.FILE_SYSTEM_TYPE_INDICATORS):
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
          scan_context.SetSourceType(
              definitions.SOURCE_TYPE_STORAGE_MEDIA_DEVICE)
        else:
          scan_context.SetSourceType(
              definitions.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

    # If all scans failed mark the scan node as scanned so we do not scan it
    # again.
    if not scan_node.scanned:
      scan_node.scanned = True

    return

  def GetVolumeIdentifiers(self, volume_system):
    """Retrieves the volume identifiers.

    Args:
      volume_system: The volume system (instance of dfvfs.VolumeSystem).

    Returns:
      A sorted list containing the volume identifiers.
    """
    volume_identifiers = []
    for volume in volume_system.volumes:
      volume_identifier = getattr(volume, u'identifier', None)
      if volume_identifier:
        volume_identifiers.append(volume_identifier)

    return sorted(volume_identifiers)

  def Scan(self, scan_context, auto_recurse=True, scan_path_spec=None):
    """Scans for supported formats.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      auto_recurse: optional boolean value to indicate if the scan should
                    automatically recurse as far as possible. The default
                    is True.
      scan_path_spec: optional path specification (instance of PathSpec)
                      to indicate where the source scanner should continue
                      scanning. The default is None which indicates the
                      scanner will start with the sources.

    Raises:
      ValueError: if the scan context is invalid.
    """
    if not scan_context:
      raise ValueError(u'Invalid scan context.')

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
      source_path_spec: the source path specification (instance of
                        dfvfs.PathSpec).

    Returns:
      The file system path specification (instance of dfvfs.PathSpec) or None
      if no supported file system type was found.

    Raises:
      BackEndError: if the source cannot be scanned or more than one file
                    system type is found.
    """
    try:
      type_indicators = analyzer.Analyzer.GetFileSystemTypeIndicators(
          source_path_spec, resolver_context=self._resolver_context)
    except RuntimeError as exception:
      raise errors.BackEndError((
          u'Unable to process source path specification with error: '
          u'{0:s}').format(exception))

    if not type_indicators:
      return

    type_indicator = type_indicators[0]
    if len(type_indicators) > 1:
      if definitions.PREFERRED_NTFS_BACK_END not in type_indicators:
        raise errors.BackEndError(
            u'Unsupported source found more than one file system types.')

      type_indicator = definitions.PREFERRED_NTFS_BACK_END

    # TODO: determine root location from file system or path specification.
    if type_indicator == definitions.TYPE_INDICATOR_NTFS:
      return path_spec_factory.Factory.NewPathSpec(
          type_indicator, location=u'\\', parent=source_path_spec)

    return path_spec_factory.Factory.NewPathSpec(
        type_indicator, location=u'/', parent=source_path_spec)

  def ScanForStorageMediaImage(self, source_path_spec):
    """Scans the path specification for a supported storage media image format.

    Args:
      source_path_spec: the source path specification (instance of
                        dfvfs.PathSpec).

    Returns:
      The storage media image path specification (instance of dfvfs.PathSpec)
      or None if no supported storage media image type was found.

    Raises:
      BackEndError: if the source cannot be scanned or more than one storage
                    media image type is found.
    """
    try:
      type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
          source_path_spec, resolver_context=self._resolver_context)
    except RuntimeError as exception:
      raise errors.BackEndError((
          u'Unable to process source path specification with error: '
          u'{0:s}').format(exception))

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
        glob_results = raw.RawGlobPathSpec(file_system, raw_path_spec)
      except errors.PathSpecError:
        glob_results = None

      if not glob_results:
        return

      return raw_path_spec

    if len(type_indicators) > 1:
      raise errors.BackEndError(
          u'Unsupported source found more than one storage media image types.')

    return path_spec_factory.Factory.NewPathSpec(
        type_indicators[0], parent=source_path_spec)

  def ScanForVolumeSystem(self, source_path_spec):
    """Scans the path specification for a supported volume system format.

    Args:
      source_path_spec: the source path specification (instance of
                        dfvfs.PathSpec).

    Returns:
      The volume system path specification (instance of dfvfs.PathSpec) or
      None if no supported volume system type was found.

    Raises:
      BackEndError: if the source cannot be scanned or more than one volume
                    system type is found.
    """
    # It is technically possible to scan for VSS-in-VSS but makes no sense
    # to do so.
    if source_path_spec.type_indicator == definitions.TYPE_INDICATOR_VSHADOW:
      return

    # Check if we already have a volume system root path specification.
    if source_path_spec.type_indicator in (
        definitions.VOLUME_SYSTEM_TYPE_INDICATORS):
      if getattr(source_path_spec, u'location', None) == u'/':
        return source_path_spec

    try:
      type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
          source_path_spec, resolver_context=self._resolver_context)
    except (IOError, RuntimeError) as exception:
      raise errors.BackEndError((
          u'Unable to process source path specification with error: '
          u'{0:s}').format(exception))

    if not type_indicators:
      return

    if len(type_indicators) > 1:
      raise errors.BackEndError(
          u'Unsupported source found more than one volume system types.')

    if (type_indicators[0] == definitions.TYPE_INDICATOR_TSK_PARTITION and
        source_path_spec.type_indicator in [
            definitions.TYPE_INDICATOR_TSK_PARTITION]):
      return

    if type_indicators[0] in definitions.VOLUME_SYSTEM_TYPE_INDICATORS:
      return path_spec_factory.Factory.NewPathSpec(
          type_indicators[0], location=u'/', parent=source_path_spec)

    return path_spec_factory.Factory.NewPathSpec(
        type_indicators[0], parent=source_path_spec)

  def Unlock(
      self, scan_context, path_spec, credential_identifier, credential_data):
    """Unlocks a locked scan node e.g. the scan node of an encrypted volume.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      path_spec: the path specification (instance of PathSpec) of
                 the locked scan node.
      credential_identifier: string containing the credential identifier used
                             to unlock the scan node.
      credential_data: the credential data used to unlock the scan node.

    Returns:
      A boolean indicating if the scan node was successfully unlocked or not.

    Raises:
      KeyError: if the scan node does not exists or is not locked.
    """
    if not scan_context.HasScanNode(path_spec):
      raise KeyError(u'Scan node does not exist.')

    if not scan_context.IsLockedScanNode(path_spec):
      raise KeyError(u'Scan node is not locked.')

    resolver.Resolver.key_chain.SetCredential(
        path_spec, credential_identifier, credential_data)

    file_object = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)
    is_locked = not file_object or file_object.is_locked
    file_object.close()

    if is_locked:
      return False

    scan_context.UnlockScanNode(path_spec)
    return True

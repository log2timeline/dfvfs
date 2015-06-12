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
      path_spec: the path specification (instance of path.PathSpec).
    """
    super(SourceScanNode, self).__init__()
    self.path_spec = path_spec
    self.parent_node = None
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

  def IsSystemLevel(self):
    """Determines if the path specfication is at system-level."""
    return self.path_spec.IsSystemLevel()


class SourceScannerContext(object):
  """Class that defines contextual information for the source scanner."""

  SOURCE_TYPE_DIRECTORY = u'directory'
  SOURCE_TYPE_FILE = u'file'
  SOURCE_TYPE_STORAGE_MEDIA_DEVICE = u'storage media device'
  SOURCE_TYPE_STORAGE_MEDIA_IMAGE = u'storage media image'

  def __init__(self):
    """Initializes the source scanner context object."""
    super(SourceScannerContext, self).__init__()
    self._root_path_spec = None
    self._scan_nodes = {}

    self.file_system_found = False
    self.last_scan_node = None
    self.source_type = None
    self.updated = False

  def AddScanNode(self, path_spec, parent_scan_node):
    """Adds a scan node for a certain path specifiation.

    Args:
      path_spec: the path specification (instance of path.PathSpec).
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

    self.last_scan_node = scan_node
    self.updated = True
    return scan_node

  def HasScanNode(self, path_spec):
    """Determines if there is a scan node for a certain path specifiation.

    Args:
      path_spec: the path specification (instance of path.PathSpec).

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
      path_spec: the path specification (instance of path.PathSpec).

    Returns:
      A scan node (instance of SourceScanNode) or None.
    """
    return self._scan_nodes.get(path_spec, None)

  def IsSourceTypeDirectory(self):
    """Determines if the source type is a directory.

    Returns:
      A boolean if the source type is or is not a directory or None if not set.
    """
    if self.source_type:
      return self.source_type == self.SOURCE_TYPE_DIRECTORY

  def IsSourceTypeFile(self):
    """Determines if the source type is a file.

    Returns:
      A boolean if the source type is or is not a file or None if not set.
    """
    if self.source_type:
      return self.source_type == self.SOURCE_TYPE_FILE

  def OpenSourcePath(self, source_path):
    """Opens the source path.

    Args:
      source_path: Unicode string containing the source path.
    """
    source_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=source_path)

    self.last_scan_node = self.AddScanNode(source_path_spec, None)

  def RemoveScanNode(self, path_spec):
    """Removes a scan node of a certain path specifiation.

    Args:
      path_spec: the path specification (instance of path.PathSpec).

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

    self.last_scan_node = parent_scan_node
    return parent_scan_node

  def SetSourceType(self, source_type):
    """Sets the source type.

    Args:
      source_type: the source type.
    """
    if self.source_type is None:
      self.source_type = source_type


class SourceScanner(object):
  """Searcher object to find volumes within a volume system."""

  def __init__(self, resolver_context=None):
    """Initializes the file-like object.

    Args:
      resolver_context: the optional resolver context (instance of
                        resolver.Context). The default is None which will use
                        the built in context which is not multi process safe.
    """
    super(SourceScanner, self).__init__()
    self._resolver_context = resolver_context

  # TODO: add functions to check if path spec type is an Image type,
  # FS type, etc.

  def _ScanNode(
      self, scan_context, scan_node, auto_recurse=True, next_layer_input=True):
    """Scans for supported formats using a scan node.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      scan_node: the scan node (instance of SourceScanNode).
      auto_recurse: optional boolean value to indicate if the scan should
                    automatically recurse as far as possible. The default
                    is False.
      next_layer_input: optional boolean value to indicate if the scan should
                        return if it needs input about the next layer. The
                        default is True.

    Returns:
      The updated source scanner context (instance of SourceScannerContext).

    Raises:
      BackEndError: if the source cannot be scanned.
      ValueError: if the scan context is invalid.
    """
    if not scan_context:
      raise ValueError(u'Invalid scan context.')

    scan_context.updated = False

    if not scan_node:
      scan_context.last_scan_node = None
      return scan_context

    if not scan_node.IsSystemLevel():
      system_level_file_entry = None

    else:
      system_level_file_entry = resolver.Resolver.OpenFileEntry(
          scan_node.path_spec, resolver_context=self._resolver_context)

      if system_level_file_entry is None:
        raise errors.BackEndError(u'Unable to open file entry.')

      if system_level_file_entry.IsDirectory():
        scan_context.SetSourceType(
            scan_context.SOURCE_TYPE_DIRECTORY)
        return scan_context

      source_path_spec = self.ScanForStorageMediaImage(scan_node.path_spec)
      if source_path_spec:
        scan_node = scan_context.AddScanNode(source_path_spec, scan_node)

        scan_context.SetSourceType(
            scan_context.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

        if not auto_recurse:
          return scan_context

    # In case we did not find a storage media image type we keep looking
    # since not all RAW storage media image naming schemas are known and
    # its type can only detected by its content.

    source_path_spec = None
    while True:
      last_source_path_spec = source_path_spec
      source_path_spec = self.ScanForVolumeSystem(scan_node.path_spec)
      if not source_path_spec:
        break

      if last_source_path_spec and last_source_path_spec == source_path_spec:
        break

      if not scan_context.HasScanNode(source_path_spec):
        scan_node = scan_context.AddScanNode(source_path_spec, scan_node)

        if system_level_file_entry and system_level_file_entry.IsDevice():
          scan_context.SetSourceType(
              scan_context.SOURCE_TYPE_STORAGE_MEDIA_DEVICE)
        else:
          scan_context.SetSourceType(
              scan_context.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

      if scan_node.type_indicator in definitions.VOLUME_SYSTEM_TYPE_INDICATORS:
        if getattr(scan_node.path_spec, u'location', None) == u'/':
          file_system_scan_node = None
        else:
          file_system_scan_node = scan_node

        # For VSS add a scan node for the current volume.
        if scan_node.type_indicator == definitions.TYPE_INDICATOR_VSHADOW:
          path_spec = self.ScanForFileSystem(scan_node.path_spec.parent)
          if path_spec:
            if not scan_context.HasScanNode(path_spec):
              file_system_scan_node = scan_context.AddScanNode(
                  path_spec, scan_node)
              scan_context.file_system_found = True
            else:
              file_system_scan_node = scan_context.GetScanNode(path_spec)

        # Determine the path specifications of the sub file entries.
        file_entry = resolver.Resolver.OpenFileEntry(
            scan_node.path_spec, resolver_context=self._resolver_context)

        for sub_file_entry in file_entry.sub_file_entries:
          if not scan_context.HasScanNode(sub_file_entry.path_spec):
            sub_scan_node = scan_context.AddScanNode(
                sub_file_entry.path_spec, scan_node)
          else:
            sub_scan_node = scan_context.GetScanNode(sub_file_entry.path_spec)

          # Since this can be expensive and not always needed we do not scan
          # VSS snapshot volumes by default.
          if scan_node.type_indicator != definitions.TYPE_INDICATOR_VSHADOW:
            if auto_recurse or not scan_context.updated:
              scan_context = self._ScanNode(
                  scan_context, sub_scan_node, auto_recurse=auto_recurse,
                  next_layer_input=next_layer_input)

        if scan_node.type_indicator == definitions.TYPE_INDICATOR_VSHADOW:
          minimum_sub_file_entries = 0
        else:
          minimum_sub_file_entries = 1

        # If there are more than sub file entry than the minumum we need more
        # information to determine the next layer.
        if file_entry.number_of_sub_file_entries > minimum_sub_file_entries:
          if next_layer_input:
            scan_context.last_scan_node = scan_node
            return scan_context

        if file_entry.number_of_sub_file_entries == 0:
          scan_context.last_scan_node = file_system_scan_node
          if scan_node.type_indicator == definitions.TYPE_INDICATOR_VSHADOW:
            # In case we detected a VSS without snapshots we already have
            # scanned for the file system.
            return scan_context
          break

      elif scan_node.type_indicator in (
          definitions.ENCRYPTED_VOLUME_TYPE_INDICATORS):
        file_object = resolver.Resolver.OpenFileObject(
            scan_node.path_spec, resolver_context=self._resolver_context)

        # If the encrypted volume could not be opened we need more information
        # to determine the next layer.
        if not file_object or file_object.is_locked:
          file_object.close()
          return scan_context

        file_object.close()

        # For BDE to go add a scan node for the unlock volume.
        if scan_node.type_indicator == definitions.TYPE_INDICATOR_BDE:
          path_spec = self.ScanForFileSystem(scan_node.path_spec.parent)
          if path_spec:
            if not scan_context.HasScanNode(path_spec):
              _ = scan_context.AddScanNode(path_spec, scan_node)

      if not auto_recurse and scan_context.updated:
        return scan_context

      if not scan_context.updated:
        return scan_context

    # Do not scan the root of a volume system for a file system.
    if scan_node.path_spec.type_indicator in (
        definitions.VOLUME_SYSTEM_TYPE_INDICATORS):
      if getattr(scan_node.path_spec, u'location', None) == u'/':
        return scan_context

    # In case we did not find a volume system type we keep looking
    # since we could be dealing with a storage media image that contains
    # a single volume.

    source_path_spec = self.ScanForFileSystem(scan_node.path_spec)
    if not source_path_spec:
      # Since RAW storage media image can only be determined by naming schema
      # we could have single file that is not a RAW storage media image yet
      # matches the naming schema.
      if scan_node.path_spec.type_indicator == definitions.TYPE_INDICATOR_RAW:
        scan_node = scan_context.RemoveScanNode(scan_node.path_spec)

        # Make sure to override the previously assigned source type.
        scan_context.source_type = scan_context.SOURCE_TYPE_FILE
      else:
        scan_context.SetSourceType(scan_context.SOURCE_TYPE_FILE)

    elif not scan_context.HasScanNode(source_path_spec):
      scan_node = scan_context.AddScanNode(source_path_spec, scan_node)

      if system_level_file_entry and system_level_file_entry.IsDevice():
        scan_context.SetSourceType(
            scan_context.SOURCE_TYPE_STORAGE_MEDIA_DEVICE)
      else:
        scan_context.SetSourceType(
            scan_context.SOURCE_TYPE_STORAGE_MEDIA_IMAGE)

      scan_context.file_system_found = True

    elif next_layer_input:
      scan_context.last_scan_node = scan_context.GetScanNode(source_path_spec)

    return scan_context

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

  def Scan(
      self, scan_context, auto_recurse=True, next_layer_input=True,
      scan_path_spec=None):
    """Scans for supported formats.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      auto_recurse: optional boolean value to indicate if the scan should
                    automatically recurse as far as possible. The default
                    is False.
      next_layer_input: optional boolean value to indicate if the scan should
                        return if it needs input about the next layer. The
                        default is True.
      scan_path_spec: optional path specification (instance of path.PathSpec)
                      to indicate where the source scanner should continue
                      scanning. The default is None which indicates the
                      scanner will start with the sources.

    Returns:
      The updated source scanner context (instance of SourceScannerContext).

    Raises:
      BackEndError: if the source cannot be scanned.
    """
    # TODO: add support to scan multiple sources.

    if not scan_path_spec:
      scan_node = scan_context.last_scan_node

    else:
      scan_node = scan_context.GetScanNode(scan_path_spec)

    return self._ScanNode(
        scan_context, scan_node, auto_recurse=auto_recurse,
        next_layer_input=next_layer_input)

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

    if len(type_indicators) > 1:
      raise errors.BackEndError(
          u'Unsupported source found more than one file system types.')

    return path_spec_factory.Factory.NewPathSpec(
        type_indicators[0], location=u'/', parent=source_path_spec)

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

    # Check if we already have a volume system path specification.
    if source_path_spec.type_indicator in (
        definitions.VOLUME_SYSTEM_TYPE_INDICATORS):
      if getattr(source_path_spec, u'location', None) == u'/':
        return source_path_spec

    try:
      type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
          source_path_spec, resolver_context=self._resolver_context)
    except RuntimeError as exception:
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

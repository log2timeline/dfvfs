# -*- coding: utf-8 -*-
"""The format analyzer."""

from __future__ import unicode_literals

import pysigscan

from dfvfs.analyzer import specification
from dfvfs.lib import definitions
from dfvfs.resolver import resolver


class Analyzer(object):
  """Format analyzer."""

  _SCAN_BUFFER_SIZE = 33 * 1024

  _analyzer_helpers = {}

  # The archive format category analyzer helpers that do not have
  # a format specification.
  _archive_remainder_list = None

  # The archive format category signature scanner.
  _archive_scanner = None

  # The archive format category specification store.
  _archive_store = None

  # The compressed stream format category analyzer helpers that do not have
  # a format specification.
  _compressed_stream_remainder_list = None

  # The compressed stream format category signature scanner.
  _compressed_stream_scanner = None

  # The compressed stream format category specification store.
  _compressed_stream_store = None

  # The file system format category analyzer helpers that do not have
  # a format specification.
  _file_system_remainder_list = None

  # The file system format category signature scanner.
  _file_system_scanner = None

  # The file system format category specification store.
  _file_system_store = None

  # The storage media image format category analyzer helpers that do not have
  # a format specification.
  _storage_media_image_remainder_list = None

  # The storage media image format category signature scanner.
  _storage_media_image_scanner = None

  # The storage media image format category specification store.
  _storage_media_image_store = None

  # The volume system format category analyzer helpers that do not have
  # a format specification.
  _volume_system_remainder_list = None

  # The volume system format category signature scanner.
  _volume_system_scanner = None

  # The volume system format category specification store.
  _volume_system_store = None

  @classmethod
  def _FlushCache(cls, format_categories):
    """Flushes the cached objects for the specified format categories.

    Args:
      format_categories (set[str]): format categories.
    """
    if definitions.FORMAT_CATEGORY_ARCHIVE in format_categories:
      cls._archive_remainder_list = None
      cls._archive_scanner = None
      cls._archive_store = None

    if definitions.FORMAT_CATEGORY_COMPRESSED_STREAM in format_categories:
      cls._compressed_stream_remainder_list = None
      cls._compressed_stream_scanner = None
      cls._compressed_stream_store = None

    if definitions.FORMAT_CATEGORY_FILE_SYSTEM in format_categories:
      cls._file_system_remainder_list = None
      cls._file_system_scanner = None
      cls._file_system_store = None

    if definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE in format_categories:
      cls._storage_media_image_remainder_list = None
      cls._storage_media_image_scanner = None
      cls._storage_media_image_store = None

    if definitions.FORMAT_CATEGORY_VOLUME_SYSTEM in format_categories:
      cls._volume_system_remainder_list = None
      cls._volume_system_scanner = None
      cls._volume_system_store = None

  @classmethod
  def _GetSignatureScanner(cls, specification_store):
    """Initializes a signature scanner based on a specification store.

    Args:
      specification_store (FormatSpecificationStore): specification store.

    Returns:
      pysigscan.scanner: signature scanner.
    """
    signature_scanner = pysigscan.scanner()
    signature_scanner.set_scan_buffer_size(cls._SCAN_BUFFER_SIZE)

    for format_specification in specification_store.specifications:
      for signature in format_specification.signatures:
        pattern_offset = signature.offset

        if pattern_offset is None:
          signature_flags = pysigscan.signature_flags.NO_OFFSET
        elif pattern_offset < 0:
          pattern_offset *= -1
          signature_flags = pysigscan.signature_flags.RELATIVE_FROM_END
        else:
          signature_flags = pysigscan.signature_flags.RELATIVE_FROM_START

        signature_scanner.add_signature(
            signature.identifier, pattern_offset, signature.pattern,
            signature_flags)

    return signature_scanner

  @classmethod
  def _GetSpecificationStore(cls, format_category):
    """Retrieves the specification store for specified format category.

    Args:
      format_category (str): format category.

    Returns:
      tuple[FormatSpecificationStore, list[AnalyzerHelper]]: a format
          specification store and remaining analyzer helpers that do not have
          a format specification.
    """
    specification_store = specification.FormatSpecificationStore()
    remainder_list = []

    for analyzer_helper in cls._analyzer_helpers.values():
      if not analyzer_helper.IsEnabled():
        continue

      if format_category in analyzer_helper.format_categories:
        format_specification = analyzer_helper.GetFormatSpecification()

        if format_specification is not None:
          specification_store.AddSpecification(format_specification)
        else:
          remainder_list.append(analyzer_helper)

    return specification_store, remainder_list

  @classmethod
  def _GetTypeIndicators(
      cls, signature_scanner, specification_store, remainder_list, path_spec,
      resolver_context=None):
    """Determines if a file contains a supported format types.

    Args:
      signature_scanner (pysigscan.scanner): signature scanner.
      specification_store (FormatSpecificationStore): specification store.
      remainder_list (list[AnalyzerHelper]): remaining analyzer helpers that
          do not have a format specification.
      path_spec (PathSpec): path specification.
      resolver_context (Optional[Context]): resolver context, where None
          represents the built-in context which is not multi process safe.

    Returns:
      list[str]: supported format type indicators.
    """
    type_indicator_list = []

    file_object = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=resolver_context)
    scan_state = pysigscan.scan_state()

    try:
      signature_scanner.scan_file_object(scan_state, file_object)

      for scan_result in iter(scan_state.scan_results):
        format_specification = specification_store.GetSpecificationBySignature(
            scan_result.identifier)

        if format_specification.identifier not in type_indicator_list:
          type_indicator_list.append(format_specification.identifier)

      for analyzer_helper in remainder_list:
        result = analyzer_helper.AnalyzeFileObject(file_object)

        if result is not None:
          type_indicator_list.append(result)

    finally:
      file_object.close()

    return type_indicator_list

  @classmethod
  def DeregisterHelper(cls, analyzer_helper):
    """Deregisters a format analyzer helper.

    Args:
      analyzer_helper (AnalyzerHelper): analyzer helper.

    Raises:
      KeyError: if analyzer helper object is not set for the corresponding
          type indicator.
    """
    if analyzer_helper.type_indicator not in cls._analyzer_helpers:
      raise KeyError(
          'Analyzer helper object not set for type indicator: {0:s}.'.format(
              analyzer_helper.type_indicator))

    analyzer_helper = cls._analyzer_helpers[analyzer_helper.type_indicator]

    cls._FlushCache(analyzer_helper.format_categories)

    del cls._analyzer_helpers[analyzer_helper.type_indicator]

  @classmethod
  def GetArchiveTypeIndicators(cls, path_spec, resolver_context=None):
    """Determines if a file contains a supported archive types.

    Args:
      path_spec (PathSpec): path specification.
      resolver_context (Optional[Context]): resolver context, where None
          represents the built-in context which is not multi process safe.

    Returns:
      list[str]: supported format type indicators.
    """
    if (cls._archive_remainder_list is None or
        cls._archive_store is None):
      specification_store, remainder_list = cls._GetSpecificationStore(
          definitions.FORMAT_CATEGORY_ARCHIVE)
      cls._archive_remainder_list = remainder_list
      cls._archive_store = specification_store

    if cls._archive_scanner is None:
      cls._archive_scanner = cls._GetSignatureScanner(cls._archive_store)

    return cls._GetTypeIndicators(
        cls._archive_scanner, cls._archive_store,
        cls._archive_remainder_list, path_spec,
        resolver_context=resolver_context)

  @classmethod
  def GetCompressedStreamTypeIndicators(cls, path_spec, resolver_context=None):
    """Determines if a file contains a supported compressed stream types.

    Args:
      path_spec (PathSpec): path specification.
      resolver_context (Optional[Context]): resolver context, where None
          represents the built-in context which is not multi process safe.

    Returns:
      list[str]: supported format type indicators.
    """
    if (cls._compressed_stream_remainder_list is None or
        cls._compressed_stream_store is None):
      specification_store, remainder_list = cls._GetSpecificationStore(
          definitions.FORMAT_CATEGORY_COMPRESSED_STREAM)
      cls._compressed_stream_remainder_list = remainder_list
      cls._compressed_stream_store = specification_store

    if cls._compressed_stream_scanner is None:
      cls._compressed_stream_scanner = cls._GetSignatureScanner(
          cls._compressed_stream_store)

    return cls._GetTypeIndicators(
        cls._compressed_stream_scanner, cls._compressed_stream_store,
        cls._compressed_stream_remainder_list, path_spec,
        resolver_context=resolver_context)

  @classmethod
  def GetFileSystemTypeIndicators(cls, path_spec, resolver_context=None):
    """Determines if a file contains a supported file system types.

    Args:
      path_spec (PathSpec): path specification.
      resolver_context (Optional[Context]): resolver context, where None
          represents the built-in context which is not multi process safe.

    Returns:
      list[str]: supported format type indicators.
    """
    if (cls._file_system_remainder_list is None or
        cls._file_system_store is None):
      specification_store, remainder_list = cls._GetSpecificationStore(
          definitions.FORMAT_CATEGORY_FILE_SYSTEM)
      cls._file_system_remainder_list = remainder_list
      cls._file_system_store = specification_store

    if cls._file_system_scanner is None:
      cls._file_system_scanner = cls._GetSignatureScanner(
          cls._file_system_store)

    return cls._GetTypeIndicators(
        cls._file_system_scanner, cls._file_system_store,
        cls._file_system_remainder_list, path_spec,
        resolver_context=resolver_context)

  @classmethod
  def GetStorageMediaImageTypeIndicators(cls, path_spec, resolver_context=None):
    """Determines if a file contains a supported storage media image types.

    Args:
      path_spec (PathSpec): path specification.
      resolver_context (Optional[Context]): resolver context, where None
          represents the built-in context which is not multi process safe.

    Returns:
      list[str]: supported format type indicators.
    """
    if (cls._storage_media_image_remainder_list is None or
        cls._storage_media_image_store is None):
      specification_store, remainder_list = cls._GetSpecificationStore(
          definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE)
      cls._storage_media_image_remainder_list = remainder_list
      cls._storage_media_image_store = specification_store

    if cls._storage_media_image_scanner is None:
      cls._storage_media_image_scanner = cls._GetSignatureScanner(
          cls._storage_media_image_store)

    return cls._GetTypeIndicators(
        cls._storage_media_image_scanner, cls._storage_media_image_store,
        cls._storage_media_image_remainder_list, path_spec,
        resolver_context=resolver_context)

  @classmethod
  def GetVolumeSystemTypeIndicators(cls, path_spec, resolver_context=None):
    """Determines if a file contains a supported volume system types.

    Args:
      path_spec (PathSpec): path specification.
      resolver_context (Optional[Context]): resolver context, where None
          represents the built-in context which is not multi process safe.

    Returns:
      list[str]: supported format type indicators.
    """
    if (cls._volume_system_remainder_list is None or
        cls._volume_system_store is None):
      specification_store, remainder_list = cls._GetSpecificationStore(
          definitions.FORMAT_CATEGORY_VOLUME_SYSTEM)
      cls._volume_system_remainder_list = remainder_list
      cls._volume_system_store = specification_store

    if cls._volume_system_scanner is None:
      cls._volume_system_scanner = cls._GetSignatureScanner(
          cls._volume_system_store)

    return cls._GetTypeIndicators(
        cls._volume_system_scanner, cls._volume_system_store,
        cls._volume_system_remainder_list, path_spec,
        resolver_context=resolver_context)

  @classmethod
  def RegisterHelper(cls, analyzer_helper):
    """Registers a format analyzer helper.

    Args:
      analyzer_helper (AnalyzerHelper): analyzer helper.

    Raises:
      KeyError: if analyzer helper object is already set for the corresponding
          type indicator.
    """
    if analyzer_helper.type_indicator in cls._analyzer_helpers:
      raise KeyError((
          'Analyzer helper object already set for type indicator: '
          '{0:s}.').format(analyzer_helper.type_indicator))

    cls._FlushCache(analyzer_helper.format_categories)

    cls._analyzer_helpers[analyzer_helper.type_indicator] = analyzer_helper

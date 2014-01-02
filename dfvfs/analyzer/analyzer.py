#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The dfVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The Virtual File System (VFS) format analyzer object."""

from dfvfs.analyzer import scanner
from dfvfs.analyzer import specification
from dfvfs.lib import definitions
from dfvfs.resolver import resolver


class Analyzer(object):
  """Class that implements the VFS format analyzer."""

  _analyzer_helpers = {}

  # The file system format category analyzer helpers that do not have
  # a format specification.
  _file_system_remainder_list = None

  # The file system format category format scanner.
  _file_system_scanner = None

  # The file system format category specification store.
  _file_system_store = None

  # The storage media image format category analyzer helpers that do not have
  # a format specification.
  _storage_media_image_remainder_list = None

  # The storage media image format category format scanner.
  _storage_media_image_scanner = None

  # The storage media image format category specification store.
  _storage_media_image_store = None

  # The volume system format category analyzer helpers that do not have
  # a format specification.
  _volume_system_remainder_list = None

  # The volume system format category format scanner.
  _volume_system_scanner = None

  # The volume system format category specification store.
  _volume_system_store = None

  @classmethod
  def _GetSpecificationStore(cls, format_category):
    """Retrieves the specification store for specified format category.

    Args:
      format_category: the format category.

    Returns:
      A tuple of a format specification store (instance of SpecificationStore)
      and the list of remaining analyzer helpers that do not have a format
      specification.
    """
    specification_store = specification.SpecificationStore()
    remainder_list = []

    for analyzer_helper in cls._analyzer_helpers.itervalues():
      if format_category in analyzer_helper.format_categories:
        format_specification = analyzer_helper.GetFormatSpecification()

        if format_specification is not None:
          specification_store.AddSpecification(format_specification)
        else:
          remainder_list.append(analyzer_helper)

    return specification_store, remainder_list

  @classmethod
  def _GetTypeIndicators(cls, scanner_object, remainder_list, path_spec):
    """Determines if a file contains a supported format types.

    Args:
      scanner_object: the format scanner (instance of OffsetBoundScanner).
      remainder_list: list of remaining analyzer helpers that do not have
                      a format specification.
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      A list of supported format type indicator.
    """
    type_indicator_list = []

    file_object = resolver.Resolver.OpenFileObject(path_spec)
    scan_results = scanner_object.ScanFileObject(file_object)

    for scan_result in scan_results:
      type_indicator_list.append(scan_result.identifier)

    for analyzer_helper in remainder_list:
      result = analyzer_helper.AnalyzeFileObject(file_object)

      if result is not None:
        type_indicator_list.append(result)

    return type_indicator_list

  @classmethod
  def _FlushCache(cls, format_categories):
    """Flushes the cached objects for the specified format categories.

    Args:
      format_categories: a list of format categories.
    """
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
  def GetFileSystemTypeIndicators(cls, path_spec):
    """Determines if a file contains a supported file system types.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      A list of supported format type indicator.
    """
    if (cls._file_system_remainder_list is None or
        cls._file_system_store is None):
      specification_store, remainder_list = cls._GetSpecificationStore(
          definitions.FORMAT_CATEGORY_FILE_SYSTEM)
      cls._file_system_remainder_list = remainder_list
      cls._file_system_store = specification_store

    if cls._file_system_scanner is None:
      cls._file_system_scanner = scanner.OffsetBoundScanner(
          cls._file_system_store)

    return cls._GetTypeIndicators(
        cls._file_system_scanner, cls._file_system_remainder_list,
        path_spec)

  @classmethod
  def GetStorageMediaImageTypeIndicators(cls, path_spec):
    """Determines if a file contains a supported storage media image types.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      A list of supported format type indicator.
    """
    if (cls._storage_media_image_remainder_list is None or
        cls._storage_media_image_store is None):
      specification_store, remainder_list = cls._GetSpecificationStore(
          definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE)
      cls._storage_media_image_remainder_list = remainder_list
      cls._storage_media_image_store = specification_store

    if cls._storage_media_image_scanner is None:
      cls._storage_media_image_scanner = scanner.OffsetBoundScanner(
          cls._storage_media_image_store)

    return cls._GetTypeIndicators(
        cls._storage_media_image_scanner,
        cls._storage_media_image_remainder_list, path_spec)

  @classmethod
  def GetVolumeSystemTypeIndicators(cls, path_spec):
    """Determines if a file contains a supported volume system types.

    Args:
      path_spec: the VFS path specification (instance of path.PathSpec).

    Returns:
      A list of supported format type indicator.
    """
    if (cls._volume_system_remainder_list is None or
        cls._volume_system_store is None):
      specification_store, remainder_list = cls._GetSpecificationStore(
          definitions.FORMAT_CATEGORY_VOLUME_SYSTEM)
      cls._volume_system_remainder_list = remainder_list
      cls._volume_system_store = specification_store

    if cls._volume_system_scanner is None:
      cls._volume_system_scanner = scanner.OffsetBoundScanner(
          cls._volume_system_store)

    return cls._GetTypeIndicators(
        cls._volume_system_scanner, cls._volume_system_remainder_list,
        path_spec)

  @classmethod
  def DeregisterHelper(cls, analyzer_helper):
    """Deregisters a format analyzer helper.

    Args:
      analyzer_helper: the analyzer helper object (instance of
                       analyzer.AnalyzerHelper).

    Raises:
      KeyError: if analyzer helper object is not set for the corresponding
                type indicator.
    """
    if analyzer_helper.type_indicator not in cls._analyzer_helpers:
      raise KeyError((
          u'Analyzer helper object not set for type indicator: {0:s}.').format(
              analyzer_helper.type_indicator))

    analyzer_helper = cls._analyzer_helpers[analyzer_helper.type_indicator]

    cls._FlushCache(analyzer_helper.format_categories)

    del cls._analyzer_helpers[analyzer_helper.type_indicator]

  @classmethod
  def RegisterHelper(cls, analyzer_helper):
    """Registers a format analyzer helper.

    Args:
      analyzer_helper: the analyzer helper object (instance of
                       analyzer.AnalyzerHelper).

    Raises:
      KeyError: if analyzer helper object is already set for the corresponding
                type indicator.
    """
    if analyzer_helper.type_indicator in cls._analyzer_helpers:
      raise KeyError((
          u'Analyzer helper object already set for type indicator: '
          u'{0:s}.').format(analyzer_helper.type_indicator))

    cls._FlushCache(analyzer_helper.format_categories)

    cls._analyzer_helpers[analyzer_helper.type_indicator] = analyzer_helper

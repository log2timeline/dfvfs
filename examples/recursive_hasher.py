#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The dfVFS Project Authors.
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
"""Script to recursively calculate a message digest hash for every file."""

# If you update this script make sure to update the corresponding wiki page
# as well: https://github.com/log2timeline/dfvfs/wiki/Development

import argparse
import hashlib
import logging
import os
import stat
import sys

from dfvfs.analyzer import analyzer
from dfvfs.lib import definitions
from dfvfs.lib import raw
from dfvfs.path import factory as path_spec_factory
from dfvfs.resolver import resolver
from dfvfs.volume import tsk_volume_system


class RecursiveHasher(object):
  """Class that recursively calculates message digest hashes of files."""

  # Class constant that defines the default read buffer size.
  _READ_BUFFER_SIZE = 32768

  def _CalculateHashFileEntry(self, file_entry):
    """Calculates a message digest hash of the data of the file entry.

    Args:
      file_entry: the file entry (instance of dfvfs.FileEntry).
    """
    hash_context = hashlib.md5()
    file_object = file_entry.GetFileObject()

    data = file_object.read(self._READ_BUFFER_SIZE)
    while data:
      hash_context.update(data)
      data = file_object.read(self._READ_BUFFER_SIZE)

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
    if file_entry.IsFile():
      hash_value = self._CalculateHashFileEntry(file_entry)
      output_writer.WriteFileHash(full_path, hash_value)

    for sub_file_entry in file_entry.sub_file_entries:
      self._CalculateHashesFileEntry(
          file_system, sub_file_entry, full_path, output_writer)

  def _GetNextLevelTSKPartionVolumeSystemPathSpec(self, source_path_spec):
    """Determines the next level volume system path specification.

    Args:
      source_path_spec: the source path specification (instance of
                        dfvfs.PathSpec).

    Returns:
      The next level volume system path specification (instance of
      dfvfs.PathSpec).

    Raises:
      RuntimeError: if the format of or within the source is not supported.
    """
    volume_system_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location=u'/',
        parent=source_path_spec)

    volume_system = tsk_volume_system.TSKVolumeSystem()
    volume_system.Open(volume_system_path_spec)

    volume_identifiers = []
    for volume in volume_system.volumes:
      volume_identifier = getattr(volume, 'identifier', None)
      if volume_identifier:
        volume_identifiers.append(volume_identifier)

    if not volume_identifiers:
      logging.warning(u'No supported partitions found.')
      return source_path_spec

    if len(volume_identifiers) == 1:
      return path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_TSK_PARTITION, location=u'/p1',
          parent=source_path_spec)

    print u'The following partitions were found:'
    print u'Identifier\tOffset\t\tSize'
    for volume in volume_system.volumes:
      if hasattr(volume, 'identifier'):
        volume_extent = volume.extents[0]
        print u'{0:s}\t\t0x{1:08x}\t{2:d}'.format(
            volume.identifier, volume_extent.offset, volume_extent.size)

    print u''

    while True:
      print (
          u'Please specify the identifier of the partition that should '
          u'be processed:')

      selected_volume_identifier = sys.stdin.readline()
      selected_volume_identifier = selected_volume_identifier.strip()

      if selected_volume_identifier in volume_identifiers:
        break

      print u''
      print (
          u'Unsupported partition identifier, please try again or abort '
          u'with Ctrl^C.')
      print u''

    location = u'/{0:s}'.format(selected_volume_identifier)

    return path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, location=location,
        parent=source_path_spec)

  def _GetNextLevelVshadowVolumeSystemPathSpec(self, source_path_spec):
    """Determines the next level volume system path specification.

    Args:
      source_path_spec: the source path specification (instance of
                        dfvfs.PathSpec).

    Returns:
      The next level volume system path specification (instance of
      dfvfs.PathSpec).

    Raises:
      RuntimeError: if the format of or within the source is not supported.
    """
    # TODO: implement.
    return source_path_spec

  def _GetUpperLevelVolumeSystemPathSpec(self, source_path_spec):
    """Determines the upper level volume system path specification.

    Args:
      source_path_spec: the source path specification (instance of
                        dfvfs.PathSpec).

    Returns:
      The upper level volume system path specification (instance of
      dfvfs.PathSpec).

    Raises:
      RuntimeError: if the format of or within the source is not supported.
    """
    type_indicators = analyzer.Analyzer.GetVolumeSystemTypeIndicators(
        source_path_spec)

    if not type_indicators:
      # No supported volume system found, we are at the upper level.
      return source_path_spec

    if len(type_indicators) > 1:
      raise RuntimeError(
          u'Unsupported source found more than one volume system types.')

    if type_indicators[0] == definitions.TYPE_INDICATOR_TSK_PARTITION:
      path_spec = self._GetNextLevelTSKPartionVolumeSystemPathSpec(
          source_path_spec)

    elif type_indicators[0] == definitions.TYPE_INDICATOR_VSHADOW:
      path_spec = self._GetNextLevelVshadowVolumeSystemPathSpec(
          source_path_spec)

    else:
      raise RuntimeError((
          u'Unsupported source found unsupported volume system '
          u'type: {0:s}.').format(type_indicators[0]))

    return path_spec

  def CalculateHashes(self, base_path_spec, output_writer):
    """Recursive calculates hashes starting with the base path specification.

    Args:
      base_path_spec: the base path specification (instance of dfvfs.PathSpec).
      output_writer: the output writer (instance of StdoutWriter).
    """
    file_system = resolver.Resolver.OpenFileSystem(base_path_spec)
    file_entry = resolver.Resolver.OpenFileEntry(base_path_spec)
    if file_entry is None:
      logging.warning(
          u'Unable to open base path specification:\n{0:s}'.format(
              base_path_spec.comparable))
      return

    self._CalculateHashesFileEntry(file_system, file_entry, u'', output_writer)

  def GetBasePathSpec(self, source_path):
    """Determines the base path specification.

    Args:
      source_path: the source path.

    Returns:
      The base path specification (instance of dfvfs.PathSpec).

    Raises:
      RuntimeError: if the source path does not exists, or if the source path
                    is not a file or directory, or if the format of or within
                    the source file is not supported.
    """
    if not os.path.exists(source_path):
      raise RuntimeError(u'No such source: {0:s}.'.format(source_path))

    stat_info = os.stat(source_path)

    if (not stat.S_ISDIR(stat_info.st_mode) and
        not stat.S_ISREG(stat_info.st_mode)):
      raise RuntimeError(
          u'Unsupported source: {0:s} not a file or directory.'.format(
              source_path))

    if stat.S_ISDIR(stat_info.st_mode):
      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_OS, location=source_path)

    elif stat.S_ISREG(stat_info.st_mode):
      path_spec = path_spec_factory.Factory.NewPathSpec(
          definitions.TYPE_INDICATOR_OS, location=source_path)

      type_indicators = analyzer.Analyzer.GetStorageMediaImageTypeIndicators(
          path_spec)

      if len(type_indicators) > 1:
        raise RuntimeError((
            u'Unsupported source: {0:s} found more than one storage media '
            u'image types.').format(source_path))

      if len(type_indicators) == 1:
        path_spec = path_spec_factory.Factory.NewPathSpec(
            type_indicators[0], parent=path_spec)

      if not type_indicators:
        # The RAW storage media image type cannot be detected based on
        # a signature so we try to detect it based on common file naming
        # schemas.
        file_system = resolver.Resolver.OpenFileSystem(path_spec)
        raw_path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_RAW, parent=path_spec)

        glob_results = raw.RawGlobPathSpec(file_system, raw_path_spec)
        if glob_results:
          path_spec = raw_path_spec

      # In case we did not find a storage media image type we keep looking
      # since not all RAW storage media image naming schemas are known and
      # its type can only detected by its content.

      path_spec = self._GetUpperLevelVolumeSystemPathSpec(path_spec)

      # In case we did not find a volume system type we keep looking
      # since we could be dealing with a store media image that contains
      # a single volume.

      type_indicators = analyzer.Analyzer.GetFileSystemTypeIndicators(
          path_spec)

      if len(type_indicators) > 1:
        raise RuntimeError((
            u'Unsupported source: {0:s} found more than one file system '
            u'types.').format(source_path))

      if not type_indicators:
        logging.warning((
          u'Unable to find a supported file system, calculating digest hash '
          u'of file: {0:s} instead.').format(source_path))
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_OS, location=source_path)

      elif type_indicators[0] != definitions.TYPE_INDICATOR_TSK:
        raise RuntimeError((
            u'Unsupported source: {0:s} found unsupported file system '
            u'type: {1:s}.').format(source_path, type_indicators[0]))

      else:
        path_spec = path_spec_factory.Factory.NewPathSpec(
            definitions.TYPE_INDICATOR_TSK, location=u'/',
            parent=path_spec)

    return path_spec


class StdoutWriter(object):
  """Class that defines a stdout output writer."""

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
    print u'{0:s}\t{1:s}'.format(hash_value, path)


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  args_parser = argparse.ArgumentParser(description=(
      'Calculates a message digest hash for every file in a directory or '
      'storage media image.'))

  args_parser.add_argument(
      'source', nargs='?', action='store', metavar='image.raw',
      default=None, help=('path of the directory or filename of a storage '
                          'media image containing the file.'))

  options = args_parser.parse_args()

  if not options.source:
    print u'Source value is missing.'
    print u''
    args_parser.print_help()
    print u''
    return False

  logging.basicConfig(
      level=logging.INFO, format=u'[%(levelname)s] %(message)s')

  output_writer = StdoutWriter()

  if not output_writer.Open():
    print u'Unable to open output writer.'
    print u''
    return False

  return_value = True
  recursive_hasher = RecursiveHasher()

  try:
    base_path_spec = recursive_hasher.GetBasePathSpec(options.source)

    recursive_hasher.CalculateHashes(base_path_spec, output_writer)

    print u''
    print u'Completed.'

  except KeyboardInterrupt:
    return_value = False

    print u''
    print u'Aborted by user.'

  output_writer.Close()

  return return_value


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)

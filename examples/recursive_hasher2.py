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
# as well: https://code.google.com/p/dfvfs/wiki/dfvfs

import argparse
import hashlib
import logging
import os
import sys

from dfvfs.helpers import source_scanner
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.resolver import resolver
from dfvfs.volume import tsk_volume_system
from dfvfs.volume import vshadow_volume_system


class RecursiveHasher(object):
  """Class that recursively calculates message digest hashes of files."""

  # Class constant that defines the default read buffer size.
  _READ_BUFFER_SIZE = 32768

  def __init__(self):
    """Initializes the recursive hasher object."""
    super(RecursiveHasher, self).__init__()
    self._scanner = source_scanner.SourceScanner()

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

  def _GetNextLevelTSKPartionVolumeSystemPathSpec(self, scan_context):
    """Determines the next level volume system path specification.

    Args:
      scan_context: the scan context (instance of source_scanner.ScanContext).

    Returns:
      The next level volume system path specification (instance of
      dfvfs.PathSpec) or None.

    Raises:
      RuntimeError: if the scan context is invalid.
    """
    if (not scan_context or not scan_context.last_scan_node or
        not scan_context.last_scan_node.path_spec):
      raise RuntimeError(u'Invalid scan context.')

    volume_system = tsk_volume_system.TSKVolumeSystem()
    volume_system.Open(scan_context.last_scan_node.path_spec)

    volume_identifiers = self._scanner.GetVolumeIdentifiers(volume_system)

    if not volume_identifiers:
      logging.warning(u'No supported partitions found.')
      return

    if len(volume_identifiers) == 1:
      selected_volume_identifier = u'p1'

    else:
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

    # We need to return the path specification as defined by the scan node.
    selected_location = u'/{0:s}'.format(selected_volume_identifier)
    scan_sub_node = scan_context.last_scan_node.GetSubNodeByLocation(
        selected_location)
    return getattr(scan_sub_node, 'path_spec', None)

  def _GetNextLevelVshadowVolumeSystemPathSpec(self, scan_context):
    """Determines the next level volume system path specification.

    Args:
      scan_context: the scan context (instance of source_scanner.ScanContext).

    Returns:
      The next level volume system path specification (instance of
      dfvfs.PathSpec) or None.

    Raises:
      RuntimeError: if the scan context is invalid.
    """
    if (not scan_context or not scan_context.last_scan_node or
        not scan_context.last_scan_node.path_spec):
      raise RuntimeError(u'Invalid scan context.')

    volume_system = vshadow_volume_system.VShadowVolumeSystem()
    volume_system.Open(scan_context.last_scan_node.path_spec)

    volume_identifiers = self._scanner.GetVolumeIdentifiers(volume_system)

    if not volume_identifiers:
      return

    print u'The following Volume Shadow Snapshots (VSS) were found:'
    print u'Identifier\tVSS store identifier'

    for volume_identifier in volume_identifiers:
      volume = volume_system.GetVolumeByIdentifier(volume_identifier)
      if not volume:
        raise errors.FileSystemScannerError(
            u'Volume missing for identifier: {0:s}.'.format(
                volume_identifier))

      vss_identifier = volume.GetAttribute('identifier')
      print u'{0:s}\t\t{1:s}'.format(
          volume.identifier, vss_identifier.value)

    print u''

    while True:
      print (
          u'Please specify the identifier of the volume shadow snapshot that '
          u'should be processed or none for no VSS:')

      selected_volume_identifier = sys.stdin.readline()
      selected_volume_identifier = selected_volume_identifier.strip()

      if not selected_volume_identifier:
        return

      if selected_volume_identifier in volume_identifiers:
        break

      print u''
      print (
          u'Unsupported volume shadow snapshot identifier, please try again or '
          u'abort with Ctrl^C.')
      print u''

    # We need to return the path specification as defined by the scan node.
    selected_location = u'/{0:s}'.format(selected_volume_identifier)
    scan_sub_node = scan_context.last_scan_node.GetSubNodeByLocation(
        selected_location)
    return getattr(scan_sub_node, 'path_spec', None)

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

    scan_context = source_scanner.SourceScannerContext()
    scan_path_spec = None

    scan_context.OpenSourcePath(source_path)

    while True:
      scan_context = self._scanner.Scan(
          scan_context, scan_path_spec=scan_path_spec)

      # The source is a directory or file.
      if scan_context.source_type in [
          scan_context.SOURCE_TYPE_DIRECTORY, scan_context.SOURCE_TYPE_FILE]:
        break

      if not scan_context.last_scan_node:
        raise RuntimeError(
            u'No supported file system found in source: {0:s}.'.format(
                source_path))

      # The source scanner found a file system.
      if scan_context.last_scan_node.type_indicator in [
          definitions.TYPE_INDICATOR_TSK]:
        break

      # The source scanner found a BitLocker encrypted volume and we need
      # a credential to unlock the volume.
      if scan_context.last_scan_node.type_indicator in [
          definitions.TYPE_INDICATOR_BDE]:
        # TODO: ask for password.
        raise RuntimeError(
            u'BitLocker encrypted volume not yet supported.')

      # The source scanner found a partition table and we need to know
      # which partition to process.
      elif scan_context.last_scan_node.type_indicator in [
          definitions.TYPE_INDICATOR_TSK_PARTITION]:
        scan_path_spec = self._GetNextLevelTSKPartionVolumeSystemPathSpec(
            scan_context)

      # The source scanner found Volume Shadow Snapshot and we need to know
      # which one to process.
      elif scan_context.last_scan_node.type_indicator in [
          definitions.TYPE_INDICATOR_VSHADOW]:
        scan_path_spec = self._GetNextLevelVshadowVolumeSystemPathSpec(
            scan_context)

        # If no VSS selected continue with the current volume.
        if not scan_path_spec:
          scan_node = scan_context.last_scan_node.GetSubNodeByLocation(u'/')
          scan_context.last_scan_node = scan_node
          break

      else:
        raise RuntimeError(
            u'Unsupported volume system found in source: {0:s}.'.format(
                source_path))

    return scan_context.last_scan_node.path_spec


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

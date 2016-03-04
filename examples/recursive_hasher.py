#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to recursively calculate a message digest hash for every file."""

# If you update this script make sure to update the corresponding wiki page
# as well: https://github.com/log2timeline/dfvfs/wiki/Development

from __future__ import print_function
import argparse
import hashlib
import logging
import sys

from dfvfs.helpers import volume_scanner
from dfvfs.resolver import resolver


class RecursiveHasher(volume_scanner.VolumeScanner):
  """Class that recursively calculates message digest hashes of files."""

  # Class constant that defines the default read buffer size.
  _READ_BUFFER_SIZE = 32768

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
  mediator = volume_scanner.VolumeScannerMediator()
  recursive_hasher = RecursiveHasher(mediator=mediator)

  try:
    base_path_specs = recursive_hasher.GetBasePathSpecs(options.source)
    if not base_path_specs:
      print(u'No supported file system found in source.')
      print(u'')
      return False

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

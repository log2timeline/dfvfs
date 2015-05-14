#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to analyze a source device, file or directory."""

from __future__ import print_function
import argparse
import logging
import os
import sys

from dfvfs.helpers import source_scanner
from dfvfs.lib import definitions


class SourceAnalyzer(object):
  """Class that recursively calculates message digest hashes of files."""

  # Class constant that defines the default read buffer size.
  _READ_BUFFER_SIZE = 32768

  def __init__(self, auto_recurse=True, next_layer_input=True):
    """Initializes the source analyzer object.

    Args:
      auto_recurse: optional boolean value to indicate if the scan should
                    automatically recurse as far as possible. The default
                    is True.
      next_layer_input: optional boolean value to indicate if the scan should
                        return if it needs input about the next layer. The
                        default is True.
    """
    super(SourceAnalyzer, self).__init__()
    self._auto_recurse = auto_recurse
    self._next_layer_input = next_layer_input
    self._scanner = source_scanner.SourceScanner()

  def Analyze(self, source_path, output_writer):
    """Analyzes the source.

    Args:
      source_path: the source path.
      output_writer: the output writer (instance of StdoutWriter).

    Raises:
      RuntimeError: if the source path does not exists, or if the source path
                    is not a file or directory, or if the format of or within
                    the source file is not supported.
    """
    if not os.path.exists(source_path):
      raise RuntimeError(u'No such source: {0:s}.'.format(source_path))

    scan_context = source_scanner.SourceScannerContext()
    scan_path_spec = None
    scan_level = 0

    scan_context.OpenSourcePath(source_path)

    while scan_context.updated:
      scan_context = self._scanner.Scan(
          scan_context, auto_recurse=self._auto_recurse,
          next_layer_input=self._next_layer_input,
          scan_path_spec=scan_path_spec)

      if not self._auto_recurse:
        output_writer.WriteScanContext(scan_context, scan_level=scan_level)
      scan_level += 1

      # The source is a directory or file.
      if scan_context.source_type in [
          scan_context.SOURCE_TYPE_DIRECTORY, scan_context.SOURCE_TYPE_FILE]:
        break

      if not scan_context.last_scan_node:
        break

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

      elif scan_context.last_scan_node.type_indicator in (
          definitions.VOLUME_SYSTEM_TYPE_INDICATORS):
        if not not self._auto_recurse:
          break

      elif scan_context.last_scan_node.type_indicator not in (
          definitions.STORAGE_MEDIA_IMAGE_TYPE_INDICATORS):
        raise RuntimeError(
            u'Unsupported volume system found in source: {0:s}.'.format(
                source_path))

      scan_path_spec = scan_context.last_scan_node.path_spec

    if not scan_context.file_system_found:
      raise RuntimeError(
          u'No supported file system found in source: {0:s}.'.format(
              source_path))

    if self._auto_recurse:
      output_writer.WriteScanContext(scan_context)


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

  def WriteScanContext(self, scan_context, scan_level=None):
    """Writes the source scanner context to stdout.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      scan_level: optional integer indicating the scan level. The default
                  is None.
    """
    if scan_level is not None:
      print(u'Scan level: {0:d}'.format(scan_level))

    print(u'Source type\t\t: {0:s}'.format(scan_context.source_type))
    print(u'')

    scan_node = scan_context.GetRootScanNode()
    self.WriteScanNode(scan_node)
    print(u'')

  def WriteScanNode(self, scan_node, indentation=u''):
    """Writes the source scanner node to stdout.

    Args:
      scan_node: the scan node (instance of SourceScanNode).
      indentation: optional indentation string. The default is an empty
                   string.
      scan_level: optional integer indicating the scan level. The default
                  is None.
    """
    if not scan_node:
      return

    values = []

    part_index = getattr(scan_node.path_spec, u'part_index', None)
    if part_index is not None:
      values.append(u'{0:d}'.format(part_index))

    store_index = getattr(scan_node.path_spec, u'store_index', None)
    if store_index is not None:
      values.append(u'{0:d}'.format(store_index))

    start_offset = getattr(scan_node.path_spec, u'start_offset', None)
    if start_offset is not None:
      values.append(u'start offset: {0:d} (0x{0:08x})'.format(start_offset))

    location = getattr(scan_node.path_spec, u'location', None)
    if location is not None:
      values.append(u'location: {0:s}'.format(location))

    print(u'{0:s}{1:s}: {2:s}'.format(
        indentation, scan_node.path_spec.type_indicator, u', '.join(values)))

    indentation = u'  {0:s}'.format(indentation)
    for sub_scan_node in scan_node.sub_nodes:
      self.WriteScanNode(sub_scan_node, indentation=indentation)


def Main():
  """The main program function.

  Returns:
    A boolean containing True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Calculates a message digest hash for every file in a directory or '
      'storage media image.'))

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='image.raw',
      default=None, help=('path of the directory or filename of a storage '
                          'media image containing the file.'))

  argument_parser.add_argument(
      u'--no-auto-recurse', u'--no_auto_recurse', dest=u'no_auto_recurse',
      action=u'store_true', default=False, help=(
          u'Indicate that the source scanner should not auto-recurse.'))

  argument_parser.add_argument(
      u'--no-next-layer-input', u'--no_next_layer_input',
      dest=u'no_next_layer_input', action=u'store_true', default=False, help=(
          u'Indicate that the source scanner should not return for next layer '
          u'input.'))

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
  source_analyzer = SourceAnalyzer(
      auto_recurse=not options.no_auto_recurse,
      next_layer_input=not options.no_next_layer_input)

  try:
    source_analyzer.Analyze(options.source, output_writer)

    print(u'Completed.')

  except KeyboardInterrupt:
    return_value = False

    print(u'Aborted by user.')

  output_writer.Close()

  return return_value


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Script to analyze a source device, file or directory."""

from __future__ import print_function
from __future__ import unicode_literals

import argparse
import getpass
import locale
import logging
import os
import sys

from dfvfs.credentials import manager as credentials_manager
from dfvfs.helpers import source_scanner
from dfvfs.lib import definitions


class SourceAnalyzer(object):
  """Analyzer to recursively check for volumes and file systems."""

  # Class constant that defines the default read buffer size.
  _READ_BUFFER_SIZE = 32768

  def __init__(self, auto_recurse=True):
    """Initializes a source analyzer.

    Args:
      auto_recurse (Optional[bool]): True if the scan should automatically
          recurse as far as possible.
    """
    super(SourceAnalyzer, self).__init__()
    self._auto_recurse = auto_recurse
    self._encode_errors = 'strict'
    self._preferred_encoding = locale.getpreferredencoding()
    self._source_scanner = source_scanner.SourceScanner()

  def _EncodeString(self, string):
    """Encodes a string in the preferred encoding.

    Returns:
      bytes: encoded string.
    """
    try:
      # Note that encode() will first convert string into a Unicode string
      # if necessary.
      encoded_string = string.encode(
          self._preferred_encoding, errors=self._encode_errors)
    except UnicodeEncodeError:
      if self._encode_errors == 'strict':
        logging.error(
            'Unable to properly write output due to encoding error. '
            'Switching to error tolerant encoding which can result in '
            'non Basic Latin (C0) characters to be replaced with "?" or '
            '"\\ufffd".')
        self._encode_errors = 'replace'

      encoded_string = string.encode(
          self._preferred_encoding, errors=self._encode_errors)

    return encoded_string

  def _PromptUserForEncryptedVolumeCredential(
      self, scan_context, locked_scan_node, output_writer):
    """Prompts the user to provide a credential for an encrypted volume.

    Args:
      scan_context (SourceScannerContext): the source scanner context.
      locked_scan_node (SourceScanNode): the locked scan node.
      output_writer (StdoutWriter): the output writer.
    """
    credentials = credentials_manager.CredentialsManager.GetCredentials(
        locked_scan_node.path_spec)

    # TODO: print volume description.
    if locked_scan_node.type_indicator == (
        definitions.TYPE_INDICATOR_APFS_CONTAINER):
      line = 'Found an APFS encrypted volume.'
    elif locked_scan_node.type_indicator == definitions.TYPE_INDICATOR_BDE:
      line = 'Found a BitLocker encrypted volume.'
    elif locked_scan_node.type_indicator == definitions.TYPE_INDICATOR_FVDE:
      line = 'Found a CoreStorage (FVDE) encrypted volume.'
    else:
      line = 'Found an encrypted volume.'

    output_writer.WriteLine(line)

    credentials_list = list(credentials.CREDENTIALS)
    credentials_list.append('skip')

    # TODO: check which credentials are available.
    output_writer.WriteLine('Supported credentials:')
    output_writer.WriteLine('')
    for index, name in enumerate(credentials_list):
      output_writer.WriteLine('  {0:d}. {1:s}'.format(index + 1, name))
    output_writer.WriteLine('')

    result = False
    while not result:
      output_writer.WriteString(
          'Select a credential to unlock the volume: ')
      # TODO: add an input reader.
      input_line = sys.stdin.readline()
      input_line = input_line.strip()

      if input_line in credentials_list:
        credential_identifier = input_line
      else:
        try:
          credential_identifier = int(input_line, 10)
          credential_identifier = credentials_list[credential_identifier - 1]
        except (IndexError, ValueError):
          output_writer.WriteLine(
              'Unsupported credential: {0:s}'.format(input_line))
          continue

      if credential_identifier == 'skip':
        break

      getpass_string = 'Enter credential data: '
      if sys.platform.startswith('win') and sys.version_info[0] < 3:
        # For Python 2 on Windows getpass (win_getpass) requires an encoded
        # byte string. For Python 3 we need it to be a Unicode string.
        getpass_string = self._EncodeString(getpass_string)

      credential_data = getpass.getpass(getpass_string)
      output_writer.WriteLine('')

      result = self._source_scanner.Unlock(
          scan_context, locked_scan_node.path_spec, credential_identifier,
          credential_data)

      if not result:
        output_writer.WriteLine('Unable to unlock volume.')
        output_writer.WriteLine('')

  def Analyze(self, source_path, output_writer):
    """Analyzes the source.

    Args:
      source_path (str): the source path.
      output_writer (StdoutWriter): the output writer.

    Raises:
      RuntimeError: if the source path does not exists, or if the source path
          is not a file or directory, or if the format of or within the source
          file is not supported.
    """
    if not os.path.exists(source_path):
      raise RuntimeError('No such source: {0:s}.'.format(source_path))

    scan_context = source_scanner.SourceScannerContext()
    scan_path_spec = None
    scan_step = 0

    scan_context.OpenSourcePath(source_path)

    while True:
      self._source_scanner.Scan(
          scan_context, auto_recurse=self._auto_recurse,
          scan_path_spec=scan_path_spec)

      if not scan_context.updated:
        break

      if not self._auto_recurse:
        output_writer.WriteScanContext(scan_context, scan_step=scan_step)
      scan_step += 1

      # The source is a directory or file.
      if scan_context.source_type in [
          definitions.SOURCE_TYPE_DIRECTORY, definitions.SOURCE_TYPE_FILE]:
        break

      # The source scanner found a locked volume, e.g. an encrypted volume,
      # and we need a credential to unlock the volume.
      for locked_scan_node in scan_context.locked_scan_nodes:
        self._PromptUserForEncryptedVolumeCredential(
            scan_context, locked_scan_node, output_writer)

      if not self._auto_recurse:
        scan_node = scan_context.GetUnscannedScanNode()
        if not scan_node:
          return
        scan_path_spec = scan_node.path_spec

    if self._auto_recurse:
      output_writer.WriteScanContext(scan_context)


class StdoutWriter(object):
  """Stdout output writer."""

  def Open(self):
    """Opens the output writer object.

    Returns:
      bool: True if open was successful or False if not.
    """
    return True

  def Close(self):
    """Closes the output writer object."""
    return

  def WriteLine(self, line):
    """Writes a line of text to stdout.

    Args:
      line (str): line of text without a new line indicator.
    """
    print(line)

  def WriteScanContext(self, scan_context, scan_step=None):
    """Writes the source scanner context to stdout.

    Args:
      scan_context (SourceScannerContext): the source scanner context.
      scan_step (Optional[int]): the scan step, where None represents no step.
    """
    if scan_step is not None:
      print('Scan step: {0:d}'.format(scan_step))

    print('Source type\t\t: {0:s}'.format(scan_context.source_type))
    print('')

    scan_node = scan_context.GetRootScanNode()
    self.WriteScanNode(scan_context, scan_node)
    print('')

  def WriteScanNode(self, scan_context, scan_node, indentation=''):
    """Writes the source scanner node to stdout.

    Args:
      scan_context (SourceScannerContext): the source scanner context.
      scan_node (SourceScanNode): the scan node.
      indentation (Optional[str]): indentation.
    """
    if not scan_node:
      return

    values = []

    part_index = getattr(scan_node.path_spec, 'part_index', None)
    if part_index is not None:
      values.append('{0:d}'.format(part_index))

    store_index = getattr(scan_node.path_spec, 'store_index', None)
    if store_index is not None:
      values.append('{0:d}'.format(store_index))

    start_offset = getattr(scan_node.path_spec, 'start_offset', None)
    if start_offset is not None:
      values.append('start offset: {0:d} (0x{0:08x})'.format(start_offset))

    location = getattr(scan_node.path_spec, 'location', None)
    if location is not None:
      values.append('location: {0:s}'.format(location))

    values = ', '.join(values)

    flags = ''
    if scan_node in scan_context.locked_scan_nodes:
      flags = ' [LOCKED]'

    print('{0:s}{1:s}: {2:s}{3:s}'.format(
        indentation, scan_node.path_spec.type_indicator, values, flags))

    indentation = '  {0:s}'.format(indentation)
    for sub_scan_node in scan_node.sub_nodes:
      self.WriteScanNode(scan_context, sub_scan_node, indentation=indentation)

  def WriteString(self, string):
    """Writes a string of text to stdout.

    Args:
      string (str): string of text.
    """
    print(string, end='')


def Main():
  """The main program function.

  Returns:
    bool: True if successful or False if not.
  """
  argument_parser = argparse.ArgumentParser(description=(
      'Calculates a message digest hash for every file in a directory or '
      'storage media image.'))

  argument_parser.add_argument(
      'source', nargs='?', action='store', metavar='image.raw', default=None,
      help=('path of the directory or filename of a storage media image '
            'containing the file.'))

  argument_parser.add_argument(
      '--no-auto-recurse', '--no_auto_recurse', dest='no_auto_recurse',
      action='store_true', default=False, help=(
          'Indicate that the source scanner should not auto-recurse.'))

  options = argument_parser.parse_args()

  if not options.source:
    print('Source value is missing.')
    print('')
    argument_parser.print_help()
    print('')
    return False

  logging.basicConfig(
      level=logging.INFO, format='[%(levelname)s] %(message)s')

  output_writer = StdoutWriter()

  if not output_writer.Open():
    print('Unable to open output writer.')
    print('')
    return False

  return_value = True
  source_analyzer = SourceAnalyzer(auto_recurse=not options.no_auto_recurse)

  try:
    source_analyzer.Analyze(options.source, output_writer)

    print('Completed.')

  except KeyboardInterrupt:
    return_value = False

    print('Aborted by user.')

  output_writer.Close()

  return return_value


if __name__ == '__main__':
  if not Main():
    sys.exit(1)
  else:
    sys.exit(0)

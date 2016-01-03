#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Script to analyze a source device, file or directory."""

from __future__ import print_function
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
  """Class that recursively calculates message digest hashes of files."""

  # Class constant that defines the default read buffer size.
  _READ_BUFFER_SIZE = 32768

  def __init__(self, auto_recurse=True):
    """Initializes the source analyzer object.

    Args:
      auto_recurse: optional boolean value to indicate if the scan should
                    automatically recurse as far as possible. The default
                    is True.
    """
    super(SourceAnalyzer, self).__init__()
    self._auto_recurse = auto_recurse
    self._encode_errors = u'strict'
    self._preferred_encoding = locale.getpreferredencoding()
    self._source_scanner = source_scanner.SourceScanner()

  def _EncodeString(self, string):
    """Encodes a string in the preferred encoding.

    Returns:
      A byte string containing the encoded string.
    """
    try:
      # Note that encode() will first convert string into a Unicode string
      # if necessary.
      encoded_string = string.encode(
          self._preferred_encoding, errors=self._encode_errors)
    except UnicodeEncodeError:
      if self._encode_errors == u'strict':
        logging.error(
            u'Unable to properly write output due to encoding error. '
            u'Switching to error tolerant encoding which can result in '
            u'non Basic Latin (C0) characters to be replaced with "?" or '
            u'"\\ufffd".')
        self._encode_errors = u'replace'

      encoded_string = string.encode(
          self._preferred_encoding, errors=self._encode_errors)

    return encoded_string

  def _PromptUserForEncryptedVolumeCredential(
      self, scan_context, locked_scan_node, output_writer):
    """Prompts the user to provide a credential for an encrypted volume.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      locked_scan_node: the locked scan node (instance of SourceScanNode).
      output_writer: the output writer (instance of StdoutWriter).
    """
    credentials = credentials_manager.CredentialsManager.GetCredentials(
        locked_scan_node.path_spec)

    # TODO: print volume description.
    if locked_scan_node.type_indicator == definitions.TYPE_INDICATOR_BDE:
      output_writer.WriteLine(u'Found a BitLocker encrypted volume.')
    else:
      output_writer.WriteLine(u'Found an encrypted volume.')

    credentials_list = list(credentials.CREDENTIALS)
    credentials_list.append(u'skip')

    # TODO: check which credentials are available.
    output_writer.WriteLine(u'Supported credentials:')
    output_writer.WriteLine(u'')
    for index, name in enumerate(credentials_list):
      output_writer.WriteLine(u'  {0:d}. {1:s}'.format(index, name))
    output_writer.WriteLine(u'')

    result = False
    while not result:
      output_writer.WriteString(
          u'Select a credential to unlock the volume: ')
      # TODO: add an input reader.
      input_line = sys.stdin.readline()
      input_line = input_line.strip()

      if input_line in credentials_list:
        credential_identifier = input_line
      else:
        try:
          credential_identifier = int(input_line, 10)
          credential_identifier = credentials_list[credential_identifier]
        except (IndexError, ValueError):
          output_writer.WriteLine(
              u'Unsupported credential: {0:s}'.format(input_line))
          continue

      if credential_identifier == u'skip':
        break

      getpass_string = u'Enter credential data: '
      if sys.platform.startswith(u'win') and sys.version_info[0] < 3:
        # For Python 2 on Windows getpass (win_getpass) requires an encoded
        # byte string. For Python 3 we need it to be a Unicode string.
        getpass_string = self._EncodeString(getpass_string)

      credential_data = getpass.getpass(getpass_string)
      output_writer.WriteLine(u'')

      result = self._source_scanner.Unlock(
          scan_context, locked_scan_node.path_spec, credential_identifier,
          credential_data)

      if not result:
        output_writer.WriteLine(u'Unable to unlock volume.')
        output_writer.WriteLine(u'')

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

  def WriteLine(self, line):
    """Writes a line of text to stdout.

    Args:
      line: line of text without a new line indicator.
    """
    print(line)

  def WriteScanContext(self, scan_context, scan_step=None):
    """Writes the source scanner context to stdout.

    Args:
      scan_context: the source scanner context (instance of
                    SourceScannerContext).
      scan_step: optional integer indicating the scan step.
    """
    if scan_step is not None:
      print(u'Scan step: {0:d}'.format(scan_step))

    print(u'Source type\t\t: {0:s}'.format(scan_context.source_type))
    print(u'')

    scan_node = scan_context.GetRootScanNode()
    self.WriteScanNode(scan_node)
    print(u'')

  def WriteScanNode(self, scan_node, indentation=u''):
    """Writes the source scanner node to stdout.

    Args:
      scan_node: the scan node (instance of SourceScanNode).
      indentation: optional indentation string.
      scan_step: optional integer indicating the scan step.
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

  def WriteString(self, string):
    """Writes a string of text to stdout.

    Args:
      line: string of text.
    """
    print(string, end=u'')


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
  source_analyzer = SourceAnalyzer(auto_recurse=not options.no_auto_recurse)

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

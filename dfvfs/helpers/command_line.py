# -*- coding: utf-8 -*-
"""Helpers for command line tools."""

from __future__ import print_function
from __future__ import unicode_literals

import abc
import codecs
import getpass
import locale
import logging
import sys
import textwrap

try:
  import win32console
except ImportError:
  win32console = None

from dfdatetime import filetime as dfdatetime_filetime

from dfvfs.helpers import volume_scanner
from dfvfs.lib import definitions
from dfvfs.lib import errors


class CLIInputReader(object):
  """Command line interface input reader interface."""

  def __init__(self, encoding='utf-8'):
    """Initializes an input reader.

    Args:
      encoding (Optional[str]): input encoding.
    """
    super(CLIInputReader, self).__init__()
    self._encoding = encoding

  # pylint: disable=redundant-returns-doc
  @abc.abstractmethod
  def Read(self):
    """Reads a string from the input.

    Returns:
      str: input.
    """


class FileObjectInputReader(CLIInputReader):
  """File object command line interface input reader.

  This input reader relies on the file-like object having a readline method.
  """

  def __init__(self, file_object, encoding='utf-8'):
    """Initializes a file object input reader.

    Args:
      file_object (file): file-like object to read from.
      encoding (Optional[str]): input encoding.
    """
    super(FileObjectInputReader, self).__init__(encoding=encoding)
    self._errors = 'strict'
    self._file_object = file_object

  def Read(self):
    """Reads a string from the input.

    Returns:
      str: input.
    """
    input_string = self._file_object.readline()

    if isinstance(input_string, bytes):
      try:
        input_string = codecs.decode(input_string, self._encoding, self._errors)
      except UnicodeDecodeError:
        if self._errors == 'strict':
          logging.error(
              'Unable to properly read input due to encoding error. '
              'Switching to error tolerant encoding which can result in '
              'non Basic Latin (C0) characters to be replaced with "?" or '
              '"\\ufffd".')
          self._errors = 'replace'

        input_string = codecs.decode(input_string, self._encoding, self._errors)

    return input_string


class StdinInputReader(FileObjectInputReader):
  """Stdin command line interface input reader."""

  def __init__(self, encoding='utf-8'):
    """Initializes a stdin input reader.

    Args:
      encoding (Optional[str]): input encoding.
    """
    super(StdinInputReader, self).__init__(sys.stdin, encoding=encoding)


class CLIOutputWriter(object):
  """Command line interface output writer interface."""

  def __init__(self, encoding='utf-8'):
    """Initializes an output writer.

    Args:
      encoding (Optional[str]): output encoding.
    """
    super(CLIOutputWriter, self).__init__()
    self._encoding = encoding

  @abc.abstractmethod
  def Write(self, string):
    """Writes a string to the output.

    Args:
      string (str): output.
    """


class FileObjectOutputWriter(CLIOutputWriter):
  """File object command line interface output writer.

  This output writer relies on the file-like object having a write method.
  """

  def __init__(self, file_object, encoding='utf-8'):
    """Initializes a file object output writer.

    Args:
      file_object (file): file-like object to read from.
      encoding (Optional[str]): output encoding.
    """
    super(FileObjectOutputWriter, self).__init__(encoding=encoding)
    self._errors = 'strict'
    self._file_object = file_object

  def Write(self, string):
    """Writes a string to the output.

    Args:
      string (str): output.
    """
    try:
      # Note that encode() will first convert string into a Unicode string
      # if necessary.
      encoded_string = codecs.encode(string, self._encoding, self._errors)
    except UnicodeEncodeError:
      if self._errors == 'strict':
        logging.error(
            'Unable to properly write output due to encoding error. '
            'Switching to error tolerant encoding which can result in '
            'non Basic Latin (C0) characters to be replaced with "?" or '
            '"\\ufffd".')
        self._errors = 'replace'

      encoded_string = codecs.encode(string, self._encoding, self._errors)

    self._file_object.write(encoded_string)


class StdoutOutputWriter(FileObjectOutputWriter):
  """Stdout command line interface output writer."""

  def __init__(self, encoding='utf-8'):
    """Initializes a stdout output writer.

    Args:
      encoding (Optional[str]): output encoding.
    """
    super(StdoutOutputWriter, self).__init__(sys.stdout, encoding=encoding)

  def Write(self, string):
    """Writes a string to the output.

    Args:
      string (str): output.
    """
    if sys.version_info[0] < 3:
      super(StdoutOutputWriter, self).Write(string)
    else:
      # sys.stdout.write() on Python 3 by default will error if string is
      # of type bytes.
      sys.stdout.write(string)


class CLITabularTableView(object):
  """Command line interface tabular table view."""

  _NUMBER_OF_SPACES_IN_TAB = 8

  def __init__(self, column_names=None, column_sizes=None):
    """Initializes a command line interface tabular table view.

    Args:
      column_names (Optional[list[str]]): column names.
      column_sizes (Optional[list[int]]): minimum column sizes, in number of
          characters. If a column name or row value is larger than the
          minimum column size the column will be enlarged. Note that the
          minimum columns size will be rounded up to the number of spaces
          of the next tab.
    """
    super(CLITabularTableView, self).__init__()
    self._columns = column_names or []
    self._column_sizes = column_sizes or []
    self._number_of_columns = len(self._columns)
    self._rows = []

  def _WriteRow(self, output_writer, values, in_bold=False):
    """Writes a row of values aligned with the width to the output writer.

    Args:
      output_writer (CLIOutputWriter): output writer.
      values (list[object]): values.
      in_bold (Optional[bool]): True if the row should be written in bold.
    """
    row_strings = []
    for value_index, value_string in enumerate(values):
      padding_size = self._column_sizes[value_index] - len(value_string)
      padding_string = ' ' * padding_size

      row_strings.extend([value_string, padding_string])

    row_strings.pop()

    row_strings = ''.join(row_strings)

    if in_bold and not win32console:
      # TODO: for win32console get current color and set intensity,
      # write the header separately then reset intensity.
      row_strings = '\x1b[1m{0:s}\x1b[0m'.format(row_strings)

    output_writer.Write('{0:s}\n'.format(row_strings))

  def AddRow(self, values):
    """Adds a row of values.

    Args:
      values (list[object]): values.

    Raises:
      ValueError: if the number of values is out of bounds.
    """
    if self._number_of_columns and len(values) != self._number_of_columns:
      raise ValueError('Number of values is out of bounds.')

    if not self._column_sizes and self._columns:
      self._column_sizes = [len(column) for column in self._columns]

    value_strings = []
    for value_index, value_string in enumerate(values):
      if not isinstance(value_string, str):
        value_string = '{0!s}'.format(value_string)
      value_strings.append(value_string)

      self._column_sizes[value_index] = max(
          self._column_sizes[value_index], len(value_string))

    self._rows.append(value_strings)

    if not self._number_of_columns:
      self._number_of_columns = len(value_strings)

  def Write(self, output_writer):
    """Writes the table to output writer.

    Args:
      output_writer (CLIOutputWriter): output writer.
    """
    # Round up the column sizes to the nearest tab.
    for column_index, column_size in enumerate(self._column_sizes):
      column_size, _ = divmod(column_size, self._NUMBER_OF_SPACES_IN_TAB)
      column_size = (column_size + 1) * self._NUMBER_OF_SPACES_IN_TAB
      self._column_sizes[column_index] = column_size

    if self._columns:
      self._WriteRow(output_writer, self._columns, in_bold=True)

    for values in self._rows:
      self._WriteRow(output_writer, values)


class CLIVolumeScannerMediator(volume_scanner.VolumeScannerMediator):
  """Command line volume scanner mediator."""

  # For context see: http://en.wikipedia.org/wiki/Byte
  _UNITS_1000 = ['B', 'kB', 'MB', 'GB', 'TB', 'EB', 'ZB', 'YB']
  _UNITS_1024 = ['B', 'KiB', 'MiB', 'GiB', 'TiB', 'EiB', 'ZiB', 'YiB']

  _USER_PROMPT_APFS = (
      'Please specify the identifier(s) of the APFS volume that should be '
      'processed: Note that a range of volumes can be defined as: 3..5. '
      'Multiple volumes can be defined as: 1,3,5 (a list of comma separated '
      'values). Ranges and lists can also be combined as: 1,3..5. The first '
      'volume is 1. All volumes can be defined as "all". If no volumes are '
      'specified none will be processed. You can abort with Ctrl^C.')

  _USER_PROMPT_LVM = (
      'Please specify the identifier(s) of the LVM volume that should be '
      'processed: Note that a range of volumes can be defined as: 3..5. '
      'Multiple volumes can be defined as: 1,3,5 (a list of comma separated '
      'values). Ranges and lists can also be combined as: 1,3..5. The first '
      'volume is 1. All volumes can be defined as "all". If no volumes are '
      'specified none will be processed. You can abort with Ctrl^C.')

  _USER_PROMPT_TSK = (
      'Please specify the identifier of the partition that should be '
      'processed. All partitions can be defined as: "all". Note that you can '
      'abort with Ctrl^C.')

  _USER_PROMPT_VSS = (
      'Please specify the identifier(s) of the VSS that should be processed: '
      'Note that a range of stores can be defined as: 3..5. Multiple stores '
      'can be defined as: 1,3,5 (a list of comma separated values). Ranges '
      'and lists can also be combined as: 1,3..5. The first store is 1. All '
      'stores can be defined as "all". If no stores are specified none will '
      'be processed. You can abort with Ctrl^C.')

  def __init__(self, input_reader=None, output_writer=None):
    """Initializes a volume scanner mediator.

    Args:
      input_reader (Optional[CLIInputReader]): input reader, where None
          indicates that the stdin input reader should be used.
      output_writer (Optional[CLIOutputWriter]): output writer, where None
          indicates that the stdout output writer should be used.
    """
    preferred_encoding = locale.getpreferredencoding()

    if not input_reader:
      input_reader = StdinInputReader(encoding=preferred_encoding)
    if not output_writer:
      output_writer = StdoutOutputWriter(encoding=preferred_encoding)

    super(CLIVolumeScannerMediator, self).__init__()
    self._encode_errors = 'strict'
    self._input_reader = input_reader
    self._output_writer = output_writer
    self._preferred_encoding = locale.getpreferredencoding()
    self._textwrapper = textwrap.TextWrapper()

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
            'non Basic Latin (C0) characters being replaced with "?" or '
            '"\\ufffd".')
        self._encode_errors = 'replace'

      encoded_string = string.encode(
          self._preferred_encoding, errors=self._encode_errors)

    return encoded_string

  def _FormatHumanReadableSize(self, size):
    """Represents a number of bytes as a human readable string.

    Args:
      size (int): size in bytes.

    Returns:
      str: human readable string of the size.
    """
    magnitude_1000 = 0
    size_1000 = float(size)
    while size_1000 >= 1000:
      size_1000 /= 1000
      magnitude_1000 += 1

    magnitude_1024 = 0
    size_1024 = float(size)
    while size_1024 >= 1024:
      size_1024 /= 1024
      magnitude_1024 += 1

    size_string_1000 = None
    if 0 < magnitude_1000 <= 7:
      size_string_1000 = '{0:.1f}{1:s}'.format(
          size_1000, self._UNITS_1000[magnitude_1000])

    size_string_1024 = None
    if 0 < magnitude_1024 <= 7:
      size_string_1024 = '{0:.1f}{1:s}'.format(
          size_1024, self._UNITS_1024[magnitude_1024])

    if not size_string_1000 or not size_string_1024:
      return '{0:d} B'.format(size)

    return '{0:s} / {1:s} ({2:d} B)'.format(
        size_string_1024, size_string_1000, size)

  def _ParseVolumeIdentifiersString(
      self, volume_identifiers_string, prefix='v'):
    """Parses a user specified volume identifiers string.

    Args:
      volume_identifiers_string (str): user specified volume identifiers. A
          range of volumes can be defined as: "3..5". Multiple volumes can be
          defined as: "1,3,5" (a list of comma separated values). Ranges and
          lists can also be combined as: "1,3..5". The first volume is 1. All
          volumes can be defined as "all". No volumes can be defined as an
          empty string or "none".
      prefix (Optional[str]): volume identifier prefix.

    Returns:
      list[str]: volume identifiers with prefix or the string "all".

    Raises:
      ValueError: if the volume identifiers string is invalid.
    """
    prefix_length = 0
    if prefix:
      prefix_length = len(prefix)

    if not volume_identifiers_string or volume_identifiers_string == 'none':
      return []

    if volume_identifiers_string == 'all':
      return ['all']

    volume_identifiers = set()
    for identifiers_range in volume_identifiers_string.split(','):
      # Determine if the range is formatted as 1..3 otherwise it indicates
      # a single volume identifier.
      if '..' in identifiers_range:
        first_identifier, last_identifier = identifiers_range.split('..')

        if prefix and first_identifier.startswith(prefix):
          first_identifier = first_identifier[prefix_length:]

        if prefix and last_identifier.startswith(prefix):
          last_identifier = last_identifier[prefix_length:]

        try:
          first_identifier = int(first_identifier, 10)
          last_identifier = int(last_identifier, 10)
        except ValueError:
          raise ValueError('Invalid volume identifiers range: {0:s}.'.format(
              identifiers_range))

        for volume_identifier in range(first_identifier, last_identifier + 1):
          if volume_identifier not in volume_identifiers:
            if prefix:
              volume_identifier = '{0:s}{1:d}'.format(prefix, volume_identifier)
            volume_identifiers.add(volume_identifier)
      else:
        identifier = identifiers_range
        if prefix and identifier.startswith(prefix):
          identifier = identifiers_range[prefix_length:]

        try:
          volume_identifier = int(identifier, 10)
        except ValueError:
          raise ValueError('Invalid volume identifier range: {0:s}.'.format(
              identifiers_range))

        if prefix:
          volume_identifier = '{0:s}{1:d}'.format(prefix, volume_identifier)
        volume_identifiers.add(volume_identifier)

    # Note that sorted will return a list.
    return sorted(volume_identifiers)

  def _PrintAPFSVolumeIdentifiersOverview(
      self, volume_system, volume_identifiers):
    """Prints an overview of APFS volume identifiers.

    Args:
      volume_system (APFSVolumeSystem): volume system.
      volume_identifiers (list[str]): allowed volume identifiers.

    Raises:
      ScannerError: if a volume cannot be resolved from the volume identifier.
    """
    header = 'The following Apple File System (APFS) volumes were found:\n'
    self._output_writer.Write(header)

    column_names = ['Identifier', 'Name']
    table_view = CLITabularTableView(column_names=column_names)

    # Sort the volume identifiers in alphanumeric order.
    for volume_identifier in sorted(volume_identifiers, key=lambda string: int(
        ''.join([character for character in string if character.isdigit()]))):
      volume = volume_system.GetVolumeByIdentifier(volume_identifier)
      if not volume:
        raise errors.ScannerError(
            'Volume missing for identifier: {0:s}.'.format(
                volume_identifier))

      volume_attribute = volume.GetAttribute('name')
      table_view.AddRow([volume.identifier, volume_attribute.value])

    self._output_writer.Write('\n')
    table_view.Write(self._output_writer)

  def _PrintLVMVolumeIdentifiersOverview(
      self, volume_system, volume_identifiers):
    """Prints an overview of LVM volume identifiers.

    Args:
      volume_system (LVMVolumeSystem): volume system.
      volume_identifiers (list[str]): allowed volume identifiers.

    Raises:
      ScannerError: if a volume cannot be resolved from the volume identifier.
    """
    header = 'The following Logical Volume Manager (LVM) volumes were found:\n'
    self._output_writer.Write(header)

    column_names = ['Identifier']
    table_view = CLITabularTableView(column_names=column_names)

    # Sort the volume identifiers in alphanumeric order.
    for volume_identifier in sorted(volume_identifiers, key=lambda string: int(
        ''.join([character for character in string if character.isdigit()]))):
      volume = volume_system.GetVolumeByIdentifier(volume_identifier)
      if not volume:
        raise errors.ScannerError(
            'Volume missing for identifier: {0:s}.'.format(
                volume_identifier))

      table_view.AddRow([volume.identifier])

    self._output_writer.Write('\n')
    table_view.Write(self._output_writer)

  def _PrintPartitionIdentifiersOverview(
      self, volume_system, volume_identifiers):
    """Prints an overview of TSK partition identifiers.

    Args:
      volume_system (TSKVolumeSystem): volume system.
      volume_identifiers (list[str]): allowed volume identifiers.

    Raises:
      ScannerError: if a volume cannot be resolved from the volume identifier.
    """
    header = 'The following partitions were found:\n'
    self._output_writer.Write(header)

    column_names = ['Identifier', 'Offset (in bytes)', 'Size (in bytes)']
    table_view = CLITabularTableView(column_names=column_names)

    # Sort the volume identifiers in alphanumeric order.
    for volume_identifier in sorted(volume_identifiers, key=lambda string: int(
        ''.join([character for character in string if character.isdigit()]))):
      volume = volume_system.GetVolumeByIdentifier(volume_identifier)
      if not volume:
        raise errors.ScannerError(
            'Partition missing for identifier: {0:s}.'.format(
                volume_identifier))

      volume_extent = volume.extents[0]
      volume_offset = '{0:d} (0x{0:08x})'.format(volume_extent.offset)
      volume_size = self._FormatHumanReadableSize(volume_extent.size)

      table_view.AddRow([volume.identifier, volume_offset, volume_size])

    self._output_writer.Write('\n')
    table_view.Write(self._output_writer)

  def _PrintVSSStoreIdentifiersOverview(
      self, volume_system, volume_identifiers):
    """Prints an overview of VSS store identifiers.

    Args:
      volume_system (VShadowVolumeSystem): volume system.
      volume_identifiers (list[str]): allowed volume identifiers.

    Raises:
      ScannerError: if a volume cannot be resolved from the volume identifier.
    """
    header = 'The following Volume Shadow Snapshots (VSS) were found:\n'
    self._output_writer.Write(header)

    column_names = ['Identifier', 'Creation Time']
    table_view = CLITabularTableView(column_names=column_names)

    # Sort the volume identifiers in alphanumeric order.
    for volume_identifier in sorted(volume_identifiers, key=lambda string: int(
        ''.join([character for character in string if character.isdigit()]))):
      volume = volume_system.GetVolumeByIdentifier(volume_identifier)
      if not volume:
        raise errors.ScannerError(
            'Volume missing for identifier: {0:s}.'.format(
                volume_identifier))

      volume_attribute = volume.GetAttribute('creation_time')
      filetime = dfdatetime_filetime.Filetime(timestamp=volume_attribute.value)
      creation_time = filetime.CopyToDateTimeString()

      if volume.HasExternalData():
        creation_time = '{0:s}\tWARNING: data stored outside volume'.format(
            creation_time)

      table_view.AddRow([volume.identifier, creation_time])

    self._output_writer.Write('\n')
    table_view.Write(self._output_writer)

  def _ReadSelectedVolumes(self, volume_system, prefix='v'):
    """Reads the selected volumes provided by the user.

    Args:
      volume_system (VolumeSystem): volume system.
      prefix (Optional[str]): volume identifier prefix.

    Returns:
      list[str]: selected volume identifiers including prefix.

    Raises:
      KeyboardInterrupt: if the user requested to abort.
      ValueError: if the volume identifiers string could not be parsed.
    """
    volume_identifiers_string = self._input_reader.Read()
    volume_identifiers_string = volume_identifiers_string.strip()

    if not volume_identifiers_string:
      return []

    selected_volumes = self._ParseVolumeIdentifiersString(
        volume_identifiers_string, prefix=prefix)

    if selected_volumes == ['all']:
      return [
          '{0:s}{1:d}'.format(prefix, volume_index)
          for volume_index in range(1, volume_system.number_of_volumes + 1)]

    return selected_volumes

  def GetAPFSVolumeIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves APFS volume identifiers.

    This method can be used to prompt the user to provide APFS volume
    identifiers.

    Args:
      volume_system (APFSVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """
    print_header = True
    while True:
      if print_header:
        self._PrintAPFSVolumeIdentifiersOverview(
            volume_system, volume_identifiers)

        print_header = False

      self._output_writer.Write('\n')

      lines = self._textwrapper.wrap(self._USER_PROMPT_APFS)
      self._output_writer.Write('\n'.join(lines))
      self._output_writer.Write('\n\nVolume identifier(s): ')

      try:
        selected_volumes = self._ReadSelectedVolumes(
            volume_system, prefix='apfs')
        if (not selected_volumes or
            not set(selected_volumes).difference(volume_identifiers)):
          break
      except ValueError:
        pass

      self._output_writer.Write('\n')

      lines = self._textwrapper.wrap(
          'Unsupported volume identifier(s), please try again or abort with '
          'Ctrl^C.')
      self._output_writer.Write('\n'.join(lines))
      self._output_writer.Write('\n\n')

    return selected_volumes

  def GetLVMVolumeIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves LVM volume identifiers.

    This method can be used to prompt the user to provide LVM volume
    identifiers.

    Args:
      volume_system (LVMVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """
    print_header = True
    while True:
      if print_header:
        self._PrintLVMVolumeIdentifiersOverview(
            volume_system, volume_identifiers)

        print_header = False

      self._output_writer.Write('\n')

      lines = self._textwrapper.wrap(self._USER_PROMPT_LVM)
      self._output_writer.Write('\n'.join(lines))
      self._output_writer.Write('\n\nVolume identifier(s): ')

      try:
        selected_volumes = self._ReadSelectedVolumes(
            volume_system, prefix='lvm')
        if (not selected_volumes or
            not set(selected_volumes).difference(volume_identifiers)):
          break
      except ValueError:
        pass

      self._output_writer.Write('\n')

      lines = self._textwrapper.wrap(
          'Unsupported volume identifier(s), please try again or abort with '
          'Ctrl^C.')
      self._output_writer.Write('\n'.join(lines))
      self._output_writer.Write('\n\n')

    return selected_volumes

  def GetPartitionIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves partition identifiers.

    This method can be used to prompt the user to provide partition identifiers.

    Args:
      volume_system (TSKVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """
    print_header = True
    while True:
      if print_header:
        self._PrintPartitionIdentifiersOverview(
            volume_system, volume_identifiers)

        print_header = False

      self._output_writer.Write('\n')

      lines = self._textwrapper.wrap(self._USER_PROMPT_TSK)
      self._output_writer.Write('\n'.join(lines))
      self._output_writer.Write('\n\nPartition identifier(s): ')

      try:
        selected_volumes = self._ReadSelectedVolumes(volume_system, prefix='p')
        if (not selected_volumes or
            not set(selected_volumes).difference(volume_identifiers)):
          break
      except ValueError:
        pass

      self._output_writer.Write('\n')

      lines = self._textwrapper.wrap(
          'Unsupported partition identifier(s), please try again or abort with '
          'Ctrl^C.')
      self._output_writer.Write('\n'.join(lines))
      self._output_writer.Write('\n\n')

    return selected_volumes

  def GetVSSStoreIdentifiers(self, volume_system, volume_identifiers):
    """Retrieves VSS store identifiers.

    This method can be used to prompt the user to provide VSS store identifiers.

    Args:
      volume_system (VShadowVolumeSystem): volume system.
      volume_identifiers (list[str]): volume identifiers including prefix.

    Returns:
      list[str]: selected volume identifiers including prefix or None.
    """
    print_header = True
    while True:
      if print_header:
        self._PrintVSSStoreIdentifiersOverview(
            volume_system, volume_identifiers)

        print_header = False

      self._output_writer.Write('\n')

      lines = self._textwrapper.wrap(self._USER_PROMPT_VSS)
      self._output_writer.Write('\n'.join(lines))
      self._output_writer.Write('\n\nVSS identifier(s): ')

      try:
        selected_volumes = self._ReadSelectedVolumes(
            volume_system, prefix='vss')
        if (not selected_volumes or
            not set(selected_volumes).difference(volume_identifiers)):
          break
      except ValueError:
        pass

      self._output_writer.Write('\n')

      lines = self._textwrapper.wrap(
          'Unsupported VSS identifier(s), please try again or abort with '
          'Ctrl^C.')
      self._output_writer.Write('\n'.join(lines))
      self._output_writer.Write('\n\n')

    return selected_volumes

  def ParseVolumeIdentifiersString(self, volume_identifiers_string):
    """Parses a user specified volume identifiers string.

    Args:
      volume_identifiers_string (str): user specified volume identifiers. A
          range of volumes can be defined as: "3..5". Multiple volumes can be
          defined as: "1,3,5" (a list of comma separated values). Ranges and
          lists can also be combined as: "1,3..5". The first volume is 1. All
          volumes can be defined as "all". No volumes can be defined as an
          empty string or "none".

    Returns:
      list[str]: volume identifiers with prefix or the string "all".

    Raises:
      ValueError: if the volume identifiers string is invalid.
    """
    return self._ParseVolumeIdentifiersString(
        volume_identifiers_string, prefix=None)

  def PrintWarning(self, warning):
    """Prints a warning.

    Args:
      warning (str): warning text.
    """
    self._output_writer.Write('[WARNING] {0:s}\n\n'.format(warning))

  def UnlockEncryptedVolume(
      self, source_scanner_object, scan_context, locked_scan_node, credentials):
    """Unlocks an encrypted volume.

    This method can be used to prompt the user to provide encrypted volume
    credentials.

    Args:
      source_scanner_object (SourceScanner): source scanner.
      scan_context (SourceScannerContext): source scanner context.
      locked_scan_node (SourceScanNode): locked scan node.
      credentials (Credentials): credentials supported by the locked scan node.

    Returns:
      bool: True if the volume was unlocked.
    """
    # TODO: print volume description.
    if locked_scan_node.type_indicator == (
        definitions.TYPE_INDICATOR_APFS_CONTAINER):
      header = 'Found an APFS encrypted volume.'
    elif locked_scan_node.type_indicator == definitions.TYPE_INDICATOR_BDE:
      header = 'Found a BitLocker encrypted volume.'
    elif locked_scan_node.type_indicator == definitions.TYPE_INDICATOR_FVDE:
      header = 'Found a CoreStorage (FVDE) encrypted volume.'
    elif locked_scan_node.type_indicator == definitions.TYPE_INDICATOR_LUKSDE:
      header = 'Found a LUKS encrypted volume.'
    else:
      header = 'Found an encrypted volume.'

    self._output_writer.Write(header)

    credentials_list = list(credentials.CREDENTIALS)
    credentials_list.append('skip')

    self._output_writer.Write('Supported credentials:\n\n')

    for index, name in enumerate(credentials_list):
      available_credential = '  {0:d}. {1:s}\n'.format(index + 1, name)
      self._output_writer.Write(available_credential)

    self._output_writer.Write('\nNote that you can abort with Ctrl^C.\n\n')

    result = False
    while not result:
      self._output_writer.Write('Select a credential to unlock the volume: ')

      input_line = self._input_reader.Read()
      input_line = input_line.strip()

      if input_line in credentials_list:
        credential_type = input_line
      else:
        try:
          credential_type = int(input_line, 10)
          credential_type = credentials_list[credential_type - 1]
        except (IndexError, ValueError):
          self._output_writer.Write(
              'Unsupported credential: {0:s}\n'.format(input_line))
          continue

      if credential_type == 'skip':
        break

      getpass_string = 'Enter credential data: '
      if sys.platform.startswith('win') and sys.version_info[0] < 3:
        # For Python 2 on Windows getpass (win_getpass) requires an encoded
        # byte string. For Python 3 we need it to be a Unicode string.
        getpass_string = self._EncodeString(getpass_string)

      credential_data = getpass.getpass(getpass_string)
      self._output_writer.Write('\n')

      if credential_type == 'key':
        try:
          credential_data = codecs.decode(credential_data, 'hex')
        except TypeError:
          self._output_writer.Write('Unsupported credential data.\n')
          continue

      result = source_scanner_object.Unlock(
          scan_context, locked_scan_node.path_spec, credential_type,
          credential_data)

      if not result:
        self._output_writer.Write('Unable to unlock volume.\n\n')

    return result

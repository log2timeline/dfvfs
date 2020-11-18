#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the helpers for command line tools."""

from __future__ import unicode_literals

import io
import os
import unittest

try:
  import win32console
except ImportError:
  win32console = None

from dfvfs.lib import definitions
from dfvfs.helpers import command_line
from dfvfs.path import factory as path_spec_factory
from dfvfs.volume import apfs_volume_system
from dfvfs.volume import lvm_volume_system
from dfvfs.volume import tsk_volume_system
from dfvfs.volume import vshadow_volume_system

from tests import test_lib as shared_test_lib


class CLIInputReaderTest(shared_test_lib.BaseTestCase):
  """Tests for the command line interface input reader interface."""

  def testInitialize(self):
    """Tests the __init__ function."""
    input_reader = command_line.CLIInputReader()
    self.assertIsNotNone(input_reader)


class FileObjectInputReaderTest(shared_test_lib.BaseTestCase):
  """Tests for the file object command line interface input reader."""

  _TEST_DATA = (
      b'A first string\n'
      b'A 2nd string\n'
      b'\xc3\xberi\xc3\xb0ja string\n'
      b'\xff\xfef\x00j\x00\xf3\x00r\x00\xf0\x00a\x00 \x00b\x00a\x00n\x00d\x00')

  def testReadAscii(self):
    """Tests the Read function with ASCII encoding."""
    file_object = io.BytesIO(self._TEST_DATA)
    input_reader = command_line.FileObjectInputReader(
        file_object, encoding='ascii')

    string = input_reader.Read()
    self.assertEqual(string, 'A first string\n')

    string = input_reader.Read()
    self.assertEqual(string, 'A 2nd string\n')

    # UTF-8 string with non-ASCII characters.
    string = input_reader.Read()
    self.assertEqual(string, '\ufffd\ufffdri\ufffd\ufffdja string\n')

    # UTF-16 string with non-ASCII characters.
    string = input_reader.Read()
    expected_string = (
        '\ufffd\ufffdf\x00j\x00\ufffd\x00r\x00\ufffd\x00a\x00 '
        '\x00b\x00a\x00n\x00d\x00')
    self.assertEqual(string, expected_string)

  def testReadUtf8(self):
    """Tests the Read function with UTF-8 encoding."""
    file_object = io.BytesIO(self._TEST_DATA)
    input_reader = command_line.FileObjectInputReader(file_object)

    string = input_reader.Read()
    self.assertEqual(string, 'A first string\n')

    string = input_reader.Read()
    self.assertEqual(string, 'A 2nd string\n')

    # UTF-8 string with non-ASCII characters.
    string = input_reader.Read()
    self.assertEqual(string, 'þriðja string\n')

    # UTF-16 string with non-ASCII characters.
    string = input_reader.Read()
    expected_string = (
        '\ufffd\ufffdf\x00j\x00\ufffd\x00r\x00\ufffd\x00a\x00 '
        '\x00b\x00a\x00n\x00d\x00')
    self.assertEqual(string, expected_string)


class StdinInputReaderTest(shared_test_lib.BaseTestCase):
  """Tests for the stdin command line interface input reader."""

  def testInitialize(self):
    """Tests the __init__ function."""
    input_reader = command_line.StdinInputReader()
    self.assertIsNotNone(input_reader)


class CLIOutputWriter(shared_test_lib.BaseTestCase):
  """Tests for the command line interface output writer interface."""

  def testInitialize(self):
    """Tests the __init__ function."""
    test_writer = command_line.CLIOutputWriter()
    self.assertIsNotNone(test_writer)


class FileObjectOutputWriterTest(shared_test_lib.BaseTestCase):
  """Tests for the file object command line interface output writer."""

  def _ReadOutput(self, file_object):
    """Reads all output added since the last call to ReadOutput.

    Args:
      file_object (file): file-like object.

    Returns:
      str: output data.
    """
    file_object.seek(0, os.SEEK_SET)
    output_data = file_object.read()

    file_object.seek(0, os.SEEK_SET)
    file_object.truncate(0)
    return output_data

  def testWriteAscii(self):
    """Tests the Write function with ASCII encoding."""
    file_object = io.BytesIO()
    output_writer = command_line.FileObjectOutputWriter(
        file_object, encoding='ascii')

    output_writer.Write('A first string\n')

    byte_stream = self._ReadOutput(file_object)
    self.assertEqual(byte_stream, b'A first string\n')

    # Unicode string with non-ASCII characters.
    output_writer.Write('þriðja string\n')

    byte_stream = self._ReadOutput(file_object)
    self.assertEqual(byte_stream, b'?ri?ja string\n')

  def testWriteUtf8(self):
    """Tests the Write function with UTF-8 encoding."""
    file_object = io.BytesIO()
    output_writer = command_line.FileObjectOutputWriter(file_object)

    output_writer.Write('A first string\n')

    byte_stream = self._ReadOutput(file_object)
    self.assertEqual(byte_stream, b'A first string\n')

    # Unicode string with non-ASCII characters.
    output_writer.Write('þriðja string\n')

    byte_stream = self._ReadOutput(file_object)
    self.assertEqual(byte_stream, b'\xc3\xberi\xc3\xb0ja string\n')


class StdoutOutputWriterTest(shared_test_lib.BaseTestCase):
  """Tests for the stdout command line interface output writer."""

  def testWriteAscii(self):
    """Tests the Write function with ASCII encoding."""
    output_writer = command_line.StdoutOutputWriter(encoding='ascii')
    output_writer.Write('A first string\n')


class CLITabularTableViewTest(shared_test_lib.BaseTestCase):
  """Tests for the command line tabular table view class."""

  # TODO: add tests for _WriteRow
  # TODO: add tests for AddRow
  # TODO: add tests for Write


class CLIVolumeScannerMediatorTest(shared_test_lib.BaseTestCase):
  """Tests for the command line volume scanner mediator."""

  # pylint: disable=protected-access

  def testEncodeString(self):
    """Tests the _EncodeString function."""
    test_mediator = command_line.CLIVolumeScannerMediator()

    encoded_string = test_mediator._EncodeString('ASCII')
    self.assertEqual(encoded_string, b'ASCII')

    test_mediator._preferred_encoding = 'ascii'
    encoded_string = test_mediator._EncodeString('\u00b5')
    self.assertEqual(encoded_string, b'?')

  def testFormatHumanReadableSize(self):
    """Tests the _FormatHumanReadableSize function."""
    test_mediator = command_line.CLIVolumeScannerMediator()

    expected_size_string = '1000 B'
    size_string = test_mediator._FormatHumanReadableSize(1000)
    self.assertEqual(size_string, expected_size_string)

    expected_size_string = '1.0KiB / 1.0kB (1024 B)'
    size_string = test_mediator._FormatHumanReadableSize(1024)
    self.assertEqual(size_string, expected_size_string)

    expected_size_string = '976.6KiB / 1.0MB (1000000 B)'
    size_string = test_mediator._FormatHumanReadableSize(1000000)
    self.assertEqual(size_string, expected_size_string)

    expected_size_string = '1.0MiB / 1.0MB (1048576 B)'
    size_string = test_mediator._FormatHumanReadableSize(1048576)
    self.assertEqual(size_string, expected_size_string)

  def testParseVolumeIdentifiersString(self):
    """Tests the _ParseVolumeIdentifiersString function."""
    test_mediator = command_line.CLIVolumeScannerMediator()

    volume_identifiers = test_mediator._ParseVolumeIdentifiersString('')
    self.assertEqual(volume_identifiers, [])

    volume_identifiers = test_mediator._ParseVolumeIdentifiersString('all')
    self.assertEqual(volume_identifiers, ['all'])

    volume_identifiers = test_mediator._ParseVolumeIdentifiersString('v1')
    self.assertEqual(volume_identifiers, ['v1'])

    volume_identifiers = test_mediator._ParseVolumeIdentifiersString('1')
    self.assertEqual(volume_identifiers, ['v1'])

    volume_identifiers = test_mediator._ParseVolumeIdentifiersString('1,3')
    self.assertEqual(volume_identifiers, ['v1', 'v3'])

    volume_identifiers = test_mediator._ParseVolumeIdentifiersString('1..3')
    self.assertEqual(volume_identifiers, ['v1', 'v2', 'v3'])

    volume_identifiers = test_mediator._ParseVolumeIdentifiersString('v1..v3')
    self.assertEqual(volume_identifiers, ['v1', 'v2', 'v3'])

    volume_identifiers = test_mediator._ParseVolumeIdentifiersString('1..3,5')
    self.assertEqual(volume_identifiers, ['v1', 'v2', 'v3', 'v5'])

    with self.assertRaises(ValueError):
      test_mediator._ParseVolumeIdentifiersString('bogus')

    with self.assertRaises(ValueError):
      test_mediator._ParseVolumeIdentifiersString('1..bogus')

  def testPrintAPFSVolumeIdentifiersOverview(self):
    """Tests the _PrintAPFSVolumeIdentifiersOverview function."""
    test_path = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_apfs_container_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/',
        parent=test_raw_path_spec)

    volume_system = apfs_volume_system.APFSVolumeSystem()
    volume_system.Open(test_apfs_container_path_spec)

    file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        output_writer=test_output_writer)

    test_mediator._PrintAPFSVolumeIdentifiersOverview(volume_system, ['apfs1'])

    file_object.seek(0, os.SEEK_SET)
    output_data = file_object.read()

    expected_output_data = [
        b'The following Apple File System (APFS) volumes were found:',
        b'',
        b'Identifier      Name',
        b'apfs1           apfs_test',
        b'']

    if not win32console:
      # Using join here since Python 3 does not support format of bytes.
      expected_output_data[2] = b''.join([
          b'\x1b[1m', expected_output_data[2], b'\x1b[0m'])

    self.assertEqual(output_data.split(b'\n'), expected_output_data)

  def testPrintLVMVolumeIdentifiersOverview(self):
    """Tests the _PrintLVMVolumeIdentifiersOverview function."""
    test_path = self._GetTestFilePath(['lvm.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_lvm_container_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, location='/', parent=test_raw_path_spec)

    volume_system = lvm_volume_system.LVMVolumeSystem()
    volume_system.Open(test_lvm_container_path_spec)

    file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        output_writer=test_output_writer)

    test_mediator._PrintLVMVolumeIdentifiersOverview(
        volume_system, ['lvm1'])

    file_object.seek(0, os.SEEK_SET)
    output_data = file_object.read()

    expected_output_data = [
        b'The following Logical Volume Manager (LVM) volumes were found:',
        b'',
        b'Identifier',
        b'lvm1',
        b'']

    if not win32console:
      # Using join here since Python 3 does not support format of bytes.
      expected_output_data[2] = b''.join([
          b'\x1b[1m', expected_output_data[2], b'\x1b[0m'])

    self.assertEqual(output_data.split(b'\n'), expected_output_data)

  def testPrintTSKPartitionIdentifiersOverview(self):
    """Tests the _PrintTSKPartitionIdentifiersOverview function."""
    test_path = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, parent=test_raw_path_spec)

    volume_system = tsk_volume_system.TSKVolumeSystem()
    volume_system.Open(test_tsk_partition_path_spec)

    file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        output_writer=test_output_writer)

    test_mediator._PrintPartitionIdentifiersOverview(
        volume_system, ['p1', 'p2'])

    file_object.seek(0, os.SEEK_SET)
    output_data = file_object.read()

    expected_output_data = [
        b'The following partitions were found:',
        b'',
        b'Identifier      Offset (in bytes)       Size (in bytes)',
        b'p1              512 (0x00000200)        64.5KiB / 66.0kB (66048 B)',
        b'p2              67072 (0x00010600)      64.5KiB / 66.0kB (66048 B)',
        b'']

    if not win32console:
      # Using join here since Python 3 does not support format of bytes.
      expected_output_data[2] = b''.join([
          b'\x1b[1m', expected_output_data[2], b'\x1b[0m'])

    self.assertEqual(output_data.split(b'\n'), expected_output_data)

  def testPrintVSSStoreIdentifiersOverview(self):
    """Tests the _PrintVSSStoreIdentifiersOverview function."""
    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)
    test_vss_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, parent=test_qcow_path_spec)

    volume_system = vshadow_volume_system.VShadowVolumeSystem()
    volume_system.Open(test_vss_path_spec)

    file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        output_writer=test_output_writer)

    test_mediator._PrintVSSStoreIdentifiersOverview(
        volume_system, ['vss1', 'vss2'])

    file_object.seek(0, os.SEEK_SET)
    output_data = file_object.read()

    expected_output_data = [
        b'The following Volume Shadow Snapshots (VSS) were found:',
        b'',
        b'Identifier      Creation Time',
        b'vss1            2013-12-03 06:35:09.7363787',
        b'vss2            2013-12-03 06:37:48.9190583',
        b'']

    if not win32console:
      # Using join here since Python 3 does not support format of bytes.
      expected_output_data[2] = b''.join([
          b'\x1b[1m', expected_output_data[2], b'\x1b[0m'])

    self.assertEqual(output_data.split(b'\n'), expected_output_data)

  # TODO: add tests for _ReadSelectedVolumes

  def testGetAPFSVolumeIdentifiers(self):
    """Tests the GetAPFSVolumeIdentifiers function."""
    test_path = self._GetTestFilePath(['apfs.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_apfs_container_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_APFS_CONTAINER, location='/',
        parent=test_raw_path_spec)

    volume_system = apfs_volume_system.APFSVolumeSystem()
    volume_system.Open(test_apfs_container_path_spec)

    # Test selection of single volume.
    input_file_object = io.BytesIO(b'1\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetAPFSVolumeIdentifiers(
        volume_system, ['apfs1'])

    self.assertEqual(volume_identifiers, ['apfs1'])

    # Test selection of single volume.
    input_file_object = io.BytesIO(b'apfs1\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetAPFSVolumeIdentifiers(
        volume_system, ['apfs1'])

    self.assertEqual(volume_identifiers, ['apfs1'])

    # Test selection of single volume with invalid input on first attempt.
    input_file_object = io.BytesIO(b'bogus\napfs1\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetAPFSVolumeIdentifiers(
        volume_system, ['apfs1'])

    self.assertEqual(volume_identifiers, ['apfs1'])

    # Test selection of all volumes.
    input_file_object = io.BytesIO(b'all\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetAPFSVolumeIdentifiers(
        volume_system, ['apfs1'])

    self.assertEqual(volume_identifiers, ['apfs1'])

    # Test selection of no volumes.
    input_file_object = io.BytesIO(b'\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetAPFSVolumeIdentifiers(
        volume_system, ['apfs1'])

    self.assertEqual(volume_identifiers, [])

  def testGetLVMVolumeIdentifiers(self):
    """Tests the GetLVMVolumeIdentifiers function."""
    test_path = self._GetTestFilePath(['lvm.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_lvm_container_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_LVM, location='/', parent=test_raw_path_spec)

    volume_system = lvm_volume_system.LVMVolumeSystem()
    volume_system.Open(test_lvm_container_path_spec)

    # Test selection of single volume.
    input_file_object = io.BytesIO(b'1\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetLVMVolumeIdentifiers(
        volume_system, ['lvm1'])

    self.assertEqual(volume_identifiers, ['lvm1'])

    # Test selection of single volume.
    input_file_object = io.BytesIO(b'lvm1\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetLVMVolumeIdentifiers(
        volume_system, ['lvm1'])

    self.assertEqual(volume_identifiers, ['lvm1'])

    # Test selection of single volume with invalid input on first attempt.
    input_file_object = io.BytesIO(b'bogus\nlvm1\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetLVMVolumeIdentifiers(
        volume_system, ['lvm1'])

    self.assertEqual(volume_identifiers, ['lvm1'])

    # Test selection of all volumes.
    input_file_object = io.BytesIO(b'all\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetLVMVolumeIdentifiers(
        volume_system, ['lvm1', 'lvm2'])

    self.assertEqual(volume_identifiers, ['lvm1', 'lvm2'])

    # Test selection of no volumes.
    input_file_object = io.BytesIO(b'\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetLVMVolumeIdentifiers(
        volume_system, ['lvm1'])

    self.assertEqual(volume_identifiers, [])

  def testGetPartitionIdentifiers(self):
    """Tests the GetPartitionIdentifiers function."""
    test_path = self._GetTestFilePath(['mbr.raw'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_raw_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_RAW, parent=test_os_path_spec)
    test_tsk_partition_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_TSK_PARTITION, parent=test_raw_path_spec)

    volume_system = tsk_volume_system.TSKVolumeSystem()
    volume_system.Open(test_tsk_partition_path_spec)

    file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        output_writer=test_output_writer)

    # Test selection of single partition.
    input_file_object = io.BytesIO(b'2\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetPartitionIdentifiers(
        volume_system, ['p1', 'p2'])

    self.assertEqual(volume_identifiers, ['p2'])

    # Test selection of single partition.
    input_file_object = io.BytesIO(b'p2\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetPartitionIdentifiers(
        volume_system, ['p1', 'p2'])

    self.assertEqual(volume_identifiers, ['p2'])

    # Test selection of single partition with invalid input on first attempt.
    input_file_object = io.BytesIO(b'bogus\np2\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetPartitionIdentifiers(
        volume_system, ['p1', 'p2'])

    self.assertEqual(volume_identifiers, ['p2'])

    # Test selection of all partitions.
    input_file_object = io.BytesIO(b'all\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetPartitionIdentifiers(
        volume_system, ['p1', 'p2'])

    self.assertEqual(volume_identifiers, ['p1', 'p2'])

    # Test selection of no partitions.
    input_file_object = io.BytesIO(b'\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetPartitionIdentifiers(
        volume_system, ['p1', 'p2'])

    self.assertEqual(volume_identifiers, [])

  def testGetVSSStoreIdentifiers(self):
    """Tests the GetVSSStoreIdentifiers function."""
    test_path = self._GetTestFilePath(['vsstest.qcow2'])
    self._SkipIfPathNotExists(test_path)

    test_os_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_OS, location=test_path)
    test_qcow_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_QCOW, parent=test_os_path_spec)
    test_vss_path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.TYPE_INDICATOR_VSHADOW, parent=test_qcow_path_spec)

    volume_system = vshadow_volume_system.VShadowVolumeSystem()
    volume_system.Open(test_vss_path_spec)

    file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        output_writer=test_output_writer)

    # Test selection of single store.
    input_file_object = io.BytesIO(b'2\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetVSSStoreIdentifiers(
        volume_system, ['vss1', 'vss2'])

    self.assertEqual(volume_identifiers, ['vss2'])

    # Test selection of single store.
    input_file_object = io.BytesIO(b'vss2\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetVSSStoreIdentifiers(
        volume_system, ['vss1', 'vss2'])

    self.assertEqual(volume_identifiers, ['vss2'])

    # Test selection of single store with invalid input on first attempt.
    input_file_object = io.BytesIO(b'bogus\nvss2\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetVSSStoreIdentifiers(
        volume_system, ['vss1', 'vss2'])

    self.assertEqual(volume_identifiers, ['vss2'])

    # Test selection of all stores.
    input_file_object = io.BytesIO(b'all\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetVSSStoreIdentifiers(
        volume_system, ['vss1', 'vss2'])

    self.assertEqual(volume_identifiers, ['vss1', 'vss2'])

    # Test selection of no stores.
    input_file_object = io.BytesIO(b'\n')
    test_input_reader = command_line.FileObjectInputReader(input_file_object)

    output_file_object = io.BytesIO()
    test_output_writer = command_line.FileObjectOutputWriter(output_file_object)

    test_mediator = command_line.CLIVolumeScannerMediator(
        input_reader=test_input_reader, output_writer=test_output_writer)

    volume_identifiers = test_mediator.GetVSSStoreIdentifiers(
        volume_system, ['vss1', 'vss2'])

    self.assertEqual(volume_identifiers, [])

  # TODO: add tests for UnlockEncryptedVolume


if __name__ == '__main__':
  unittest.main()

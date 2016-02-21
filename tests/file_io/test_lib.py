# -*- coding: utf-8 -*-
"""Shared test cases."""

import os
import unittest

from dfvfs.file_io import tsk_file_io
from dfvfs.file_io import tsk_partition_file_io
from dfvfs.lib import errors
from dfvfs.path import tsk_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.resolver import context


class ImageFileTestCase(unittest.TestCase):
  """The unit test case for storage media image based test data."""

  _INODE_ANOTHER_FILE = 16
  _INODE_PASSWORDS_TXT = 15

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def _TestOpenCloseInode(self, parent_path_spec):
    """Test the open and close functionality using an inode.

    Args:
      parent_path_spec: the parent path specification.
    """
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=self._INODE_PASSWORDS_TXT, parent=parent_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

  def _TestOpenCloseLocation(self, parent_path_spec):
    """Test the open and close functionality using a location.

    Args:
      parent_path_spec: the parent path specification.
    """
    path_spec = tsk_path_spec.TSKPathSpec(
        location=u'/passwords.txt', parent=parent_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

  def _TestSeek(self, parent_path_spec):
    """Test the seek functionality.

    Args:
      parent_path_spec: the parent path specification.
    """
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=self._INODE_ANOTHER_FILE, location=u'/a_directory/another_file',
        parent=parent_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 22)

    file_object.seek(10)
    self.assertEqual(file_object.read(5), b'other')
    self.assertEqual(file_object.get_offset(), 15)

    file_object.seek(-10, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'her f')

    file_object.seek(2, os.SEEK_CUR)
    self.assertEqual(file_object.read(2), b'e.')

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    file_object.seek(300, os.SEEK_SET)
    self.assertEqual(file_object.get_offset(), 300)
    self.assertEqual(file_object.read(2), b'')

    with self.assertRaises(IOError):
      file_object.seek(-10, os.SEEK_SET)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), 300)

    with self.assertRaises(IOError):
      file_object.seek(10, 5)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), 300)

    file_object.close()

  def _TestRead(self, parent_path_spec):
    """Test the read functionality.

    Args:
      parent_path_spec: the parent path specification.
    """
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=self._INODE_PASSWORDS_TXT, location=u'/passwords.txt',
        parent=parent_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    read_buffer = file_object.read()

    expected_buffer = (
        b'place,user,password\n'
        b'bank,joesmith,superrich\n'
        b'alarm system,-,1234\n'
        b'treasure chest,-,1111\n'
        b'uber secret laire,admin,admin\n')

    self.assertEqual(read_buffer, expected_buffer)

    # TODO: add boundary scenarios.

    file_object.close()


class PartitionedImageFileTestCase(unittest.TestCase):
  """The unit test case for partitioned storage media image based test data."""

  _BYTES_PER_SECTOR = 512

  # mmls test_data/tsk_volume_system.raw
  # DOS Partition Table
  # Offset Sector: 0
  # Units are in 512-byte sectors
  #
  #      Slot    Start        End          Length       Description
  # 00:  Meta    0000000000   0000000000   0000000001   Primary Table (#0)
  # 01:  -----   0000000000   0000000000   0000000001   Unallocated
  # 02:  00:00   0000000001   0000000350   0000000350   Linux (0x83)
  # 03:  Meta    0000000351   0000002879   0000002529   DOS Extended (0x05)
  # 04:  Meta    0000000351   0000000351   0000000001   Extended Table (#1)
  # 05:  -----   0000000351   0000000351   0000000001   Unallocated
  # 06:  01:00   0000000352   0000002879   0000002528   Linux (0x83)

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def _TestOpenClose(self, parent_path_spec):
    """Test the open and close functionality.

    Args:
      parent_path_spec: the parent path specification.
    """
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=2, parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 350 * self._BYTES_PER_SECTOR)
    file_object.close()

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=13, parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p2', parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 2528 * self._BYTES_PER_SECTOR)
    file_object.close()

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p0', parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location=u'/p3', parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        start_offset=(352 * self._BYTES_PER_SECTOR), parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 2528 * self._BYTES_PER_SECTOR)
    file_object.close()

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        start_offset=(350 * self._BYTES_PER_SECTOR), parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

  def _TestSeek(self, parent_path_spec):
    """Test the seek functionality.

    Args:
      parent_path_spec: the parent path specification.
    """
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=6, parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)
    partition_offset = 352 * self._BYTES_PER_SECTOR

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 2528 * self._BYTES_PER_SECTOR)

    file_object.seek(0x7420)
    self.assertEqual(file_object.get_offset(), 0x33420 - partition_offset)
    self.assertEqual(
        file_object.read(16), b'lost+found\x00\x00\x00\x00\x00\x00')
    self.assertEqual(file_object.get_offset(), 0x33430 - partition_offset)

    file_object.seek(-1251324, os.SEEK_END)
    self.assertEqual(file_object.get_offset(), 0x36804 - partition_offset)
    self.assertEqual(file_object.read(8), b'\x03\x00\x00\x00\x04\x00\x00\x00')
    self.assertEqual(file_object.get_offset(), 0x3680c - partition_offset)

    file_object.seek(4, os.SEEK_CUR)
    self.assertEqual(file_object.get_offset(), 0x36810 - partition_offset)
    self.assertEqual(file_object.read(7), b'\x06\x00\x00\x00\x00\x00\x00')
    self.assertEqual(file_object.get_offset(), 0x36817 - partition_offset)

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    expected_offset = (2528 * self._BYTES_PER_SECTOR) + 100
    file_object.seek(expected_offset, os.SEEK_SET)
    self.assertEqual(file_object.get_offset(), expected_offset)
    self.assertEqual(file_object.read(20), b'')

    with self.assertRaises(IOError):
      file_object.seek(-10, os.SEEK_SET)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), expected_offset)

    with self.assertRaises(IOError):
      file_object.seek(10, 5)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), expected_offset)

    file_object.close()

  def _TestRead(self, parent_path_spec):
    """Test the read functionality.

    Args:
      parent_path_spec: the parent path specification.
    """
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=6, parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)
    partition_offset = 352 * self._BYTES_PER_SECTOR

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 2528 * self._BYTES_PER_SECTOR)

    file_object.seek(0x2e900 - partition_offset)

    expected_data = (
        b'\xc0\x41\x00\x00\x00\x30\x00\x00\xc8\x8c\xb9\x52\xc8\x8c\xb9\x52'
        b'\xc8\x8c\xb9\x52\x00\x00\x00\x00\x00\x00\x02\x00\x18\x00\x00\x00')

    self.assertEqual(file_object.read(32), expected_data)

    file_object.close()


class SylogTestCase(unittest.TestCase):
  """The unit test case for the syslog test data."""

  def _TestGetSizeFileObject(self, file_object):
    """Runs the get size tests on the file-like object.

    Args:
      file_object: the file-like object with the test data.
    """
    self.assertEqual(file_object.get_size(), 1247)

  def _TestReadFileObject(self, file_object, base_offset=167):
    """Runs the read tests on the file-like object.

    Args:
      file_object: the file-like object with the test data.
      base_offset: optional base offset use in the tests, the default is 167.
    """
    file_object.seek(base_offset, os.SEEK_SET)

    self.assertEqual(file_object.get_offset(), base_offset)

    expected_buffer = (
        b'Jan 22 07:53:01 myhostname.myhost.com CRON[31051]: (root) CMD '
        b'(touch /var/run/crond.somecheck)\n')

    read_buffer = file_object.read(95)

    self.assertEqual(read_buffer, expected_buffer)

    expected_offset = base_offset + 95

    self.assertEqual(file_object.get_offset(), expected_offset)

  def _TestSeekFileObject(self, file_object, base_offset=167):
    """Runs the seek tests on the file-like object.

    Args:
      file_object: the file-like object with the test data.
      base_offset: optional base offset use in the tests, the default is 167.
    """
    file_object.seek(base_offset + 10)
    self.assertEqual(file_object.read(5), b'53:01')

    expected_offset = base_offset + 15
    self.assertEqual(file_object.get_offset(), expected_offset)

    file_object.seek(-10, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'times')

    file_object.seek(2, os.SEEK_CUR)
    self.assertEqual(file_object.read(2), b'--')

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    file_object.seek(2000, os.SEEK_SET)
    self.assertEqual(file_object.get_offset(), 2000)
    self.assertEqual(file_object.read(2), b'')

    # Test with an invalid offset.
    with self.assertRaises(IOError):
      file_object.seek(-10, os.SEEK_SET)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), 2000)

    # Test with an invalid whence.
    with self.assertRaises(IOError):
      file_object.seek(10, 5)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), 2000)


class PaddedSyslogTestCase(SylogTestCase):
  """The unit test case for padded syslog test data.

  The syslog test data is padded with '=' characters.
  """

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self.padding_size = 0

  def _TestGetSizeFileObject(self, file_object):
    """Runs the get size tests on the file-like object.

    Args:
      file_object: the file-like object with the test data.
    """
    self.assertEqual(file_object.get_size(), 1247 + self.padding_size)

  def _TestSeekFileObject(self, file_object, base_offset=167):
    """Runs the seek tests on the file-like object.

    Args:
      file_object: the file-like object with the test data.
      base_offset: optional base offset use in the tests, the default is 167.
    """
    file_object.seek(base_offset + 10)
    self.assertEqual(file_object.read(5), b'53:01')

    expected_offset = base_offset + 15
    self.assertEqual(file_object.get_offset(), expected_offset)

    file_object.seek(-10 - self.padding_size, os.SEEK_END)
    self.assertEqual(file_object.read(5), b'times')

    file_object.seek(2, os.SEEK_CUR)
    self.assertEqual(file_object.read(2), b'--')

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    file_object.seek(2000, os.SEEK_SET)
    self.assertEqual(file_object.get_offset(), 2000)
    self.assertEqual(file_object.read(2), b'')

    # Test with an invalid offset.
    with self.assertRaises(IOError):
      file_object.seek(-10, os.SEEK_SET)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), 2000)

    # Test with an invalid whence.
    with self.assertRaises(IOError):
      file_object.seek(10, 5)

    # On error the offset should not change.
    self.assertEqual(file_object.get_offset(), 2000)

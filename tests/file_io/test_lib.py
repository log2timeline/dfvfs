# -*- coding: utf-8 -*-
"""Shared test cases."""

from __future__ import unicode_literals

import os

from dfvfs.file_io import tsk_file_io
from dfvfs.file_io import tsk_partition_file_io
from dfvfs.lib import definitions
from dfvfs.lib import errors
from dfvfs.path import factory as path_spec_factory
from dfvfs.path import tsk_path_spec
from dfvfs.path import tsk_partition_path_spec
from dfvfs.resolver import context
from dfvfs.resolver import resolver

from tests import test_lib as shared_test_lib


class Ext2ImageFileTestCase(shared_test_lib.BaseTestCase):
  """Shared functionality for storage media image with an ext2 file system."""

  _INODE_ANOTHER_FILE = 15
  _INODE_PASSWORDS_TXT = 14

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def _TestOpenCloseInode(self, parent_path_spec):
    """Test the open and close functionality using an inode.

    Args:
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.PREFERRED_EXT_BACK_END, inode=self._INODE_PASSWORDS_TXT,
        parent=parent_path_spec)
    file_object = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

  def _TestOpenCloseLocation(self, parent_path_spec):
    """Test the open and close functionality using a location.

    Args:
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.PREFERRED_EXT_BACK_END, location='/passwords.txt',
        parent=parent_path_spec)
    file_object = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

  def _TestSeek(self, parent_path_spec):
    """Test the seek functionality.

    Args:
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.PREFERRED_EXT_BACK_END, inode=self._INODE_ANOTHER_FILE,
        location='/a_directory/another_file', parent=parent_path_spec)
    file_object = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

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
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.PREFERRED_EXT_BACK_END, inode=self._INODE_PASSWORDS_TXT,
        location='/passwords.txt', parent=parent_path_spec)
    file_object = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

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


class ImageFileTestCase(shared_test_lib.BaseTestCase):
  """The unit test case for storage media image based test data."""

  _INODE_ANOTHER_FILE = 16
  _INODE_PASSWORDS_TXT = 15

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def _TestOpenCloseInode(self, parent_path_spec):
    """Test the open and close functionality using an inode.

    Args:
      parent_path_spec (PathSpec): parent path specification.
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
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = tsk_path_spec.TSKPathSpec(
        location='/passwords.txt', parent=parent_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

  def _TestSeek(self, parent_path_spec):
    """Test the seek functionality.

    Args:
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=self._INODE_ANOTHER_FILE, location='/a_directory/another_file',
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
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=self._INODE_PASSWORDS_TXT, location='/passwords.txt',
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


class NTFSImageFileTestCase(shared_test_lib.BaseTestCase):
  """Shared functionality for storage media image with a NTFS file system."""

  _MFT_ENTRY_ANOTHER_FILE = 67
  _MFT_ENTRY_PASSWORDS_TXT = 66

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def _TestOpenCloseMFTEntry(self, path_spec, file_object):
    """Test the open and close functionality using a MFT entry.

    Args:
      path_spec (PathSpec): path specification.
      file_object (FileIO): file-like object.
    """
    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

    # TODO: add a failing scenario.

  def _TestOpenCloseLocation(self, path_spec, file_object):
    """Test the open and close functionality using a location.

    Args:
      path_spec (PathSpec): path specification.
      file_object (FileIO): file-like object.
    """
    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 116)
    file_object.close()

    # Try open with a path specification that has no parent.
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

  def _TestSeek(self, path_spec, file_object):
    """Test the seek functionality.

    Args:
      path_spec (PathSpec): path specification.
      file_object (FileIO): file-like object.
    """
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

  def _TestRead(self, path_spec, file_object):
    """Test the read functionality.

    Args:
      path_spec (PathSpec): path specification.
      file_object (FileIO): file-like object.
    """
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

  def _TestReadADS(self, path_spec, file_object):
    """Test the read functionality on an alternate data stream (ADS).

    Args:
      path_spec (PathSpec): path specification.
      file_object (FileIO): file-like object.
    """
    file_object.open(path_spec=path_spec)

    expected_buffer = (
        b'\xf0\x12\x03\xf8\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

    read_buffer = file_object.read(size=16)
    self.assertEqual(read_buffer, expected_buffer)

    file_object.seek(-8, os.SEEK_END)

    expected_buffer = b'\x20\x00\x00\x00\x20\x02\x00\x00'

    read_buffer = file_object.read(size=16)
    self.assertEqual(read_buffer, expected_buffer)


class MBRPartitionedImageFileTestCase(shared_test_lib.BaseTestCase):
  """Tests for MBR partitioned storage media image based test data."""

  # mmls test_data/mbr.raw
  # DOS Partition Table
  # Offset Sector: 0
  # Units are in 512-byte sectors
  #
  #       Slot      Start        End          Length       Description
  # 000:  Meta      0000000000   0000000000   0000000001   Primary Table (#0)
  # 001:  -------   0000000000   0000000000   0000000001   Unallocated
  # 002:  000:000   0000000001   0000000129   0000000129   Linux (0x83)
  # 003:  Meta      0000000130   0000008191   0000008062   DOS Extended (0x05)
  # 004:  Meta      0000000130   0000000130   0000000001   Extended Table (#1)
  # 005:  -------   0000000130   0000000130   0000000001   Unallocated
  # 006:  001:000   0000000131   0000000259   0000000129   Linux (0x83)
  # 007:  -------   0000000260   0000008191   0000007932   Unallocated

  _BYTES_PER_SECTOR = 512

  _OFFSET_P1 = 1 * _BYTES_PER_SECTOR
  _SIZE_P1 = 129 * _BYTES_PER_SECTOR

  _OFFSET_P2 = 131 * _BYTES_PER_SECTOR
  _SIZE_P2 = 129 * _BYTES_PER_SECTOR

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def _TestOpenClose(self, parent_path_spec):
    """Test the open and close functionality.

    Args:
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=2, parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), self._SIZE_P1)
    file_object.close()

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=13, parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p2', parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), self._SIZE_P2)
    file_object.close()

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p0', parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        location='/p3', parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        start_offset=self._OFFSET_P2, parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), self._SIZE_P2)
    file_object.close()

    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        start_offset=self._SIZE_P1, parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

  def _TestSeek(self, parent_path_spec):
    """Test the seek functionality.

    Args:
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=6, parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), self._SIZE_P2)

    file_object.seek(4128)
    self.assertEqual(file_object.get_offset(), 0x11620 - self._OFFSET_P2)
    self.assertEqual(
        file_object.read(16), b'lost+found\x00\x00\x0c\x00\x00\x00')
    self.assertEqual(file_object.get_offset(), 0x11630 - self._OFFSET_P2)

    file_object.seek(-28156, os.SEEK_END)
    self.assertEqual(file_object.get_offset(), 0x19a04 - self._OFFSET_P2)

    data = file_object.read(8)
    self.assertEqual(data, b' is a te')
    self.assertEqual(file_object.get_offset(), 0x19a0c - self._OFFSET_P2)

    file_object.seek(4, os.SEEK_CUR)
    self.assertEqual(file_object.get_offset(), 0x19a10 - self._OFFSET_P2)

    data = file_object.read(7)
    self.assertEqual(data, b'ile.\n\nW')
    self.assertEqual(file_object.get_offset(), 0x19a17 - self._OFFSET_P2)

    # Conforming to the POSIX seek the offset can exceed the file size
    # but reading will result in no data being returned.
    expected_offset = self._SIZE_P2 + 100
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
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = tsk_partition_path_spec.TSKPartitionPathSpec(
        part_index=6, parent=parent_path_spec)
    file_object = tsk_partition_file_io.TSKPartitionFile(self._resolver_context)

    file_object.open(path_spec=path_spec)

    try:
      self.assertEqual(file_object.get_size(), self._SIZE_P2)

      file_object.seek(0x19e00 - self._OFFSET_P2)

      data = file_object.read(32)
    finally:
      file_object.close()

    self.assertEqual(data, b'place,user,password\nbank,joesmit')


class SylogTestCase(shared_test_lib.BaseTestCase):
  """The unit test case for the syslog test data."""

  def _TestGetSizeFileObject(self, file_object):
    """Runs the get size tests on the file-like object.

    Args:
      file_object (file): file-like object with the test data.
    """
    self.assertEqual(file_object.get_size(), 1247)

  def _TestReadFileObject(self, file_object, base_offset=167):
    """Runs the read tests on the file-like object.

    Args:
      file_object (file): file-like object with the test data.
      base_offset (Optional[int]): base offset use in the tests.
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
      file_object (file): file-like object with the test data.
      base_offset (Optional[int]): base offset use in the tests.
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
      file_object (file): file-like object with the test data.
    """
    self.assertEqual(file_object.get_size(), 1247 + self.padding_size)

  def _TestSeekFileObject(self, file_object, base_offset=167):
    """Runs the seek tests on the file-like object.

    Args:
      file_object (file): file-like object with the test data.
      base_offset (Optional[int]): base offset use in the tests.
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


class WindowsFATImageFileTestCase(shared_test_lib.BaseTestCase):
  """Shared functionality for storage media image with a FAT file system."""

  _INODE_ANOTHER_FILE = 615
  _INODE_PASSWORDS_TXT = 10

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def _TestOpenCloseMFTEntry(self, parent_path_spec):
    """Test the open and close functionality using a MFT entry.

    Args:
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=self._INODE_PASSWORDS_TXT, parent=parent_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 126)
    file_object.close()

    # TODO: add a failing scenario.

  def _TestOpenCloseLocation(self, parent_path_spec):
    """Test the open and close functionality using a location.

    Args:
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = tsk_path_spec.TSKPathSpec(
        location='/passwords.txt', parent=parent_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 126)
    file_object.close()

    # Try open with a path specification that has no parent.
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      file_object.open(path_spec=path_spec)

  def _TestSeek(self, parent_path_spec):
    """Test the seek functionality.

    Args:
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=self._INODE_ANOTHER_FILE, location='/a_directory/another_file',
        parent=parent_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 24)

    file_object.seek(10)
    self.assertEqual(file_object.read(5), b'other')
    self.assertEqual(file_object.get_offset(), 15)

    file_object.seek(-12, os.SEEK_END)
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
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = tsk_path_spec.TSKPathSpec(
        inode=self._INODE_PASSWORDS_TXT, location='/passwords.txt',
        parent=parent_path_spec)
    file_object = tsk_file_io.TSKFile(self._resolver_context)

    file_object.open(path_spec=path_spec)
    read_buffer = file_object.read()

    expected_buffer = (
        b'place,user,password \r\n'
        b'bank,joesmith,superrich \r\n'
        b'alarm system,-,1234 \r\n'
        b'treasure chest,-,1111 \r\n'
        b'uber secret laire,admin,admin \r\n')

    self.assertEqual(read_buffer, expected_buffer)

    # TODO: add boundary scenarios.

    file_object.close()


class WindowsNTFSImageFileTestCase(shared_test_lib.BaseTestCase):
  """Shared functionality for storage media image with a NTFS file system."""

  _MFT_ENTRY_ANOTHER_FILE = 36
  _MFT_ENTRY_PASSWORDS_TXT = 35

  def setUp(self):
    """Sets up the needed objects used throughout the test."""
    self._resolver_context = context.Context()

  def tearDown(self):
    """Cleans up the needed objects used throughout the test."""
    self._resolver_context.Empty()

  def _TestOpenCloseMFTEntry(self, parent_path_spec):
    """Test the open and close functionality using a MFT entry.

    Args:
      parent_path_spec (PathSpec): parent path specification.
    """
    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.PREFERRED_NTFS_BACK_END, mft_attribute=1,
        mft_entry=self._MFT_ENTRY_PASSWORDS_TXT, parent=parent_path_spec)
    file_object = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 126)
    file_object.close()

    # TODO: add a failing scenario.

  def _TestOpenCloseLocation(self, parent_path_spec):
    """Test the open and close functionality using a location.

    Args:
      parent_path_spec (PathSpec): parent path specification.
    """
    if definitions.PREFERRED_NTFS_BACK_END == definitions.TYPE_INDICATOR_TSK:
      location = '/passwords.txt'
    else:
      location = '\\passwords.txt'

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.PREFERRED_NTFS_BACK_END, location=location,
        parent=parent_path_spec)
    file_object = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 126)
    file_object.close()

    # Try open with a path specification that has no parent.
    path_spec.parent = None

    with self.assertRaises(errors.PathSpecError):
      resolver.Resolver.OpenFileObject(
          path_spec, resolver_context=self._resolver_context)

  def _TestSeek(self, parent_path_spec):
    """Test the seek functionality.

    Args:
      parent_path_spec (PathSpec): parent path specification.
    """
    if definitions.PREFERRED_NTFS_BACK_END == definitions.TYPE_INDICATOR_TSK:
      location = '/a_directory/another_file'
    else:
      location = '\\a_directory\\another_file'

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.PREFERRED_NTFS_BACK_END, location=location,
        mft_attribute=2, mft_entry=self._MFT_ENTRY_ANOTHER_FILE,
        parent=parent_path_spec)
    file_object = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

    file_object.open(path_spec=path_spec)
    self.assertEqual(file_object.get_size(), 24)

    file_object.seek(10)
    self.assertEqual(file_object.read(5), b'other')
    self.assertEqual(file_object.get_offset(), 15)

    file_object.seek(-12, os.SEEK_END)
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
      parent_path_spec (PathSpec): parent path specification.
    """
    if definitions.PREFERRED_NTFS_BACK_END == definitions.TYPE_INDICATOR_TSK:
      location = '/passwords.txt'
    else:
      location = '\\passwords.txt'

    path_spec = path_spec_factory.Factory.NewPathSpec(
        definitions.PREFERRED_NTFS_BACK_END, location=location,
        mft_attribute=2, mft_entry=self._MFT_ENTRY_PASSWORDS_TXT,
        parent=parent_path_spec)
    file_object = resolver.Resolver.OpenFileObject(
        path_spec, resolver_context=self._resolver_context)

    file_object.open(path_spec=path_spec)
    read_buffer = file_object.read()

    expected_buffer = (
        b'place,user,password \r\n'
        b'bank,joesmith,superrich \r\n'
        b'alarm system,-,1234 \r\n'
        b'treasure chest,-,1111 \r\n'
        b'uber secret laire,admin,admin \r\n')

    self.assertEqual(read_buffer, expected_buffer)

    # TODO: add boundary scenarios.

    file_object.close()

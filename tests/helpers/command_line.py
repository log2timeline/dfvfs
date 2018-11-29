#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Tests for the volume scanner objects."""

from __future__ import unicode_literals

import unittest

from dfvfs.helpers import command_line

from tests import test_lib as shared_test_lib


class CLITabularTableViewTest(shared_test_lib.BaseTestCase):
  """Tests for the command line tabular table view class."""

  # TODO: add tests for _PrintRow
  # TODO: add tests for AddRow
  # TODO: add tests for Print


class CLIVolumeScannerMediatorTest(shared_test_lib.BaseTestCase):
  """Tests for the command line volume scanner mediator."""

  # pylint: disable=protected-access

  # TODO: add tests for _EncodeString

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

  # TODO: add tests for _ParseVSSStoresString
  # TODO: add tests for GetPartitionIdentifiers
  # TODO: add tests for UnlockEncryptedVolume


if __name__ == '__main__':
  unittest.main()

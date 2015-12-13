#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the fake file system builder object."""

import unittest

from dfvfs.helpers import fake_file_system_builder


class FakeFileSystemBuilderTest(unittest.TestCase):
  """The unit test for the fake file system builder object."""

  maxDiff = None


if __name__ == '__main__':
  unittest.main()

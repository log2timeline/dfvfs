#!/usr/bin/python
# -*- coding: utf-8 -*-
"""Tests for the format specification classes."""

import unittest

from dfvfs.analyzer import specification


class SpecificationStoreTest(unittest.TestCase):
  """Class to test the specification store."""

  def testAddSpecification(self):
    """Function to test the add specification function."""
    store = specification.SpecificationStore()

    format_regf = specification.Specification('REGF')
    format_regf.AddNewSignature('regf', offset=0)

    format_esedb = specification.Specification('ESEDB')
    format_esedb.AddNewSignature('\xef\xcd\xab\x89', offset=4)

    store.AddSpecification(format_regf)
    store.AddSpecification(format_esedb)

    with self.assertRaises(KeyError):
      store.AddSpecification(format_regf)


if __name__ == '__main__':
  unittest.main()

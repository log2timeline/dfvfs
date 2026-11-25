#!/usr/bin/env python3
"""Tests for the Virtual File System (VFS) path specification interface."""

import unittest

from dfvfs.path import path_spec

from tests.path import test_lib


class TestPathSpec(path_spec.PathSpec):
    """Path specification for testing."""

    TYPE_INDICATOR = "test"

    def __init__(self, parent=None, **kwargs):
        """Initializes a path specification.

        Args:
          parent (Optional[PathSpec]): parent path specification.
        """
        super().__init__(parent=parent, **kwargs)
        self.attribute = "MyAttribute"


class TestComparablePathSpec(path_spec.PathSpec):
    """Path specification with its own comparable property for testing."""

    TYPE_INDICATOR = "test_comparable"

    def __init__(self, location=None, parent=None, **kwargs):
        """Initializes a path specification.

        Args:
          location (Optional[str]): location.
          parent (Optional[PathSpec]): parent path specification.
        """
        super().__init__(parent=parent, **kwargs)
        self.location = location
        self.calls = 0

    @property
    def comparable(self):
        """str: comparable representation of the path specification."""
        self.__dict__["calls"] += 1
        return self._GetComparable(sub_comparable_string=f"location: {self.location}")


class PathSpecTest(test_lib.PathSpecTestCase):
    """Tests for the VFS path specification interface."""

    # pylint: disable=protected-access

    def testInitialize(self):
        """Tests the __init__ function."""
        with self.assertRaises(ValueError):
            path_spec.PathSpec()

    def testEqualAndHash(self):
        """Tests the __eq__ and __hash__ functions."""
        test_path_spec = TestComparablePathSpec(location="/a")
        same_path_spec = TestComparablePathSpec(location="/a")
        other_path_spec = TestComparablePathSpec(location="/b")

        self.assertEqual(test_path_spec, test_path_spec)
        self.assertEqual(test_path_spec, same_path_spec)
        self.assertEqual(hash(test_path_spec), hash(same_path_spec))
        self.assertNotEqual(test_path_spec, other_path_spec)
        self.assertNotEqual(test_path_spec, "/a")

    def testComparableCache(self):
        """Tests the comparable property is cached and invalidated."""
        parent_path_spec = TestComparablePathSpec(location="/p")
        test_path_spec = TestComparablePathSpec(location="/a", parent=parent_path_spec)

        expected = (
            "type: test_comparable, location: /p\n"
            "type: test_comparable, location: /a\n"
        )
        self.assertEqual(test_path_spec.comparable, expected)
        self.assertEqual(test_path_spec.calls, 1)
        self.assertEqual(parent_path_spec.calls, 1)

        hash(test_path_spec)
        self.assertEqual(test_path_spec, test_path_spec)
        self.assertEqual(test_path_spec.comparable, expected)
        self.assertEqual(test_path_spec.calls, 1)
        self.assertEqual(parent_path_spec.calls, 1)

        # Changing the path specification itself invalidates the cache.
        test_path_spec.location = "/b"
        self.assertEqual(test_path_spec.comparable.splitlines()[-1].split()[-1], "/b")
        self.assertEqual(test_path_spec.calls, 2)

        # Changing the parent invalidates the cache of the child.
        parent_path_spec.location = "/q"
        self.assertTrue(
            test_path_spec.comparable.startswith(
                "type: test_comparable, location: /q\n"
            )
        )

        # Replacing the parent invalidates the cache.
        test_path_spec.parent = None
        self.assertEqual(
            test_path_spec.comparable, "type: test_comparable, location: /b\n"
        )

        # The cache is not part of the attributes.
        self.assertNotIn("_comparable_cache", test_path_spec.CopyToDict())

    def testComparableCacheBaseClass(self):
        """Tests the comparable cache for a class without its own property."""
        parent_path_spec = TestPathSpec()
        test_path_spec = TestPathSpec(parent=parent_path_spec)
        self.assertEqual(test_path_spec.comparable, "type: test\ntype: test\n")

        parent_path_spec.attribute = "other"
        test_path_spec.attribute = "other"
        self.assertEqual(test_path_spec.comparable, "type: test\ntype: test\n")
        self.assertEqual(
            test_path_spec.CopyToDict(),
            {"attribute": "other", "parent": {"attribute": "other"}},
        )

    def testGetComparable(self):
        """Tests the _GetComparable function."""
        test_path_spec = TestPathSpec()

        test_comparable = test_path_spec._GetComparable()
        self.assertEqual(test_comparable, "type: test\n")

    def testComparable(self):
        """Tests the comparable property."""
        test_path_spec = TestPathSpec()

        self.assertEqual(test_path_spec.comparable, "type: test\n")

    def testTypeIndicator(self):
        """Tests the type_indicator property."""
        test_path_spec = TestPathSpec()

        self.assertEqual(test_path_spec.type_indicator, "test")

    def testCopyToDict(self):
        """Tests the CopyToDict function."""
        test_path_spec = TestPathSpec()

        test_dict = test_path_spec.CopyToDict()
        self.assertEqual(test_dict, {"attribute": "MyAttribute"})

    def testHasParent(self):
        """Tests the HasParent function."""
        test_path_spec = TestPathSpec()

        self.assertFalse(test_path_spec.HasParent())

    def testIsFileSystem(self):
        """Tests the IsFileSystem function."""
        test_path_spec = TestPathSpec()

        self.assertFalse(test_path_spec.IsFileSystem())

    def testIsSystemLevel(self):
        """Tests the IsSystemLevel function."""
        test_path_spec = TestPathSpec()

        self.assertFalse(test_path_spec.IsSystemLevel())

    def testIsVolumeSystem(self):
        """Tests the IsVolumeSystem function."""
        test_path_spec = TestPathSpec()

        self.assertFalse(test_path_spec.IsVolumeSystem())

    def testIsVolumeSystemRoot(self):
        """Tests the IsVolumeSystemRoot function."""
        test_path_spec = TestPathSpec()

        self.assertFalse(test_path_spec.IsVolumeSystemRoot())


if __name__ == "__main__":
    unittest.main()

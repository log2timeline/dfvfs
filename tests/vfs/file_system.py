#!/usr/bin/env python3
"""Tests for the VFS file system object interface."""

import unittest

from dfvfs.path import fake_path_spec
from dfvfs.resolver import context
from dfvfs.vfs import file_system

from tests import test_lib as shared_test_lib


class TestFileSystem(file_system.FileSystem):
    """File system for testing."""

    # pylint: disable=abstract-method

    TYPE_INDICATOR = "test"


class FileSystemTest(shared_test_lib.BaseTestCase):
    """Tests the VFS file system object interface."""

    def setUp(self):
        """Sets up the needed objects used throughout the test."""
        self._resolver_context = context.Context()

    def testInitialize(self):
        """Test the __init__ function."""
        path_spec = fake_path_spec.FakePathSpec(location="/")

        with self.assertRaises(ValueError):
            file_system.FileSystem(self._resolver_context, path_spec)

    # TODO: add tests for type_indicator property.
    # TODO: add tests for _Close function.
    # TODO: add tests for _Open function.
    # TODO: add tests for BasenamePath function.
    # TODO: add tests for Close function.
    # TODO: add tests for DirnamePath function.
    # TODO: add tests for GetDataStreamByPathSpec function.
    # TODO: add tests for GetFileObjectByPathSpec function.
    # TODO: add tests for GetPathSegmentAndSuffix function.

    def testJoinPath(self):
        """Test the join path functionality."""
        path_spec = fake_path_spec.FakePathSpec(location="/")

        test_file_system = TestFileSystem(self._resolver_context, path_spec)

        expected_path = "/test1/test2/test3"

        path = test_file_system.JoinPath(["test1", "test2", "test3"])
        self.assertEqual(path, expected_path)

        path = test_file_system.JoinPath(["/test1", "test2//", "test3/"])
        self.assertEqual(path, expected_path)

        path = test_file_system.JoinPath(["/test1/test2/", "/test3/"])
        self.assertEqual(path, expected_path)

        path = test_file_system.JoinPath(["/test1///test2", "test3"])
        self.assertEqual(path, expected_path)

    def testJoinPathFastPath(self):
        """Test the join path fast path against the generic implementation."""
        path_spec = fake_path_spec.FakePathSpec(location="/")

        test_file_system = TestFileSystem(self._resolver_context, path_spec)

        def _ReferenceJoinPath(path_segments):
            """Joins path segments without the fast path."""
            separator = test_file_system.PATH_SEPARATOR
            path_segments = [segment.split(separator) for segment in path_segments]
            path_segments = [
                element for sublist in path_segments for element in sublist
            ]
            path_segments = list(filter(None, path_segments))
            return "".join([separator, separator.join(path_segments)])

        values = [
            "",
            "/",
            "//",
            "a",
            "/a",
            "a/",
            "/a/",
            "/a//b",
            "/a/b",
            "a/b",
            ".",
            "/.",
            "/./a",
            "..",
            "/a/..",
            "/a b",
            "\u00e9",
        ]
        for location in values:
            for name in values:
                self.assertEqual(
                    test_file_system.JoinPath([location, name]),
                    _ReferenceJoinPath([location, name]),
                    msg=f"{location!r} {name!r}",
                )

        for segments in ([], ["a"], ["/a", "b", "c"], ["", "", ""]):
            self.assertEqual(
                test_file_system.JoinPath(segments), _ReferenceJoinPath(segments)
            )

    # TODO: add tests for Open function.

    def testSplitPath(self):
        """Test the split path functionality."""
        path_spec = fake_path_spec.FakePathSpec(location="/")

        test_file_system = TestFileSystem(self._resolver_context, path_spec)

        expected_path_segments = ["test1", "test2", "test3"]

        path_segments = test_file_system.SplitPath("/test1/test2/test3")
        self.assertEqual(path_segments, expected_path_segments)

        path_segments = test_file_system.SplitPath("/test1/test2/test3/")
        self.assertEqual(path_segments, expected_path_segments)

        path_segments = test_file_system.SplitPath("/test1///test2/test3")
        self.assertEqual(path_segments, expected_path_segments)


if __name__ == "__main__":
    unittest.main()

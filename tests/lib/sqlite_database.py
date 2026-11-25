#!/usr/bin/env python3
"""Tests for the SQLite database file helper."""

import io
import os
import sqlite3
import tempfile
import unittest

from dfvfs.lib import sqlite_database

from tests import test_lib as shared_test_lib


class TestFileObject(io.BytesIO):
    """In-memory file-like object that records the size of every read."""

    def __init__(self, data):
        """Initializes the file-like object.

        Args:
          data (bytes): data.
        """
        super().__init__(data)
        self.read_sizes = []

    def read(self, size=-1):
        """Reads data and records the requested size."""
        self.read_sizes.append(size)
        return super().read(size)


class SQLiteDatabaseFileTest(shared_test_lib.BaseTestCase):
    """Tests for the SQLite database file."""

    # pylint: disable=protected-access

    def _CreateDatabase(self, number_of_rows):
        """Creates a SQLite database.

        Args:
          number_of_rows (int): number of rows to store.

        Returns:
          bytes: database file content.
        """
        with tempfile.TemporaryDirectory(ignore_cleanup_errors=True) as temp_directory:
            path = os.path.join(temp_directory, "test.db")
            connection = sqlite3.connect(path)
            connection.execute("CREATE TABLE test (id INTEGER, value TEXT)")
            connection.executemany(
                "INSERT INTO test VALUES (?, ?)",
                ((index, "x" * 100) for index in range(number_of_rows)),
            )
            connection.commit()
            connection.close()

            with open(path, "rb") as file_object:
                return file_object.read()

    def testOpenClose(self):
        """Tests the Open and Close functions."""
        test_file_object = TestFileObject(self._CreateDatabase(10))

        database_file = sqlite_database.SQLiteDatabaseFile()
        database_file.Open(test_file_object)
        try:
            self.assertEqual(database_file.GetNumberOfRows("test"), 10)
            self.assertTrue(os.path.exists(database_file._temp_file_path))
        finally:
            temp_file_path = database_file._temp_file_path
            database_file.Close()

        self.assertFalse(os.path.exists(temp_file_path))

        with self.assertRaises(ValueError):
            database_file.Open(None)

        with self.assertRaises(OSError):
            database_file.Open(TestFileObject(b"Not a SQLite database file"))

    def testOpenCopiesInLargeChunks(self):
        """Tests that Open copies a larger database using large read buffers."""
        # Approximately 6 MiB of database content.
        test_file_object = TestFileObject(self._CreateDatabase(45000))
        self.assertGreater(len(test_file_object.getvalue()), 4 * 1024 * 1024)

        database_file = sqlite_database.SQLiteDatabaseFile()
        database_file.Open(test_file_object)
        try:
            self.assertEqual(database_file.GetNumberOfRows("test"), 45000)

            with open(database_file._temp_file_path, "rb") as file_object:
                self.assertEqual(file_object.read(), test_file_object.getvalue())
        finally:
            database_file.Close()

        # One read for the signature, then reads of the copy buffer size, which
        # must be at least 1 MiB to limit the number of read calls.
        self.assertGreaterEqual(
            sqlite_database.SQLiteDatabaseFile._COPY_BUFFER_SIZE, 1024 * 1024
        )
        self.assertEqual(
            set(test_file_object.read_sizes[1:]),
            {sqlite_database.SQLiteDatabaseFile._COPY_BUFFER_SIZE},
        )
        self.assertLessEqual(len(test_file_object.read_sizes), 6)


if __name__ == "__main__":
    unittest.main()

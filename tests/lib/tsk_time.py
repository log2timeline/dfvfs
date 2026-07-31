#!/usr/bin/env python3
"""Tests for the SleuthKit (TSK) timestamp."""

import decimal
import unittest

import pytsk3

from dfvfs.lib import tsk_time


class TSKTimeTest(unittest.TestCase):
    """Tests for the SleuthKit timestamp."""

    # pylint: disable=protected-access

    def testGetNormalizedTimestamp(self):
        """Tests the _GetNormalizedTimestamp function."""
        if pytsk3.TSK_VERSION_NUM >= 0x040200FF:
            fraction_of_second = 546875000
        else:
            fraction_of_second = 5468750

        tsk_time_object = tsk_time.TSKTime(
            fraction_of_second=fraction_of_second, timestamp=1281643591
        )
        normalized_timestamp = tsk_time_object._GetNormalizedTimestamp()
        self.assertEqual(normalized_timestamp, decimal.Decimal("1281643591.546875"))

        tsk_time_object = tsk_time.TSKTime(
            fraction_of_second=fraction_of_second,
            time_zone_offset=60,
            timestamp=1281643591,
        )
        normalized_timestamp = tsk_time_object._GetNormalizedTimestamp()
        self.assertEqual(normalized_timestamp, decimal.Decimal("1281639991.546875"))

        tsk_time_object = tsk_time.TSKTime(
            fraction_of_second=fraction_of_second, timestamp=1281643591
        )
        tsk_time_object.time_zone_offset = 60

        normalized_timestamp = tsk_time_object._GetNormalizedTimestamp()
        self.assertEqual(normalized_timestamp, decimal.Decimal("1281639991.546875"))

        tsk_time_object = tsk_time.TSKTime()

        normalized_timestamp = tsk_time_object._GetNormalizedTimestamp()
        self.assertIsNone(normalized_timestamp)

    def testCopyFromDateTimeString(self):
        """Tests the CopyFromDateTimeString function."""
        tsk_time_object = tsk_time.TSKTime()

        if pytsk3.TSK_VERSION_NUM >= 0x040200FF:
            expected_fraction_of_second = 546875000
        else:
            expected_fraction_of_second = 5468750

        tsk_time_object.CopyFromDateTimeString("2010-08-12 21:06:31.546875")
        self.assertEqual(tsk_time_object.timestamp, 1281647191)
        self.assertEqual(
            tsk_time_object.fraction_of_second, expected_fraction_of_second
        )
        tsk_time_object.CopyFromDateTimeString("2010-08-12 21:06:31.546875-01:00")
        self.assertEqual(tsk_time_object.timestamp, 1281647191)
        self.assertEqual(tsk_time_object._time_zone_offset, -60)

        tsk_time_object.CopyFromDateTimeString("2010-08-12 21:06:31.546875+01:00")
        self.assertEqual(tsk_time_object._timestamp, 1281647191)
        self.assertEqual(tsk_time_object._time_zone_offset, 60)

    def testCopyToDateTimeString(self):
        """Tests the CopyToDateTimeString function."""
        if pytsk3.TSK_VERSION_NUM >= 0x040200FF:
            fraction_of_second = 546875000
        else:
            fraction_of_second = 5468750

        tsk_time_object = tsk_time.TSKTime(
            fraction_of_second=fraction_of_second, timestamp=1281643591
        )
        if pytsk3.TSK_VERSION_NUM >= 0x040200FF:
            expected_date_time_string = "2010-08-12 20:06:31.546875000"
        else:
            expected_date_time_string = "2010-08-12 20:06:31.5468750"
        date_time_string = tsk_time_object.CopyToDateTimeString()
        self.assertEqual(date_time_string, expected_date_time_string)

        tsk_time_object = tsk_time.TSKTime()

        date_time_string = tsk_time_object.CopyToDateTimeString()
        self.assertIsNone(date_time_string)

    def testCopyToSerializableDict(self):
        """Test the CopyToSerializableDict function."""
        if pytsk3.TSK_VERSION_NUM >= 0x040200FF:
            fraction_of_second = 546875000
        else:
            fraction_of_second = 5468750

        tsk_time_object = tsk_time.TSKTime(
            fraction_of_second=fraction_of_second, timestamp=1281643591
        )
        expected_serializable_dict = {
            "__class_name__": "TSKTime",
            "__type__": "DateTimeValues",
            "fraction_of_second": fraction_of_second,
            "timestamp": 1281643591,
        }
        serializable_dict = tsk_time_object.CopyToSerializableDict()
        self.assertEqual(serializable_dict, expected_serializable_dict)

    def testGetDate(self):
        """Tests the GetDate function."""
        if pytsk3.TSK_VERSION_NUM >= 0x040200FF:
            fraction_of_second = 546875000
        else:
            fraction_of_second = 5468750

        tsk_time_object = tsk_time.TSKTime(
            fraction_of_second=fraction_of_second, timestamp=1281643591
        )
        date_tuple = tsk_time_object.GetDate()
        self.assertEqual(date_tuple, (2010, 8, 12))

        tsk_time_object = tsk_time.TSKTime()

        date_tuple = tsk_time_object.GetDate()
        self.assertEqual(date_tuple, (None, None, None))

    def testGetPlasoTimestamp(self):
        """Tests the GetPlasoTimestamp function."""
        if pytsk3.TSK_VERSION_NUM >= 0x040200FF:
            fraction_of_second = 546875000
        else:
            fraction_of_second = 5468750

        tsk_time_object = tsk_time.TSKTime(
            fraction_of_second=fraction_of_second, timestamp=1281643591
        )
        micro_posix_timestamp = tsk_time_object.GetPlasoTimestamp()
        self.assertEqual(micro_posix_timestamp, 1281643591546875)

        tsk_time_object = tsk_time.TSKTime()

        micro_posix_timestamp = tsk_time_object.GetPlasoTimestamp()
        self.assertIsNone(micro_posix_timestamp)


if __name__ == "__main__":
    unittest.main()

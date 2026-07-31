"""The SleuthKit (TSK) timestamp."""

import decimal

from dfdatetime import definitions as dfdatetime_definitions
from dfdatetime import factory as dfdatetime_factory
from dfdatetime import interface as dfdatetime_interface

import pytsk3


class TSKTime(dfdatetime_interface.DateTimeValues):
    """The SleuthKit timestamp.

    Attributes:
      fraction_of_second (int): fraction of second, which is an integer that
          contains the number 100 nanoseconds before Sleuthkit 4.2.0 or
          number of nanoseconds in Sleuthkit 4.2.0 and later.
    """

    _100_NANOSECONDS_PER_SECOND = 10000000
    _NANOSECONDS_PER_SECOND = 1000000000

    def __init__(
        self,
        fraction_of_second=None,
        precision=None,
        time_zone_offset=None,
        timestamp=None,
    ):
        """Initializes a SleuthKit timestamp.

        Args:
          fraction_of_second (Optional[int]): fraction of second, which is
              an integer that contains the number 100 nanoseconds before
              Sleuthkit 4.2.0 or number of nanoseconds in Sleuthkit 4.2.0
              and later.
          precision (Optional[int]): precision of the date and time value, which
              should be one of the PRECISION_VALUES in dfDateTime definitions.
          time_zone_offset (Optional[int]): time zone offset in number of minutes
              from UTC or None if not set.
          timestamp (Optional[int]): POSIX timestamp.
        """
        # Sleuthkit 4.2.0 switched from 100 nanoseconds granularity to
        # 1 nanosecond granularity.
        if pytsk3.TSK_VERSION_NUM >= 0x040200FF:
            granularity = dfdatetime_definitions.PRECISION_1_NANOSECOND
        else:
            granularity = dfdatetime_definitions.PRECISION_100_NANOSECONDS

        super().__init__(
            precision=precision or granularity, time_zone_offset=time_zone_offset
        )
        self._granularity = granularity
        self._timestamp = timestamp
        self.fraction_of_second = fraction_of_second

    @property
    def timestamp(self):
        """int: POSIX timestamp in microseconds or None if timestamp is not set."""
        return self._timestamp

    def _GetNormalizedTimestamp(self):
        """Retrieves the normalized timestamp.

        Returns:
          decimal.Decimal: normalized timestamp, which contains the number of
              seconds since January 1, 1970 00:00:00 and a fraction of second used
              for increased precision, or None if the normalized timestamp cannot be
              determined.
        """
        if self._normalized_timestamp is None:
            if self._timestamp is not None:
                self._normalized_timestamp = decimal.Decimal(self._timestamp)

                if self.fraction_of_second is not None:
                    fraction_of_second = decimal.Decimal(self.fraction_of_second)

                    if (
                        self._granularity
                        == dfdatetime_definitions.PRECISION_1_NANOSECOND
                    ):
                        fraction_of_second /= self._NANOSECONDS_PER_SECOND
                    else:
                        fraction_of_second /= self._100_NANOSECONDS_PER_SECOND

                    self._normalized_timestamp += fraction_of_second

                if self._time_zone_offset:
                    self._normalized_timestamp -= self._time_zone_offset * 60

        return self._normalized_timestamp

    def CopyFromDateTimeString(self, time_string):
        """Copies a SleuthKit timestamp from a date and time string.

        Args:
          time_string (str): date and time value formatted as:
              YYYY-MM-DD hh:mm:ss.######[+-]##:##

              Where # are numeric digits ranging from 0 to 9 and the seconds
              fraction can be either 3, 6 or 9 digits. The time of day, seconds
              fraction and time zone offset are optional. The default time zone
              is UTC.
        """
        date_time_values = self._CopyDateTimeFromString(time_string)

        year = date_time_values.get("year", 0)
        month = date_time_values.get("month", 0)
        day_of_month = date_time_values.get("day_of_month", 0)
        hours = date_time_values.get("hours", 0)
        minutes = date_time_values.get("minutes", 0)
        seconds = date_time_values.get("seconds", 0)
        nanoseconds = date_time_values.get("nanoseconds")
        time_zone_offset = date_time_values.get("time_zone_offset", 0)

        self._timestamp = self._GetNumberOfSecondsFromElements(
            year, month, day_of_month, hours, minutes, seconds
        )

        if nanoseconds is not None:
            self.fraction_of_second = nanoseconds
        else:
            # TODO: kept for backwards compatibility with older dfdatetime versions.
            self.fraction_of_second = date_time_values.get("microseconds", 0) * 1000

        self._precision = dfdatetime_definitions.PRECISION_1_NANOSECOND
        self._time_zone_offset = time_zone_offset

        self._normalized_timestamp = None
        self.is_local_time = False

    def CopyToDateTimeString(self):
        """Copies the date time value to a date and time string.

        Returns:
          str: date and time value formatted as:
              YYYY-MM-DD hh:mm:ss or
              YYYY-MM-DD hh:mm:ss.####### or
              YYYY-MM-DD hh:mm:ss.#########
        """
        if self._timestamp is None:
            return None

        number_of_days, hours, minutes, seconds = self._GetTimeValues(self._timestamp)

        year, month, day_of_month = self._GetDateValues(number_of_days, 1970, 1, 1)

        if self.fraction_of_second is None:
            return (
                f"{year:04d}-{month:02d}-{day_of_month:02d} "
                f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            )

        if self._precision == dfdatetime_definitions.PRECISION_1_NANOSECOND:
            return (
                f"{year:04d}-{month:02d}-{day_of_month:02d} "
                f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                f".{self.fraction_of_second:09d}"
            )

        return (
            f"{year:04d}-{month:02d}-{day_of_month:02d} "
            f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            f".{self.fraction_of_second:07d}"
        )

    def CopyToSerializableDict(self):
        """Copies the date time value to a serializable dictionary.

        Returns:
          dict[str, object]: serializable dictionary.
        """
        serializable_dict = self._CreateSerializableDict()

        serializable_dict["fraction_of_second"] = self.fraction_of_second
        serializable_dict["timestamp"] = self._timestamp

        return serializable_dict

    def GetDate(self):
        """Retrieves the date represented by the date and time values.

        Returns:
           tuple[int, int, int]: year, month, day of month or (None, None, None)
               if the date and time values do not represent a date.
        """
        if self._timestamp is None:
            return None, None, None

        try:
            number_of_days, _, _, _ = self._GetTimeValues(self._timestamp)
            return self._GetDateValues(number_of_days, 1970, 1, 1)
        except ValueError:
            return None, None, None


dfdatetime_factory.Factory.RegisterDateTimeValues(TSKTime)

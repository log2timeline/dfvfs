#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2014 The dfVFS Project Authors.
# Please see the AUTHORS file for details on individual authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""The date and time definitions."""

import calendar
import time


class PosixTimestamp(object):
  """Class that implements a POSIX timestamp."""

  @classmethod
  def FromTimeElements(cls, time_elements_tuple):
    """Copies a timestamp from the time elements tuple."""
    return calendar.timegm(time_elements_tuple)

  @classmethod
  def GetNow(cls):
    """Retrieves the current time (now) as a timestamp in UTC."""
    time_elements = time.gmtime()
    return calendar.timegm(time_elements)

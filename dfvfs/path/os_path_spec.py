#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The dfVFS Project Authors.
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
"""The operating system path specification implementation."""

from dfvfs.lib import definitions
from dfvfs.path import factory
from dfvfs.path import location_path_spec


class OSPathSpec(location_path_spec.LocationPathSpec):
  """Class that implements the operating system path specification."""

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_OS

  def __init__(self, location=None, **kwargs):
    """Initializes the path specification object.

       Note that the operating specific path specification cannot have a parent.

    Args:
      location: optional operating specific location string e.g. /opt/dfvfs or
                C:\\Opt\\dfvfs. The default is None.
      kwargs: a dictionary of keyword arguments dependending on the path
              specification.
    """
    super(OSPathSpec, self).__init__(location=location, parent=None, **kwargs)


# Register the path specification with the factory.
factory.Factory.RegisterPathSpec(OSPathSpec)

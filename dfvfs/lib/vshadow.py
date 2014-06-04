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
"""Helper functions for the Volume Shadow Snapshots (VSS) support."""


def VShadowPathSpecGetStoreIndex(path_spec):
  """Retrieves the store index from the path specification.

  Args:
    path_spec: the path specification (instance of path.PathSpec).
  """
  store_index = getattr(path_spec, 'store_index', None)

  if store_index is None:
    location = getattr(path_spec, 'location', None)

    if location is None or not location.startswith(u'/vss'):
      return

    store_index = None
    try:
      store_index = int(location[4:], 10) - 1
    except ValueError:
      pass

    if store_index is None or store_index < 0:
      return

  return store_index

#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright 2013 The PyVFS Project Authors.
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
"""Sleuthkit (TSK) image object for Volume Shadow Snapshots (VSS)."""

import pytsk3


class VShadowImgInfo(pytsk3.Img_Info):
  """SleuthKit image object (pytsk3.Img_Info) to read VSS volumes."""

  def __init__(self, store):
    """Initializes the VSS image object (pytsk3.Img_Info).

    Args:
      store: The store object (pyvshadow.store) that exposes a Volume
             Shadow Snapshot.
    """
    self._store = store
    super(VShadowImgInfo, self).__init__()

  def close(self):
    """Closes the image object."""
    # TODO: This previously broke pytsk, change if this has been fixed.
    # self._store = None
    pass

  def read(self, offset, size):
    """Reads a byte string from the image object at the specified offset.

    Args:
      offset: The offset where to start reading.
      size: Integer value containing the number of bytes to read.

    Returns:
      A byte string containing the data read.
    """
    self._store.seek(offset)
    return self._store.read(size)

  def get_size(self):
    """Retrieves the size."""
    return self._store.get_size()

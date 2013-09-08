#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright 2012 The Plaso Project Authors.
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
"""This file contains a class to handle opening up files within VSS."""
from pyvfs.vfs import sleuthkit


class VssFile(sleuthkit.TskFile):
  """Class to open up files in Volume Shadow Copies."""
  TYPE = 'VSS'

  def _OpenFileSystem(self, path, offset):
    """Open a filesystem object for a VSS file."""
    if not hasattr(self.pathspec, 'vss_store_number'):
      raise IOError((u'Unable to open VSS file: {%s} -> No VSS store number '
                     'defined.') % self.name)

    if not hasattr(self, '_fscache'):
      raise IOError('No FS cache provided, unable to contine.')

    self._fs_obj = self._fscache.Open(
        path, offset, self.pathspec.vss_store_number)

    self._fs = self._fs_obj.fs

  def Open(self, filehandle=None):
    """Open a VSS file, which is a subset of a TSK file."""
    super(VssFile, self).Open(filehandle)

    self.display_name = u'%s:vss_store_%d' % (
        self.display_name, self.pathspec.vss_store_number)

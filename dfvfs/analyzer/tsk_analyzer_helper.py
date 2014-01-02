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
"""The SleuthKit (TSK) format analyzer helper implementation."""

import pytsk3

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.lib import definitions
from dfvfs.lib import tsk_image


class TSKAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the TSK analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_FILE_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_TSK

  def AnalyzeFileObject(self, file_object):
    """Retrieves the format specification.

    Args:
      file_object: a file-like object (instance of file_io.FileIO).

    Returns:
      The type indicator if the file-like object contains a supported format
      or None otherwise.
    """
    tsk_image_object = tsk_image.TSKFileSystemImage(file_object)

    try:
      _ = pytsk3.FS_Info(tsk_image_object)
    except IOError:
      return

    return self.type_indicator


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(TSKAnalyzerHelper())

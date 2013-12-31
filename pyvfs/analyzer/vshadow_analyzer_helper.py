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
"""The Volume Shadow Snapshots (VSS) format analyzer helper implementation."""

from pyvfs.analyzer import analyzer
from pyvfs.analyzer import analyzer_helper
from pyvfs.analyzer import specification
from pyvfs.lib import definitions


class VShadowAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the VSS analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_VOLUME_SYSTEM])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VSHADOW

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
    format_specification = specification.Specification(self.type_indicator)

    # VSS identifier (GUID).
    format_specification.AddNewSignature(
        '\x6b\x87\x08\x38\x76\xc1\x48\x4e\xb7\xae\x04\x04\x6e\x6c\xc7\x52',
         offset=7680, is_bound=True)

    return format_specification


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(VShadowAnalyzerHelper())

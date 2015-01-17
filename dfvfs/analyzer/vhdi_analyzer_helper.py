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
"""The VHDI format analyzer helper implementation."""

from dfvfs.analyzer import analyzer
from dfvfs.analyzer import analyzer_helper
from dfvfs.analyzer import specification
from dfvfs.lib import definitions


class VhdiAnalyzerHelper(analyzer_helper.AnalyzerHelper):
  """Class that implements the VHDI analyzer helper."""

  FORMAT_CATEGORIES = frozenset([
      definitions.FORMAT_CATEGORY_STORAGE_MEDIA_IMAGE])

  TYPE_INDICATOR = definitions.TYPE_INDICATOR_VHDI

  def GetFormatSpecification(self):
    """Retrieves the format specification."""
    format_specification = specification.Specification(self.type_indicator)

    # VHDI image signature in footer.
    format_specification.AddNewSignature(b'conectix', offset=-512)

    # VHDI image signature in copy of footer in differential
    # or dynamic disk image.
    format_specification.AddNewSignature(b'conectix', offset=0)

    return format_specification


# Register the analyzer helpers with the analyzer.
analyzer.Analyzer.RegisterHelper(VhdiAnalyzerHelper())
